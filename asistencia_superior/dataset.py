"""Construcción del dataset del proyecto a partir de los microdatos de la EPH (INDEC).

Pasos:
1. Lee las bases de personas (usu_individual_*) y de hogares (usu_hogar_*) de los cuatro
   trimestres guardados en data/raw.
2. Agrega a cada persona los datos de su hogar y los del jefe o jefa de hogar.
3. Delimita la población: jóvenes de 18 a 24 años con secundario completo que no
   terminaron un estudio superior (NIVEL_ED 4 o 5).
4. Construye la variable objetivo `asiste_superior` con CH10 y CH12.
5. Guarda todas las observaciones en data/interim y una fila por persona
   (la observación más reciente) en data/processed.

Uso:  python asistencia_superior/dataset.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

from asistencia_superior.config import INTERIM_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR

TRIMESTRES = ["T225", "T325", "T425", "T126"]

# Claves de vinculación
CLAVE_HOGAR = ["CODUSU", "NRO_HOGAR", "ANO4", "TRIMESTRE"]
CLAVE_PERSONA = ["CODUSU", "NRO_HOGAR", "COMPONENTE"]

# Variables de la base de hogares que se agregan a cada joven
VARIABLES_HOGAR = ["IV1", "II1", "II7", "IX_TOT", "IX_MEN10"]

# Variables usadas solo para delimitar la población y construir la respuesta.
# No se guardan en el dataset procesado para que no se usen como predictoras.
VARIABLES_SOLO_RESPUESTA = ["CH10", "CH12", "NIVEL_ED"]

# Variables excluidas del dataset procesado por fuga de información:
# - educativas derivadas: NIVEL_ED, CH11, CH13, CH14, CAT_INAC
# - montos de beca de estudio (V11_01_M, V11_02_M) y cuota alimentaria (V12_M) del joven,
#   que en los datos aparecen casi solo entre quienes estudian.
# El ingreso del hogar se usa sin los ingresos propios del joven (ver ingreso_resto_hogar_pc).


def leer_eph(ruta: Path) -> pd.DataFrame:
    """Lee un archivo usu_*.txt de la EPH (separador ';', con o sin comillas)."""
    return pd.read_csv(ruta, sep=";", low_memory=False)


def cargar_trimestres(raw_dir: Path = RAW_DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    personas = pd.concat(
        [leer_eph(raw_dir / f"usu_individual_{t}.txt") for t in TRIMESTRES], ignore_index=True
    )
    hogares = pd.concat(
        [leer_eph(raw_dir / f"usu_hogar_{t}.txt") for t in TRIMESTRES], ignore_index=True
    )
    return personas, hogares


def datos_del_jefe(personas: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con nivel educativo, sexo y condición de actividad del jefe/a (CH03 == 1)."""
    jefes = personas.loc[personas["CH03"] == 1, CLAVE_HOGAR + ["NIVEL_ED", "CH04", "ESTADO"]]
    return jefes.rename(
        columns={"NIVEL_ED": "jefe_nivel_ed", "CH04": "jefe_sexo", "ESTADO": "jefe_estado"}
    ).drop_duplicates(CLAVE_HOGAR)


def construir_observaciones(personas: pd.DataFrame, hogares: pd.DataFrame) -> pd.DataFrame:
    """Población de estudio con la variable objetivo (todas las observaciones del panel)."""
    poblacion = personas[personas["CH06"].between(18, 24) & personas["NIVEL_ED"].isin([4, 5])].copy()

    # Variable objetivo: asiste actualmente (CH10 = 1) a terciario, universitario o posgrado (CH12 = 6, 7, 8)
    poblacion["asiste_superior"] = (
        (poblacion["CH10"] == 1) & poblacion["CH12"].isin([6, 7, 8])
    ).astype(int)

    # Datos del hogar
    poblacion = poblacion.merge(
        hogares[CLAVE_HOGAR + VARIABLES_HOGAR], on=CLAVE_HOGAR, how="left", validate="m:1"
    )

    # Datos del jefe o jefa de hogar. Si el joven es el jefe/a (o su cónyuge), la educación
    # del jefe/a sería su propia educación (o la de su pareja): se marca como "no aplica".
    poblacion = poblacion.merge(datos_del_jefe(personas), on=CLAVE_HOGAR, how="left", validate="m:1")
    poblacion["es_jefe_o_conyuge"] = poblacion["CH03"].isin([1, 2]).astype(int)
    for col in ["jefe_nivel_ed", "jefe_sexo", "jefe_estado"]:
        poblacion.loc[poblacion["es_jefe_o_conyuge"] == 1, col] = np.nan

    # Ingresos: ITF = 0 y DECCFR = 12 indican hogar sin respuesta de ingresos (no ingreso cero).
    sin_respuesta = poblacion["DECCFR"] == 12
    poblacion["ingresos_sin_respuesta"] = sin_respuesta.astype(int)
    ingreso_propio = poblacion["P47T"].where(poblacion["P47T"] >= 0)
    resto = (poblacion["ITF"] - ingreso_propio).where(~sin_respuesta)
    otros_miembros = (poblacion["IX_TOT"] - 1).replace(0, np.nan)
    poblacion["ingreso_resto_hogar_pc"] = (resto / otros_miembros).clip(lower=0)
    poblacion.loc[poblacion["IX_TOT"] == 1, "ingreso_resto_hogar_pc"] = 0.0

    # Hacinamiento: personas por ambiente de uso exclusivo del hogar
    poblacion["personas_por_ambiente"] = poblacion["IX_TOT"] / poblacion["II1"].where(
        poblacion["II1"] > 0
    )
    poblacion["trimestre_id"] = (
        poblacion["ANO4"].astype(str) + "T" + poblacion["TRIMESTRE"].astype(str)
    )
    return poblacion


COLUMNAS_PROCESADAS = {
    # identificación y diseño muestral
    "CODUSU": "codusu",
    "NRO_HOGAR": "nro_hogar",
    "COMPONENTE": "componente",
    "trimestre_id": "trimestre",
    "PONDERA": "ponderador",
    # variable objetivo
    "asiste_superior": "asiste_superior",
    # joven
    "CH04": "sexo",
    "CH06": "edad",
    "CH03": "parentesco_jefe",
    "es_jefe_o_conyuge": "es_jefe_o_conyuge",
    "CH07": "estado_civil",
    "CH08": "cobertura_salud",
    "CH15": "lugar_nacimiento",
    "ESTADO": "condicion_actividad",
    # hogar
    "IX_TOT": "personas_hogar",
    "IX_MEN10": "menores_10_hogar",
    "personas_por_ambiente": "personas_por_ambiente",
    "IV1": "tipo_vivienda",
    "II7": "tenencia_vivienda",
    "ingreso_resto_hogar_pc": "ingreso_resto_hogar_pc",
    "ingresos_sin_respuesta": "ingresos_sin_respuesta",
    # jefe o jefa de hogar
    "jefe_nivel_ed": "jefe_nivel_educativo",
    "jefe_sexo": "jefe_sexo",
    "jefe_estado": "jefe_condicion_actividad",
    # ubicación
    "REGION": "region",
    "AGLOMERADO": "aglomerado",
}


def una_fila_por_persona(observaciones: pd.DataFrame) -> pd.DataFrame:
    """La EPH es un panel: se conserva la observación más reciente de cada persona."""
    ordenadas = observaciones.sort_values(["ANO4", "TRIMESTRE"])
    return ordenadas.drop_duplicates(CLAVE_PERSONA, keep="last")


def main(
    raw_dir: Path = RAW_DATA_DIR,
    interim_path: Path = INTERIM_DATA_DIR / "eph_jovenes_18a24_todas_las_observaciones.csv",
    output_path: Path = PROCESSED_DATA_DIR / "eph_jovenes_asistencia_superior.csv",
) -> pd.DataFrame:
    personas, hogares = cargar_trimestres(raw_dir)
    observaciones = construir_observaciones(personas, hogares)
    columnas_interim = (
        ["ANO4", "TRIMESTRE"] + list(COLUMNAS_PROCESADAS)
        + VARIABLES_SOLO_RESPUESTA + ["P47T", "ITF", "IPCF", "DECCFR", "II1"]
    )
    observaciones[list(dict.fromkeys(columnas_interim))].to_csv(interim_path, index=False)

    dataset = una_fila_por_persona(observaciones)[list(COLUMNAS_PROCESADAS)].rename(
        columns=COLUMNAS_PROCESADAS
    )
    dataset.to_csv(output_path, index=False)
    print(f"Observaciones: {len(observaciones):,} | Personas únicas: {len(dataset):,}")
    print(f"Guardado en {output_path}")
    return dataset


if __name__ == "__main__":
    main()

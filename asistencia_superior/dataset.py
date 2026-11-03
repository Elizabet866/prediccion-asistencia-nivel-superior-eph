"""Construcción del dataset del proyecto a partir de los microdatos de la EPH (INDEC).

Pasos:
1. Lee las bases de personas (usu_individual_*) y de hogares (usu_hogar_*) de los cuatro
   trimestres guardados en data/raw.
2. Delimita la población: jóvenes de 18 a 24 años con secundario completo que no
   terminaron un estudio superior (NIVEL_ED 4 o 5).
3. Construye la variable objetivo `asiste_superior` con CH10 y CH12 y excluye las
   observaciones cuya asistencia no puede determinarse (sin dato en CH10 o CH12).
4. Agrega a cada joven los datos de su hogar y los del jefe o jefa de hogar.
5. Clasifica la situación del ingreso del resto del hogar y calcula su percentil dentro de la
   distribución de ingresos de su propio trimestre (medida comparable entre trimestres).
6. Conserva una observación por persona (la más reciente con respuesta válida).
7. Asigna la partición temporal (entrenamiento 2025 / prueba 1T 2026) y marca como excluidos
   de entrenamiento a los jóvenes de viviendas que también tienen jóvenes en prueba.

Uso:  python asistencia_superior/dataset.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

from asistencia_superior.config import INTERIM_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR

TRIMESTRES = ["T225", "T325", "T425", "T126"]
TRIMESTRE_PRUEBA = "2026T1"

# Claves de vinculación
CLAVE_HOGAR = ["CODUSU", "NRO_HOGAR", "ANO4", "TRIMESTRE"]
CLAVE_PERSONA = ["CODUSU", "NRO_HOGAR", "COMPONENTE"]

# Variables de la base de hogares que se agregan a cada joven
VARIABLES_HOGAR = ["IV1", "II1", "II7", "IX_TOT", "IX_MEN10"]

# Variables usadas solo para delimitar la población y construir la respuesta.
# No se guardan en el dataset procesado para que no se usen como predictoras.
VARIABLES_SOLO_RESPUESTA = ["CH10", "CH12", "NIVEL_ED"]

# Variables excluidas por fuga de información (ver docs/informe_dataset.md, sección 6):
# - CH10, CH12, NIVEL_ED, CH11, CH13, CH14: preguntas educativas del propio joven;
# - CAT_INAC: su categoría 3 es "Estudiante", es decir, la respuesta misma;
# - V11_01_M, V11_02_M: becas de estudio (requieren estar estudiando);
# - V12_M: cuotas de alimentos o ayuda de personas que no viven en el hogar (puede depender de
#   que el joven estudie). El ingreso del hogar se usa sin los ingresos propios del joven.


def leer_eph(ruta: Path) -> pd.DataFrame:
    """Lee un archivo usu_*.txt de la EPH (separador ';', con o sin comillas, coma decimal)."""
    return pd.read_csv(ruta, sep=";", decimal=",", low_memory=False)


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


def percentil_en_trimestre(valores: pd.Series, trimestre: pd.Series, personas: pd.DataFrame) -> pd.Series:
    """Percentil (0-100) de cada valor dentro de la distribución ponderada del ingreso per cápita
    familiar (IPCF, ponderador PONDIH) de todas las personas con respuesta de ingresos de su trimestre."""
    resultado = pd.Series(np.nan, index=valores.index)
    respondieron = personas[personas["DECCFR"].between(0, 10)]
    for clave, grupo in respondieron.groupby(["ANO4", "TRIMESTRE"]):
        id_trimestre = f"{clave[0]}T{clave[1]}"
        orden = grupo.sort_values("IPCF")
        acumulado = orden["PONDIH"].cumsum().to_numpy() / orden["PONDIH"].sum()
        filas = (trimestre == id_trimestre) & valores.notna()
        posicion = np.searchsorted(orden["IPCF"].to_numpy(), valores[filas].to_numpy(), side="right")
        resultado[filas] = np.where(posicion > 0, acumulado[np.maximum(posicion - 1, 0)], 0.0) * 100
    return resultado


def construir_observaciones(personas: pd.DataFrame, hogares: pd.DataFrame) -> pd.DataFrame:
    """Población de estudio con la variable objetivo (todas las observaciones del panel)."""
    poblacion = personas[personas["CH06"].between(18, 24) & personas["NIVEL_ED"].isin([4, 5])].copy()

    # Variable objetivo: asiste actualmente (CH10 = 1) a terciario, universitario o posgrado (CH12 = 6, 7, 8)
    poblacion["asiste_superior"] = (
        (poblacion["CH10"] == 1) & poblacion["CH12"].isin([6, 7, 8])
    ).astype(int)
    # Respuesta conocida: CH10 con un código válido y, si asiste, un nivel válido en CH12
    poblacion["respuesta_conocida"] = (
        poblacion["CH10"].isin([1, 2, 3])
        & ~((poblacion["CH10"] == 1) & ~poblacion["CH12"].between(1, 9))
    ).astype(int)

    # Datos del hogar
    poblacion = poblacion.merge(
        hogares[CLAVE_HOGAR + VARIABLES_HOGAR], on=CLAVE_HOGAR, how="left", validate="m:1"
    )

    # Datos del jefe o jefa de hogar. Si el joven es el propio jefe/a, la "educación del jefe/a"
    # sería su propia educación: queda vacía ("no aplica"). Para el cónyuge se conservan,
    # porque corresponden a otra persona (su pareja).
    poblacion = poblacion.merge(datos_del_jefe(personas), on=CLAVE_HOGAR, how="left", validate="m:1")
    poblacion["es_jefe_hogar"] = (poblacion["CH03"] == 1).astype(int)
    for col in ["jefe_nivel_ed", "jefe_sexo", "jefe_estado"]:
        poblacion.loc[poblacion["es_jefe_hogar"] == 1, col] = np.nan

    poblacion["trimestre_id"] = (
        poblacion["ANO4"].astype(str) + "T" + poblacion["TRIMESTRE"].astype(str)
    )

    # Ingreso del resto del hogar: cuatro situaciones distintas
    vive_solo = poblacion["IX_TOT"] == 1
    sin_respuesta = poblacion["DECCFR"] == 12            # "no respuesta de ingresos" (diseño de registro)
    ingreso_propio = poblacion["P47T"].where(poblacion["P47T"] >= 0)
    resto = poblacion["ITF"] - ingreso_propio
    assert (resto[~sin_respuesta & ~vive_solo] >= 0).all(), "Ingreso del resto del hogar negativo"
    poblacion["ingreso_resto_hogar_pc"] = (resto / (poblacion["IX_TOT"] - 1)).where(~sin_respuesta & ~vive_solo)
    poblacion["situacion_ingreso_resto"] = np.select(
        [vive_solo, sin_respuesta, poblacion["ingreso_resto_hogar_pc"] == 0],
        ["no_aplica_vive_solo", "sin_respuesta", "cero_observado"],
        default="positivo",
    )
    poblacion["percentil_ingreso_resto"] = percentil_en_trimestre(
        poblacion["ingreso_resto_hogar_pc"], poblacion["trimestre_id"], personas
    )

    # Hacinamiento: personas por ambiente de uso exclusivo del hogar
    poblacion["personas_por_ambiente"] = poblacion["IX_TOT"] / poblacion["II1"].where(
        poblacion["II1"] > 0
    )
    return poblacion


def una_fila_por_persona(observaciones: pd.DataFrame) -> pd.DataFrame:
    """La EPH es un panel: se conserva la observación más reciente de cada persona,
    entre las que tienen la respuesta conocida."""
    validas = observaciones[observaciones["respuesta_conocida"] == 1]
    return validas.sort_values(["ANO4", "TRIMESTRE"]).drop_duplicates(CLAVE_PERSONA, keep="last")


def asignar_particion(dataset: pd.DataFrame) -> pd.Series:
    """Partición temporal. Los jóvenes de 2025 que viven en una vivienda (CODUSU) que también
    tiene jóvenes en la prueba se excluyen del entrenamiento."""
    es_prueba = dataset["trimestre_id"] == TRIMESTRE_PRUEBA
    viviendas_prueba = set(dataset.loc[es_prueba, "CODUSU"])
    compartida = ~es_prueba & dataset["CODUSU"].isin(viviendas_prueba)
    return pd.Series(
        np.select([es_prueba, compartida], ["prueba", "excluida_vivienda_en_prueba"], "entrenamiento"),
        index=dataset.index,
    )


COLUMNAS_PROCESADAS = {
    # identificación, partición y diseño muestral
    "CODUSU": "codusu",
    "NRO_HOGAR": "nro_hogar",
    "COMPONENTE": "componente",
    "trimestre_id": "trimestre",
    "particion": "particion",
    "PONDERA": "ponderador",
    # variable objetivo
    "asiste_superior": "asiste_superior",
    # joven
    "CH04": "sexo",
    "CH06": "edad",
    "CH03": "parentesco_jefe",
    "es_jefe_hogar": "es_jefe_hogar",
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
    "situacion_ingreso_resto": "situacion_ingreso_resto",
    "ingreso_resto_hogar_pc": "ingreso_resto_hogar_pc",
    "percentil_ingreso_resto": "percentil_ingreso_resto",
    # jefe o jefa de hogar
    "jefe_nivel_ed": "jefe_nivel_educativo",
    "jefe_sexo": "jefe_sexo",
    "jefe_estado": "jefe_condicion_actividad",
    # ubicación
    "REGION": "region",
    "AGLOMERADO": "aglomerado",
}


def main(
    raw_dir: Path = RAW_DATA_DIR,
    interim_path: Path = INTERIM_DATA_DIR / "eph_jovenes_18a24_todas_las_observaciones.csv",
    output_path: Path = PROCESSED_DATA_DIR / "eph_jovenes_asistencia_superior.csv",
) -> pd.DataFrame:
    personas, hogares = cargar_trimestres(raw_dir)
    observaciones = construir_observaciones(personas, hogares)
    columnas_interim = (
        ["ANO4", "TRIMESTRE", "respuesta_conocida"]
        + [c for c in COLUMNAS_PROCESADAS if c != "particion"]
        + VARIABLES_SOLO_RESPUESTA + ["P47T", "ITF", "IPCF", "DECCFR", "II1"]
    )
    observaciones[list(dict.fromkeys(columnas_interim))].to_csv(interim_path, index=False)

    personas_unicas = una_fila_por_persona(observaciones)
    personas_unicas["particion"] = asignar_particion(personas_unicas)
    dataset = personas_unicas[list(COLUMNAS_PROCESADAS)].rename(columns=COLUMNAS_PROCESADAS)
    dataset.to_csv(output_path, index=False)
    print(f"Observaciones: {len(observaciones):,} | Personas con respuesta conocida: {len(dataset):,}")
    print(dataset["particion"].value_counts().to_string())
    print(f"Guardado en {output_path}")
    return dataset


if __name__ == "__main__":
    main()

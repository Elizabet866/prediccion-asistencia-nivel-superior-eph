# Predicción de la asistencia al nivel superior en jóvenes (EPH – INDEC)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Proyecto de Aprendizaje Automático que busca predecir si un joven de 18 a 24 años con secundario completo **asiste actualmente** a un estudio superior (terciario o universitario), a partir de sus características personales y las de su hogar, usando los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC.

- **Autora:** Liliana Elizabeth Iñigo
- **Materia:** Aprendizaje Automático · **Docente:** Nicolás Caballero
- **Tipo de problema:** clasificación binaria supervisada
- **Descripción completa del proyecto y objetivos:** [docs/descripcion_y_objetivos.md](docs/descripcion_y_objetivos.md)

---

## Planteo de la predicción

### Variable objetivo: `asiste_superior`

| Valor | Significado |
|---|---|
| `1` | El joven **asiste actualmente** a un estudio superior (terciario, universitario o posgrado) |
| `0` | El joven **no asiste actualmente** al nivel superior |

Se construye con dos preguntas de la EPH: `CH10 = 1` (asiste a un establecimiento educativo) y `CH12` = 6, 7 u 8 (el nivel que cursa es terciario, universitario o posgrado).

### Qué representa cada fila

**Cada fila es un joven** de 18 a 24 años con secundario completo y sin un estudio superior terminado, que vive en uno de los aglomerados urbanos relevados por la EPH. Los datos describen su situación y la de su hogar **en el trimestre en que fue encuestado**. Si el joven fue encuestado en dos trimestres, queda solo la observación más reciente, para que cada persona aparezca una sola vez.

### Cuándo se hace la predicción y con qué información

La predicción se hace **en el momento de la encuesta**, con datos del joven y de su hogar que **pueden conocerse sin saber si asiste o no**:

- **Disponibles (predictoras):** edad, sexo, parentesco con el jefe/a, estado civil, cobertura de salud, lugar de nacimiento, composición y vivienda del hogar, ingreso del resto del hogar, educación y situación laboral del jefe/a, región y aglomerado.
- **No disponibles (excluidas por fuga de información):** todo lo que ya contiene la respuesta o es consecuencia de estudiar: nivel educativo del propio joven (`NIVEL_ED`), las preguntas educativas (`CH10` a `CH14`), la categoría de inactividad "estudiante" (`CAT_INAC`), las becas de estudio y la cuota alimentaria.
- **Zona gris:** la condición de actividad del joven (ocupado, desocupado, inactivo) se registra al mismo tiempo que la asistencia y puede ser en parte consecuencia de estudiar. Se probarán los modelos con y sin esta variable.

### Los dos tiempos del modelo

| Momento | Qué se hace | Con qué datos |
|---|---|---|
| **1. Uso de la predicción** | Estimar si un joven asiste al nivel superior a partir de sus características y las de su hogar. Por ejemplo, para identificar perfiles con menor asistencia y orientar acompañamientos o becas. | Las variables disponibles del joven y su hogar, sin información educativa propia. |
| **2. Evaluación y reentrenamiento** | Comparar las predicciones con la realidad y corregir o reentrenar el modelo. | El INDEC publica una nueva base de la EPH cada trimestre con la respuesta real (`CH10`, `CH12`). Con cada publicación se puede medir si el modelo sigue acertando y reentrenarlo con los datos nuevos. |

Para simular este segundo momento en la Entrega 3, se puede **entrenar con los trimestres de 2025 y evaluar con el 1T 2026**: el modelo se prueba con datos "del futuro" respecto de lo que aprendió. Como cada persona aparece una sola vez, ningún joven queda a la vez en entrenamiento y en prueba.

---

## Origen de los datos

| | |
|---|---|
| **Fuente** | Encuesta Permanente de Hogares (EPH), modalidad continua – Instituto Nacional de Estadística y Censos (INDEC) |
| **Descarga** | https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos |
| **Trimestres** | 2.º, 3.º y 4.º trimestre de 2025 y 1.er trimestre de 2026 (los cuatro más recientes publicados) |
| **Fecha de descarga** | 22 de octubre de 2026 |
| **Cómo se recopilan** | Encuesta por muestreo a hogares, realizada por el INDEC en forma continua. Cada hogar se entrevista en varios trimestres (panel rotativo) |
| **Cobertura** | 31 aglomerados urbanos del país (32 códigos, porque el Gran Buenos Aires se divide en CABA y partidos del conurbano). No incluye población rural |
| **Formato original** | Texto separado por `;`, una base de personas y una de hogares por trimestre |
| **Uso** | Datos públicos; se cita la fuente |

### Archivos originales (`data/raw/`)

| Archivo | Contenido | Filas | Columnas |
|---|---|---:|---:|
| `usu_individual_T225.txt` | Personas, 2T 2025 | 46.086 | 235 |
| `usu_individual_T325.txt` | Personas, 3T 2025 | 44.946 | 235 |
| `usu_individual_T425.txt` | Personas, 4T 2025 | 43.703 | 235 |
| `usu_individual_T126.txt` | Personas, 1T 2026 | 43.739 | 234 |
| `usu_hogar_T225.txt` | Hogares, 2T 2025 | 16.169 | 98 |
| `usu_hogar_T325.txt` | Hogares, 3T 2025 | 15.860 | 98 |
| `usu_hogar_T425.txt` | Hogares, 4T 2025 | 15.534 | 98 |
| `usu_hogar_T126.txt` | Hogares, 1T 2026 | 15.447 | 98 |

En total: **178.474 registros de personas** y **63.010 de hogares**. La base de personas del 1T 2026 no trae la columna `CAT_INAC` (cambio en el diseño de registro del INDEC); no afecta al proyecto porque esa variable se excluye.

---

## Preprocesamiento

Todo el proceso está documentado paso a paso en la notebook [`notebooks/1.0-lei-descripcion-dataset-eph.ipynb`](notebooks/1.0-lei-descripcion-dataset-eph.ipynb) y se puede reproducir con el script [`asistencia_superior/dataset.py`](asistencia_superior/dataset.py).

1. **Unión de los cuatro trimestres** de cada base.
2. **Vinculación persona – hogar** con `CODUSU` + `NRO_HOGAR` + `ANO4` + `TRIMESTRE` (100 % de coincidencia).
3. **Vinculación con el jefe o jefa de hogar:** persona del mismo hogar con `CH03 = 1` (100 % de los hogares tiene uno). Si el joven es jefe/a o cónyuge, los datos del jefe/a quedan vacíos y se marca `es_jefe_o_conyuge = 1`.
4. **Población de estudio:** edad (`CH06`) entre 18 y 24 años y `NIVEL_ED` = 4 (secundario completo) o 5 (superior incompleto). Se incluye el 5 porque quien cursa el superior figura con ese código. Se excluye el 6 (superior completo, 502 observaciones). Resultado: **13.883 observaciones**.
5. **Variable objetivo `asiste_superior`:** 1 si `CH10 = 1` (asiste) y `CH12` = 6, 7 u 8 (terciario, universitario o posgrado); 0 en otro caso. Mide la asistencia **en el momento de la encuesta**.
6. **Ingresos:** cuando el hogar no responde ingresos, la EPH registra `ITF = 0` y `DECCFR = 12`; se marcan con `ingresos_sin_respuesta = 1` y el ingreso queda vacío. Se calcula el **ingreso per cápita del resto del hogar**, sin los ingresos propios del joven (que incluyen becas de estudio).
7. **Panel:** la misma persona puede aparecer en dos trimestres. Se conserva **una fila por persona** (la observación más reciente): **9.665 personas**.
8. **Exclusión de variables con fuga de información:** `CH10`, `CH12`, `NIVEL_ED`, `CH11`, `CH13`, `CH14`, `CAT_INAC`, montos de beca de estudio (`V11_01_M`, `V11_02_M`) y cuota alimentaria (`V12_M`). La revisión con datos está en la sección 7 de la notebook.

---

## Descripción del dataset

Archivo principal: [`data/processed/eph_jovenes_asistencia_superior.csv`](data/processed/eph_jovenes_asistencia_superior.csv)

- **Instancias:** 9.665 personas (una fila por persona)
- **Columnas:** 26 → 5 de identificación y diseño muestral, 1 variable objetivo y 20 predictoras candidatas
- **Clases:** `asiste_superior = 1`: **5.299 (54,8 %)** · `asiste_superior = 0`: **4.366 (45,2 %)** → clases equilibradas

<img src="reports/figures/balance_clases.png" width="420" alt="Balance de clases">

| Columna | Tipo | Rol | Faltantes |
|---|---|---|---:|
| `codusu`, `nro_hogar`, `componente` | texto / entero | identificación de la persona | 0 |
| `trimestre` | texto | trimestre de la observación | 0 |
| `ponderador` | entero | factor de expansión (no predictora) | 0 |
| `asiste_superior` | binaria | **variable objetivo** | 0 |
| `sexo`, `parentesco_jefe`, `estado_civil`, `cobertura_salud`, `lugar_nacimiento`, `condicion_actividad` | categóricas (códigos) | predictoras del joven | 0 |
| `edad` | numérica discreta | predictora del joven | 0 |
| `es_jefe_o_conyuge` | binaria | predictora del joven | 0 |
| `personas_hogar`, `menores_10_hogar` | numéricas discretas | predictoras del hogar | 0 |
| `personas_por_ambiente` | numérica continua | predictora del hogar (hacinamiento) | 4 |
| `tipo_vivienda`, `tenencia_vivienda` | categóricas (códigos) | predictoras del hogar | 0 |
| `ingreso_resto_hogar_pc` | numérica continua (pesos) | predictora del hogar | 2.784 (hogares sin respuesta de ingresos) |
| `ingresos_sin_respuesta` | binaria | predictora del hogar | 0 |
| `jefe_nivel_educativo`, `jefe_sexo`, `jefe_condicion_actividad` | categóricas (códigos) | predictoras del jefe/a | 1.337 (jóvenes que son jefe/a o cónyuge) |
| `region`, `aglomerado` | categóricas (códigos) | ubicación | 0 |

Códigos y significado de cada variable: [`references/diccionario_variables.md`](references/diccionario_variables.md).

Archivo intermedio: [`data/interim/eph_jovenes_18a24_todas_las_observaciones.csv`](data/interim/eph_jovenes_18a24_todas_las_observaciones.csv) — las 13.883 observaciones antes de quitar repetidos del panel, con las variables usadas para construir la respuesta (`CH10`, `CH12`, `NIVEL_ED`) para poder verificarla.

### Observaciones para las próximas etapas

- `condicion_actividad` no es un indicador educativo, pero se mide al mismo tiempo que la asistencia (muchos jóvenes son inactivos *porque* estudian). Se compararán los modelos con y sin esta variable.
- Los faltantes de ingreso se imputarán dentro del pipeline de preparación (clase 3), sin usar información del conjunto de prueba.
- El análisis no usa el ponderador para entrenar; se usará solo si se calculan porcentajes poblacionales en el análisis exploratorio.

---

## Cómo reproducir

```bash
# 1. Crear el entorno (Anaconda)
conda create --name prediccion-asistencia-nivel-superior-eph python=3.12 -y
conda activate prediccion-asistencia-nivel-superior-eph

# 2. Instalar dependencias (incluye este proyecto como paquete)
pip install -r requirements.txt

# 3. Generar data/interim y data/processed a partir de data/raw
python asistencia_superior/dataset.py
```

También se puede abrir y ejecutar la notebook de `notebooks/` con Jupyter.

---

## Organización del proyecto

Estructura generada con la plantilla [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science) (versión 2).

```
├── LICENSE            <- Licencia MIT
├── Makefile           <- Comandos útiles (`make data`, `make requirements`)
├── README.md          <- Este documento
├── data
│   ├── external       <- Datos de terceros (sin uso por ahora)
│   ├── interim        <- Población de estudio con todas las observaciones del panel
│   ├── processed      <- Dataset final para modelar (una fila por persona)
│   └── raw            <- Bases originales de la EPH, sin modificar
│
├── docs               <- Descripción del proyecto, objetivos y ajustes por devoluciones
│
├── models             <- Modelos entrenados (Entrega 3)
│
├── notebooks          <- Notebooks numeradas: número, iniciales de la autora y descripción
│                         (ej. `1.0-lei-descripcion-dataset-eph`)
│
├── pyproject.toml     <- Configuración del paquete `asistencia_superior` y de ruff
│
├── references         <- Diccionario de variables
│
├── reports
│   └── figures        <- Gráficos generados
│
├── requirements.txt   <- Dependencias para reproducir el análisis
│
└── asistencia_superior   <- Código fuente del proyecto
    ├── __init__.py
    ├── config.py               <- Rutas del proyecto
    ├── dataset.py              <- Construcción del dataset a partir de data/raw
    ├── features.py             <- Preparación de variables (Entrega 3)
    ├── modeling
    │   ├── predict.py          <- Predicción con modelos entrenados (Entrega 3)
    │   └── train.py            <- Entrenamiento de modelos (Entrega 3)
    └── plots.py                <- Gráficos (Entrega 3)
```

## Estado de las entregas

| Entrega | Contenido | Estado |
|---|---|---|
| 1 | Descripción y formulación del objetivo | Entregada en el campus (PDF). Versión con ajustes en [docs/](docs/descripcion_y_objetivos.md) |
| 2 | Descripción del dataset y origen | Este repositorio |
| 3 | Modelo, análisis de resultados y video | Pendiente |

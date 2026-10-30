# Predicción de la asistencia al nivel superior en jóvenes (EPH – INDEC)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Proyecto de Aprendizaje Automático que busca predecir si un joven de 18 a 24 años con secundario completo **asiste actualmente** a un estudio superior (terciario o universitario), a partir de sus características personales y las de su hogar, usando los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC.

- **Autora:** Liliana Elizabeth Iñigo
- **Materia:** Aprendizaje Automático
- **Docente:** Nicolás Caballero
- **Tipo de problema:** clasificación binaria supervisada

## Contenido

1. [Descripción del proyecto y objetivos](#1-descripción-del-proyecto-y-objetivos)
2. [Planteo de la predicción](#2-planteo-de-la-predicción)
3. [Datos](#3-datos)
4. [Dónde encontrar cada parte del trabajo](#4-dónde-encontrar-cada-parte-del-trabajo)
5. [Cómo reproducir](#5-cómo-reproducir)
6. [Organización del proyecto](#6-organización-del-proyecto)

---

## 1. Descripción del proyecto y objetivos

> Contenido de la primera entrega, actualizado con la devolución del docente. El detalle de cada ajuste está en [docs/ajustes_devolucion_entrega1.md](docs/ajustes_devolucion_entrega1.md).

### Contexto y relevancia del problema

La transición entre la escuela secundaria y los estudios superiores (terciarios o universitarios) es una etapa decisiva en la trayectoria de los jóvenes. Aunque finalizar la secundaria es un logro fundamental, la asistencia a estudios superiores suele estar muy vinculada con las condiciones socioeconómicas del hogar: los ingresos de la familia, el nivel educativo de quien está a cargo del hogar y la región del país donde viven.

El aprendizaje automático permite analizar en conjunto estos factores y estimar, a partir de las características de un joven y de su hogar, si **asiste actualmente** al nivel superior. El modelo describe la situación en el momento de la encuesta: no predice una decisión futura. Identificar qué perfiles tienen menor asistencia resulta valioso para pensar intervenciones educativas y focalizar acompañamientos, tutorías o becas de estudio.

A diferencia de proyectos anteriores del repositorio del Politécnico enfocados en la deserción escolar en el secundario o en la inserción laboral, este trabajo hace foco en una subpoblación puntual: quienes ya completaron el nivel medio y todavía no terminaron un estudio superior.

La EPH releva **31 aglomerados urbanos**, por lo que los resultados corresponden a los jóvenes que viven en esos aglomerados y no a toda la población joven del país.

### Objetivo general

Desarrollar un modelo de clasificación supervisada que permita predecir la asistencia al nivel superior en jóvenes de 18 a 24 años con secundario completo, residentes en los aglomerados urbanos relevados por la EPH, a partir de variables individuales y del hogar.

### Objetivos específicos

1. **Delimitar la población de estudio:** filtrar y acondicionar la base de microdatos de la EPH para trabajar con jóvenes de 18 a 24 años que declararon tener el secundario completo.
2. **Preparar las variables del estudio:** construir indicadores de contexto individual y del hogar a partir de los registros de la encuesta (por ejemplo, nivel educativo del jefe o jefa de hogar, tramos de ingresos familiares o región geográfica).
3. **Entrenar y ajustar modelos supervisados:** entrenar algoritmos de clasificación vistos durante la cursada y ajustar sus hiperparámetros, mediante técnicas de partición y validación de datos.
4. **Evaluar e interpretar los resultados:** comparar el rendimiento de los modelos entrenados e identificar cuáles son las características que tienen mayor peso en la predicción.

### Tipo de problema

**Clasificación binaria supervisada.** La variable objetivo `asiste_superior` toma dos valores: 1 (asiste actualmente al nivel superior) y 0 (no asiste actualmente). Su construcción se explica en la [sección 2](#2-planteo-de-la-predicción).

### Modelos candidatos

Se evaluarán modelos vistos en la cursada:

1. **Regresión logística (modelo base):** punto de partida claro y de referencia. Sus coeficientes indican el cambio en el **logaritmo de las odds** de asistir por cada cambio en una variable; la relación con la probabilidad no es directa ni constante.
2. **K vecinos más cercanos (KNN):** clasifica a cada joven según la similitud con otros perfiles cercanos, sin suponer una relación lineal.
3. **Máquinas de vectores de soporte (SVM):** buscan límites de separación entre las clases; requieren variables escaladas y codificadas.
4. **Árboles de decisión / Random Forest:** capturan reglas simples e interacciones entre condiciones del hogar (por ejemplo, ingresos y clima educativo familiar) y aportan una medida de importancia de variables.

La importancia predictiva de una variable muestra cuánto ayuda al modelo a clasificar, pero **no demuestra que esa característica cause** la asistencia o la falta de asistencia.

---

## 2. Planteo de la predicción

### Variable objetivo: `asiste_superior`

| Valor | Significado |
|---|---|
| `1` | El joven **asiste actualmente** a un estudio superior (terciario, universitario o posgrado) |
| `0` | El joven **no asiste actualmente** al nivel superior |

Se construye con dos preguntas de la EPH: `CH10 = 1` (asiste a un establecimiento educativo) y `CH12` = 6, 7 u 8 (el nivel que cursa es terciario, universitario o posgrado). Como `CH12` también registra niveles cursados en el pasado, se interpreta siempre junto con `CH10`. Estas dos variables se usan **solo** para construir la respuesta. El detalle está en el [informe técnico](docs/informe_dataset.md#33-variable-objetivo).

### Qué representa cada fila

**Cada fila es un joven** de 18 a 24 años con secundario completo y sin un estudio superior terminado, que vive en uno de los aglomerados urbanos relevados por la EPH. Los datos describen su situación y la de su hogar **en el trimestre en que fue encuestado**. Si el joven fue encuestado en dos trimestres, queda solo la observación más reciente, para que cada persona aparezca una sola vez.

### Cuándo se hace la predicción y con qué información

La predicción se hace **en el momento de la encuesta**, con datos del joven y de su hogar que **pueden conocerse sin saber si asiste o no**:

- **Disponibles (predictoras):** edad, sexo, parentesco con el jefe/a, estado civil, cobertura de salud, lugar de nacimiento, composición y vivienda del hogar, ingreso del resto del hogar, educación y situación laboral del jefe/a, región y aglomerado.
- **No disponibles (excluidas por fuga de información):** todo lo que ya contiene la respuesta o es consecuencia de estudiar: nivel educativo del propio joven (`NIVEL_ED`), las preguntas educativas (`CH10` a `CH14`), la categoría de inactividad "estudiante" (`CAT_INAC`), las becas de estudio y la cuota alimentaria.
- **Zona gris:** la condición de actividad del joven (ocupado, desocupado, inactivo) se registra al mismo tiempo que la asistencia y puede ser en parte consecuencia de estudiar. Queda señalada para revisarla con cuidado.

### Los dos tiempos

| Momento | Qué se hace | Con qué datos |
|---|---|---|
| **1. Uso de la predicción** | Estimar si un joven asiste al nivel superior a partir de sus características y las de su hogar; por ejemplo, para identificar perfiles con menor asistencia y orientar acompañamientos o becas. | Las variables disponibles del joven y su hogar, sin información educativa propia. |
| **2. Evaluación con la realidad y corrección** | Comparar lo estimado con lo que efectivamente ocurrió y corregir o reentrenar. | El INDEC publica una nueva base de la EPH cada trimestre, con la respuesta real (`CH10`, `CH12`) de los jóvenes encuestados. |

---

## 3. Datos

- **Fuente:** Encuesta Permanente de Hogares (EPH) continua del INDEC — 2.º, 3.º y 4.º trimestre de 2025 y 1.er trimestre de 2026, descargados el 22/10/2026 de https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos
- **Archivos originales:** 8 bases (4 de personas y 4 de hogares) en [`data/raw/`](data/raw/), sin modificar.
- **Dataset del proyecto:** [`data/processed/eph_jovenes_asistencia_superior.csv`](data/processed/eph_jovenes_asistencia_superior.csv) — **9.665 jóvenes** (una fila por persona) y **26 columnas**. Clases equilibradas: 54,8 % asiste y 45,2 % no asiste.

La descripción completa del dataset (origen, construcción, variables, tipos de datos, diccionario y decisiones) está en el **informe técnico [`docs/informe_dataset.md`](docs/informe_dataset.md)**.

---

## 4. Dónde encontrar cada parte del trabajo

| Qué | Dónde |
|---|---|
| Informe técnico del dataset: origen, cantidad de registros, variables, tipos y diccionario de datos | [`docs/informe_dataset.md`](docs/informe_dataset.md) |
| Carga de las bases originales y construcción del dataset | [`notebooks/1.0-lei-carga-y-construccion-dataset.ipynb`](notebooks/1.0-lei-carga-y-construccion-dataset.ipynb) |
| Análisis exploratorio de datos (EDA) | [`notebooks/2.0-lei-analisis-exploratorio.ipynb`](notebooks/2.0-lei-analisis-exploratorio.ipynb) |
| Preprocesamiento: recodificación, partición, imputación, codificación y escalado | [`notebooks/3.0-lei-preprocesamiento.ipynb`](notebooks/3.0-lei-preprocesamiento.ipynb) |
| Matrices preparadas (con y sin escalado) | [`data/processed/`](data/processed/) |
| Gráficos generados | [`reports/figures/`](reports/figures/) |
| Ajustes realizados a partir de la devolución de la primera entrega | [`docs/ajustes_devolucion_entrega1.md`](docs/ajustes_devolucion_entrega1.md) |

---

## 5. Cómo reproducir

```bash
# 1. Crear el entorno (Anaconda)
conda create --name prediccion-asistencia-nivel-superior-eph python=3.12 -y
conda activate prediccion-asistencia-nivel-superior-eph

# 2. Instalar dependencias (incluye este proyecto como paquete)
pip install -r requirements.txt

# 3. Generar data/interim y el dataset de data/processed a partir de data/raw
python asistencia_superior/dataset.py
```

Después se pueden ejecutar con Jupyter las notebooks de `notebooks/`, en orden (1.0, 2.0 y 3.0).

---

## 6. Organización del proyecto

Estructura generada con la plantilla [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science) (versión 2). Las carpetas y archivos marcados como *plantilla* vienen de Cookiecutter y todavía no se usan.

```
├── LICENSE            <- Licencia MIT
├── Makefile           <- Comandos útiles (`make data`, `make requirements`)
├── README.md          <- Este documento
├── data
│   ├── external       <- Datos de terceros (plantilla, sin uso)
│   ├── interim        <- Población de estudio con todas las observaciones del panel
│   ├── processed      <- Dataset final (una fila por persona) y matrices preparadas
│   └── raw            <- Bases originales de la EPH, sin modificar
│
├── docs               <- Informe técnico del dataset, descripción del proyecto y ajustes por devoluciones
│
├── models             <- (plantilla, sin uso)
│
├── notebooks          <- Notebooks numeradas: número, iniciales de la autora y descripción
│                         (1.0 carga y construcción, 2.0 análisis exploratorio, 3.0 preprocesamiento)
│
├── pyproject.toml     <- Configuración del paquete `asistencia_superior` y de ruff
│
├── references         <- Material de referencia (diseño de registro de la EPH)
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
    ├── features.py             <- (plantilla, sin uso)
    ├── modeling                <- (plantilla, sin uso)
    └── plots.py                <- (plantilla, sin uso)
```

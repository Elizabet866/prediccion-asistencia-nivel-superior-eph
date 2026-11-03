# Ajustes a partir de la devolución de la segunda entrega

**Proyecto:** Predicción de la asistencia actual al nivel superior en jóvenes de 18 a 24 años con secundario completo (EPH – INDEC)

**Autora:** Liliana Elizabeth Iñigo

**Materia:** Aprendizaje Automático

**Docente:** Nicolás Caballero

Este documento resume cada observación de la devolución de la segunda entrega, qué se cambió y dónde puede verse. Todavía no se entrenan modelos.

## Resumen de cambios en los números

| | Antes | Ahora |
|---|---:|---:|
| Observaciones con respuesta desconocida | 3, asignadas a la clase 0 | 3, excluidas |
| Personas en el dataset | 9.665 | 9.663 |
| Columnas del dataset | 26 | 28 |
| Entrenamiento | 6.168 | 6.059 |
| Prueba | 3.497 | 3.497 |
| Excluidos por vivienda compartida | — | 107 |
| Medida de ingreso usada en el modelo | Pesos corrientes con log(1 + x) | Percentil dentro del trimestre |
| Datos usados en el EDA | Todo el dataset | Solo entrenamiento |

## 1. Etiquetas desconocidas

> No asignar la clase 0 cuando la respuesta es desconocida. Verificar cuántas quedan después de conservar una observación por persona y actualizar los conteos.

| Qué se hizo | Dónde |
|---|---|
| Se definió `respuesta_conocida`: `CH10` con un código válido (1, 2 o 3) y, si asiste, un nivel válido en `CH12`. Las 3 observaciones sin respuesta determinable (`CH10 = 1` con `CH12 = 99`; `CH10` = 0 y 9) se **excluyen** del conjunto supervisado; ya no se les asigna la clase 0. | Notebook 1.0, sección 5; [informe, 3.3](informe_dataset.md#33-variable-objetivo-y-respuestas-desconocidas) |
| La observación por persona se elige **entre las que tienen respuesta conocida**. Una de las 3 observaciones pertenecía a una persona con otra observación válida (se usa esa); las otras dos personas no tenían ninguna válida. Se pierden **2 personas**: el dataset queda con **9.663**. | Notebook 1.0, sección 9; [informe, 3.4](informe_dataset.md#34-panel-una-fila-por-persona) |
| La exclusión se justifica porque la etiqueta es desconocida y la encuesta no ofrece otro dato válido para resolverla, no porque los casos sean pocos. Se evaluó la alternativa semisupervisada y no se aplica: con 3 casos sin etiqueta frente a más de 9.000 etiquetados no aportaría información. | [Informe, 3.3](informe_dataset.md#33-variable-objetivo-y-respuestas-desconocidas) |
| Se actualizaron todos los conteos (dataset, partición, clases, faltantes). | Notebooks 1.0 a 3.0; informe; README |

## 2. Ingreso del resto del hogar igual a cero

> 675 son cero pero solo 540 viven solos: revisar los otros 135. Revisar negativos antes del `clip`. Separar "no aplica porque vive solo", "ingreso cero observado" y "sin respuesta". Un cero válido no debería convertirse en faltante.

| Qué se hizo | Dónde |
|---|---|
| Se creó `situacion_ingreso_resto` con cuatro categorías: `no_aplica_vive_solo` (540), `sin_respuesta` (2.783, `DECCFR = 12`), `cero_observado` (135) y `positivo` (6.205). | Notebook 1.0, sección 7.1; [informe, 7.3](informe_dataset.md#73-ingreso) |
| Se revisaron los 135 ceros: son **ceros reales**. En todos, el hogar respondió ingresos y, o bien declaró un ingreso total de 0, o bien todo el ingreso del hogar es del propio joven. | Notebook 1.0, sección 7.1 |
| Se verificó antes de calcular que `ITF − P47T` nunca es negativo: no hay casos, así que se **eliminó el `clip`**. | Notebook 1.0, sección 7.1; `asistencia_superior/dataset.py` |
| El cero observado se conserva como **dato válido** (ya no se convierte en faltante). Se eliminaron `ingreso_resto_cero` e `ingresos_sin_respuesta`, reemplazados por `situacion_ingreso_resto`, que entra al modelo como categoría (one-hot). En el EDA las cuatro situaciones muestran asistencias muy distintas (80 % vive solo, 37 % cero observado), lo que confirma que no debían mezclarse. | Notebook 2.0, sección 4; notebook 3.0, secciones 3 y 5 |

## 3. Comparabilidad del ingreso entre trimestres

> Se combinan pesos corrientes de períodos distintos. Expresarlos en moneda de un mismo período o justificar otra medida comparable, especialmente porque se entrena con 2025 y se prueba con 2026.

| Qué se hizo | Dónde |
|---|---|
| Se creó `percentil_ingreso_resto`: la posición del ingreso del resto del hogar dentro de la distribución del ingreso per cápita familiar (`IPCF`) de **todas las personas de la EPH de su mismo trimestre** cuyo hogar respondió, ponderada con `PONDIH`. Es la lógica de los deciles del INDEC (`DECCFR`), que también se calculan por trimestre. | Notebook 1.0, sección 7.2; [informe, 7.3](informe_dataset.md#73-ingreso) |
| Se muestra la comparación: la mediana en pesos sube de alrededor de 410.000 (2T 2025) a 527.000 (1T 2026), mientras que la mediana del percentil se mantiene entre 52 y 56. | Notebook 1.0, sección 7.2 |
| El monto en pesos queda en el dataset solo como referencia y **no entra al modelo**. El percentil no necesita logaritmo (va de 0 a 100 sin cola larga), solo imputación y escalado. | Notebook 3.0, secciones 1 y 5 |
| Se dejó registrada la alternativa (deflactar con el índice de precios) y la limitación del percentil (pierde el nivel absoluto del ingreso). | [Informe, 7.3 y 10](informe_dataset.md#73-ingreso) |

Al corregir este punto también se detectó que los montos con decimales de la EPH usan coma decimal; ahora las bases se leen con `decimal=","`.

## 4. Precisión sobre la fuga de información

> Una asociación fuerte no demuestra por sí sola que haya fuga. Confirmar con el diseño de registro el significado de becas, cuota alimentaria y otros ingresos, y justificar la exclusión por el escenario de uso. Distinguir al joven jefe/a del cónyuge.

| Qué se hizo | Dónde |
|---|---|
| Se confirmaron las definiciones con el diseño de registro del INDEC (1T 2025): `V11_01_M` beca de estudio del gobierno para continuar o finalizar estudios; `V11_02_M` beca de estudio de instituciones no gubernamentales; `V12_M` cuotas de alimentos o ayuda en dinero de personas que no viven en el hogar; `CAT_INAC` 3 = Estudiante. | Notebook 1.0, sección 8; [informe, 6](informe_dataset.md#6-variables-excluidas-por-fuga-de-información) |
| Cada exclusión se justifica ahora por la **definición** de la variable y por el **escenario de uso** (orientar becas o acompañamientos): la beca para continuar estudios supone estar estudiando; la cuota alimentaria puede extenderse si el hijo estudia (art. 663 del Código Civil y Comercial) y la ayuda de personas de afuera del hogar incluye la de jóvenes que se mudaron para estudiar. | Notebook 1.0, sección 8; informe, 6 |
| Las tablas de asociación quedan como comprobación complementaria y se calculan **solo con observaciones de 2025**. | Notebook 1.0, sección 8 |
| Joven **jefe/a**: sus datos de "jefe" quedan como no aplica (`es_jefe_hogar = 1`). Joven **cónyuge**: conserva el nivel educativo, el sexo y la condición de actividad de su pareja, que es otra persona. Con este cambio, 332 cónyuges recuperan esos datos. | Notebook 1.0, sección 6; notebook 3.0, sección 3; [informe, 3.1](informe_dataset.md#31-vinculación-persona--hogar--jefe-o-jefa) |

## 5. Protección del conjunto de prueba

> El EDA usó todo el dataset para justificar agrupaciones y selección. Las decisiones basadas en frecuencias o relaciones deberían definirse solo con entrenamiento. Revisar hogares compartidos entre entrenamiento y prueba y explicar su relación con el uso previsto.

| Qué se hizo | Dónde |
|---|---|
| La partición temporal se define en la notebook 1.0, **antes** del EDA, y queda en la columna `particion`. | Notebook 1.0, sección 10 |
| El **EDA usa solo el entrenamiento** (6.059 jóvenes de 2025). Se recalcularon todas las cifras. | Notebook 2.0 |
| En la preparación se separan las reglas fijadas por el **significado de los códigos** (Ns/Nr → faltante, no aplica, etiquetas), que se aplican a los dos conjuntos, de las **agrupaciones de categorías poco frecuentes**, que se verifican con las frecuencias del entrenamiento y después se aplican sin cambios a la prueba. | Notebook 3.0, secciones 3 y 4; [informe, 7.2](informe_dataset.md#72-recodificación-y-agrupación-de-categorías) |
| Se revisaron las **viviendas**: 100 viviendas (92 hogares) tienen jóvenes en 2025 y en 1T 2026. Se excluyen del entrenamiento sus 107 jóvenes de 2025, para evaluar sobre viviendas no vistas al entrenar (el escenario más exigente y el que no sobreestima el desempeño). La prueba no cambia. | Notebook 1.0, sección 10; [informe, 3.5](informe_dataset.md#35-partición-temporal-y-viviendas-compartidas) |
| Dentro del entrenamiento hay hogares con más de un joven. Las matrices guardan `codusu` (no como variable de entrada) para poder agrupar por hogar en la validación cruzada de la etapa de modelado. | Notebook 3.0, secciones 2 y 7 |

## Nota sobre representatividad

> Una proporción ponderada parecida a la no ponderada no justifica conclusiones poblacionales.

| Qué se hizo | Dónde |
|---|---|
| Se quitó la comparación entre proporción ponderada y no ponderada como justificación. Los análisis se presentan como descripción de la **muestra analizada**, sin ponderar. | Notebook 2.0, sección 1; [informe, 9](informe_dataset.md#9-alcance-y-representatividad) |
| Se explica por qué generalizar no es directo: se combinan trimestres (cada ponderador expande un trimestre), se conserva una observación por persona y se excluyen viviendas compartidas. | [Informe, 9](informe_dataset.md#9-alcance-y-representatividad) |

## Archivos modificados

- `asistencia_superior/dataset.py`
- `notebooks/1.0-lei-carga-y-construccion-dataset.ipynb`
- `notebooks/2.0-lei-analisis-exploratorio.ipynb`
- `notebooks/3.0-lei-preprocesamiento.ipynb`
- `data/interim/eph_jovenes_18a24_todas_las_observaciones.csv`
- `data/processed/` (dataset y las dos matrices preparadas)
- `reports/figures/` (gráficos regenerados)
- `docs/informe_dataset.md`, `docs/ajustes_devolucion_entrega1.md` y `README.md`

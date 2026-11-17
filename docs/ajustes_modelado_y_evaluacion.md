# Ajustes a partir de la devolución del proyecto final

**Proyecto:** Predicción de la asistencia actual al nivel superior en jóvenes de 18 a 24 años con secundario completo (EPH – INDEC)

**Autora:** Liliana Elizabeth Iñigo

**Materia:** Aprendizaje Automático

**Docente:** Nicolás Caballero

Este documento resume cada observación de la devolución del proyecto final, qué se cambió y dónde puede verse.

## Resumen de cambios en los resultados

Al corregir el preprocesamiento dentro de la validación, los resultados cambiaron muy poco. Las decisiones se mantienen: regresión logística con umbral 0,55.

| | Antes | Ahora |
|---|---:|---:|
| C elegido para la regresión logística | 10 | 1 |
| F1 "no asiste" en validación (logística) | 0,733 | 0,732 |
| F1 "no asiste" en la prueba | 0,747 | 0,748 |
| Recall "no asiste" en la prueba | 0,765 | 0,767 |
| Precisión "no asiste" en la prueba | 0,730 | 0,730 |
| Exactitud en la prueba | 0,759 | 0,760 |
| Jóvenes que no asisten identificados (de 1.625) | 1.243 | 1.246 |

## 1. Preprocesamiento dentro de la validación

> La corrección principal es incorporar el preprocesamiento dentro de cada pliegue de validación.

| Qué se hizo | Dónde |
|---|---|
| Antes, la imputación, el escalado y la codificación se ajustaban una vez con todo el entrenamiento y la validación cruzada se hacía sobre esas matrices: en cada pliegue, la parte de validación ya había influido en las medianas y en la escala. Ahora el preprocesador (`ColumnTransformer`) se combina con cada modelo en un `Pipeline`, y `GridSearchCV`, `cross_validate` y `cross_val_predict` lo ajustan **en cada pliegue solo con su parte de entrenamiento**. | Notebook 4.0, secciones 2 y 5 |
| La notebook 3.0 ya no guarda matrices transformadas. Guarda el **dataset recodificado** (reglas por código y agrupaciones, que no aprenden nada de los datos) y define el preprocesador. Se eliminaron `matriz_preparada_escalada.csv` y `matriz_preparada_sin_escalar.csv`. | Notebook 3.0, secciones 5 y 7; `data/processed/eph_jovenes_recodificado.csv` |
| El análisis de sensibilidad (sin `condicion_actividad`), la elección del umbral y la comparación de KNN con y sin escalado también usan `Pipeline`. | Notebook 4.0, secciones 7, 8 y 11 |

## 2. Interpretación de los coeficientes categóricos

> El One-Hot Encoding conserva todas las categorías. En ese esquema, `exp(coeficiente)` no representa directamente la comparación de una categoría "contra las demás".

| Qué se hizo | Dónde |
|---|---|
| Cada categoría se compara con una **categoría de referencia** de su misma variable (la más frecuente en el entrenamiento): `exp(coef_A − coef_ref)` es el factor por el que cambian las chances de asistir de la categoría A frente a la de referencia, con las demás variables constantes. Las numéricas se leen por desvío estándar y `sexo_mujer` como mujer frente a varón. | Notebook 4.0, sección 10; `reports/coeficientes_regresion_logistica.csv` |
| Se corrigió la lectura en el README y en las conclusiones. Por ejemplo, un joven ocupado tiene chances de 0,13 veces las de uno inactivo, y con solo plan público de salud, 0,27 veces las de quien tiene obra social o prepaga. | README, sección 4; notebook 4.0, sección 12 |

## 3. Guardar el proceso completo para nuevas predicciones

> El archivo del modelo no incluye el preprocesador necesario para nuevas entradas.

| Qué se hizo | Dónde |
|---|---|
| `models/regresion_logistica_final.joblib` guarda ahora el `Pipeline` completo (preprocesador + regresión logística), el umbral y las columnas de entrada. Recibe las 18 variables recodificadas. La notebook comprueba que el archivo guardado reproduce exactamente las predicciones de la prueba. | Notebook 4.0, sección 11; [`models/README.md`](../models/README.md) |

## 4. Escenario de aplicación

> El percentil de ingreso se calcula utilizando la distribución del trimestre correspondiente. Esto supone disponer de esa base trimestral o de una referencia equivalente.

| Qué se hizo | Dónde |
|---|---|
| Se aclara que, para aplicar el modelo, hace falta la base trimestral de la EPH (o una distribución de referencia equivalente) para calcular el percentil del ingreso; no alcanza con los datos aislados de una persona. | README, secciones 2 y 5; notebook 4.0, secciones 1 y 12; [`models/README.md`](../models/README.md) |

## 5. No asistencia y necesidad de acompañamiento

> Asistir no implica no necesitar acompañamiento, y no asistir tampoco demuestra necesidad de una beca. Conviene corregir esa equivalencia en la interpretación de los errores.

| Qué se hizo | Dónde |
|---|---|
| Se reescribió la interpretación de los errores: 379 jóvenes que no asisten quedan sin identificar y 461 que sí asisten quedan marcados como "no asiste". Son errores sobre la **condición de asistencia**, no sobre la necesidad de apoyo. | Notebook 4.0, sección 9; README, sección 4 |
| El uso del modelo se plantea como un insumo para orientar políticas. Decidir a quién ofrecer una beca o un acompañamiento requiere información adicional. Se agregó como limitación. | Notebook 4.0, secciones 1 y 12; README, secciones 2, 4 y 5 |
| El umbral se justifica solo como el mejor equilibrio en validación entre identificar a quienes no asisten y no marcar de más, sin suponer qué error es más costoso para una persona. | Notebook 4.0, sección 8.2 |

## 6. Duración del video

> Un poco más largo de lo recomendado.

El video entregado (8 minutos) no se modificó. Queda registrada la observación.

## Archivos modificados

- `notebooks/3.0-lei-preprocesamiento.ipynb`
- `notebooks/4.0-lei-modelado-y-evaluacion.ipynb`
- `data/processed/eph_jovenes_recodificado.csv` (nuevo); se eliminaron las dos matrices preparadas
- `models/regresion_logistica_final.joblib` y `models/README.md`
- `reports/` (métricas y coeficientes) y `reports/figures/` (gráficos del modelado)
- `README.md`, `docs/informe_dataset.md` y `docs/ajustes_dataset_y_preprocesamiento.md`

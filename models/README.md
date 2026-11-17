# Modelos

Modelo final del proyecto, generado por la notebook [`4.0-lei-modelado-y-evaluacion`](../notebooks/4.0-lei-modelado-y-evaluacion.ipynb).

| Archivo | Contenido |
|---|---|
| `regresion_logistica_final.joblib` | Diccionario con el proceso completo: `pipeline` (preprocesador + regresión logística, ajustados con todo el conjunto de entrenamiento), `umbral` (0,55, elegido por validación) y `columnas_entrada` (las 18 variables de entrada en el orden esperado) |

## Qué recibe

El `pipeline` recibe las **18 variables recodificadas**, con el mismo formato que [`data/processed/eph_jovenes_recodificado.csv`](../data/processed/eph_jovenes_recodificado.csv) (sin `codusu`, `particion` ni `asiste_superior`). Él mismo hace la imputación, el escalado y la codificación aprendidos con el entrenamiento, así que no hace falta preparar matrices aparte.

Un joven se clasifica como "asiste" si la probabilidad estimada de asistir es mayor o igual que el umbral, y como "no asiste" en caso contrario.

```python
import joblib
import pandas as pd

guardado = joblib.load("../models/regresion_logistica_final.joblib")   # reemplazar por la ruta local si corresponde
datos = pd.read_csv("../data/processed/eph_jovenes_recodificado.csv")  # o nuevas filas con el mismo formato
X = datos[guardado["columnas_entrada"]]
probabilidad = guardado["pipeline"].predict_proba(X)[:, 1]
prediccion = (probabilidad >= guardado["umbral"]).astype(int)          # 1 = asiste, 0 = no asiste
```

## Requisitos para aplicarlo a datos nuevos

- **Base trimestral de la EPH:** el percentil del ingreso del resto del hogar se calcula con la distribución de **todo el trimestre** (notebook 1.0, sección 7.2). Para un trimestre nuevo hace falta esa base completa (o una distribución de referencia equivalente); no alcanza con los datos aislados de una persona.
- **Mismas reglas de construcción y recodificación:** las variables se arman como en la notebook 1.0 y se recodifican como en la notebook 3.0 (secciones 3 y 4).
- **Qué clasifica:** una condición educativa (asiste o no asiste actualmente). No mide la necesidad de una beca o de un acompañamiento; esa decisión requiere información adicional.

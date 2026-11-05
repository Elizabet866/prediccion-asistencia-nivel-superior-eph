# Modelos

Modelo final del proyecto, generado por la notebook [`4.0-lei-modelado-y-evaluacion`](../notebooks/4.0-lei-modelado-y-evaluacion.ipynb).

| Archivo | Contenido |
|---|---|
| `regresion_logistica_final.joblib` | Diccionario con el modelo de regresión logística entrenado con todo el conjunto de entrenamiento (`modelo`), el umbral de decisión elegido por validación (`umbral` = 0,55) y la lista de columnas de entrada en el orden esperado (`columnas`) |

Uso: el modelo recibe filas con el mismo formato que `data/processed/matriz_preparada_escalada.csv` (sin `codusu`, `particion` ni `asiste_superior`). Un joven se clasifica como "asiste" si la probabilidad estimada de asistir es mayor o igual que el umbral, y como "no asiste" en caso contrario.

```python
import joblib
guardado = joblib.load("../models/regresion_logistica_final.joblib")   # reemplazar por la ruta local si corresponde
probabilidad = guardado["modelo"].predict_proba(X[guardado["columnas"]])[:, 1]
prediccion = (probabilidad >= guardado["umbral"]).astype(int)
```

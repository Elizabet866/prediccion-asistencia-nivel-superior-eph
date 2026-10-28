# Descripción del proyecto y formulación de objetivos

**Alumna:** Iñigo Liliana Elizabeth · **Materia:** Aprendizaje Automático · **Docente:** Nicolás Caballero
**Versión:** actualizada con la devolución de la primera entrega (los cambios se detallan en [ajustes_devolucion_entrega1.md](ajustes_devolucion_entrega1.md)).

## Título del proyecto

**Predicción de la asistencia al nivel superior en jóvenes de aglomerados urbanos de Argentina a partir de la EPH**

## 1. Contexto y relevancia del problema

La transición entre la escuela secundaria y los estudios superiores (terciarios o universitarios) es una etapa decisiva en la trayectoria de los jóvenes. Aunque finalizar la secundaria es un logro fundamental, la asistencia a estudios superiores suele estar muy vinculada con las condiciones socioeconómicas del hogar: los ingresos de la familia, el nivel educativo de quien está a cargo del hogar y la región del país donde viven.

El aprendizaje automático permite analizar en conjunto estos factores y estimar, a partir de las características de un joven y de su hogar, si **asiste actualmente** al nivel superior. El modelo describe la situación en el momento de la encuesta: no predice una decisión futura. Identificar qué perfiles tienen menor asistencia resulta valioso para pensar intervenciones educativas y focalizar acompañamientos, tutorías o becas de estudio.

A diferencia de proyectos anteriores del repositorio del Politécnico enfocados en la deserción escolar en el secundario o en la inserción laboral, este trabajo hace foco en una subpoblación puntual: quienes ya completaron el nivel medio y todavía no terminaron un estudio superior.

Para este estudio se utilizan los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC, disponibles en https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos. La EPH releva **31 aglomerados urbanos**, por lo que los resultados corresponden a los jóvenes que viven en esos aglomerados y no a toda la población joven del país.

## 2. Formulación de objetivos

### Objetivo general

Desarrollar un modelo de clasificación supervisada que permita predecir la asistencia al nivel superior en jóvenes de 18 a 24 años con secundario completo, residentes en los aglomerados urbanos relevados por la EPH, a partir de variables individuales y del hogar.

### Objetivos específicos

1. **Delimitar la población de estudio:** filtrar y acondicionar la base de microdatos de la EPH para trabajar con jóvenes de 18 a 24 años que declararon tener el secundario completo.
2. **Preparar las variables del estudio:** construir indicadores de contexto individual y del hogar a partir de los registros de la encuesta (por ejemplo, nivel educativo del jefe o jefa de hogar, tramos de ingresos familiares o región geográfica).
3. **Entrenar y ajustar modelos supervisados:** entrenar algoritmos de clasificación vistos durante la cursada y ajustar sus hiperparámetros, mediante técnicas de partición y validación de datos.
4. **Evaluar e interpretar los resultados:** comparar el rendimiento de los modelos entrenados e identificar cuáles son las características que tienen mayor peso en la predicción.

**Cómo se construye el filtro de "secundario completo":** se usa `NIVEL_ED` con los códigos **4** (secundario completo) y **5** (superior universitario incompleto). Quien terminó el secundario y está cursando el nivel superior figura con 5, no con 4: si se usara solo el 4 quedarían afuera justamente los jóvenes que asisten. Se excluye el código **6** (superior completo): esos jóvenes ya terminaron una carrera y no asistir no significa que no hayan accedido (502 observaciones).

## 3. Tipo de problema de aprendizaje automático

Clasificación binaria supervisada.

- **Variable objetivo (`asiste_superior`):** surge de las respuestas de la persona encuestada sobre si asiste a un establecimiento educativo (`CH10`) y a qué nivel corresponde (`CH12`). Como `CH12` también registra niveles cursados en el pasado, se interpreta siempre junto con `CH10`:
  - `1`: el joven asiste actualmente al nivel superior (`CH10 = 1` y `CH12` = terciario, universitario o posgrado).
  - `0`: el joven no asiste actualmente al nivel superior.
- `CH10` y `CH12` se usan **solo** para construir la respuesta. Ni ellas ni otros indicadores educativos derivados (`NIVEL_ED`, `CH11`, `CH13`, `CH14`, `CAT_INAC`) se usan como predictoras.
- **Variables de entrada (X):** características personales y del entorno familiar relevadas en la encuesta (edad, sexo, situación laboral, educación del jefe o jefa de hogar, ingresos del hogar, vivienda y región).

## 4. Modelos candidatos

Se evaluarán modelos vistos en la cursada:

1. **Regresión logística (modelo base):** punto de partida claro y de referencia. Sus coeficientes indican el cambio en el **logaritmo de las odds** de asistir por cada cambio en una variable; la relación con la probabilidad no es directa ni constante.
2. **K vecinos más cercanos (KNN):** clasifica a cada joven según la similitud con otros perfiles cercanos, sin suponer una relación lineal.
3. **Máquinas de vectores de soporte (SVM):** buscan límites de separación entre las clases; requieren variables escaladas y codificadas.
4. **Árboles de decisión / Random Forest:** capturan reglas simples e interacciones entre condiciones del hogar (por ejemplo, ingresos y clima educativo familiar) y aportan una medida de importancia de variables.

La importancia predictiva de una variable muestra cuánto ayuda al modelo a clasificar, pero **no demuestra que esa característica cause** la asistencia o la falta de asistencia.

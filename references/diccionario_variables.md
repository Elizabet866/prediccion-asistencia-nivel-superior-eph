# Diccionario de variables

Dataset: `data/processed/eph_jovenes_asistencia_superior.csv` — 9.665 filas (una por persona) y 26 columnas.

Los códigos provienen del diseño de registro de la EPH continua (INDEC). El diseño de registro oficial se consulta en
https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos (no se sube al repositorio en PDF).

## Identificación y diseño muestral

| Columna | Origen EPH | Tipo | Descripción |
|---|---|---|---|
| `codusu` | `CODUSU` | texto | Código de la vivienda |
| `nro_hogar` | `NRO_HOGAR` | entero | Número de hogar dentro de la vivienda |
| `componente` | `COMPONENTE` | entero | Número de la persona dentro del hogar. `codusu` + `nro_hogar` + `componente` identifican a la persona |
| `trimestre` | `ANO4` + `TRIMESTRE` | texto | Trimestre de la observación conservada (`2025T2`, `2025T3`, `2025T4`, `2026T1`) |
| `ponderador` | `PONDERA` | entero | Factor de expansión: cuántas personas de la población representa cada caso. No es predictora |

## Variable objetivo

| Columna | Construcción | Valores |
|---|---|---|
| `asiste_superior` | `CH10 == 1` (asiste) y `CH12` ∈ {6, 7, 8} (terciario, universitario, posgrado) | 1 = asiste actualmente al nivel superior · 0 = no asiste actualmente |

## Variables del joven

| Columna | Origen EPH | Tipo | Códigos |
|---|---|---|---|
| `sexo` | `CH04` | categórica | 1 Varón · 2 Mujer |
| `edad` | `CH06` | numérica | 18 a 24 años |
| `parentesco_jefe` | `CH03` | categórica | 1 Jefe/a · 2 Cónyuge/pareja · 3 Hijo/a o hijastro/a · 4 Yerno/nuera · 5 Nieto/a · 6 Madre/padre · 7 Suegro/a · 8 Hermano/a · 9 Otros familiares · 10 No familiares |
| `es_jefe_o_conyuge` | derivada de `CH03` | binaria | 1 = el joven es jefe/a o cónyuge del jefe/a (los datos del jefe/a quedan vacíos) |
| `estado_civil` | `CH07` | categórica | 1 Unido/a · 2 Casado/a · 3 Separado/a o divorciado/a · 4 Viudo/a · 5 Soltero/a · 9 Ns/Nr |
| `cobertura_salud` | `CH08` | categórica | 1 Obra social · 2 Mutual, prepaga o servicio de emergencia · 3 Planes y seguros públicos · 4 No paga ni le descuentan · 9 Ns/Nr · 12, 13, 23 combinaciones de las anteriores |
| `lugar_nacimiento` | `CH15` | categórica | 1 En esta localidad · 2 En otra localidad de esta provincia · 3 En otra provincia · 4 En un país limítrofe · 5 En otro país · 9 Ns/Nr |
| `condicion_actividad` | `ESTADO` | categórica | 0 Entrevista individual no realizada · 1 Ocupado/a · 2 Desocupado/a · 3 Inactivo/a. **A vigilar:** se mide al mismo tiempo que la asistencia |

## Variables del hogar

| Columna | Origen EPH | Tipo | Descripción / códigos |
|---|---|---|---|
| `personas_hogar` | `IX_TOT` (base hogares) | numérica | Cantidad de miembros del hogar |
| `menores_10_hogar` | `IX_MEN10` (base hogares) | numérica | Cantidad de miembros menores de 10 años |
| `personas_por_ambiente` | `IX_TOT / II1` | numérica | Hacinamiento: personas por ambiente de uso exclusivo del hogar |
| `tipo_vivienda` | `IV1` (base hogares) | categórica | 1 Casa · 2 Departamento · 3 Pieza de inquilinato · 4 Pieza en hotel o pensión · 5 Local no construido para habitación · 6 Otros |
| `tenencia_vivienda` | `II7` (base hogares) | categórica | 1 Propietario de la vivienda y el terreno · 2 Propietario solo de la vivienda · 3 Inquilino · 4 Ocupante por pago de impuestos/expensas · 5 Ocupante en relación de dependencia · 6 Ocupante gratuito (con permiso) · 7 Ocupante de hecho · 8 En sucesión · 9 Otra situación · 0 Sin dato |
| `ingreso_resto_hogar_pc` | `(ITF − P47T) / (IX_TOT − 1)` | numérica (pesos corrientes) | Ingreso per cápita del resto del hogar, sin los ingresos propios del joven. Vacío si el hogar no respondió ingresos. 0 si el joven vive solo |
| `ingresos_sin_respuesta` | `DECCFR == 12` | binaria | 1 = el hogar no respondió ingresos (en la EPH figura `ITF = 0`, que no es ingreso cero) |

## Variables del jefe o jefa de hogar

Se toman de la persona del mismo hogar con `CH03 = 1`. Quedan vacías si el joven es jefe/a o cónyuge.

| Columna | Origen EPH | Tipo | Códigos |
|---|---|---|---|
| `jefe_nivel_educativo` | `NIVEL_ED` del jefe/a | categórica ordinal | 1 Primaria incompleta · 2 Primaria completa · 3 Secundaria incompleta · 4 Secundaria completa · 5 Superior universitario incompleto · 6 Superior universitario completo · 7 Sin instrucción |
| `jefe_sexo` | `CH04` del jefe/a | categórica | 1 Varón · 2 Mujer |
| `jefe_condicion_actividad` | `ESTADO` del jefe/a | categórica | 0 Entrevista individual no realizada · 1 Ocupado/a · 2 Desocupado/a · 3 Inactivo/a |

## Ubicación

| Columna | Origen EPH | Tipo | Códigos |
|---|---|---|---|
| `region` | `REGION` | categórica | 1 Gran Buenos Aires · 40 Noroeste · 41 Noreste · 42 Cuyo · 43 Pampeana · 44 Patagonia |
| `aglomerado` | `AGLOMERADO` | categórica | 32 códigos (31 aglomerados urbanos; el Gran Buenos Aires se divide en 32 CABA y 33 Partidos del GBA). Ver tabla abajo |

| Código | Aglomerado | Código | Aglomerado |
|---|---|---|---|
| 2 | Gran La Plata | 22 | Gran Catamarca |
| 3 | Bahía Blanca – Cerri | 23 | Gran Salta |
| 4 | Gran Rosario | 25 | La Rioja |
| 5 | Gran Santa Fe | 26 | Gran San Luis |
| 6 | Gran Paraná | 27 | Gran San Juan |
| 7 | Posadas | 29 | Gran Tucumán – Tafí Viejo |
| 8 | Gran Resistencia | 30 | Santa Rosa – Toay |
| 9 | Comodoro Rivadavia – Rada Tilly | 31 | Ushuaia – Río Grande |
| 10 | Gran Mendoza | 32 | Ciudad Autónoma de Buenos Aires |
| 12 | Corrientes | 33 | Partidos del GBA |
| 13 | Gran Córdoba | 34 | Mar del Plata |
| 14 | Concordia | 36 | Río Cuarto |
| 15 | Formosa | 38 | San Nicolás – Villa Constitución |
| 17 | Neuquén – Plottier | 91 | Rawson – Trelew |
| 18 | Santiago del Estero – La Banda | 93 | Viedma – Carmen de Patagones |
| 19 | Jujuy – Palpalá | | |
| 20 | Río Gallegos | | |

## Variables de la EPH que NO se usan como predictoras

| Variable EPH | Motivo |
|---|---|
| `CH10`, `CH12` | Construyen la variable objetivo |
| `NIVEL_ED` (del joven) | Delimita la población; con 4 nadie asiste y con 5 asiste el 94 % → fuga |
| `CH11`, `CH13`, `CH14` | Indicadores educativos derivados (tipo de establecimiento, finalización del nivel, último año aprobado) |
| `CAT_INAC` | La categoría 3 "estudiante" coincide con la respuesta; además no existe en la base 1T 2026 |
| `V11_01_M`, `V11_02_M` | Montos de beca de estudio del joven: el 95 % de quienes la cobran asiste |
| `V12_M` | Cuota alimentaria: el 91 % de quienes la reciben asiste |
| `P47T`, `ITF`, `IPCF`, deciles | Incluyen los montos anteriores; se reemplazan por `ingreso_resto_hogar_pc` |

> Los significados de los códigos de ingresos (V11, V12) deben confirmarse con el diseño de registro 2025–2026, que cambió respecto de años anteriores.

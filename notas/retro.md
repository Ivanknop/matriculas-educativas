# Retrospectiva: proyecto `analisis_matricula` → mejoras a `edu-data-template`

Sesión analizada: transcript `1943f575…` (2026-11-08, 00:49–15:24), plantilla **v0.1.0**.
Fuentes: los mensajes del usuario, las respuestas, las preguntas (AskUserQuestion), los
permisos denegados, los errores de herramientas y el diff de los archivos de la plantilla
(`git clone` de v0.1.0) contra el proyecto.

Nada de esto está aplicado. Es una propuesta.

---

## 0. Resumen

| # | Hallazgo | Tipo | Destino propuesto |
|---|---|---|---|
| C2 | Sexo: se mostró solo "% mujeres"; el usuario quería varones **y** mujeres | Corrección | CLAUDE.md (regla nueva) |
| C3 | El visor no era "on demand": 4 gráficos + tablas de una vez, sin mapa ni portada | Corrección | Skill nueva `visor-interactivo` |
| C4 | Las tablas debajo de los gráficos no aportaban (y yo las recomendé) | Corrección | Skill `visor-interactivo` |
| C5 | Se propuso un alcance con códigos sin explicar (`snu`, `_20`) | Insistencia | CLAUDE.md + `dataset-nuevo` §8 |
| C6 | El usuario tuvo que pedir el plan ("muestrame el plan…") | Insistencia | CLAUDE.md (precisar "plan primero") |
| C7 | La auditoría propuso una nota de efecto despreciable y un cotejo externo que no importaba | Corrección | `validar-calidad` + skill nueva `auditar` |
| C8 | README con contenido de la plantilla: el usuario pidió borrarlo | Corrección | `nuevo_proyecto.sh` + `publicar` |
| C9 | Cambio normativo de PBA (Res. 1650/24) y serie "total sin PBA" | Información de dominio | Específico. El patrón genérico va a `validar-calidad` |
| C10 | "Todo lo que implique mejora en performance es importante" | Preferencia | CLAUDE.md (regla nueva) |
| P1 | Cifra mal en una alerta ("22 de 24"): los textos no estaban testeados | Error propio | CLAUDE.md (precisar) + `edu_data.cifras` |
| P2 | Un test leía `data/processed/`: habría roto la CI | Error propio | CLAUDE.md + plantilla `conftest.py` |
| P3 | Decisiones guardadas en la memoria de Claude: hoy ese archivo no existe | Error propio | CLAUDE.md (regla nueva) |
| P4 | Se denegó copiar el diccionario y el PDF a `data/raw/`, pero un script escribió ahí | Fricción de la plantilla | CLAUDE.md + `dataset-nuevo` §0 + `edu_data.descarga` |
| P5 | No se pudo ver el visor renderizado: faltan librerías de navegador en el contenedor | Fricción de la plantilla | Dockerfile / post-create |
| P6 | CLAUDE.md dice que los crudos "no se versionan"; `publicar` los versiona | Contradicción de la plantilla | CLAUDE.md |
| P7 | La heurística "vacíos sin ningún 0 → sin oferta" habría clasificado mal la sobreedad | Fricción de la plantilla | `dataset-nuevo` §4 + CLAUDE.md |

C = el usuario corrigió o tuvo que insistir. P = problema detectado por mí o por la
simulación de CI, sin intervención del usuario.

---

## 1. Correcciones e insistencias del usuario


### C2. Sexo: mostrar las dos categorías
- **Qué pasó.** El dataset solo trae varones (`v_`). El primer visor mostraba "% mujeres". El
  usuario: *"La división de sexo debe mostrar varones y mujeres, por más que el dataset solo
  distinga uno"*.
- **Qué faltaba.** Una regla de presentación: si una categoría se deriva por resta, se muestran
  todas las categorías, y se aclara cuál es derivada.
- **Destino.** CLAUDE.md, porque aplica a cualquier dataset con sexo, sector o ámbito informado
  parcialmente.

### C3. Diseño del visor
- **Qué pasó.** CLAUDE.md dice "preferir un visor interactivo on demand". Lo interpreté como "un
  selector arriba y todo lo demás abajo": 4 gráficos de línea más 3 tablas. El usuario lo
  rediseñó con tres pedidos:
  1. Un **mapa** como selector de la unidad territorial.
  2. Cada gráfico **on demand**: primero se elige el indicador y recién después aparecen los
     filtros (sexo, sector, ámbito).
  3. **Dos pestañas**: una portada muy breve (qué es, por qué existe un total alternativo) con un
     link "ir al mapa", y la pestaña del mapa.
- **Qué faltaba.** Una definición operativa de "on demand" y un patrón de visor. Es el segundo
  proyecto que escribe un visor desde cero: la plantilla no trae ninguno.
- **Destino.** Skill nueva `visor-interactivo` (borrador en §6.2) y funciones reutilizables
  (`edu_data.visor`, `edu_data.ar.geo`).

### C4. Tablas debajo de los gráficos
- **Qué pasó.** Para el contenido del visor ofrecí "Líneas + tablas (Recomendado)" y el usuario
  lo aceptó. Después pidió quitarlas: *"no aporta, si alguien busca ese detalle, lo pide después
  por privado"*. El archivo bajó de 1,8 MB a 0,5 MB.
- **Qué faltaba.** Un default: el visor no repite en tabla lo que ya muestra el gráfico. El valor
  exacto va en el tooltip.
- **Destino.** Skill `visor-interactivo`.

### C5. Códigos sin explicar en la propuesta de alcance
- **Qué pasó.** Propuse "SNU fuera" y "`_20` aparte". El usuario: *"que es snu, que es ese
  _20?"*.
- **Qué faltaba.** Una regla: en las preguntas al usuario, ningún código crudo sin su glosa en
  lenguaje llano y su tamaño (cuántos casos, qué peso tiene).
- **Destino.** CLAUDE.md (estilo de comunicación) y `dataset-nuevo` §8.

### C6. El plan no se mostró antes de pedir permiso para arrancar
- **Qué pasó.** Terminé con "¿Arranco?" sin un plan consolidado. El usuario tuvo que pedirlo:
  *"muestrame el plan de trabajo que vas a llevar adelante"*. Después lo aprobó: "da arranque".
- **Qué faltaba.** Precisar en CLAUDE.md que "plan primero" significa mostrar el plan por
  etapas, con archivos y tests, en el mismo mensaje en que se pide autorización.
- **Destino.** CLAUDE.md.

### C7. Auditoría: materialidad y alcance
- **Qué pasó.** En la revisión integral propuse una nota por una fila con ámbito vacío (29
  alumnos) y confirmar el desfase con un Anuario. El usuario: *"Sin agregar la nota del ámbito
  vacío, es despreciable. No importa lo del anuario"*.
- **Qué faltaba.** Un criterio de materialidad: lo que no mueve ninguna cifra mostrada se
  informa en una línea y no genera nota ni alerta. Y una regla para los cotejos externos: se
  proponen como opcionales, no como pendientes.
- **Tensión con la plantilla.** "No se ocultan ni corrigen en silencio" empuja a anotar todo. Hay
  que distinguir **informar** (siempre, en la respuesta) de **registrar o mostrar** (solo si es
  material).
- **Destino.** `validar-calidad` y skill nueva `auditar`.

### C8. README del proyecto
- **Qué pasó.** El README generado conservaba "Requisitos", "Uso", "Qué incluye" y "Comandos
  frecuentes", todo de la plantilla. El usuario: *"Borre todo lo relacionado al template, deje
  fuentes y resultados y qué analiza"*.
- **Qué faltaba.** `nuevo_proyecto.sh` solo quita los bloques `plantilla:inicio/fin`. El resto
  del contenido del entorno queda en el README del proyecto.
- **Destino.** Plantilla: mover el contenido del entorno a `docs/entorno.md`, o envolverlo en
  `plantilla:` y dejarlo en un archivo aparte. Skill `publicar`: antes de publicar, revisar que el
  README sea del proyecto.

### C9. Cambio normativo de Buenos Aires y "total país sin PBA"
- **Qué pasó.** El usuario aportó la Res. 1650/24 (fin de la repitencia en bloque en PBA) y pidió
  tres unidades: total país, cada provincia y total país sin Buenos Aires.
- **Qué faltaba.** Nada en la plantilla: es conocimiento de dominio. La parte genérica sí la
  detecté: una unidad grande que mueve el total. Ya proponía la serie "sin esa unidad".
- **Destino.**
  - Lo específico queda en el proyecto: alertas y `PROVINCIA_EXCLUIDA`.
  - Lo genérico va a `validar-calidad`: cuando una alerta en una unidad con más del X % del total
    explica el movimiento del total, proponer la serie "total sin <unidad>".
  - Función `sumar_excluyendo` en `edu_data.metricas`.

### C10. Performance
- **Qué pasó.** *"Todo lo que implique mejora en performance es importante"*. Resultado: la
  construcción completa bajó de unos 29 s a unos 7 s y los tests de unos 40 s a unos 10 s.
  - El cambio en `io.py` es genérico: arma el DataFrame una sola vez y resuelve los enteros con
    una regex.
  - Las lecturas se hacen en paralelo.
  - Las fixtures de los tests son de sesión.
  - Los agregados se derivan de la base intermedia y no de la larga.
- **Destino.** CLAUDE.md (preferencia de trabajo), el upstream de `io.py` y
  `edu_data.series.leer_en_paralelo`.

---

## 2. Pasos hechos a mano que se repiten en cualquier dataset

| Paso | Cómo se hizo | ¿Se repite? | Destino |
|---|---|---|---|
| Descubrir los links reales de descarga (la página arma la tabla desde una planilla de Google; los archivos están en SharePoint con cookie) | Scripts en el scratchpad y después `src/edu_data/descarga.py` | Sí, para cualquier base de la misma página (matrícula por edad, egresados, trayectoria…) | `edu_data.descarga` (genérico: descargar sin pisar, con reintentos) + `edu_data.ar.datos_abiertos_educacion` (planilla + SharePoint) |
| Reintentar un 503 | A mano | Sí | `edu_data.descarga` |
| Bajar el diccionario Excel y el PDF metodológico a `data/raw/` | Scratchpad → `cp` denegado → script | Sí | `dataset-nuevo` §0: todo insumo por script desde el inicio |
| Detectar encoding, separador y BOM | `detectar_formato` (plantilla) | Ya cubierto | — |
| Leer el diccionario Excel por hoja | `listar_hojas` / `leer_hoja` (plantilla) | Ya cubierto | — |
| Normalizar nombres de columna entre años (`Departamento` en 2024) | `diff_columnas` + `str.lower` en el lector | Ya cubierto en parte | `leer_csv_oficial` ya pasa a minúsculas: documentarlo en la skill |
| Cruzar variables del CSV con el diccionario y listar las que no tienen definición | Script ad hoc | Sí | `edu_data.perfil.cruzar_diccionario(df, dicc, col_variable)` |
| Encontrar el error del diccionario (descripciones de `s_lactantes`/`s_deambulantes` intercambiadas) | Lectura manual | El chequeo sí se repite | `dataset-nuevo` §8: comparar la descripción con el prefijo y el perfil |
| Decidir si vacío = sin oferta o = cero no escrito | Perfil + cruce con el denominador | Sí | `edu_data.perfil.vacios_con_denominador(df, pares)` + regla corregida |
| Verificar el período con un shock (pandemia) | Tabla de repitencia por archivo | Sí | `edu_data.perfil.buscar_shock(t, valor, periodos_esperados)` |
| Asignar el nivel por año corrido según la estructura provincial (primaria de 6 o 7 años) y validarlo con datos (repitencia de 7º parecida a la de 6º o a la de 8º) | Constantes + script de validación | Sí para cualquier base del RA argentino | `edu_data.ar.niveles` |
| Leer N archivos anuales con un patrón de nombre, en paralelo, y unirlos | `matricula.archivos_raw` + `_leer_en_paralelo` | Sí | `edu_data.series` |
| Pasar de ancho a largo con prefijos de bloque (`v_`, `r_`, `s_`) | `matricula._bloque` | Sí (formato típico del RA) | `edu_data.series.ancho_a_largo(df, prefijos, sufijos)` |
| Porcentaje con NA si el denominador es NA o 0 | `descripcion.pct` | Sí | `edu_data.metricas.pct` |
| Total país, por provincia y "total sin X" | `por_provincia_y_pais`, `sumar_corte` | Sí | `edu_data.metricas` |
| Formatear cifras redondeando una sola vez | `_num` en los tests | Sí | `edu_data.cifras.formatear` |
| Testear las cifras escritas en textos (alertas, portada) | `tests/test_textos_cifras.py` a mano | Sí | `edu_data.cifras.verificar_cifras` + regla |
| Geometría de provincias (IGN), recorte antártico, recuadro de CABA, SVG | `src/edu_data/geo.py` | Sí para cualquier visor argentino por provincia | `edu_data.ar.geo` |
| Plantilla HTML + JSON embebido + marca GENERADO | `visor_matricula.py` / `.html` | Sí | `edu_data.visor.renderizar` + skill `visor-interactivo` |
| Comando único raw → outputs con tiempos por paso | `construir_todo.py` | Sí | `edu_data.construir` (helper `paso`) + convención |
| Tests con datos reales: fixtures de sesión, *skip* en local y *fail* en CI | `tests/conftest.py` | Sí | plantilla `tests/conftest.py` (helper `requiere_crudos`) |
| Recalcular los totales con otro motor (DuckDB sobre los CSV) para auditar | Script ad hoc | Sí | Skill `auditar` + `edu_data.auditoria.recalcular_duckdb` (opcional) |
| Simular la CI en una copia limpia | Skill `publicar` §4 | Ya cubierto (y encontró P2) | — |
| Verificar el visor renderizado (capturas) | Falló: faltan librerías del sistema | Sí | Dockerfile (P5) |

---

## 3. Propuestas por destino

### 3.1 CLAUDE.md: reglas nuevas o corregidas

Borrador completo de las secciones afectadas. Se reemplazan o agregan en el CLAUDE.md de la
plantilla.

```markdown
## Forma de trabajo
- Por defecto, siempre plan primero (modo plan: explorar, preguntar, proponer pasos).
  No se escribe ni modifica código hasta que el desarrollador lo pida explícitamente.
- Al pedir autorización para implementar, mostrar en el mismo mensaje el plan por etapas
  (archivos que se crean, tests, comando de construcción). No cerrar con "¿arranco?" sin plan.
- No se hacen commits ni push sin autorización explícita.
- Ante rediseños o pedidos ambiguos, preguntar antes: alcance, formato, ejes, cortes, medida.
- En preguntas y propuestas, ningún código crudo sin glosa: `_snu` → "superior no universitario
  (profesorados), ~1 M de alumnos". Nombre llano + tamaño o peso.
- Las decisiones sobre los datos (alcance, imputaciones, desfases, exclusiones) se escriben en
  `data/diccionario_<base>.md`, no en la memoria de Claude: la memoria vive fuera del repo y se
  pierde con el contenedor.
- La performance importa: leer en paralelo, armar DataFrames de una vez, derivar agregados de
  la base más chica posible, fixtures de tests con `scope="session"`. Medir antes y después.
- Para actualizar el proyecto a una versión nueva de la plantilla: skill `actualizar-plantilla`.

## Estructura
- `data/raw/` — insumos originales tal como se descargaron (datos, diccionarios, documentos
  metodológicos, geometrías). **No se modifican nunca.** Se llenan con un script de descarga en
  `src/` que nunca pisa archivos existentes, no con `cp` ni a mano.
  Por defecto no se versionan; la skill `publicar` puede decidir versionarlos (datos abiertos y
  livianos que la CI necesita) y en ese caso se anota acá.
- ...

## Convenciones de trabajo con datos
- ...
- Período de referencia: separar "año del archivo" de "período que informa".
  - Antes de construir cualquier tabla, buscar un shock conocido (pandemia 2020, un cambio
    normativo con fecha) y ver en qué archivo aparece.
  - Si aparece en el archivo t+1, la hipótesis por defecto es que **todo el archivo** informa
    t: matrícula, flujos y secciones. No desfasar por variable sin evidencia ni pedido.
  - Si un documento oficial contradice la evidencia, mostrar las dos cosas y preguntar.
  - La decisión se toma con el usuario en la primera respuesta, se codifica como
    `DESFASE_PERIODO` y en todo el pipeline la columna de año es el período. El año del archivo
    se conserva aparte (`anio_archivo`).
- Vacío no es cero: un vacío que significa "no aplica / sin oferta" queda NA en todo el
  pipeline, también en tablas y gráficos (punto vacío o línea omitida, con nota).
  Excepción: un "cero no escrito" puede imputarse a 0 solo con decisión del usuario. La señal
  es una columna sin ningún 0 cuyos vacíos caen donde el denominador existe. Se conserva el
  original y se registra la cantidad de celdas imputadas.
- Categorías derivadas por resta (mujeres = total − varones, privado = total − estatal): se
  calculan en el pipeline y se muestran **todas** las categorías, aclarando cuál es derivada.

## Calidad de datos
- Todo análisis corre controles de pertinencia (skill `validar-calidad`) y reporta en la
  respuesta los datos que parezcan mal.
- Materialidad: todo hallazgo se informa en la respuesta, pero solo va al registro de alertas
  (y a las visualizaciones) si mueve alguna cifra mostrada. Lo despreciable se dice en una línea.
- Las alertas revisadas van a un único registro; las visualizaciones las marcan.
  No se ocultan ni corrigen en silencio.
- Si se corrige un dato, se conserva el original (`<columna>_informado`) y se documenta.

## Análisis y visualización
- ...
- Cada número mostrado se contrasta con el cálculo en Python (tests). Incluye las cifras
  escritas en textos: alertas, portadas de visores, README. Redondear una sola vez, al mostrar
  (`edu_data.cifras`).
- Visores: skill `visor-interactivo`.

## Tests
- Los tests parten de `data/raw/`, nunca de `data/processed/` ni de `outputs/`: en la CI corren
  antes de construir.
- Sin crudos: *skip* en local, *fail* en CI (`requiere_crudos` en `tests/conftest.py`).
```

### 3.2 Skills

| Skill | Acción | Por qué |
|---|---|---|
| `dataset-nuevo` | Modificar: §0 descarga, §4 vacíos, §7 período, §8 glosas | C5, P4, P7 |
| `validar-calidad` | Modificar: materialidad, "total sin unidad", cifras de textos | C7, C9, P1 |
| `publicar` | Modificar: README propio, coherencia con CLAUDE.md, tests sin `processed` | C8, P2, P6 |
| `visor-interactivo` | **Nueva** | C2, C3, C4. Segundo visor escrito desde cero |
| `auditar` | **Nueva** | El pedido de "revisión integral" es un procedimiento de varios pasos que se repite |

Los borradores completos están en §6.

### 3.3 Funciones reutilizables en `src/edu_data/`

| Módulo | Funciones | Origen en este proyecto |
|---|---|---|
| `io.py` (upstream) | Optimizaciones de `leer_csv_oficial` y `unificar_esquema` | Diff ya hecho (ver §6.6) |
| `series.py` (nuevo) | `archivos_por_periodo(dir, patron, desfase=0)`, `leer_en_paralelo(rutas, lector, procesos=4)`, `ancho_a_largo(df, claves, bloques)` | `matricula.archivos_raw`, `_leer_en_paralelo`, `_bloque` |
| `metricas.py` (nuevo) | `pct(parte, total)` (NA si el total es 0 o NA), `sumar_por(df, claves, medidas)`, `sumar_excluyendo(df, unidad_col, excluir)` | `descripcion.pct`, `sumar_corte`, `por_provincia_y_pais` |
| `cifras.py` (nuevo) | `formatear(valor, decimales=1)` (coma decimal, redondeo único), `cifras_en_texto(texto)`, `verificar_cifras(texto, esperados)` | `tests/test_textos_cifras.py` |
| `perfil.py` (agregar) | `vacios_con_denominador(df, pares)`, `cruzar_diccionario(df, dicc)`, `buscar_shock(t, valor, periodo, esperado)` | Scripts de exploración |
| `visor.py` (nuevo) | `renderizar(plantilla, datos, destino, marca)`: JSON embebido y escapado (`</` → `<\/`) + marca GENERADO | `visor_matricula.generar` |
| `construir.py` (nuevo) | `paso(nombre, funcion)` con tiempos; `preparar_sitio(html, destino)` → `index.html` | `construir_todo.py` |
| `descarga.py` (nuevo, genérico) | `descargar(url, destino, reintentos=3)` que nunca pisa archivos | `descarga.py` |
| `ar/` (nuevo, opcional) | `ar.geo` (provincias IGN → SVG, recorte antártico, recuadro de CABA); `ar.niveles` (`PRIMARIA_6`, `PRIMARIA_7`, `nivel_de(grado, provincia)`); `ar.provincias` (nombres normalizados entre fuentes); `ar.datos_abiertos_educacion` (planilla + SharePoint) | `geo.py`, `matricula.py`, `descarga.py` |
| `tests/conftest.py` (plantilla) | `requiere_crudos(condicion, motivo)`: *skip* local, *fail* con `CI` | `conftest.py` del proyecto |

**Decisión para vos:** ¿la plantilla es solo para datos argentinos? Si sí, `ar/` va directo. Si
no, conviene un paquete aparte o un flag del generador (`-pais ar`), como el `-so windows`
actual.

### 3.4 Nada (propio de este dataset)
Ver §4.2.

---

## 4. Genérico vs. específico

### 4.1 Genérico → plantilla
- Todas las reglas de §3.1.
- Las skills `visor-interactivo` y `auditar`, y los cambios a `dataset-nuevo`,
  `validar-calidad` y `publicar`.
- `io.py` optimizado, `series`, `metricas`, `cifras`, `visor`, `construir`, `descarga`, el helper
  de `conftest`.
- **Semi-genérico (Argentina):** `ar.geo`, `ar.niveles`, `ar.provincias`,
  `ar.datos_abiertos_educacion`. Sirven para cualquier base del Relevamiento Anual o de la página
  de datos abiertos de la Secretaría.
- Plantilla: README sin contenido del entorno, Dockerfile con navegador headless, ajuste de
  `settings.json` (§5).

### 4.2 Específico → queda en el proyecto
- `DESFASE_PERIODO = 1` (el valor; el mecanismo es genérico).
- Imputación de sobreedad vacía a 0 (`imputar_sobreedad`) y su evidencia.
- `_1314` pendiente, `localizacion` descartada (filtrada en 2024), `_20` (no graduada desde
  2023), SNU fuera de alcance.
- El error del diccionario oficial (`s_lactantes`/`s_deambulantes`).
- Las alertas: Santa Cruz 2019–2023, Santiago del Estero 2010, Catamarca 2011, pandemia 2020,
  quiebre 2016, PBA 2024 (Res. 1650/24), `_sec20` en 0.
- `PROVINCIA_EXCLUIDA = "Buenos Aires"` y la serie "total país sin PBA".
- Medida de repitencia (% de repitentes sobre la matrícula del mismo año, no la tasa
  DINIECE): decidida con el usuario.
- ID de la planilla de Google y links de SharePoint (vigentes al 2026-11-08).
- El contenido y los textos del visor.

---

## 5. Elementos de la plantilla poco relevantes o que generaron problemas

### Generaron problemas
1. **`deny: Write/Edit(data/raw/**)` en `settings.json`.** Bloqueó dos veces copiar el diccionario
   y el PDF oficiales (dos `cp` denegados, el último a las 13:50). Quedaron en el scratchpad, que se
   pierde. Después `geo.py` y `descarga.py` escribieron en `data/raw/` sin problema.
   - La regla protege poco y molesta en el caso legítimo (agregar insumos nuevos).
   - Propuesta: mantener el *deny* de Edit (modificar) y documentar en `dataset-nuevo` que los
     insumos entran **solo por script de descarga**, que nunca pisa. Así el permiso y el
     procedimiento dicen lo mismo.
2. **"No se versionan" (CLAUDE.md) vs. `publicar` §2 (versionar crudos livianos).** Al final de la
   sesión, CLAUDE.md quedó contradiciendo el `.gitignore` del proyecto. Lo marqué y no lo toqué.
   Propuesta en §3.1.
3. **README generado con contenido de la plantilla** (C8).
4. **Heurística de `dataset-nuevo` §4** ("una columna con vacíos y sin ningún cero → el vacío
   marca ausencia de oferta"). Aplicada a la sobreedad, que nunca trae 0, habría dado la
   conclusión opuesta a la correcta. La señal útil es el cruce con el denominador (P7).
5. **Dockerfile sin dependencias de navegador.** Playwright no pudo lanzar Chromium. El visor se
   probó en un navegador simulado y el usuario tuvo que mirarlo a ojo dos veces. Propuesta:
   en `post-create.sh`, `uv run playwright install --with-deps chromium`, o las librerías en el
   Dockerfile. Pesa unos 300 MB: evaluar si vale la pena.
6. **`<columna>_informado` por columna.** Con 13 grados duplicó las columnas de sobreedad, y tuve
   que preguntar si era aceptable. Propuesta: permitir, para imputaciones masivas de un mismo
   tipo, una columna de conteo o una marca por bloque (`celdas_<x>_imputadas`) en lugar de N
   columnas `_informado`.

### No fueron relevantes en este proyecto (no implica sacarlos)
- `notebooks/` y la convención `NN_tema.ipynb`: no se usó ningún notebook. El flujo fue scripts
  en `src/`, tests y visor. Tampoco se usó el kernel de Jupyter de `post-create.sh`.
- Las reglas de ponderadores, valores plausibles y pesos replicados: es un censo. Se descartaron
  bien en una línea.
- `csvstat`/`csvcut` (permisos y csvkit en el Dockerfile): no se usaron. Todo pasó por
  pandas/DuckDB.
- `actualizar-plantilla`: no aplicaba en esta sesión.
- `.devcontainer/certs/`: no aplicaba.
- `publicar.yml.ejemplo`: quedó duplicado junto a `publicar.yml`. Propuesta: que `publicar`
  lo borre después de copiarlo, o mantenerlo solo en la plantilla.
- `.plantilla.json` con URL SSH: en un contenedor sin clave el clon falla. La skill ya lo prevé;
  podría guardarse la URL HTTPS directamente.

### Lo que funcionó (conservar)
- Preguntas con un ejemplo de lectura en cada opción (medida de repitencia): el usuario eligió sin
  repreguntar.
- El registro único de alertas y su marca en el visor.
- La marca `GENERADO por` y la separación HTML de diseño / Python de datos.
- La simulación de la CI en una copia limpia (`publicar` §4): encontró P2 antes del push.
- Las identidades contables y el recálculo independiente con DuckDB en la auditoría.

---

## 6. Borradores completos

### 6.1 `dataset-nuevo` — secciones nuevas o reemplazadas

```markdown
## 0. Descarga reproducible
- Toda descarga va en `src/edu_data/descarga.py` (o `<base>_descarga.py`) desde el primer
  archivo: datos, diccionarios, documentos metodológicos y geometrías. Usar
  `edu_data.descarga.descargar` (reintentos, nunca pisa un archivo existente).
- No copiar a `data/raw/` con `cp` ni dejar insumos en carpetas temporales.
- Anotar en el docstring cómo se encontraron los links (p. ej. planilla de Google detrás de la
  página, SharePoint con cookie) y la fecha en que estaban vigentes.

## 4. Vacíos y ceros
- `edu_data.perfil.perfil_columnas(df)`: vacíos y ceros por columna.
- `edu_data.perfil.vacios_con_denominador(df, pares)`: para cada columna, cuántos vacíos caen
  donde su denominador (matrícula del grado, total) existe.
- Lectura:
  - Vacíos solo donde el denominador también está vacío → "no aplica / sin oferta": NA.
  - Columna sin ningún 0 y con vacíos donde el denominador existe → probable **cero no
    escrito**. Proponer imputar a 0, con la evidencia (cantidad de celdas, si crece cuando el
    indicador baja). Decide el usuario.
  - Vacíos dispersos con denominador y con ceros presentes en la columna → dato perdido: NA.
- Documentar la decisión en el diccionario. Si se imputa: original conservado y conteo de
  celdas imputadas.

## 7. Período de referencia
- Buscar al menos un shock con fecha conocida: pandemia 2020 (repitencia y abandono casi nulos,
  promoción automática), un cambio normativo citado por el usuario, un cambio de estructura.
  `edu_data.perfil.buscar_shock(...)`.
- ¿En qué archivo aparece?
  - En el del mismo año → sin desfase.
  - En el del año siguiente → la hipótesis por defecto es que **todo el archivo** informa el
    año anterior. No desfasar por variable sin evidencia específica.
- Si la documentación oficial dice otra cosa ("captura al 30 de abril"), mostrar las dos
  evidencias y **preguntar en la primera respuesta**, como pregunta separada y visible.
- Codificar `DESFASE_PERIODO` con la evidencia en el comentario. La columna de año del pipeline
  es el período; `anio_archivo` se conserva. Visores y textos muestran el período.

## 8. Diccionario
- `edu_data.perfil.cruzar_diccionario(df, dicc)`: variables sin definición, definiciones sin
  variable.
- Controlar que la descripción coincida con el prefijo y el perfil de la variable (p. ej. dos
  descripciones intercambiadas entre salas).
- Pedir al usuario lo que falte en la **primera** respuesta, no al final.
- Al proponer alcance, cada código con glosa llana y tamaño: "`_snu` (superior no universitario:
  profesorados), ~1 M de alumnos, sin repitencia ni sobreedad".
- Las decisiones del usuario van al diccionario, no a la memoria de Claude.
```

### 6.2 Skill nueva: `.claude/skills/visor-interactivo/SKILL.md`

```markdown
---
name: visor-interactivo
description: Diseñar y generar un visor HTML interactivo (mapa, selector de unidad, gráficos
  on demand) a partir de una base procesada. Usar cuando el usuario pide un visor, un tablero,
  "ver la evolución", un mapa por provincia o mostrar resultados de forma interactiva.
---

# Visor interactivo

## 1. Preguntar antes (una sola tanda, con previews ASCII)
- Unidades: total, cada unidad territorial, totales alternativos (p. ej. "total sin X" si una
  alerta de una unidad grande mueve el total).
- Selector de unidad: **mapa** si la unidad es territorial (default), lista si no.
- Indicadores disponibles y, para cada uno, qué cortes tiene en el dataset (sexo, sector,
  ámbito…). Avisar qué cortes **no** existen para un indicador.
- Destino: HTML local en `outputs/` (default) / Pages (skill `publicar`).

## 2. Estructura por defecto
- **Pestaña 1, "Acerca de los datos":** 3–4 párrafos breves.
  - Qué es la fuente.
  - Qué se puede ver.
  - Por qué existen los totales alternativos.
  - Cómo leer el período (si hay desfase).
  - Termina con un botón "Ir al mapa".
- **Pestaña 2, mapa:** botones para los totales arriba y el mapa neutro (sin coroplético salvo
  pedido). Clic en una unidad → panel.
- **Panel, on demand:**
  1. Primero se elige el indicador. No se muestra nada más hasta elegirlo.
  2. Recién entonces aparecen los filtros que ese indicador admite. Los que no aplican, se
     muestran deshabilitados con la nota "El dataset no informa <corte> para este indicador".
  3. Un gráfico de evolución por la dimensión principal (p. ej. nivel).
  4. Debajo, solo la lista de alertas de la selección.
- **Sin tablas debajo del gráfico.** El valor exacto va en el tooltip. Una tabla de detalle solo
  con pedido explícito.
- Sexo u otras categorías derivadas por resta: mostrar todas las categorías (Total / Varones /
  Mujeres), con una nota de cuál es derivada.
- Corte sin oferta: "Sin oferta para este corte", no ceros. NA = punto vacío o línea cortada.

## 3. Arquitectura
- `src/edu_data/visor_<base>.py`: arma un dict con **todos** los números (precalculados en
  Python, vectorizado: todos los cortes de una vez, no unidad por unidad).
- `src/edu_data/visor_<base>.html`: diseño, con un marcador para el JSON.
- `edu_data.visor.renderizar(plantilla, datos, destino, marca)`: embebe el JSON escapado y la
  marca `GENERADO por …`. Salida autocontenida, rutas relativas, sin CDN si va a Pages.
- Mapa: `edu_data.ar.geo.caminos_svg()` (Argentina) o equivalente. Geometría descargada por
  script a `data/raw/`.
- Alertas: `alerta_para(ALERTAS, …)` → anillo en el punto del indicador afectado y texto en el
  tooltip.
- Cargar la skill `dataviz` para colores, marcas y modo oscuro.
- Medir el tamaño del HTML. Si pasa de ~1 MB, revisar qué datos sobran.

## 4. Verificación
- Tests: cada serie del visor = tabla testeada = cálculo independiente sobre `data/raw/`, en
  varios cortes (incluido uno rural/privado chico). Las categorías derivadas suman el total.
- Cifras de los textos (portada, alertas): `edu_data.cifras.verificar_cifras`.
- Capturas con Playwright en desktop y en un ancho de 375 px: mapa, tooltip, panel, modo oscuro.
  Si el navegador no está disponible, decirlo y pedir al usuario qué revisar a ojo.

## 5. Entrega
- Decir qué archivo editar (`.py` datos, `.html` diseño) y el comando para regenerar.
- No publicar sin la skill `publicar`.
```

### 6.3 `validar-calidad` — agregados

```markdown
## Revisión
- Para cada señal, mirar el detalle: ¿shock real (pandemia, cambio normativo) o problema de carga?
- Distinguir lo que **afecta el total** (unidades grandes o todas a la vez) de lo local.
  Si una sola unidad explica el movimiento del total (p. ej. >30 % del total y un cambio
  normativo), proponer la serie "total sin <unidad>" (`edu_data.metricas.sumar_excluyendo`).
- **Materialidad:** si la señal no mueve ninguna cifra mostrada (p. ej. 29 alumnos sin ámbito
  sobre 9 M), se informa en una línea en la respuesta y **no** va al registro ni a notas.
- Las señales revisadas que resultan coherentes se documentan en el diccionario como
  "revisadas, sin alerta", para no reabrirlas.
- Cotejos externos (anuarios, otra fuente): proponerlos como opcionales, no como pendientes.
- No corregir sin pedido. Si se corrige, conservar el original (`<indicador>_informado`) y
  documentarlo.

## Registro de alertas
- ...
- `texto`: una línea en lenguaje llano y con números. **Cada número del texto tiene un test**
  (`edu_data.cifras.verificar_cifras`) que lo recalcula desde `data/raw/`. Contar sobre la misma
  medida que se muestra (p. ej. "21 de 24 provincias" sobre el %, no sobre el conteo).
- Un texto que se ve tanto en el total como en una unidad debe leerse bien en los dos casos.
```

### 6.4 `publicar` — agregados

```markdown
## 2. Qué se versiona
- ...
- Si se decide versionar crudos, actualizar en el mismo cambio la línea de `data/raw/` en
  CLAUDE.md ("se versionan: <patrones>, motivo") para que no se contradigan.

## 2b. README
- El README describe el proyecto: qué analiza, datos (período, unidad, decisiones clave),
  fuentes, resultados y cómo reproducir. Nada del entorno o de la plantilla (eso queda en
  `docs/entorno.md`).
- Sin cifras en el README salvo que estén testeadas.
- Proponer la descripción corta del repo (campo About) y los topics.

## 4. Simular la CI antes del push
- ...
- Señal típica de falla: un test que lee `data/processed/` u `outputs/` (en la CI los tests
  corren antes de construir). Corregir para que parta de `data/raw/`.
- Con `CI=true`, los tests de datos deben fallar, no saltearse, si faltan los crudos.

## 7. Después de publicar
- Borrar `publicar.yml.ejemplo` del proyecto, o confirmar con el usuario si lo conserva.
```

### 6.5 Skill nueva: `.claude/skills/auditar/SKILL.md`

```markdown
---
name: auditar
description: Revisión integral de datos y código de un proyecto (recálculo independiente,
  cifras de textos, duplicación, performance). Usar cuando el usuario pide auditar, una
  "revisión integral", "revisar todo" o antes de una entrega o publicación importante.
---

# Auditoría de datos y código

Solo lectura: se informa y se propone. Se corrige después de que el usuario elige qué.

## 1. Datos
1. **Recálculo independiente.** Recalcular los totales principales con otro motor (DuckDB
   leyendo los CSV de `data/raw/` directamente), sin pasar por el lector del proyecto. Comparar
   contra `data/processed/` y contra las series del visor: diferencias = 0 esperadas.
2. **Identidades.** Correr todas las del diccionario: partes = total, subconjunto ≤ total,
   coherencias lógicas (p. ej. sobreedad ≥ repitentes).
3. **Imputaciones.** Verificar que solo se aplicaron donde correspondía y con el valor
   decidido.
4. **Rangos.** Porcentajes en 0–100, sin NaN en lo que se muestra, proporciones plausibles.
5. **Cifras en textos.** Listar cada número escrito (alertas, portada, README) y si tiene test.
6. **Señales sin revisar.** Correr `validar-calidad` y listar lo que no está ni en el registro ni
   en "revisadas".

## 2. Código
- Duplicación (dos caminos para el mismo cálculo), nombres engañosos, trucos frágiles.
- Performance: medir la construcción completa y los tests (`time`). Buscar lecturas repetidas,
  bucles por unidad que se pueden vectorizar, DataFrames armados columna a columna, agregados
  calculados desde la base más grande.
- Reproducibilidad: ¿un solo comando raw → outputs? ¿descarga por script? ¿tests sin
  `data/processed/`?
- Ruff, tests, marca GENERADO en todo lo de `outputs/`.

## 3. Reporte
- Primero el veredicto: ¿hay errores de cálculo? Después, una lista numerada:
  - errores (con la cifra correcta);
  - riesgos;
  - deuda técnica;
  - mejoras de performance, con una estimación.
- Aplicar la **materialidad**: lo despreciable va en una línea, sin proponer notas.
- Cotejos externos (anuarios, otras fuentes) como opcionales.
- Cerrar preguntando qué se corrige. Después de corregir: resultados idénticos valor por valor
  (salvo los cambios buscados) y tiempos antes/después.
```

### 6.6 `src/edu_data/io.py` — upstream (diff contra v0.1.0)

```diff
+# Entero sin ceros a la izquierda: el caso más común se resuelve con una sola regex
+_ENTERO_LIMPIO = re.compile(r"^-?(?:0|[1-9]\d*)$")
 ...
 def _tipar_columna(serie, decimal):
     ...
+    if valores.str.match(_ENTERO_LIMPIO).all():
+        return serie.astype("Int64")
 ...
 def leer_csv_oficial(...):
-    df = pd.DataFrame(index=crudo.index)
+    # Las columnas se arman aparte y el DataFrame se crea una sola vez: agregarlas de a una
+    # fragmenta el bloque de memoria y es mucho más lento en archivos anchos
+    columnas = {}
     ...
-        df[columna] = _tipar_columna(serie, decimal)
+        columnas[columna] = _tipar_columna(serie, decimal)
     ...
+    df = pd.DataFrame(columnas, index=crudo.index)
 ...
 def unificar_esquema(...):
-        for columna in ausentes:
-            if columna in tipos:
-                nuevo[columna] = nuevo[columna].astype(tipos[columna])
+        # attrs se asignan al final: pandas los copia en cada operación sobre el DataFrame
+        nuevo.attrs = {}
+        tipos_ausentes = {c: tipos[c] for c in ausentes if c in tipos}
+        if tipos_ausentes:
+            nuevo = nuevo.astype(tipos_ausentes)
```

### 6.7 Firmas propuestas para los módulos nuevos

```python
# edu_data/series.py
def archivos_por_periodo(directorio: Path, patron: re.Pattern, desfase: int = 0) -> dict[int, Path]:
    """{período: ruta}; período = año del nombre − desfase. Error si hay períodos repetidos."""

def leer_en_paralelo(rutas: list[Path], lector: Callable, procesos: int = 4) -> list[pd.DataFrame]:
    """Aplica `lector` a cada ruta en procesos separados, conservando el orden."""

def ancho_a_largo(df: pd.DataFrame, claves: list[str], bloques: dict[str, str],
                  sufijos: list[str]) -> pd.DataFrame:
    """bloques={"matricula": "_{}", "varones": "v_{}"} → una fila por clave × sufijo."""

# edu_data/metricas.py
def pct(parte: pd.Series, total: pd.Series) -> pd.Series:
    """100·parte/total; NA si total es NA o 0. Sin redondear."""

def sumar_excluyendo(df, unidad: str, excluir: list[str], claves: list[str], etiqueta: str):
    """Total de las unidades menos `excluir`, con la etiqueta dada (p. ej. 'Total sin X')."""

# edu_data/cifras.py
def formatear(valor: float, decimales: int = 1) -> str:
    """Coma decimal, sin ',0' final; redondeo único desde el valor sin redondear."""

def verificar_cifras(texto: str, esperados: list[float], decimales: int = 1) -> list[str]:
    """Cifras esperadas que no aparecen en `texto` (vacía = ok)."""

# edu_data/perfil.py
def vacios_con_denominador(df: pd.DataFrame, pares: dict[str, str]) -> pd.DataFrame:
    """Por columna: vacíos, vacíos con denominador presente, ceros. Señal de cero no escrito."""

def cruzar_diccionario(df: pd.DataFrame, dicc: pd.DataFrame, col: str = "variable") -> dict:
    """{'sin_definicion': [...], 'sin_variable': [...]} sin distinguir mayúsculas."""

def buscar_shock(t: pd.DataFrame, valor: str, periodo: str, esperado: int) -> pd.DataFrame:
    """Variación por período; marca dónde cae el mínimo/máximo frente al año esperado."""

# edu_data/visor.py
def renderizar(plantilla: Path, datos: dict, destino: Path, marca: str) -> Path:
    """Inserta el JSON (escapando '</') en el marcador de la plantilla y antepone la marca."""

# edu_data/construir.py
def paso(nombre: str, funcion: Callable, *args) -> Any:
    """Corre un paso de construcción e imprime su duración."""

# edu_data/descarga.py
def descargar(url: str, destino: Path, reintentos: int = 3, abridor=None) -> bool:
    """Baja `url` a `destino` si no existe. False si ya estaba. Reintenta 5xx con espera."""

# tests/conftest.py (plantilla)
def requiere_crudos(condicion: bool, motivo: str) -> None:
    """Sin crudos: pytest.skip en local, pytest.fail si la variable CI está definida."""
```

### 6.8 Plantilla: entorno y generador
- `scripts/nuevo_proyecto.sh`: mover "Requisitos", "Uso", "Qué incluye" y "Comandos frecuentes"
  a `docs/entorno.md` (o envolverlos en `plantilla:`). El README generado queda solo con las
  secciones del proyecto.
- `.devcontainer/post-create.sh` (opcional, pesa ~300 MB):
  `uv run --with playwright playwright install --with-deps chromium`.
- `.claude/settings.json`: mantener `deny Edit(data/raw/**)`, revisar `deny Write(data/raw/**)`
  según §5.1, y agregar `Bash(time:*)` y `Bash(duckdb:*)` a `allow` si se adopta `auditar`.
- `CHANGELOG.md` v0.2.0: listar todo lo anterior, con "Pasos manuales" para quien actualice
  (p. ej. borrar el README de entorno si ya se reescribió).

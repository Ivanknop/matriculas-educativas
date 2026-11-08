# Diccionario: Matrícula agregada (Relevamiento Anual)

## Qué es
- **Fuente:** Relevamiento Anual (RA), Educación Común. Subsecretaría de Información y Evaluación
  Educativa, Secretaría de Educación (Ministerio de Capital Humano). Es un **censo** de todos los
  establecimientos: no hay muestra ni ponderador.
- **Archivos:** `data/raw/AAAA Matricula - agregada.csv`, archivos 2011 a 2025 (15 archivos).
- **Año: el del archivo = ciclo lectivo de la matrícula** (inscriptos al 30 de abril, fecha
  única de captura según el documento metodológico). Serie: **2011 a 2025**. En todo el
  pipeline, tablas y visor, `anio` es el año del archivo. Decisión del desarrollador (corrige un
  desfase de un año que se había aplicado antes a toda la base).
  - **Repitentes y sobreedad** son de los inscriptos de ese año, pero **reflejan cómo terminó el
    ciclo anterior**: quien no promovió en el ciclo t−1 aparece como repitente en la matrícula
    de t.
  - Evidencia, pandemia: la promoción acompañada del ciclo 2020 se ve recién en la **matrícula
    2021**: repitencia de primaria 0,67 % y de secundaria 1,72 %, contra 2,49 % y 8,31 % en
    2020. El visor lo marca con una banda entre 2020 y 2021 (`EVENTOS` en
    `src/edu_data/visor_matricula.py`).
  - Evidencia, Buenos Aires: la Res. 1650/24 rige en el ciclo 2024 y se ve en la matrícula 2025.
  - **Repitentes**: alumnos que cursan por segunda vez el año en el que están inscriptos.
- **Documentos de referencia** (en `data/raw/`, los baja `edu_data.descarga`):
  `Diccionario de bases RA anonimizadas.xlsx`, hoja "Matricula", y
  `Notas metodologicas acerca del proceso de anonimizacion.pdf`.

## Unidad y forma
- **Fila:** agregado de provincia × departamento × sector × ámbito. Entre 1.191 (archivo 2011) y
  1.217 (archivo 2025) filas por archivo. La clave es única en todos los años.
- **Formato ancho:** un bloque de columnas por grado, con prefijo según la medida:

| Prefijo | Medida | Grados disponibles |
|---|---|---|
| (ninguno) / `_` | Matrícula total | salas, `_1`…`_12`, `_1314`, `_20`, `_snu` |
| `v_` | Matrícula de varones | ídem |
| `r_` | Repitentes | `_1`…`_12`, `_1314`, `_20` |
| `s_` | Alumnos con sobreedad | salas, `_1`…`_12`, `_1314` |
| `_sec` | Secciones independientes | salas, `_1`…`_12`, `_1314`, `_20` |
| `multi_*`, `multinivel` | Secciones múltiples / multinivel | por nivel |

- **Sexo:** solo la matrícula trae varones. **Mujeres = matrícula − varones** (derivada).
  Repitentes y sobreedad **no** vienen por sexo.

## Identificación
| Variable | Qué es | Tipo | Valores / códigos | Notas |
|---|---|---|---|---|
| `provincia` | Jurisdicción | texto | 24 jurisdicciones (incluye "Ciudad de Buenos Aires") | Sin códigos |
| `departamento` | Departamento / partido / comuna | texto | Nombre; "Enmascarado" | Ver abajo |
| `sector` | Sector de gestión | texto | Estatal, Privado | |
| `ambito` | Ámbito | texto | Urbano, Rural | 1 fila vacía (2021) |

**"Enmascarado"** (unas 67 filas por año): por secreto estadístico (Ley 17.622) se fusionan en
una fila por provincia, sector y ámbito los departamentos con 3 localizaciones o menos. No afecta
los totales provinciales ni el del país.

## Variables
| Variable | Qué mide (lenguaje llano) | Tipo | Unidad | Fuente de la definición |
|---|---|---|---|---|
| `lactantes`, `deambulantes`, `s2`…`s5` | Matrícula de nivel inicial por sala | entero | alumnos | diccionario oficial |
| `_1`…`_12` | Matrícula por **año corrido**: años de estudio numerados de forma continua desde 1º de primaria hasta el último de secundaria | entero | alumnos | diccionario oficial; "año corrido" interpretado |
| `_1314` | "Matrícula _1314 año corrido" | entero | alumnos | diccionario oficial. **Significado pendiente** (ver Pendientes) |
| `_20` | Matrícula de **organización no graduada**: alumnos sin asignación a un año de estudio (cursada por módulos o trayectos). Existe desde 2023 | entero | alumnos | diccionario oficial |
| `_snu` | Matrícula del **Superior No Universitario** (profesorados, tecnicaturas superiores) | entero | alumnos | diccionario oficial. **Fuera del alcance** |
| `v_<grado>` | Varones matriculados | entero | alumnos | diccionario oficial |
| `r_<grado>` | Repitentes | entero | alumnos | diccionario oficial |
| `s_<grado>` | Alumnos con **sobreedad** | entero | alumnos | diccionario oficial; criterio abajo |
| `_sec<grado>` | Secciones independientes | entero | secciones | diccionario oficial |
| `multi_ini`, `multi_pri`, `multi_sec` | Secciones múltiples (plurigrado) de inicial, primaria y secundaria | entero | secciones | diccionario oficial |
| `multinivel` | Secciones multinivel | entero | secciones | diccionario oficial |
| `localizacion` | Solo en el archivo 2024, no figura en el diccionario. Parece la cantidad de localizaciones | — | — | **Se descarta** en la lectura |

**Sobreedad (criterio):** se ingresa a 1º con 5 o 6 años y se suma un año por grado (1º: 5/6,
2º: 6/7, …) hasta terminar la secundaria con 17/18 años; en técnicas, un año más (18/19).
Sobreedad = tener más edad que la que corresponde al año que se cursa. El conteo `s_` viene
calculado por el Ministerio; esta base no trae edades para verificarlo (la base "Matrícula por
edad" lo permitiría).

**Error del diccionario oficial:** las descripciones de `s_lactantes` y `s_deambulantes` están
intercambiadas. Sin efecto: la sobreedad de inicial está fuera del alcance.

## Nivel educativo (derivado)
El archivo no trae nivel. Se asigna por grado y por la estructura de primaria de cada provincia
(constantes `PRIMARIA_6` y `PRIMARIA_7` en `src/edu_data/matricula.py`):

| Nivel | Grados |
|---|---|
| inicial | salas (solo matrícula) |
| primaria | 1º–6º; 7º en provincias de primaria de 7 años |
| secundaria | 8º–12º y `_1314`; 7º en provincias de primaria de 6 años |
| no_graduada | `_20` (aparte) |

- **Primaria de 6 años:** Buenos Aires, Catamarca, Chubut, Córdoba, Corrientes, Entre Ríos,
  Formosa, La Pampa, San Juan, San Luis, Tierra del Fuego, Tucumán.
- **Primaria de 7 años:** Chaco, Ciudad de Buenos Aires, Jujuy, La Rioja, Mendoza, Misiones,
  Neuquén, Río Negro, Salta, Santa Cruz, Santa Fe, Santiago del Estero.
- Se aplica igual a toda la serie. **Verificación:** en todas las provincias y años, la repitencia
  de 7º se parece a la de 6º donde la primaria es de 7 años y a la de 8º donde es de 6. Ninguna
  provincia muestra un cambio de estructura en el período.

## Relaciones e identidades
- `v_g ≤ g`, `r_g ≤ g`, `s_g ≤ g` para cada grado: **cierran en los 15 años** (0 fallas).
- Total país = suma de provincias, y formato largo = totales del archivo: verificado en tests.
- Derivadas: `mujeres = matricula − varones`; `nivel` (tabla de arriba).

## Vacíos y ceros
- **Matrícula vacía = sin oferta** de ese grado en esa fila. Evidencia: en matrícula no aparece
  ningún 0, y donde está vacía también lo están varones y repitentes. Queda NA, nunca 0; en el
  formato largo, la fila no existe.
- **Sobreedad vacía con matrícula presente = 0** (decisión del usuario). Evidencia: la fuente no
  escribe ningún 0 de sobreedad en 15 años, y estos vacíos crecen a medida que baja la sobreedad
  (171 celdas en 2011, 2.175 en 2025). El original queda en `s_<grado>_informado` (ancho) y
  `sobreedad_informado` (largo); `sobreedad_imputada` marca la celda. En total: 15.992 de 220.032
  celdas de primaria y secundaria, con el 1,6 % de la matrícula.
- **Sobreedad vacía sin matrícula:** queda NA.
- Columnas que no existen en un año (`_20` antes de 2023): NA, no 0.

## Diferencias entre períodos
| Archivo | Cambio |
|---|---|
| 2023 | Aparecen `_20`, `v_20`, `r_20`, `_sec20` (organización no graduada) |
| 2024 | `Departamento` con mayúscula (se normaliza); aparece `localizacion` (se descarta) |
| 2025 | Vuelve al esquema del archivo 2023 |

## Base procesada (`uv run python -m edu_data.construir_todo`)
`matricula_corte` se arma desde el formato largo; `matricula_nivel` y `matricula_grado` se
derivan de ella (un solo camino para los números, verificado en tests contra el largo).

| Archivo en `data/processed/` | Contenido |
|---|---|
| `matricula_largo.parquet` | Una fila por año × provincia × departamento × sector × ámbito × grado con oferta. SNU excluido |
| `matricula_nivel.parquet` | Por año × provincia × nivel, más `provincia = "Total país"` |
| `matricula_grado.parquet` | Por año × provincia × nivel × grado, más total país |
| `matricula_corte.parquet` | Por año × provincia × sector × ámbito × nivel × grado (base de los cortes del visor) |

Medidas: `matricula`, `varones`, `mujeres`, `repitentes`, `sobreedad` y, en los agregados,
`celdas_sobreedad_imputadas`. Un grupo sin ningún dato queda NA (p. ej. repitentes en inicial).

## Visor
`uv run python -m edu_data.visor_matricula` genera `outputs/visor_matricula.html`: una pestaña de
descripción y un mapa. Al elegir una provincia, el total país o el total país sin Buenos Aires,
se elige el indicador (matrícula, repitencia, sobreedad) y se filtra por sector y ámbito; el
sexo solo aplica a la matrícula. "Sin Buenos Aires" existe solo por la Res. 1650/24.
Fuentes del visor: `src/edu_data/visor_matricula.py` (datos) y `visor_matricula.html` (diseño).

## Calidad
Alertas revisadas en `src/edu_data/alertas.py`; controles en `outputs/validacion_matricula_*.csv`
(`uv run python -m edu_data.validar_matricula`).
- **2021, todo el país:** efecto de la pandemia (ciclo 2020) en repitencia y sobreedad (real).
- **2017, todo el país:** la repitencia de primaria sube de 2,15 % a 3,16 % (2º a 6º a la vez)
  y la de 12º se duplica, en 21 de 24 provincias, y el nivel se mantiene. Posible cambio de
  criterio del relevamiento; a confirmar con el Anuario.
- **Santiago del Estero 2011, secundaria:** repitencia 2,4 % y matrícula 9 % por debajo de 2012.
- **Catamarca 2012, secundaria:** la matrícula cae 11 % y rebota 7 % al año siguiente.
- **Santa Cruz 2020–2024, secundaria:** repitencia 0 %; sobreedad de 39,5 % a 7,8 % y rebote en
  2025. Empieza antes del efecto de la pandemia (2021).
- **Buenos Aires 2025, secundaria — cambio normativo, no error.** La Resolución 1650/24
  (nuevo régimen académico) elimina la repitencia en bloque: solo se recuperan las materias
  desaprobadas. Rige en el ciclo 2024 y el efecto aparece en la matrícula 2025, porque los
  repitentes reflejan el cierre del ciclo anterior. La repitencia baja de 6,2 % a 2,5 % y la
  sobreedad de 19,9 % a 15,5 %, en buena parte porque hay menos repitentes nuevos, que casi
  siempre tienen sobreedad. Desde 2025 la repitencia de Buenos Aires no es comparable con los
  años anteriores, y como la provincia es casi el 42 % de la secundaria del país, tampoco lo
  es el total país.
- **`_sec20` 2024–2025:** alumnos de organización no graduada con 0 secciones.
- **Santa Fe 2022–2025, secundaria — revisada, coherente (sin alerta).** La repitencia pasa de
  7,5 % (2022) a 15,5 % (2025), por encima de la mediana (11,8 %). La suba se ve en 9º a 11º
  (de 12 % a 20 %), se concentra en el sector estatal (20,2 % en 2025) y la sobreedad la
  acompaña (de 21,1 % a 26,4 %): dinámica real, no un problema de carga.
- Los atípicos de 2011–2013 en primaria son el comienzo de una tendencia descendente (unidad
  pedagógica 1º–2º: repitencia de 1º de 6,7 % a 0,7 % entre 2011 y 2015), no errores.

## Pendientes
- **`_1314`:** el diccionario dice "Matrícula _1314 año corrido". Hipótesis: años 13 y 14 de
  las secundarias técnicas (un año más que la común). Hoy cuenta como secundaria y se marca con
  `grado_1314_pendiente`.
- **`localizacion` (archivo 2024):** confirmar qué es; hoy se descarta.
- **Hipótesis sin confirmar:** que `_20` corresponda a programas de reingreso o terminalidad
  (p. ej. PIT 14-17 en Córdoba).
- **Causa de las alertas** de Santa Cruz (¿cambio de régimen académico?) y del quiebre de 2017.

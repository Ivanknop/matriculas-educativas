# Repitencia y sobreedad en la Educación Común argentina

Descripción estructural de la matrícula de Educación Común en Argentina entre 2010 y 2024, con
foco en la **repitencia** y la **sobreedad**. Es un trabajo descriptivo: muestra niveles y
evolución, sin modelar causas.

## Qué analiza
- **Indicadores:** matrícula (total, varones y mujeres), porcentaje de repitentes y porcentaje
  de alumnos con sobreedad, ambos sobre la matrícula del mismo año y grado.
- **Unidades:** total país, cada una de las 24 jurisdicciones y el total país sin Buenos Aires.
- **Aperturas:** nivel (inicial, primaria, secundaria), año de estudio, sector (estatal o
  privado) y ámbito (urbano o rural).

## Datos
- **Origen:** Relevamiento Anual de la Secretaría de Educación, un censo de todas las escuelas
  (no tiene muestra ni ponderadores).
- **Período:** cada archivo informa el año anterior al de su nombre. Los archivos 2011–2025
  cubren los períodos 2010–2024. Se comprobó con la pandemia, cuya repitencia casi nula de 2020
  está en el archivo 2021.
- **Unidad:** cada fila es un agregado de provincia × departamento × sector × ámbito, no una
  escuela ni un alumno.
- **Nivel:** el archivo no lo trae. Se asigna por año de estudio y por la estructura de
  primaria de cada provincia (6 o 7 años), así que 7º es primaria o secundaria según la
  provincia.
- **Sexo:** solo la matrícula distingue varones; mujeres = total − varones. La repitencia y la
  sobreedad no vienen por sexo.
- **Sobreedad:** la fuente nunca escribe 0. Un vacío donde hay matrícula se toma como 0 y se
  conserva el valor original.
- **Vacío no es cero:** un grado sin matrícula es un grado sin oferta y queda vacío, no en 0.
- **Total país sin Buenos Aires:** desde 2024 Buenos Aires aplica un nuevo régimen académico en
  secundaria (Res. 1650/24) sin repitencia en bloque. Como la provincia pesa mucho en el total,
  esta serie muestra la tendencia del resto del país.
- **Alertas de calidad:** hay quiebres y datos dudosos revisados, entre ellos la pandemia (2020),
  un posible cambio de criterio nacional en la repitencia (2016) y la repitencia nula de la
  secundaria de Santa Cruz (2019–2023). Están en `src/edu_data/alertas.py` y el visor las marca.
- **Fuera del alcance:** el nivel superior no universitario y la organización no graduada.

Detalle de variables, decisiones y alertas en
[`data/diccionario_matricula.md`](data/diccionario_matricula.md).

## Fuentes
- [Datos abiertos de la Secretaría de Educación](https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/datos-abiertos-de-la-secretaria-de-educacion):
  archivos "Matricula - agregada", diccionario de variables y documento metodológico.
- [Límites provinciales del IGN](https://infra.datos.gob.ar/georef/provincias.geojson)
  (georef, datos.gob.ar), para el mapa.

Catálogo con fechas de descarga y formatos en [`data/README.md`](data/README.md). Los crudos
(datos abiertos, unos 6 MB) se versionan en `data/raw/` para que la publicación sea
reproducible; `uv run python -m edu_data.descarga` baja lo que falte, sin reemplazar archivos.

## Resultados
- `outputs/visor_matricula.html`: visor interactivo. Tiene una pestaña de descripción y un mapa;
  al elegir una provincia o un total se elige el indicador y se filtra por sexo, sector y ámbito.
- `outputs/validacion_matricula_*.csv`: controles de calidad (saltos y valores atípicos).

Para regenerar todo: `uv run python -m edu_data.construir_todo` (con `--descargar` si falta algo
en `data/raw/`). Tests: `uv run pytest`. Cada push a `main` corre lint, tests y construcción, y
publica el visor en GitHub Pages (`.github/workflows/publicar.yml`).

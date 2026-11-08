# Catálogo de datasets

Una entrada por dataset (o serie de archivos) en `data/raw/`.
El diccionario de cada base va en `data/diccionario_<base>.md`, a partir de
[`_plantilla_diccionario.md`](_plantilla_diccionario.md).

| Archivo | Fuente / URL | Descargado | Período que informa | Unidad de análisis | Encoding / separador | Ponderador | Notas |
|---|---|---|---|---|---|---|---|
| `AAAA Matricula - agregada.csv` (2011–2025, 15 archivos) | Relevamiento Anual, Educación Común. Secretaría de Educación. [Datos abiertos](https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/datos-abiertos-de-la-secretaria-de-educacion) (links a SharePoint del Ministerio). Descarga: `uv run python -m edu_data.descarga` | 2026-11-08 | **El año del archivo** (ciclo lectivo de la matrícula, inscriptos al 30 de abril). Repitentes y sobreedad reflejan el cierre del ciclo anterior: la pandemia (ciclo 2020) se ve en el archivo 2021 y la Res. 1650/24 de Buenos Aires (ciclo 2024) en el 2025 | Agregado provincia × departamento × sector × ámbito | UTF-8 con BOM, `;`, CRLF | No (censo) | [Diccionario](diccionario_matricula.md). Lector: `src/edu_data/matricula.py` |
| `provincias_georef.geojson` | Límites provinciales del IGN, distribuidos por georef ([datos.gob.ar](https://infra.datos.gob.ar/georef/provincias.geojson)). Se descarga con `uv run python -m edu_data.geo` | 2026-11-08 | — | Provincia (24) | GeoJSON, EPSG:4326 | — | Solo para el mapa del visor. Se recorta el sector antártico (al sur de 56° S); nombres de CABA y Tierra del Fuego adaptados al dataset |
| `Diccionario de bases RA anonimizadas.xlsx` y `Notas metodologicas acerca del proceso de anonimizacion.pdf` | Misma página de datos abiertos (links de SharePoint); los baja `edu_data.descarga` | 2026-11-08 | — | — | Excel / PDF | — | Diccionario oficial (hoja "Matricula") y documento metodológico |
| `Diccionario de bases RA anonimizadas(Presentacion).csv` | Hoja "Presentación" del diccionario oficial | Ya estaba (2026-11-07) | — | — | latin-1 | — | Solo el índice de bases; el detalle está en el Excel del diccionario (misma página) |

- **Período que informa**: puede no coincidir con el año del archivo; indicar cómo se verificó.
- **Encoding / separador**: lo detectado (p. ej. `cp1252`, `;`, CRLF), no lo supuesto.

"""Base "Matricula - agregada" del Relevamiento Anual (Educación Común), archivos 2011 en adelante.

Construcción: `uv run python -m edu_data.matricula` (regenera desde data/raw/).
Decisiones y definiciones: data/diccionario_matricula.md.
"""

import multiprocessing
import os
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from edu_data.io import leer_csv_oficial, unificar_esquema

RAIZ = Path(__file__).resolve().parents[2]
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
PATRON_ARCHIVO = re.compile(r"^(\d{4}) Matricula - agregada\.csv$")

# Cada archivo informa el período anterior al año de su nombre (decisión del usuario). Evidencia:
# la repitencia casi nula de la pandemia (2020) está en el archivo 2021, y la Res. 1650/24 de
# Buenos Aires (2024) se ve en el archivo 2025. En todo el pipeline `anio` es el período.
DESFASE_PERIODO = 1

DIMENSIONES = ["provincia", "departamento", "sector", "ambito"]
# Solo viene en 2024 y no figura en el diccionario: se descarta (decisión del usuario)
COLUMNAS_DESCARTADAS = ["localizacion"]

SALAS = ["lactantes", "deambulantes", "s2", "s3", "s4", "s5"]
GRADOS = [str(g) for g in range(1, 13)] + ["1314"]
NO_GRADUADA = "20"
# Lectura en paralelo: con más de 4 procesos el arranque pesa más que lo que se gana
MAX_PROCESOS = 4

# Estructura del nivel primario (Ministerio de Educación). Se verificó con la repitencia de 7º,
# que se parece a la de 6º en las provincias de 7 años y a la de 8º en las de 6 años.
PRIMARIA_6 = frozenset(
    {
        "Buenos Aires",
        "Catamarca",
        "Chubut",
        "Córdoba",
        "Corrientes",
        "Entre Ríos",
        "Formosa",
        "La Pampa",
        "San Juan",
        "San Luis",
        "Tierra del Fuego",
        "Tucumán",
    }
)
PRIMARIA_7 = frozenset(
    {
        "Chaco",
        "Ciudad de Buenos Aires",
        "Jujuy",
        "La Rioja",
        "Mendoza",
        "Misiones",
        "Neuquén",
        "Río Negro",
        "Salta",
        "Santa Cruz",
        "Santa Fe",
        "Santiago del Estero",
    }
)

MEDIDAS = ["matricula", "varones", "mujeres", "repitentes", "sobreedad"]
IMPUTADAS = "celdas_sobreedad_imputadas"
CORTE = ["sector", "ambito", "nivel", "grado", "grado_orden"]
TOTAL_PAIS = "Total país"
# Única provincia que se excluye en un total: su régimen académico cambia desde 2024
PROVINCIA_EXCLUIDA = "Buenos Aires"
SIN_BA = f"{TOTAL_PAIS} sin {PROVINCIA_EXCLUIDA}"


def col_matricula(grado: str) -> str:
    return grado if grado in SALAS else f"_{grado}"


def archivos_raw(directorio: Path = DIR_RAW) -> dict[int, Path]:
    """Archivos de la serie por año del archivo."""
    encontrados = {}
    for ruta in directorio.iterdir():
        coincidencia = PATRON_ARCHIVO.match(ruta.name)
        if coincidencia:
            encontrados[int(coincidencia.group(1))] = ruta
    return dict(sorted(encontrados.items()))


def imputar_sobreedad(df: pd.DataFrame) -> pd.DataFrame:
    """Sobreedad vacía con matrícula presente → 0; el original queda en `s_<grado>_informado`.

    La fuente nunca escribe 0 en sobreedad: el vacío con matrícula significa "ninguno".
    """
    nuevas = {}
    for grado in GRADOS:
        sobreedad, matricula = f"s_{grado}", f"_{grado}"
        if sobreedad not in df:
            continue
        imputar = df[sobreedad].isna() & df[matricula].notna()
        nuevas[sobreedad] = df[sobreedad].mask(imputar, 0)
        nuevas[f"{sobreedad}_informado"] = df[sobreedad]
    # Una sola asignación: cada asignación suelta copia los attrs del DataFrame
    return df.assign(**nuevas)


def leer_anio(ruta: Path) -> pd.DataFrame:
    """Un año: lectura oficial, columnas en minúscula, descartadas fuera, sobreedad imputada."""
    df = leer_csv_oficial(ruta, claves=[*DIMENSIONES, *COLUMNAS_DESCARTADAS])
    df = df.drop(columns=[c for c in COLUMNAS_DESCARTADAS if c in df])
    # Todo lo que no es dimensión es conteo; una columna vacía entera se leería como texto
    conteos = [c for c in df.columns if c not in DIMENSIONES]
    df[conteos] = df[conteos].astype("Int64")
    return imputar_sobreedad(df)


def _leer_en_paralelo(rutas: list[Path]) -> list[pd.DataFrame]:
    """Lee los archivos en procesos aparte: la sobrecarga de pandas por columna es de CPU.

    forkserver con el módulo precargado: arranque rápido y sin el riesgo de fork con los hilos
    de pyarrow ya abiertos.
    """
    procesos = min(MAX_PROCESOS, len(rutas), os.cpu_count() or 1)
    if procesos < 2:
        return [leer_anio(r) for r in rutas]
    contexto = multiprocessing.get_context("forkserver")
    contexto.set_forkserver_preload([__name__])
    with ProcessPoolExecutor(max_workers=procesos, mp_context=contexto) as ejecutor:
        return list(ejecutor.map(leer_anio, rutas))


def leer_serie(directorio: Path = DIR_RAW) -> pd.DataFrame:
    """Todos los años en formato ancho, con esquema común (columnas ausentes → NA).

    `anio` = período que informa; `anio_archivo` = año del nombre del archivo.
    """
    rutas = archivos_raw(directorio)
    if not rutas:
        raise FileNotFoundError(f"No hay archivos 'AAAA Matricula - agregada.csv' en {directorio}")
    dfs = dict(zip(rutas, _leer_en_paralelo(list(rutas.values())), strict=True))
    unificados = unificar_esquema(dfs)
    serie = pd.concat(
        [
            df.assign(anio=archivo - DESFASE_PERIODO, anio_archivo=archivo)
            for archivo, df in unificados.items()
        ],
        ignore_index=True,
    )
    ausentes = {archivo: df.attrs["columnas_ausentes"] for archivo, df in unificados.items()}
    serie.attrs["columnas_ausentes"] = ausentes
    primeras = ["anio", "anio_archivo"]
    return serie[[*primeras, *[c for c in serie.columns if c not in primeras]]]


def nivel_de(grado: str, provincia: pd.Series) -> pd.Series:
    """Nivel de cada fila para un grado: 7º depende de la estructura de la provincia."""
    desconocidas = set(provincia.unique()) - PRIMARIA_6 - PRIMARIA_7
    if desconocidas:
        raise ValueError(f"Provincias sin estructura de primaria asignada: {desconocidas}")
    if grado in SALAS:
        return pd.Series("inicial", index=provincia.index)
    if grado == NO_GRADUADA:
        return pd.Series("no_graduada", index=provincia.index)
    if grado == "7":
        return provincia.map(lambda p: "primaria" if p in PRIMARIA_7 else "secundaria")
    nivel = "primaria" if grado in GRADOS[:6] else "secundaria"
    return pd.Series(nivel, index=provincia.index)


def _bloque(ancho: pd.DataFrame, grado: str) -> pd.DataFrame:
    vacia = pd.Series(pd.NA, index=ancho.index, dtype="Int64")

    def columna(nombre: str) -> pd.Series:
        return ancho[nombre].astype("Int64") if nombre in ancho else vacia

    matricula = columna(col_matricula(grado))
    varones = columna(f"v_{grado}")
    # Sobreedad solo en grados de primaria y secundaria (alcance acordado)
    con_sobreedad = grado in GRADOS
    sobreedad = columna(f"s_{grado}") if con_sobreedad else vacia
    informado = columna(f"s_{grado}_informado") if con_sobreedad else vacia
    bloque = ancho[["anio", *DIMENSIONES]].assign(
        grado=grado,
        nivel=nivel_de(grado, ancho["provincia"]),
        matricula=matricula,
        varones=varones,
        mujeres=matricula - varones,
        repitentes=columna(f"r_{grado}"),
        sobreedad=sobreedad,
        sobreedad_informado=informado,
        sobreedad_imputada=sobreedad.notna() & informado.isna(),
        grado_1314_pendiente=grado == "1314",
    )
    # Matrícula vacía = sin oferta: la fila no aporta y no se convierte en 0
    return bloque[bloque["matricula"].notna()]


def a_formato_largo(ancho: pd.DataFrame) -> pd.DataFrame:
    """Una fila por año, provincia, departamento, sector, ámbito y grado (SNU excluido)."""
    grados = [*SALAS, *GRADOS, NO_GRADUADA]
    largo = pd.concat([_bloque(ancho, g) for g in grados], ignore_index=True)
    orden = {g: i for i, g in enumerate(grados)}
    largo["grado_orden"] = largo["grado"].map(orden).astype("Int64")
    largo["sobreedad_imputada"] = largo["sobreedad_imputada"].astype(bool)
    # Las columnas ausentes por año son del formato ancho; copiarlas en cada operación es caro
    largo.attrs = {}
    return largo.sort_values(["anio", *DIMENSIONES, "grado_orden"], ignore_index=True)


def agregar(tabla: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Suma de medidas por `por`; un grupo sin ningún dato queda NA (no 0).

    Acepta el formato largo o una tabla ya agregada (que trae `celdas_sobreedad_imputadas`).
    """
    imputadas = "sobreedad_imputada" if "sobreedad_imputada" in tabla else IMPUTADAS
    agrupado = tabla.groupby(por, dropna=False, observed=True)
    resultado = agrupado[MEDIDAS].sum(min_count=1)
    resultado[IMPUTADAS] = agrupado[imputadas].sum()
    return resultado.reset_index()


def por_provincia_y_pais(tabla: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Agregado por provincia más una fila de total país (`provincia = "Total país"`)."""
    provincias = agregar(tabla, ["anio", "provincia", *por])
    pais = agregar(provincias, ["anio", *por]).assign(provincia=TOTAL_PAIS)
    return pd.concat([pais, provincias], ignore_index=True)[provincias.columns]


def construir(directorio_raw: Path = DIR_RAW, destino: Path = DIR_PROCESSED) -> dict[str, Path]:
    """Regenera las bases procesadas desde data/raw/."""
    largo = a_formato_largo(leer_serie(directorio_raw))
    # Provincia × sector × ámbito × grado: base de los cortes y de los otros agregados
    corte = agregar(largo, ["anio", "provincia", *CORTE])
    tablas = {
        "matricula_largo": largo,
        "matricula_corte": corte,
        "matricula_nivel": por_provincia_y_pais(corte, ["nivel"]),
        "matricula_grado": por_provincia_y_pais(corte, ["nivel", "grado", "grado_orden"]),
    }
    destino.mkdir(parents=True, exist_ok=True)
    rutas = {}
    for nombre, tabla in tablas.items():
        rutas[nombre] = destino / f"{nombre}.parquet"
        tabla.to_parquet(rutas[nombre], index=False)
    return rutas


if __name__ == "__main__":
    for nombre, ruta in construir().items():
        print(f"{nombre}: {ruta.relative_to(RAIZ)} ({len(pd.read_parquet(ruta)):,} filas)")

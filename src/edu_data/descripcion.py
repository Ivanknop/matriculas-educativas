"""Tablas descriptivas de matrícula, repitencia y sobreedad (total país o una provincia).

% de repitentes = repitentes / matrícula del mismo año y grado (no es la tasa oficial t+1).
% de sobreedad = alumnos con sobreedad / matrícula del mismo año y grado.
Unidades: una provincia, TOTAL_PAIS o SIN_BA (total país sin PROVINCIA_EXCLUIDA).
"""

from itertools import product

import pandas as pd

from edu_data.alertas import ALERTAS
from edu_data.matricula import (
    DIR_PROCESSED,
    GRADOS,
    MEDIDAS,
    PROVINCIA_EXCLUIDA,
    SIN_BA,
    TOTAL_PAIS,
)
from edu_data.validacion_base import alerta_para

NIVELES = ["inicial", "primaria", "secundaria", "no_graduada"]
INDICADORES_ALERTA = ("matricula", "repitentes", "sobreedad")
TODOS = "Todos"
SECTORES = [TODOS, "Estatal", "Privado"]
AMBITOS = [TODOS, "Urbano", "Rural"]


def pct(parte: pd.Series, total: pd.Series) -> pd.Series:
    """Porcentaje con 2 decimales; total 0 o NA → NA."""
    total = total.astype("Float64")
    return (100 * parte.astype("Float64") / total.mask(total == 0)).round(2)


def _con_porcentajes(t: pd.DataFrame) -> pd.DataFrame:
    return t.assign(
        pct_mujeres=pct(t["mujeres"], t["matricula"]),
        pct_varones=pct(t["varones"], t["matricula"]),
        pct_repitentes=pct(t["repitentes"], t["matricula"]),
        pct_sobreedad=pct(t["sobreedad"], t["matricula"]),
    )


def alertas_por_fila(
    t: pd.DataFrame, unidades: pd.Series, indicadores=INDICADORES_ALERTA
) -> pd.Series:
    """Textos de alerta de cada fila (año y nivel de `t`, unidad de `unidades`), o NA."""

    def texto(anio, nivel, unidad):
        unidad = None if unidad == TOTAL_PAIS else unidad
        textos = [alerta_para(ALERTAS, anio, i, unidad, nivel=nivel) for i in indicadores]
        unicos = list(dict.fromkeys(x for x in textos if x))
        return " | ".join(unicos) if unicos else pd.NA

    valores = [texto(a, n, u) for a, n, u in zip(t["anio"], t["nivel"], unidades, strict=True)]
    return pd.Series(valores, index=t.index, dtype="string")


def tabla_nivel(nivel: pd.DataFrame, provincia: str = TOTAL_PAIS) -> pd.DataFrame:
    """Por año y nivel: matrícula por sexo, % mujeres y varones, % repitentes, % sobreedad y
    alertas (una columna combinada y una por indicador)."""
    t = nivel[nivel["provincia"] == provincia].copy()
    t["nivel"] = pd.Categorical(t["nivel"], NIVELES, ordered=True)
    t = _con_porcentajes(t.sort_values(["nivel", "anio"], ignore_index=True))
    t["nivel"] = t["nivel"].astype("string")
    unidades = pd.Series(provincia, index=t.index)
    t["alerta"] = alertas_por_fila(t, unidades)
    for indicador in INDICADORES_ALERTA:
        t[f"alerta_{indicador}"] = alertas_por_fila(t, unidades, [indicador])
    columnas = ["anio", "nivel", *MEDIDAS[:3], "pct_mujeres", "pct_varones"]
    columnas += ["pct_repitentes", "pct_sobreedad", "alerta"]
    return t[[*columnas, *[f"alerta_{i}" for i in INDICADORES_ALERTA]]]


def tabla_grado(grado: pd.DataFrame, provincia: str = TOTAL_PAIS) -> pd.DataFrame:
    """Por año y año corrido (1º–12º y 13/14): matrícula por sexo, % repitentes y % sobreedad.

    7º suma provincias donde es primaria y donde es secundaria.
    """
    t = grado[(grado["provincia"] == provincia) & grado["grado"].isin(GRADOS)]
    t = t.groupby(["anio", "grado", "grado_orden"], as_index=False)[MEDIDAS].sum(min_count=1)
    t["pct_repitentes"] = pct(t["repitentes"], t["matricula"])
    t["pct_sobreedad"] = pct(t["sobreedad"], t["matricula"])
    return t.sort_values(["grado_orden", "anio"], ignore_index=True).drop(columns="grado_orden")


def _filtrar_unidad(corte: pd.DataFrame, unidad: str) -> pd.DataFrame:
    if unidad == TOTAL_PAIS:
        return corte
    if unidad == SIN_BA:
        return corte[corte["provincia"] != PROVINCIA_EXCLUIDA]
    return corte[corte["provincia"] == unidad]


def sumar_corte(
    corte: pd.DataFrame,
    unidad: str,
    claves: list[str],
    sector: str | None = None,
    ambito: str | None = None,
) -> pd.DataFrame:
    """Suma la base provincia × sector × ámbito para una unidad y un corte.

    `sector`/`ambito` None = todos. El resultado lleva `provincia = unidad`, listo para
    `tabla_nivel`/`tabla_grado`.
    """
    t = _filtrar_unidad(corte, unidad)
    if sector is not None:
        t = t[t["sector"] == sector]
    if ambito is not None:
        t = t[t["ambito"] == ambito]
    suma = t.groupby(["anio", *claves], as_index=False, observed=True)[MEDIDAS].sum(min_count=1)
    return suma.assign(provincia=unidad)


def tabla_cortes(corte: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    """Todas las unidades × sector × ámbito de una vez (vectorizado, para el visor).

    Columnas: unidad, sector, ambito, anio, `claves`, medidas y porcentajes. Da los mismos
    valores que `sumar_corte` + `tabla_nivel`, sin recorrer unidad por unidad.
    """
    partes = []
    for sector, ambito in product(SECTORES, AMBITOS):
        t = corte
        if sector != TODOS:
            t = t[t["sector"] == sector]
        if ambito != TODOS:
            t = t[t["ambito"] == ambito]
        por = ["anio", *claves]
        provincias = t.groupby(["provincia", *por], observed=True)[MEDIDAS].sum(min_count=1)
        provincias = provincias.reset_index().rename(columns={"provincia": "unidad"})
        pais = t.groupby(por, observed=True)[MEDIDAS].sum(min_count=1).reset_index()
        resto = t[t["provincia"] != PROVINCIA_EXCLUIDA].groupby(por, observed=True)
        sin_ba = resto[MEDIDAS].sum(min_count=1).reset_index()
        for tabla in (pais.assign(unidad=TOTAL_PAIS), sin_ba.assign(unidad=SIN_BA), provincias):
            partes.append(tabla.assign(sector=sector, ambito=ambito))
    return _con_porcentajes(pd.concat(partes, ignore_index=True))


def cargar_corte() -> pd.DataFrame:
    return pd.read_parquet(DIR_PROCESSED / "matricula_corte.parquet")


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_parquet(DIR_PROCESSED / "matricula_nivel.parquet"),
        pd.read_parquet(DIR_PROCESSED / "matricula_grado.parquet"),
    )


def ancha(t: pd.DataFrame, filas: str, valor: str) -> pd.DataFrame:
    """Vista año en columnas, para leer la evolución."""
    orden = list(dict.fromkeys(t[filas]))
    return t.pivot(index=filas, columns="anio", values=valor).loc[orden]


if __name__ == "__main__":
    nivel, grado = cargar()
    tn, tg = tabla_nivel(nivel), tabla_grado(grado)
    pd.set_option("display.width", 250)
    for valor in ["matricula", "pct_mujeres", "pct_repitentes", "pct_sobreedad"]:
        print(f"\n== {valor} por nivel\n{ancha(tn, 'nivel', valor).to_string()}")
    for valor in ["pct_repitentes", "pct_sobreedad"]:
        print(f"\n== {valor} por año corrido\n{ancha(tg, 'grado', valor).to_string()}")
    print("\n== alertas\n" + tn.dropna(subset="alerta")[["anio", "nivel", "alerta"]].to_string())

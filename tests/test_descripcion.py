"""Cada número de la descripción del total país, contrastado con un cálculo independiente
sobre el formato ancho (sin pasar por el formato largo ni los agregados)."""

import pandas as pd
import pytest

from edu_data import descripcion as d
from edu_data import matricula as m


@pytest.fixture(scope="module")
def tablas(base_nivel, base_grado):
    return d.tabla_nivel(base_nivel), d.tabla_grado(base_grado)


def _grados_nivel(nivel: str, provincia: str) -> list[str]:
    septimo_en_primaria = provincia in m.PRIMARIA_7
    primaria = m.GRADOS[:6] + (["7"] if septimo_en_primaria else [])
    return primaria if nivel == "primaria" else [g for g in m.GRADOS if g not in primaria]


def _suma_nivel(ancho, anio: int, nivel: str, prefijo: str) -> int:
    filas = ancho[ancho["anio"] == anio]
    total = 0
    for provincia, df in filas.groupby("provincia"):
        total += sum(int(df[f"{prefijo}{g}"].sum()) for g in _grados_nivel(nivel, provincia))
    return total


def _valor(tabla, anio, columna, **filtros):
    fila = tabla[tabla["anio"] == anio]
    for k, v in filtros.items():
        fila = fila[fila[k] == v]
    assert len(fila) == 1
    return fila[columna].iloc[0]


@pytest.mark.parametrize("anio", [2010, 2016, 2020, 2024])
@pytest.mark.parametrize("nivel", ["primaria", "secundaria"])
def test_porcentajes_por_nivel(ancho, tablas, anio, nivel):
    tn, _ = tablas
    mat = _suma_nivel(ancho, anio, nivel, "_")
    for prefijo, columna in [("r_", "pct_repitentes"), ("s_", "pct_sobreedad")]:
        esperado = round(100 * _suma_nivel(ancho, anio, nivel, prefijo) / mat, 2)
        assert _valor(tn, anio, columna, nivel=nivel) == esperado
    mujeres = mat - _suma_nivel(ancho, anio, nivel, "v_")
    assert _valor(tn, anio, "pct_mujeres", nivel=nivel) == round(100 * mujeres / mat, 2)
    assert _valor(tn, anio, "matricula", nivel=nivel) == mat


def test_matricula_inicial_y_no_graduada(ancho, tablas):
    tn, _ = tablas
    a2024 = ancho[ancho["anio"] == 2024]
    assert _valor(tn, 2024, "matricula", nivel="inicial") == sum(
        int(a2024[s].sum()) for s in m.SALAS
    )
    assert _valor(tn, 2024, "matricula", nivel="no_graduada") == 9112
    # Antes de 2022 la columna no existe: no hay fila (no es 0)
    assert tn[(tn["nivel"] == "no_graduada") & (tn["anio"] < 2022)].empty
    assert pd.isna(_valor(tn, 2024, "pct_repitentes", nivel="inicial"))


@pytest.mark.parametrize(
    ("anio", "grado", "rep", "sob"),
    [(2010, "1", 6.74, 11.11), (2018, "8", 13.49, 30.92), (2024, "12", 1.73, 16.56)],
)
def test_porcentajes_por_grado(ancho, tablas, anio, grado, rep, sob):
    _, tg = tablas
    filas = ancho[ancho["anio"] == anio]
    mat = filas[f"_{grado}"].sum()
    assert _valor(tg, anio, "pct_repitentes", grado=grado) == round(
        100 * filas[f"r_{grado}"].sum() / mat, 2
    )
    assert _valor(tg, anio, "pct_repitentes", grado=grado) == rep
    assert _valor(tg, anio, "pct_sobreedad", grado=grado) == sob


def test_alertas_marcadas_en_total(tablas):
    tn, _ = tablas
    assert "Pandemia" in _valor(tn, 2020, "alerta", nivel="secundaria")
    assert "Quiebre" in _valor(tn, 2016, "alerta", nivel="primaria")
    assert "6,2 %" in _valor(tn, 2024, "alerta", nivel="secundaria")
    # Alertas provinciales sin afecta_total no aparecen en el total país
    assert "Santa Cruz" not in str(_valor(tn, 2021, "alerta", nivel="secundaria"))


@pytest.mark.parametrize(("anio", "rep", "sob"), [(2023, 7.84, 22.16), (2024, 8.44, 22.33)])
def test_secundaria_sin_buenos_aires(ancho, corte, anio, rep, sob):
    t = d.tabla_nivel(d.sumar_corte(corte, m.SIN_BA, ["nivel"]), m.SIN_BA)
    resto = ancho[ancho["provincia"] != "Buenos Aires"]
    mat = _suma_nivel(resto, anio, "secundaria", "_")
    esperado_rep = round(100 * _suma_nivel(resto, anio, "secundaria", "r_") / mat, 2)
    assert _valor(t, anio, "pct_repitentes", nivel="secundaria") == esperado_rep == rep
    assert _valor(t, anio, "pct_sobreedad", nivel="secundaria") == sob


@pytest.mark.parametrize(
    ("unidad", "sector", "ambito"),
    [
        (m.TOTAL_PAIS, d.TODOS, d.TODOS),
        (m.SIN_BA, "Estatal", d.TODOS),
        ("Salta", "Estatal", "Rural"),
        ("Ciudad de Buenos Aires", "Privado", "Urbano"),
    ],
)
def test_tabla_cortes_igual_a_sumar_corte(corte, unidad, sector, ambito):
    # La versión vectorizada del visor debe dar lo mismo que el camino unidad por unidad
    vectorizada = d.tabla_cortes(corte, ["nivel"])
    elegida = vectorizada[
        (vectorizada["unidad"] == unidad)
        & (vectorizada["sector"] == sector)
        & (vectorizada["ambito"] == ambito)
    ]
    filtro = {"sector": None if sector == d.TODOS else sector}
    filtro["ambito"] = None if ambito == d.TODOS else ambito
    directa = d.tabla_nivel(d.sumar_corte(corte, unidad, ["nivel"], **filtro), unidad)
    columnas = ["matricula", "varones", "mujeres", "pct_repitentes", "pct_sobreedad"]
    claves = ["anio", "nivel"]
    a = elegida.sort_values(claves).set_index(claves)[columnas].astype("Float64")
    b = directa.sort_values(claves).set_index(claves)[columnas].astype("Float64")
    pd.testing.assert_frame_equal(a, b, check_names=False)

"""Cada número del visor contrastado con un cálculo independiente sobre el formato ancho."""

import json
import re

import pytest

from edu_data import descripcion as d
from edu_data import geo
from edu_data import matricula as m
from edu_data import visor_matricula as v

pytestmark = pytest.mark.skipif(not geo.ARCHIVO.exists(), reason="falta provincias_georef.geojson")
ANIOS = list(range(2010, 2025))


@pytest.fixture(scope="module")
def datos(corte):
    return v.datos_visor(corte, geo.caminos_svg(), ANIOS)


def _grados(nivel: str, provincia: str) -> list[str]:
    primaria = m.GRADOS[:6] + (["7"] if provincia in m.PRIMARIA_7 else [])
    if nivel == "primaria":
        return primaria
    return [g for g in m.GRADOS if g not in primaria]


def _independiente(ancho, anio, nivel, prefijo, provincias=None, sector=None, ambito=None):
    t = ancho[ancho["anio"] == anio]
    if provincias is not None:
        t = t[t["provincia"].isin(provincias)]
    if sector:
        t = t[t["sector"] == sector]
    if ambito:
        t = t[t["ambito"] == ambito]
    total = 0
    for provincia, df in t.groupby("provincia"):
        total += sum(int(df[f"{prefijo}{g}"].sum()) for g in _grados(nivel, provincia))
    return total


def _serie(datos, unidad, sector, ambito, nivel, campo, anio):
    corte = datos["unidades"][unidad]["cortes"][v.clave_corte(sector, ambito)]
    return corte["nivel"][nivel][campo][ANIOS.index(anio)]


def test_unidades_del_selector(datos):
    unidades = list(datos["unidades"])
    assert unidades[:2] == [m.TOTAL_PAIS, d.SIN_BA]
    assert sorted(unidades[2:]) == sorted(m.PRIMARIA_6 | m.PRIMARIA_7)
    cortes = datos["unidades"]["Salta"]["cortes"]
    assert len(cortes) == 9


@pytest.mark.parametrize(
    ("unidad", "provincias", "sector", "ambito", "nivel", "anio"),
    [
        (m.TOTAL_PAIS, None, None, None, "secundaria", 2024),
        (
            d.SIN_BA,
            sorted((m.PRIMARIA_6 | m.PRIMARIA_7) - {"Buenos Aires"}),
            None,
            None,
            "secundaria",
            2024,
        ),
        ("Salta", ["Salta"], "Estatal", "Rural", "secundaria", 2018),
        ("Córdoba", ["Córdoba"], "Privado", "Urbano", "primaria", 2024),
        ("Ciudad de Buenos Aires", ["Ciudad de Buenos Aires"], "Estatal", None, "primaria", 2012),
    ],
)
def test_corte_contra_ancho(ancho, datos, unidad, provincias, sector, ambito, nivel, anio):
    args = (ancho, anio, nivel)
    filtros = {"provincias": provincias, "sector": sector, "ambito": ambito}
    mat = _independiente(*args, "_", **filtros)
    varones = _independiente(*args, "v_", **filtros)
    rep = round(100 * _independiente(*args, "r_", **filtros) / mat, 2)
    sob = round(100 * _independiente(*args, "s_", **filtros) / mat, 2)
    serie = lambda campo: _serie(datos, unidad, sector, ambito, nivel, campo, anio)  # noqa: E731
    assert serie("matricula") == mat
    assert serie("varones") == varones
    assert serie("mujeres") == mat - varones
    assert serie("pct_repitentes") == rep
    assert serie("pct_sobreedad") == sob


def test_total_pais_igual_a_descripcion_testeada(datos, base_nivel):
    tn = d.tabla_nivel(base_nivel)
    sec = tn[tn["nivel"] == "secundaria"].set_index("anio")
    serie = datos["unidades"][m.TOTAL_PAIS]["cortes"]["Todos|Todos"]["nivel"]["secundaria"]
    assert serie["pct_repitentes"] == sec["pct_repitentes"].tolist()


def test_sin_oferta_queda_vacio(datos):
    corte = datos["unidades"]["Ciudad de Buenos Aires"]["cortes"]["Todos|Rural"]
    assert corte == {"nivel": {}}


def test_varones_mas_mujeres_igual_matricula(datos):
    for unidad in datos["unidades"].values():
        for corte in unidad["cortes"].values():
            for bloque in corte["nivel"].values():
                for mat, var, muj in zip(
                    bloque["matricula"], bloque["varones"], bloque["mujeres"], strict=True
                ):
                    assert mat is None or mat == var + muj


def test_alertas_por_unidad(datos):
    pais = datos["unidades"][m.TOTAL_PAIS]["alertas"]["secundaria"]
    assert "1650/24" in pais["alerta_repitentes"][-1]
    assert pais["alerta_matricula"][-1] is None
    sin_ba = datos["unidades"][d.SIN_BA]["alertas"]["secundaria"]
    assert sin_ba["alerta_repitentes"][-1] is None
    santa_cruz = datos["unidades"]["Santa Cruz"]["alertas"]["secundaria"]
    assert "Santa Cruz" not in santa_cruz["alerta_repitentes"][ANIOS.index(2021)]
    assert santa_cruz["alerta_repitentes"][ANIOS.index(2021)]


def test_mapa_tiene_todas_las_provincias(datos):
    mapa = datos["mapa"]
    nombres = set(mapa["provincias"]) | {geo.CABA}
    assert nombres == m.PRIMARIA_6 | m.PRIMARIA_7
    assert mapa["caba"]["path"].startswith("M")


def test_html_generado(tmp_path, datos):
    html = v.generar(tmp_path / "visor.html", datos).read_text(encoding="utf-8")
    assert "GENERADO por src/edu_data/visor_matricula.py" in html
    assert "__DATOS__" not in html and "__MARCA__" not in html
    assert "Ir al mapa" in html and "1650/24" in html
    bloque = re.search(r'<script id="datos" type="application/json">(.*?)</script>', html, re.S)
    assert len(json.loads(bloque.group(1))["unidades"]) == 26

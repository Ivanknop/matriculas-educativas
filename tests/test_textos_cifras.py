"""Las cifras escritas en textos (alertas y pestaña "Acerca" del visor) contra los datos."""

from pathlib import Path

import pytest

from edu_data import descripcion as d
from edu_data import matricula as m
from edu_data.alertas import ALERTAS

PLANTILLA_VISOR = Path(m.__file__).with_name("visor_matricula.html")


@pytest.fixture(scope="module")
def tasas(base_nivel):
    t = base_nivel[base_nivel["nivel"].isin(["primaria", "secundaria"])].copy()
    # Sin redondeo previo: redondear dos veces (a 2 y después a 1 decimal) puede cambiar la cifra
    t["rep"] = 100 * t["repitentes"].astype(float) / t["matricula"].astype(float)
    t["sob"] = 100 * t["sobreedad"].astype(float) / t["matricula"].astype(float)
    return t.set_index(["provincia", "nivel", "anio"])


def _texto(unidad: str | None, periodo: int) -> str:
    textos = [a.texto for a in ALERTAS if periodo in a.periodos and a.unidades == unidad]
    assert len(textos) == 1, (unidad, periodo)
    return textos[0]


def _num(valor: float) -> str:
    """Formato de los textos: coma decimal, sin decimal si es entero."""
    texto = f"{valor:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


@pytest.mark.parametrize(
    ("unidad", "periodo", "citas"),
    [
        (
            ["Santa Cruz"],
            2019,
            [("rep", 2018, 0), ("rep", 2019, 1), ("rep", 2024, 0)],
        ),
        (
            ["Santa Cruz"],
            2024,
            [("sob", 2018, 1), ("sob", 2023, 1), ("sob", 2024, 0)],
        ),
        (
            ["Buenos Aires"],
            2024,
            [("rep", 2023, 1), ("rep", 2024, 1), ("sob", 2023, 1), ("sob", 2024, 1)],
        ),
        (["Santiago del Estero"], 2010, [("rep", 2010, 1)]),
        (["Catamarca"], 2011, [("rep", 2011, 1), ("rep", 2010, 1), ("rep", 2012, 1)]),
    ],
)
def test_cifras_de_alertas_provinciales(tasas, unidad, periodo, citas):
    texto = _texto(unidad, periodo)
    for indicador, anio, decimales in citas:
        valor = tasas.loc[(unidad[0], "secundaria", anio), indicador]
        assert _num(round(valor, decimales)) + " %" in texto, (indicador, anio, valor)


def test_cifras_del_quiebre_2016(tasas, base_nivel):
    texto = _texto(None, 2016)
    pais = d.tabla_nivel(base_nivel).set_index(["nivel", "anio"])["pct_repitentes"]
    antes, despues = pais[("primaria", 2015)], pais[("primaria", 2016)]
    assert f"{antes:.2f} %".replace(".", ",") in texto
    assert f"{despues:.2f} %".replace(".", ",") in texto
    provincias = tasas.drop(index=m.TOTAL_PAIS, level="provincia").xs("primaria", level="nivel")
    porcentaje = d.pct(
        base_nivel.set_index(["provincia", "nivel", "anio"])["repitentes"],
        base_nivel.set_index(["provincia", "nivel", "anio"])["matricula"],
    ).xs("primaria", level="nivel")
    porcentaje = porcentaje.drop(index=m.TOTAL_PAIS, level="provincia").unstack("anio")
    suben = int(((porcentaje[2016] - porcentaje[2015]) > 0.1).sum())
    assert f"{suben} de {len(provincias.index.unique('provincia'))} provincias" in texto


def test_peso_de_buenos_aires_citado_en_el_visor(base_nivel):
    sec = base_nivel[(base_nivel["nivel"] == "secundaria") & (base_nivel["anio"] == 2024)]
    sec = sec.set_index("provincia")["matricula"]
    peso = 100 * sec[m.PROVINCIA_EXCLUIDA] / sec[m.TOTAL_PAIS]
    assert peso > 40
    assert "más del 40 %" in PLANTILLA_VISOR.read_text(encoding="utf-8")

"""Visor HTML: pestaña de descripción y mapa del país; al elegir una unidad (provincia, total
país o total país sin Buenos Aires) se pide el indicador y se filtra por sexo, sector y ámbito.

Generar: `uv run python -m edu_data.visor_matricula` → outputs/visor_matricula.html.
Requiere data/processed/ (`edu_data.matricula`) y data/raw/provincias_georef.geojson
(`edu_data.geo`).
"""

import json
from datetime import date
from itertools import product
from pathlib import Path

import pandas as pd

from edu_data.descripcion import (
    AMBITOS,
    INDICADORES_ALERTA,
    SECTORES,
    TODOS,
    alertas_por_fila,
    cargar_corte,
    tabla_cortes,
)
from edu_data.geo import caminos_svg
from edu_data.matricula import DESFASE_PERIODO, RAIZ, SIN_BA, TOTAL_PAIS, archivos_raw

DESTINO = RAIZ / "outputs" / "visor_matricula.html"
PLANTILLA = Path(__file__).with_name("visor_matricula.html")
MARCA = "GENERADO por src/edu_data/visor_matricula.py — editar en src/edu_data/visor_matricula.*"

NIVELES_VISOR = ["inicial", "primaria", "secundaria"]
CAMPOS = ["matricula", "varones", "mujeres", "pct_repitentes", "pct_sobreedad"]
CAMPOS_ALERTA = [f"alerta_{i}" for i in INDICADORES_ALERTA]


def clave_corte(sector: str | None, ambito: str | None) -> str:
    return f"{sector or TODOS}|{ambito or TODOS}"


def _valor(v):
    if pd.isna(v):
        return None
    if isinstance(v, str):
        return v
    return int(v) if float(v).is_integer() else float(v)


def _por_anio(grupo: pd.DataFrame, anios: list[int], campos: list[str]) -> dict:
    """{campo: [valor por período, None si no hay dato]}."""
    por_anio = grupo.set_index("anio").reindex(anios)[campos].astype(object)
    return {c: [_valor(v) for v in por_anio[c]] for c in campos}


def datos_visor(corte: pd.DataFrame, geo: dict, anios: list[int]) -> dict:
    """Series por unidad × sector × ámbito × nivel, y alertas por unidad (sin corte)."""
    t = tabla_cortes(corte, ["nivel"])
    t = t[t["nivel"].isin(NIVELES_VISOR)]
    unidades = [TOTAL_PAIS, SIN_BA, *sorted(corte["provincia"].unique())]
    salida = {
        u: {
            "cortes": {clave_corte(s, a): {"nivel": {}} for s, a in product(SECTORES, AMBITOS)},
            "alertas": {},
        }
        for u in unidades
    }
    for (unidad, sector, ambito, nivel), grupo in t.groupby(
        ["unidad", "sector", "ambito", "nivel"]
    ):
        series = salida[unidad]["cortes"][clave_corte(sector, ambito)]["nivel"]
        series[nivel] = _por_anio(grupo, anios, CAMPOS)

    # Las alertas son de la serie de la unidad: se marcan igual con cualquier corte
    base = t[(t["sector"] == TODOS) & (t["ambito"] == TODOS)].copy()
    for indicador, campo in zip(INDICADORES_ALERTA, CAMPOS_ALERTA, strict=True):
        base[campo] = alertas_por_fila(base, base["unidad"], [indicador])
    for (unidad, nivel), grupo in base.groupby(["unidad", "nivel"]):
        salida[unidad]["alertas"][nivel] = _por_anio(grupo, anios, CAMPOS_ALERTA)
    return {"anios": anios, "unidades": salida, "mapa": geo}


def generar(destino: Path = DESTINO, datos: dict | None = None) -> Path:
    if datos is None:
        anios = [a - DESFASE_PERIODO for a in archivos_raw()]
        datos = datos_visor(cargar_corte(), caminos_svg(), anios)
    # "</" dentro de un <script> cerraría la etiqueta: se escapa
    json_datos = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (
        PLANTILLA.read_text(encoding="utf-8")
        .replace("__MARCA__", MARCA)
        .replace("__FECHA__", date.today().isoformat())
        .replace("__DATOS__", json_datos)
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return destino


if __name__ == "__main__":
    print(f"Visor: {generar().relative_to(RAIZ)}")

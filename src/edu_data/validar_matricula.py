"""Controles de pertinencia de la base de matrícula, por provincia y nivel.

Ejecutar: `uv run python -m edu_data.validar_matricula` (después de `edu_data.matricula`).
Escribe outputs/validacion_matricula_<control>.csv.
"""

from pathlib import Path

import pandas as pd

from edu_data.alertas import ALERTAS
from edu_data.descripcion import pct
from edu_data.matricula import DIR_PROCESSED, RAIZ, TOTAL_PAIS
from edu_data.validacion_base import alerta_para, atipicos_robustos, saltos_interanuales

DIR_OUTPUTS = RAIZ / "outputs"
MARCA = "# GENERADO por src/edu_data/validar_matricula.py — editar en ese script\n"
NIVELES = ["primaria", "secundaria"]
# Umbrales orientativos de la skill validar-calidad: stocks ±10 %
UMBRAL_MATRICULA = 0.10
Z_TASAS = 3.0


def tabla_tasas(nivel: pd.DataFrame) -> pd.DataFrame:
    """Tasas simples (sobre matrícula del mismo año) solo para controlar la serie."""
    t = nivel[nivel["nivel"].isin(NIVELES)].copy()
    t["pct_repitentes"] = pct(t["repitentes"], t["matricula"])
    t["pct_sobreedad"] = pct(t["sobreedad"], t["matricula"])
    t["pct_varones"] = pct(t["varones"], t["matricula"])
    return t


def _con_alerta(t: pd.DataFrame, indicador: str) -> pd.DataFrame:
    def texto(fila):
        unidad = None if fila["provincia"] == TOTAL_PAIS else fila["provincia"]
        return alerta_para(ALERTAS, fila["anio"], indicador, unidad, nivel=fila["nivel"])

    return t.assign(alerta_registrada=t.apply(texto, axis=1) if len(t) else None)


def controles(nivel: pd.DataFrame) -> dict[str, pd.DataFrame]:
    t = tabla_tasas(nivel)
    grupo = ["provincia", "nivel"]
    salida = {
        "saltos_matricula": _con_alerta(
            saltos_interanuales(t, "matricula", grupo, "anio", UMBRAL_MATRICULA), "matricula"
        )
    }
    for tasa, indicador in [("pct_repitentes", "repitentes"), ("pct_sobreedad", "sobreedad")]:
        salida[f"atipicos_{indicador}"] = _con_alerta(
            atipicos_robustos(t, tasa, grupo, Z_TASAS), indicador
        )
    return salida


def escribir(tablas: dict[str, pd.DataFrame], destino: Path = DIR_OUTPUTS) -> dict[str, Path]:
    destino.mkdir(parents=True, exist_ok=True)
    rutas = {}
    for nombre, tabla in tablas.items():
        rutas[nombre] = destino / f"validacion_matricula_{nombre}.csv"
        with open(rutas[nombre], "w", encoding="utf-8") as archivo:
            archivo.write(MARCA)
            tabla.to_csv(archivo, index=False)
    return rutas


def main() -> dict[str, Path]:
    nivel = pd.read_parquet(DIR_PROCESSED / "matricula_nivel.parquet")
    return escribir(controles(nivel))


if __name__ == "__main__":
    for nombre, ruta in main().items():
        print(f"{nombre}: {len(pd.read_csv(ruta, comment='#'))} filas → {ruta.relative_to(RAIZ)}")

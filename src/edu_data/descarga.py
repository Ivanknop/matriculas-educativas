"""Descarga de los archivos oficiales a data/raw/. Nunca reemplaza un archivo existente.

La página de datos abiertos de la Secretaría de Educación arma su tabla con una planilla de
Google; cada fila apunta a un link público de SharePoint del Ministerio. SharePoint pide una
cookie de sesión: se visita el link y después se pide la descarga con `download=1`.

Uso: `uv run python -m edu_data.descarga`.
"""

import csv
import http.cookiejar
import io
import time
import urllib.error
import urllib.request
from pathlib import Path

from edu_data import geo
from edu_data.matricula import DIR_RAW, PATRON_ARCHIVO

PAGINA = (
    "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/"
    "datos-abiertos-de-la-secretaria-de-educacion"
)
ID_PLANILLA = "1XaSz7AJ-EkpLqj_qjx3TPdBfJaQvqEZwg3sOYagtOsI"
URL_PLANILLA = (
    f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/gviz/tq?tqx=out:csv&sheet=Hoja%201"
)
# Los documentos de referencia vienen agrupados en la fila de encabezado de la planilla, que no
# se puede leer fila a fila: sus links se fijan acá (vigentes al 2026-11-08)
DOCUMENTOS = {
    "Diccionario de bases RA anonimizadas.xlsx": (
        "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/"
        "santiago_pomeranz_educacion_gob_ar/ETNQUApUc51BiLJLGAWuKtkB3PDw1t4QJZCX9d61_6D8-Q?e=hEkxgc"
    ),
    "Notas metodologicas acerca del proceso de anonimizacion.pdf": (
        "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:b:/g/personal/"
        "santiago_pomeranz_educacion_gob_ar/EbFo6lf_I4dJllsyiHnnmPwB7oTpxZ41K1Kwyj5XNFA2hw?e=yMzm8j"
    ),
}
AGENTE = "Mozilla/5.0 (edu-data-script)"
REINTENTOS = 3


def links_matricula(texto_planilla: str) -> dict[str, str]:
    """{nombre de archivo: link} de las filas "AAAA Matricula - agregada.csv" de la planilla."""
    filas = list(csv.reader(io.StringIO(texto_planilla)))
    # Columnas de la planilla: año, nombre, descripción, link
    return {f[1].strip(): f[3].strip() for f in filas[1:] if PATRON_ARCHIVO.match(f[1].strip())}


def _abrir(url: str, abridor=None) -> bytes:
    abridor = abridor or urllib.request.build_opener()
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with abridor.open(pedido, timeout=60) as respuesta:
        return respuesta.read()


def descargar_sharepoint(url: str, destino: Path) -> None:
    """Descarga un link público de SharePoint; reintenta los errores del servidor."""
    for intento in range(1, REINTENTOS + 1):
        abridor = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )
        try:
            _abrir(url, abridor)
            contenido = _abrir(url + "&download=1", abridor)
        except urllib.error.HTTPError as error:
            if error.code < 500 or intento == REINTENTOS:
                raise
            time.sleep(2 * intento)
            continue
        if contenido.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
            raise RuntimeError(f"SharePoint devolvió una página, no el archivo: {url}")
        destino.write_bytes(contenido)
        return


def descargar_todo(destino: Path = DIR_RAW) -> list[Path]:
    """Baja lo que falte en `destino`: CSV de matrícula, documentos y límites provinciales."""
    links = {**links_matricula(_abrir(URL_PLANILLA).decode("utf-8")), **DOCUMENTOS}
    nuevos = []
    for nombre, url in sorted(links.items()):
        ruta = destino / nombre
        if ruta.exists():
            continue
        descargar_sharepoint(url, ruta)
        nuevos.append(ruta)
    if geo.descargar(destino / geo.ARCHIVO.name):
        nuevos.append(destino / geo.ARCHIVO.name)
    return nuevos


if __name__ == "__main__":
    nuevos = descargar_todo()
    print(
        f"{len(nuevos)} archivos nuevos en data/raw/" if nuevos else "data/raw/ ya estaba completo"
    )
    for ruta in nuevos:
        print(f"  {ruta.name}")

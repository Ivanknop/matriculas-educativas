"""Límites provinciales (IGN, distribuidos por georef/datos.gob.ar) para el mapa del visor.

Descargar: `uv run python -m edu_data.geo` → data/raw/provincias_georef.geojson.
"""

import urllib.request

import geopandas as gpd
from shapely.geometry import box

from edu_data.matricula import DIR_RAW

URL = "https://infra.datos.gob.ar/georef/provincias.geojson"
ARCHIVO = DIR_RAW / "provincias_georef.geojson"

# Nombres de georef → nombres del dataset de matrícula
NOMBRES = {
    "Ciudad Autónoma de Buenos Aires": "Ciudad de Buenos Aires",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego",
}
CABA = "Ciudad de Buenos Aires"
# Se recorta el sector antártico (al sur de 56° S): sin él, el continente queda diminuto
RECORTE = box(-75, -56, -52, -21)
# Cónica conforme de Lambert centrada en Argentina
PROYECCION = "+proj=lcc +lat_1=-24 +lat_2=-48 +lat_0=-36 +lon_0=-64 +datum=WGS84 +units=m"
TOLERANCIA_M = 2_500
ANCHO_SVG = 420


def descargar(destino=ARCHIVO) -> bool:
    """Baja los límites si no están; data/raw/ no se reemplaza. Devuelve si descargó."""
    if destino.exists():
        return False
    pedido = urllib.request.Request(URL, headers={"User-Agent": "edu-data-script"})
    with urllib.request.urlopen(pedido, timeout=60) as respuesta:
        destino.write_bytes(respuesta.read())
    return True


def provincias(ruta=ARCHIVO) -> gpd.GeoDataFrame:
    """Provincias con el nombre del dataset, recortadas y proyectadas."""
    g = gpd.read_file(ruta)[["nombre", "geometry"]]
    g["provincia"] = g["nombre"].replace(NOMBRES)
    g["geometry"] = g.geometry.intersection(RECORTE)
    return g.to_crs(PROYECCION)[["provincia", "geometry"]]


def _anillos_a_path(geom, x, y) -> str:
    poligonos = getattr(geom, "geoms", [geom])
    partes = []
    for poligono in poligonos:
        for anillo in [poligono.exterior, *poligono.interiors]:
            puntos = [f"{x(px):.1f},{y(py):.1f}" for px, py in anillo.coords]
            partes.append("M" + "L".join(puntos) + "Z")
    return "".join(partes)


def caminos_svg(ruta=ARCHIVO) -> dict:
    """Paths SVG por provincia (simplificados) y un recuadro ampliado para CABA."""
    g = provincias(ruta)
    minx, miny, maxx, maxy = g.total_bounds
    escala = ANCHO_SVG / (maxx - minx)
    alto = (maxy - miny) * escala

    def x(px):
        return (px - minx) * escala

    def y(py):
        return (maxy - py) * escala

    simples = g.geometry.simplify(TOLERANCIA_M, preserve_topology=True)
    resto = {
        p: _anillos_a_path(geom, x, y)
        for p, geom in zip(g["provincia"], simples, strict=True)
        if p != CABA
    }
    # CABA es de unos pocos píxeles: va ampliada en un recuadro, sin simplificar
    caba = g.loc[g["provincia"] == CABA, "geometry"].iloc[0]
    cminx, cminy, cmaxx, cmaxy = caba.bounds
    lado, ox, oy = 70, ANCHO_SVG - 95, alto * 0.30
    cesc = lado / max(cmaxx - cminx, cmaxy - cminy)
    caba_path = _anillos_a_path(
        caba, lambda px: ox + (px - cminx) * cesc, lambda py: oy + (cmaxy - py) * cesc
    )
    real = caba.centroid
    return {
        "ancho": ANCHO_SVG,
        "alto": round(alto, 1),
        "provincias": resto,
        "caba": {
            "path": caba_path,
            "recuadro": [ox - 8, oy - 8, lado + 16, lado + 16],
            "real": [round(x(real.x), 1), round(y(real.y), 1)],
        },
    }


if __name__ == "__main__":
    print(f"Descargado: {ARCHIVO}" if descargar() else f"Ya existía: {ARCHIVO}")

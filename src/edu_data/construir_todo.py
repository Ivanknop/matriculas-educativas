"""Construcción completa, en orden: (descarga) → base procesada → controles → visor → sitio.

Uso: `uv run python -m edu_data.construir_todo` (agregar `--descargar` para bajar lo que falte
en data/raw/). Regenera todo desde data/raw/; no reutiliza intermedios viejos.
"""

import argparse
import shutil
import time
from pathlib import Path

from edu_data import descarga, matricula, validar_matricula, visor_matricula

# Lo que publica GitHub Pages: el visor como index.html (todo embebido, sin rutas externas)
SITIO = matricula.RAIZ / "outputs" / "sitio"


def preparar_sitio(visor: Path = visor_matricula.DESTINO, destino: Path = SITIO) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    return Path(shutil.copyfile(visor, destino / "index.html"))


def _paso(nombre: str, funcion):
    inicio = time.perf_counter()
    resultado = funcion()
    print(f"{nombre}: {time.perf_counter() - inicio:.1f} s")
    return resultado


def construir_todo(descargar: bool = False) -> None:
    if descargar:
        _paso("descarga", descarga.descargar_todo)
    _paso("base procesada", matricula.construir)
    _paso("controles de calidad", validar_matricula.main)
    _paso("visor", visor_matricula.generar)
    _paso("sitio", preparar_sitio)


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--descargar", action="store_true", help="bajar lo que falte")
    construir_todo(argumentos.parse_args().descargar)

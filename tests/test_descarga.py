"""Descarga sin red: lectura de la planilla y que data/raw/ nunca se reemplace."""

from edu_data import descarga

PLANILLA = (
    '"ano Año","nombre Nombre","descripcion Descripción","btn-consultar Consultar"\n'
    '"2025","2025 Matricula - agregada.csv","Composición","https://sp/a?e=1"\n'
    '"2025","2025 Matricula por edad - agregada.csv","Por edad","https://sp/b?e=2"\n'
    '"2024","2024 Matricula - agregada.csv","Composición","https://sp/c?e=3"\n'
    '"2024","2024 Trayectoria - agregada.csv","Trayectoria","https://sp/d?e=4"\n'
)


def test_links_solo_matricula_agregada():
    assert descarga.links_matricula(PLANILLA) == {
        "2025 Matricula - agregada.csv": "https://sp/a?e=1",
        "2024 Matricula - agregada.csv": "https://sp/c?e=3",
    }


def test_no_reemplaza_archivos_existentes(tmp_path, monkeypatch):
    existente = tmp_path / "2024 Matricula - agregada.csv"
    existente.write_text("original")
    pedidos = []
    monkeypatch.setattr(descarga, "_abrir", lambda url, abridor=None: PLANILLA.encode())
    monkeypatch.setattr(descarga, "DOCUMENTOS", {})
    monkeypatch.setattr(descarga.geo, "descargar", lambda destino: False)

    def falsa(url, destino):
        pedidos.append(url)
        destino.write_text("nuevo")

    monkeypatch.setattr(descarga, "descargar_sharepoint", falsa)
    nuevos = descarga.descargar_todo(tmp_path)
    assert [r.name for r in nuevos] == ["2025 Matricula - agregada.csv"]
    assert pedidos == ["https://sp/a?e=1"]
    assert existente.read_text() == "original"

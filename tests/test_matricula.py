import pandas as pd
import pytest

from edu_data import matricula as m
from edu_data.alertas import ALERTAS
from edu_data.validacion_base import alerta_para

# --- Unidad: archivo sintético con la forma del oficial (UTF-8 con BOM, ";", CRLF) ---

ENCABEZADO = "provincia;Departamento;sector;ambito;Localizacion;s5;_6;_7;v_6;v_7;r_6;r_7;s_6;s_7"
FILAS = [
    "Santa Fe;Rosario;Estatal;Urbano;12;10;100;90;50;40;5;4; ;9",
    "Córdoba;Capital;Privado;Urbano;8; ;80; ;40; ;2; ; ; ",
]


@pytest.fixture
def raw_sintetico(tmp_path):
    texto = "\r\n".join([ENCABEZADO, *FILAS]) + "\r\n"
    (tmp_path / "2015 Matricula - agregada.csv").write_bytes(texto.encode("utf-8-sig"))
    (tmp_path / "2015 Matricula por edad - agregada.csv").write_text("no se lee")
    return tmp_path


def test_lectura_descarta_localizacion_y_normaliza_nombres(raw_sintetico):
    serie = m.leer_serie(raw_sintetico)
    assert "localizacion" not in serie
    assert "departamento" in serie
    # El año es el del archivo (ciclo lectivo de la matrícula)
    assert serie["anio"].unique().tolist() == [2015]


def test_sobreedad_vacia_con_matricula_pasa_a_cero_y_conserva_original(raw_sintetico):
    serie = m.leer_serie(raw_sintetico)
    santa_fe, cordoba = serie.iloc[0], serie.iloc[1]
    assert santa_fe["s_6"] == 0 and pd.isna(santa_fe["s_6_informado"])
    assert santa_fe["s_7"] == 9 and santa_fe["s_7_informado"] == 9
    assert cordoba["s_6"] == 0
    # Sin matrícula (sin oferta) la sobreedad sigue vacía
    assert pd.isna(cordoba["s_7"])


def test_formato_largo_nivel_sexo_y_sin_oferta(raw_sintetico):
    largo = m.a_formato_largo(m.leer_serie(raw_sintetico))
    clave = largo.set_index(["provincia", "grado"])
    # 7º es primaria en Santa Fe (7 años)
    assert clave.loc[("Santa Fe", "7"), "nivel"] == "primaria"
    assert clave.loc[("Santa Fe", "6"), "mujeres"] == 50
    assert bool(clave.loc[("Santa Fe", "6"), "sobreedad_imputada"])
    assert not bool(clave.loc[("Santa Fe", "7"), "sobreedad_imputada"])
    assert clave.loc[("Santa Fe", "s5"), "nivel"] == "inicial"
    assert pd.isna(clave.loc[("Santa Fe", "s5"), "sobreedad"])
    # Córdoba sin 7º ni sala de 5: no hay fila (vacío no se vuelve 0)
    assert ("Córdoba", "7") not in clave.index
    assert ("Córdoba", "s5") not in clave.index


def test_nivel_de_septimo_segun_estructura():
    provincias = pd.Series(["Buenos Aires", "Ciudad de Buenos Aires"])
    assert m.nivel_de("7", provincias).tolist() == ["secundaria", "primaria"]
    assert m.nivel_de("6", provincias).tolist() == ["primaria", "primaria"]
    assert m.nivel_de("8", provincias).tolist() == ["secundaria", "secundaria"]


def test_nivel_de_rechaza_provincia_sin_estructura():
    with pytest.raises(ValueError, match="sin estructura"):
        m.nivel_de("7", pd.Series(["Atlántida"]))


def test_estructura_cubre_24_provincias_sin_superposicion():
    assert len(m.PRIMARIA_6) == len(m.PRIMARIA_7) == 12
    assert not m.PRIMARIA_6 & m.PRIMARIA_7


def test_agregar_grupo_sin_datos_queda_na():
    largo = pd.DataFrame(
        {
            "anio": [2015, 2015],
            "provincia": ["A", "A"],
            "nivel": ["inicial", "primaria"],
            **{c: pd.array([10, 20], dtype="Int64") for c in ["matricula", "varones", "mujeres"]},
            "repitentes": pd.array([None, 3], dtype="Int64"),
            "sobreedad": pd.array([None, 4], dtype="Int64"),
            "sobreedad_imputada": [False, True],
        }
    )
    tabla = m.por_provincia_y_pais(largo, ["nivel"]).set_index(["provincia", "nivel"])
    assert pd.isna(tabla.loc[(m.TOTAL_PAIS, "inicial"), "repitentes"])
    assert tabla.loc[(m.TOTAL_PAIS, "primaria"), "celdas_sobreedad_imputadas"] == 1


def test_alertas_registradas():
    texto = alerta_para(ALERTAS, 2022, "repitentes", "Santa Cruz", nivel="secundaria")
    assert texto and "17 %" in texto
    assert alerta_para(ALERTAS, 2022, "repitentes", "Santa Cruz", nivel="primaria") is None


# --- Integración: archivos reales de data/raw/ (fixtures de conftest; se saltean si faltan) ---

ANIOS = list(range(2011, 2026))


def test_serie_completa_y_clave_unica(ancho):
    assert sorted(ancho["anio"].unique()) == ANIOS
    assert ancho.groupby("anio")["provincia"].nunique().eq(24).all()
    assert not ancho.duplicated(["anio", *m.DIMENSIONES]).any()
    assert set(ancho["provincia"]) == m.PRIMARIA_6 | m.PRIMARIA_7
    assert "localizacion" not in ancho


def test_no_graduada_es_na_antes_de_2022(ancho):
    assert ancho.loc[ancho["anio"] < 2023, "_20"].isna().all()
    assert ancho.loc[ancho["anio"] >= 2023, "_20"].notna().any()


def test_identidades_parte_menor_o_igual_que_total(largo):
    for parte in ["varones", "repitentes", "sobreedad"]:
        excede = largo[parte] > largo["matricula"]
        assert not excede.fillna(False).any(), parte
    assert (largo["mujeres"] >= 0).all()


def test_sobreedad_solo_imputada_donde_hay_matricula(ancho):
    for grado in m.GRADOS:
        sin_oferta = ancho[f"_{grado}"].isna()
        assert ancho.loc[sin_oferta, f"s_{grado}"].isna().all()
        assert ancho.loc[~sin_oferta, f"s_{grado}"].notna().all()
        informado = ancho[f"s_{grado}_informado"].dropna()
        assert (ancho.loc[informado.index, f"s_{grado}"] == informado).all()


def test_totales_contrastados_con_la_exploracion(ancho):
    a2011 = ancho[ancho["anio"] == 2011]
    assert sum(a2011[f"_{g}"].sum() for g in m.GRADOS) == 8_351_514
    a2021 = ancho[ancho["anio"] == 2021]
    primeros_6 = m.GRADOS[:6]
    tasa = sum(a2021[f"r_{g}"].sum() for g in primeros_6) / sum(
        a2021[f"_{g}"].sum() for g in primeros_6
    )
    assert round(100 * tasa, 2) == 0.67


def test_largo_reproduce_totales_del_archivo(ancho, largo):
    columnas = [m.col_matricula(g) for g in [*m.SALAS, *m.GRADOS, m.NO_GRADUADA]]
    esperado = ancho.groupby("anio")[columnas].sum().sum(axis=1)
    obtenido = largo.groupby("anio")["matricula"].sum()
    pd.testing.assert_series_equal(obtenido, esperado, check_names=False, check_dtype=False)
    rep_esperado = ancho.groupby("anio")[[f"r_{g}" for g in [*m.GRADOS, "20"]]].sum().sum(axis=1)
    rep_obtenido = largo.groupby("anio")["repitentes"].sum()
    pd.testing.assert_series_equal(rep_obtenido, rep_esperado, check_names=False, check_dtype=False)


def test_agregados_desde_corte_iguales_a_desde_largo(largo, base_nivel, base_grado):
    # Las bases de nivel y grado se derivan de la de cortes: deben dar lo mismo que desde el largo
    pares = [(base_nivel, ["nivel"]), (base_grado, ["nivel", "grado", "grado_orden"])]
    for derivada, por in pares:
        directa = m.por_provincia_y_pais(largo, por)
        claves = ["anio", "provincia", *por]
        pd.testing.assert_frame_equal(
            derivada.sort_values(claves, ignore_index=True),
            directa.sort_values(claves, ignore_index=True),
        )


def test_agregado_pais_igual_suma_provincias(base_nivel):
    tabla = base_nivel
    pais = tabla[tabla["provincia"] == m.TOTAL_PAIS].set_index(["anio", "nivel"])
    provincias = tabla[tabla["provincia"] != m.TOTAL_PAIS].groupby(["anio", "nivel"])
    for medida in ["matricula", "varones", "repitentes"]:
        suma = provincias[medida].sum()
        assert (pais[medida] == suma).all(), medida

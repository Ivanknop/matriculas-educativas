"""Registro único de alertas de calidad revisadas. Las visualizaciones las consultan con
`edu_data.validacion_base.alerta_para`. Detalle y evidencia: data/diccionario_matricula.md.
"""

from edu_data.validacion_base import Alerta

ALERTAS = [
    Alerta(
        periodos=[2021],
        indicadores=["repitentes", "sobreedad"],
        afecta_total=True,
        texto=(
            "Efecto de la pandemia: la promoción acompañada del ciclo 2020 se ve en la "
            "matrícula 2021, con repitencia casi nula y menos sobreedad. Shock real"
        ),
    ),
    Alerta(
        periodos=[2017],
        indicadores=["repitentes"],
        afecta_total=True,
        texto=(
            "Quiebre nacional: la repitencia sube a la vez en 21 de 24 provincias y se mantiene "
            "(total país, primaria: 2,15 % a 3,16 %). Posible cambio de criterio, a confirmar"
        ),
    ),
    Alerta(
        periodos=[2011],
        unidades=["Santiago del Estero"],
        indicadores=["repitentes", "matricula"],
        filtros={"nivel": "secundaria"},
        texto=(
            "Repitencia de secundaria 2,4 % (8º: 3,4 %) contra 9–11 % los años siguientes, y "
            "matrícula 9 % menor que en 2012: probable problema de carga"
        ),
    ),
    Alerta(
        periodos=[2012],
        unidades=["Catamarca"],
        indicadores=["matricula", "repitentes"],
        filtros={"nivel": "secundaria"},
        texto=(
            "Matrícula de secundaria cae 11 % y rebota 7 % en 2013; repitencia 3,2 % entre "
            "4,7 % y 4,8 %: probable problema de carga"
        ),
    ),
    Alerta(
        periodos=[2020, 2021, 2022, 2023, 2024],
        unidades=["Santa Cruz"],
        indicadores=["repitentes"],
        filtros={"nivel": "secundaria"},
        texto=(
            "Repitencia de secundaria cae de 17 % (2019) a 0,4 % (2020) y 0 % hasta 2024; "
            "vuelve a 15 % en 2025. Anterior al efecto de la pandemia: régimen o carga, sin "
            "confirmar"
        ),
    ),
    Alerta(
        periodos=[2022, 2023, 2024, 2025],
        unidades=["Santa Cruz"],
        indicadores=["sobreedad"],
        filtros={"nivel": "secundaria"},
        texto=(
            "Sobreedad de secundaria cae de 39,5 % (2019) a 7,8 % (2024) y rebota a 20 % en 2025: "
            "demasiado rápido para ser solo efecto de no repetir; sin confirmar"
        ),
    ),
    Alerta(
        periodos=[2025],
        unidades=["Buenos Aires"],
        indicadores=["repitentes", "sobreedad"],
        filtros={"nivel": "secundaria"},
        afecta_total=True,
        # Res. 1650/24 (Buenos Aires): rige en el ciclo 2024; se ve en los repitentes de 2025
        texto=(
            "Cambio normativo (Res. 1650/24, ciclo 2024): termina la repitencia en bloque; solo "
            "se recuperan materias. Repitencia de 6,2 % a 2,5 % y sobreedad de 19,9 % a 15,5 %. "
            "No comparable con años previos; pesa en el total"
        ),
    ),
    Alerta(
        periodos=[2024, 2025],
        indicadores=["secciones"],
        filtros={"nivel": "no_graduada"},
        texto="Hay alumnos de organización no graduada (_20) pero 0 secciones (_sec20)",
    ),
]

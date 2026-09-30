from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(
    "data/processed/radar156.parquet"
)


st.set_page_config(
    page_title="Radar 156",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """
    Carrega o dataset analítico já processado.
    """

    df = pd.read_parquet(
        DATA_FILE
    )

    df["semana"] = pd.to_datetime(
        df["semana"]
    )

    return df


if not DATA_FILE.exists():
    st.error(
        "O arquivo radar156.parquet não foi encontrado. "
        "Execute primeiro: python scripts/preparar_dados.py"
    )

    st.stop()


df = load_data()


st.title("Radar 156")

st.write(
    "Monitoramento de alterações relevantes "
    "na demanda por serviços municipais."
)

st.caption(
    "O radar combina comportamento recente, "
    "pendência e tempo de atendimento para "
    "destacar sinais que merecem investigação."
)


st.subheader("Filtros")

temas = sorted(
    df["tema"]
    .dropna()
    .unique()
)

tema_selecionado = st.selectbox(
    "Tema",
    ["Todos"] + temas,
)


filtered = df.copy()

if tema_selecionado != "Todos":
    filtered = filtered[
        filtered["tema"]
        == tema_selecionado
    ]


distritos = sorted(
    filtered.loc[
        filtered["distrito_valido"],
        "distrito",
    ]
    .dropna()
    .unique()
)

distrito_selecionado = st.selectbox(
    "Distrito",
    ["Todos"] + distritos,
)


if distrito_selecionado != "Todos":
    filtered = filtered[
        filtered["distrito"]
        == distrito_selecionado
    ]


semanas = sorted(
    pd.to_datetime(
        filtered["semana"]
        .dropna()
        .unique()
    )
)


if not semanas:
    st.warning(
        "Nenhum dado encontrado para "
        "os filtros selecionados."
    )

    st.stop()


semana_selecionada = st.selectbox(
    "Semana de referência",
    semanas,
    index=len(semanas) - 1,
    format_func=lambda date: (
        pd.Timestamp(date)
        .strftime("%d/%m/%Y")
    ),
)


current = filtered[
    filtered["semana"]
    == semana_selecionada
].copy()


st.subheader("Dados da semana")

st.dataframe(
    current.head(20),
    use_container_width=True,
)
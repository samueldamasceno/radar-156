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
    "Monitoramento da demanda por "
    "serviços municipais."
)

st.dataframe(
    df.head(20),
    use_container_width=True,
)
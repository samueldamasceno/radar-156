from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(
    "data/processed/radar156.parquet"
)


df = pd.read_parquet(
    DATA_FILE
)


st.title("Radar 156")

st.write(
    "Monitoramento da demanda por "
    "serviços municipais."
)

st.dataframe(
    df.head(20),
    use_container_width=True,
)
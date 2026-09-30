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


# A última semana disponível começa em 29/06 e é parcial.
# Por isso, a penúltima semana é a referência inicial.
if len(semanas) >= 2:
    default_week_index = (
        len(semanas) - 2
    )
else:
    default_week_index = 0


semana_selecionada = st.selectbox(
    "Semana de referência",
    semanas,
    index=default_week_index,
    format_func=lambda date: (
        pd.Timestamp(date)
        .strftime("%d/%m/%Y")
    ),
)


volume_minimo = st.slider(
    "Volume mínimo por sinal",
    min_value=1,
    max_value=50,
    value=5,
    step=1,
    help=(
        "Reduz ruído causado por combinações com "
        "pouquíssimas solicitações."
    ),
)


current = filtered[
    filtered["semana"]
    == semana_selecionada
].copy()


signals = current[
    current["solicitacoes"]
    >= volume_minimo
].copy()


st.subheader("Dados da semana")

st.dataframe(
    signals.head(20),
    use_container_width=True,
)
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


def format_integer(value):
    """
    Formata inteiros no padrão brasileiro.
    """

    if pd.isna(value):
        return "N/D"

    return (
        f"{int(value):,}"
        .replace(",", ".")
    )


def format_percent(value):
    """
    Recebe proporção 0-1.
    """

    if pd.isna(value):
        return "N/D"

    return (
        f"{value * 100:.1f}%"
        .replace(".", ",")
    )


def format_change(value):
    """
    Recebe percentual já em pontos percentuais.
    Ex: 25.5 significa +25,5%.
    """

    if pd.isna(value):
        return "Sem baseline"

    return (
        f"{value:+.1f}%"
        .replace(".", ",")
    )


def format_days(value):
    if pd.isna(value):
        return "N/D"

    return (
        f"{value:.1f} dias"
        .replace(".", ",")
    )


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


if len(semanas) >= 2:
    default_week_index = len(semanas) - 2
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


territorial_current = current[
    current["distrito_valido"]
].copy()


ranking = territorial_current[
    (
        territorial_current["solicitacoes"]
        >= volume_minimo
    )
    & territorial_current["indice_atencao"].notna()
].copy()


ranking = ranking.sort_values(
    [
        "indice_atencao",
        "score_anomalia",
        "solicitacoes",
    ],
    ascending=[
        False,
        False,
        False,
    ],
)


st.subheader("Sinais encontrados")

st.dataframe(
    ranking.head(20),
    use_container_width=True,
)
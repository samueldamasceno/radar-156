from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
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
    df = pd.read_parquet(
        DATA_FILE
    )

    df["semana"] = pd.to_datetime(
        df["semana"]
    )

    return df


def format_integer(value):
    if pd.isna(value):
        return "N/D"

    return (
        f"{int(value):,}"
        .replace(",", ".")
    )


def format_percent(value):
    if pd.isna(value):
        return "N/D"

    return (
        f"{value * 100:.1f}%"
        .replace(".", ",")
    )


def format_change(value):
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


st.subheader(
    "Situação na semana selecionada"
)


total = int(
    current["solicitacoes"].sum()
)

pendentes = int(
    current["pendentes"].sum()
)


if total > 0:
    taxa_pendente_geral = (
        pendentes / total
    )
else:
    taxa_pendente_geral = np.nan


territorial_volume = int(
    current.loc[
        current["distrito_valido"],
        "solicitacoes",
    ].sum()
)


if total > 0:
    cobertura = (
        territorial_volume / total
    )
else:
    cobertura = np.nan


sinais_elevados = int(
    (
        ranking["indice_atencao"]
        >= 75
    ).sum()
)

anomalias = int(
    ranking["anomalia"].sum()
)


col1, col2, col3, col4, col5 = (
    st.columns(5)
)

col1.metric(
    "Solicitações",
    format_integer(total),
)

col2.metric(
    "Pendentes",
    format_percent(
        taxa_pendente_geral
    ),
)

col3.metric(
    "Cobertura territorial",
    format_percent(cobertura),
)

col4.metric(
    "Atenção elevada",
    format_integer(
        sinais_elevados
    ),
)

col5.metric(
    "Sinais atípicos",
    format_integer(anomalias),
)


st.caption(
    "Cobertura territorial representa a parcela "
    "das solicitações que possui distrito nominal "
    "identificado."
)


st.subheader(
    "Evolução das solicitações"
)


weekly = (
    filtered
    .groupby(
        "semana",
        as_index=False,
    )
    .agg(
        solicitacoes=(
            "solicitacoes",
            "sum",
        ),
        pendentes=(
            "pendentes",
            "sum",
        ),
    )
)


fig_weekly = px.line(
    weekly,
    x="semana",
    y="solicitacoes",
    markers=True,
    labels={
        "semana": "",
        "solicitacoes":
        "Solicitações",
    },
)


st.plotly_chart(
    fig_weekly,
    use_container_width=True,
)


st.caption(
    "A última semana do período é parcial "
    "e não deve ser comparada diretamente "
    "com semanas completas."
)


st.subheader(
    "Pontos que merecem investigação"
)

st.dataframe(
    ranking.head(20),
    use_container_width=True,
)
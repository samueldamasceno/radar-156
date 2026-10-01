from pathlib import Path
import textwrap

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
    df = pd.read_parquet(DATA_FILE)
    df["semana"] = pd.to_datetime(
        df["semana"]
    )
    return df


def format_integer(value):
    if pd.isna(value):
        return "N/D"
    return f"{int(value):,}".replace(",", ".")


def format_percent(value):
    if pd.isna(value):
        return "N/D"
    return f"{value * 100:.1f}%".replace(".", ",")


def format_change(value):
    if pd.isna(value):
        return "Sem baseline"
    return f"{value:+.1f}%".replace(".", ",")


def format_days(value):
    if pd.isna(value):
        return "N/D"
    return f"{value:.1f} dias".replace(".", ",")


if not DATA_FILE.exists():
    st.error(
        "O arquivo radar156.parquet não foi encontrado. "
        "Execute primeiro: python scripts/preparar_dados.py"
    )
    st.stop()


df = load_data()


pagina = st.sidebar.radio(
    "Navegação",
    [
        "Visão geral",
        "Radar de atenção",
        "Investigar sinal",
        "Metodologia",
    ],
)


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
    df["tema"].dropna().unique()
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
        "Nenhum dado encontrado para os filtros selecionados."
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
    & territorial_current[
        "indice_atencao"
    ].notna()
].copy()

ranking = ranking.sort_values(
    [
        "indice_atencao",
        "score_anomalia",
        "solicitacoes",
    ],
    ascending=[False, False, False],
)


if pagina == "Visão geral":

    st.subheader(
        "Situação na semana selecionada"
    )

    total = int(
        current["solicitacoes"].sum()
    )
    pendentes = int(
        current["pendentes"].sum()
    )

    taxa_pendente_geral = (
        pendentes / total
        if total > 0
        else np.nan
    )

    territorial_volume = int(
        current.loc[
            current["distrito_valido"],
            "solicitacoes",
        ].sum()
    )

    cobertura = (
        territorial_volume / total
        if total > 0
        else np.nan
    )

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

    if tema_selecionado == "Todos":
        chart_title = "Temas com maior demanda"
        category_column = "tema"
    else:
        chart_title = "Serviços com maior demanda"
        category_column = "servico"

    st.subheader(chart_title)

    top_categories = (
        current
        .groupby(
            category_column,
            as_index=False,
        )
        .agg(
            solicitacoes=(
                "solicitacoes",
                "sum",
            )
        )
        .nlargest(
            8,
            "solicitacoes",
        )
        .sort_values(
            "solicitacoes",
            ascending=True,
        )
    )

    top_categories[
        "categoria_grafico"
    ] = (
        top_categories[
            category_column
        ]
        .astype(str)
        .map(
            lambda value: "<br>".join(
                textwrap.wrap(
                    str(value),
                    width=52,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
        )
    )

    fig_categories = px.bar(
        top_categories,
        x="solicitacoes",
        y="categoria_grafico",
        orientation="h",
        hover_name=category_column,
        labels={
            "solicitacoes": "Solicitações",
            "categoria_grafico": "",
        },
    )

    st.plotly_chart(
        fig_categories,
        use_container_width=True,
    )

    st.subheader(
        "Pontos que merecem investigação"
    )

    st.caption(
        "Combinações distrito + serviço ordenadas "
        "pelo Índice de Atenção."
    )

    if ranking.empty:
        st.info(
            "Nenhum sinal encontrado com "
            "os filtros atuais."
        )
    else:
        ranking_display = ranking.head(15).copy()

        ranking_display[
            "Variação"
        ] = ranking_display[
            "variacao_percentual"
        ]

        ranking_display[
            "Pendência"
        ] = (
            ranking_display[
                "taxa_pendente"
            ] * 100
        )

        ranking_display[
            "Tempo médio"
        ] = ranking_display[
            "tempo_medio_dias"
        ]

        ranking_display[
            "Atípico"
        ] = np.where(
            ranking_display["anomalia"],
            "Sim",
            "Não",
        )

        ranking_display = (
            ranking_display[
                [
                    "distrito",
                    "tema",
                    "servico",
                    "solicitacoes",
                    "Variação",
                    "Pendência",
                    "Tempo médio",
                    "indice_atencao",
                    "Atípico",
                ]
            ]
            .rename(
                columns={
                    "distrito": "Distrito",
                    "tema": "Tema",
                    "servico": "Serviço",
                    "solicitacoes": "Solicitações",
                    "indice_atencao": "Índice",
                }
            )
        )

        st.dataframe(
            ranking_display,
            width="stretch",
            hide_index=True,
            column_config={
                "Solicitações":
                st.column_config.NumberColumn(
                    format="%d",
                ),
                "Variação":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),
                "Pendência":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),
                "Tempo médio":
                st.column_config.NumberColumn(
                    format="%.1f dias",
                ),
                "Índice":
                st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
            },
        )


elif pagina == "Radar de atenção":

    st.subheader(
        "Radar de atenção"
    )

    st.markdown(
        "Cada ponto representa uma combinação entre "
        "**distrito e serviço** na semana selecionada. "
        "O eixo horizontal mostra a mudança de demanda "
        "em relação ao comportamento recente. "
        "O eixo vertical mostra a proporção de solicitações "
        "ainda abertas ou em andamento. "
        "O tamanho representa o volume de solicitações."
    )

    if ranking.empty:

        st.info(
            "Não existem sinais disponíveis "
            "para esses filtros."
        )

    else:

        plot_df = ranking.copy()

        plot_df[
            "variacao_grafico"
        ] = (
            plot_df[
                "variacao_percentual"
            ]
            .clip(
                lower=-100,
                upper=500,
            )
            .fillna(0)
        )

        plot_df[
            "pendencia_percentual"
        ] = (
            plot_df[
                "taxa_pendente"
            ] * 100
        )

        fig_radar = px.scatter(
            plot_df,
            x="variacao_grafico",
            y="pendencia_percentual",
            size="solicitacoes",
            color="indice_atencao",
            color_continuous_scale=[
                [0.0, "#4D37FF"],
                [0.55, "#8A5BFF"],
                [1.0, "#FF5C35"],
            ],
            size_max=34,
            hover_name="servico",
            hover_data={
                "distrito": True,
                "tema": True,
                "solicitacoes": True,
                "indice_atencao": ":.1f",
                "variacao_grafico": ":.1f",
                "pendencia_percentual": ":.1f",
            },
            labels={
                "variacao_grafico":
                "Variação da demanda (%)",
                "pendencia_percentual":
                "Solicitações pendentes (%)",
                "indice_atencao":
                "Índice",
                "distrito":
                "Distrito",
                "tema":
                "Tema",
                "solicitacoes":
                "Solicitações",
            },
        )

        fig_radar.add_vline(
            x=0,
            line_dash="dash",
            line_width=1,
        )

        fig_radar.add_hline(
            y=50,
            line_dash="dash",
            line_width=1,
        )

        st.plotly_chart(
            fig_radar,
            use_container_width=True,
        )

        st.caption(
            "Valores de variação superiores a 500% "
            "são limitados visualmente no gráfico para "
            "preservar a legibilidade. Os valores reais "
            "continuam armazenados no dataset."
        )

        st.subheader(
            "Maiores índices de atenção"
        )

        top_radar = (
            ranking
            .head(10)
            .sort_values(
                "indice_atencao",
                ascending=True,
            )
        )

        top_radar[
            "identificacao"
        ] = (
            top_radar["distrito"]
            + " · "
            + top_radar["servico"]
        )

        fig_top = px.bar(
            top_radar,
            x="indice_atencao",
            y="identificacao",
            orientation="h",
            labels={
                "indice_atencao":
                "Índice de Atenção",
                "identificacao": "",
            },
        )

        fig_top.update_xaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True,
        )


elif pagina == "Investigar sinal":

    st.subheader(
        "Investigação de sinal"
    )

    st.caption(
        "Selecione uma ocorrência para entender "
        "por que ela apareceu no Radar."
    )

    if ranking.empty:
        st.info(
            "Não existem sinais disponíveis "
            "para os filtros selecionados."
        )
        st.stop()

    candidates = (
        ranking
        .head(100)
        .reset_index(
            drop=True
        )
    )

    option = st.selectbox(
        "Sinal para investigar",
        options=list(
            range(
                len(candidates)
            )
        ),
        format_func=lambda i: (
            f"{candidates.iloc[i]['distrito']} | "
            f"{candidates.iloc[i]['servico']}"
        ),
    )

    selected = (
        candidates
        .iloc[option]
    )

    st.markdown(
        f"### {selected['distrito']}"
    )

    st.markdown(
        f"**{selected['servico']}**"
    )

    st.caption(
        f"Tema: {selected['tema']}"
    )


elif pagina == "Metodologia":
    st.info(
        "Metodologia em desenvolvimento."
    )
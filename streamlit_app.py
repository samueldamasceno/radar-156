from pathlib import Path
import textwrap

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_FILE = Path("data/processed/radar156.parquet")


st.set_page_config(
    page_title="Radar 156",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --radar-red: #FF5C35;
        --radar-red-soft: #FF8065;
        --radar-blue: #4D37FF;
        --radar-sky: #67D8FF;
        --radar-bg: #0B0B0E;
        --radar-bg-soft: #111116;
        --radar-surface: #17171D;
        --radar-surface-2: #202028;
        --radar-line: #34343E;
        --radar-ink: #08080A;
        --radar-text: #F4F1E8;
        --radar-muted: #A7A3AD;
        --radar-muted-2: #77737E;
        --shadow-sm: 3px 3px 0 #050506;
        --shadow-md: 5px 5px 0 #050506;
        --shadow-lg: 8px 8px 0 #050506;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            ui-sans-serif,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stApp {
        color: var(--radar-text);
        background:
            linear-gradient(
                rgba(255,255,255,.018) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(255,255,255,.018) 1px,
                transparent 1px
            ),
            radial-gradient(
                circle at 78% -10%,
                rgba(255,92,53,.14),
                transparent 30rem
            ),
            radial-gradient(
                circle at 8% 8%,
                rgba(77,55,255,.10),
                transparent 28rem
            ),
            var(--radar-bg);

        background-size:
            30px 30px,
            30px 30px,
            auto,
            auto,
            auto;
    }

    .block-container {
        max-width: 1520px;
        padding-top: 1.65rem;
        padding-bottom: 5rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        background: rgba(11,11,14,.92);
        border-bottom: 1px solid rgba(255,255,255,.06);
        backdrop-filter: blur(10px);
    }

    h1,
    h2,
    h3,
    h4,
    p,
    label,
    .stCaption {
        color: var(--radar-text);
    }

    h1 {
        font-size: clamp(2.9rem, 5vw, 5rem) !important;
        line-height: .9 !important;
        letter-spacing: -.065em !important;
        font-weight: 900 !important;
    }

    h2 {
        letter-spacing: -.045em !important;
        font-weight: 900 !important;
    }

    h3 {
        letter-spacing: -.035em !important;
        font-weight: 850 !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(255,92,53,.06),
                transparent 16rem
            ),
            #0D0D11;

        border-right: 1px solid #292932;
        box-shadow: none;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem 1.15rem;
    }

    .sidebar-brand {
    margin: .05rem 0 1rem;
    padding: .15rem .15rem 1.15rem;
    border-bottom: 1px solid #2A2A33;
    }

    .sidebar-brand-kicker {
        margin-bottom: .55rem;
        color: var(--radar-red);
        font-size: .62rem;
        font-weight: 900;
        letter-spacing: .18em;
        text-transform: uppercase;
    }

    .sidebar-brand-title {
        margin: 0;
        color: var(--radar-text);
        font-size: 1.75rem;
        font-weight: 950;
        letter-spacing: -.06em;
        line-height: .95;
    }

    .sidebar-brand-line {
        width: 42px;
        height: 4px;
        margin: .85rem 0 .75rem;
        background: var(--radar-red);
    }

    .sidebar-brand-copy {
        max-width: 230px;
        color: #777781;
        font-size: .78rem;
        font-weight: 650;
        line-height: 1.5;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
    gap: .25rem;
    margin-top: .15rem;
    counter-reset: radar-nav;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        position: relative;
        display: flex !important;
        align-items: center !important;
        min-height: 48px;
        padding: .78rem .85rem .78rem 3rem;
        border: 1px solid transparent;
        border-radius: 8px;
        background: transparent;
        color: var(--radar-text) !important;
        box-shadow: none;
        cursor: pointer;
        counter-increment: radar-nav;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        content: "0" counter(radar-nav);
        position: absolute;
        left: .9rem;
        top: 50%;
        transform: translateY(-50%);
        color: #5F5F69;
        font-size: .62rem;
        font-weight: 900;
        letter-spacing: .08em;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        margin: 0 !important;
        color: #D6D3CC !important;
        font-size: .86rem !important;
        font-weight: 760 !important;
        letter-spacing: -.015em;
    }

    [data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
        position: absolute !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
    }

    [data-testid="stSidebar"]
    [role="radiogroup"]
    input[type="radio"] + div,

    [data-testid="stSidebar"]
    [role="radiogroup"]
    label > div:first-child:has(input[type="radio"]),

    [data-testid="stSidebar"]
    [role="radiogroup"]
    [data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_FILE)
    df["semana"] = pd.to_datetime(df["semana"])
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


def standard_layout(fig, height=420):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=24, r=24, t=42, b=24),
        paper_bgcolor="#17171D",
        plot_bgcolor="#17171D",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#F4F1E8",
        ),
        colorway=[
            "#FF5C35",
            "#4D37FF",
            "#67D8FF",
            "#FF8065",
            "#B7ADFF",
        ],
        hoverlabel=dict(
            bgcolor="#08080A",
            bordercolor="#FF5C35",
            font_color="#FFFFFF",
            font_size=13,
        ),
        hovermode="closest",
        legend=dict(
            font=dict(color="#D8D3DC"),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(244,241,232,.24)",
        linewidth=1,
        tickfont=dict(color="#AAA6B0"),
        title_font=dict(color="#F4F1E8"),
        ticks="outside",
        tickcolor="rgba(244,241,232,.24)",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(244,241,232,.08)",
        zeroline=False,
        linecolor="rgba(244,241,232,.24)",
        linewidth=1,
        tickfont=dict(color="#AAA6B0"),
        title_font=dict(color="#F4F1E8"),
        ticks="outside",
        tickcolor="rgba(244,241,232,.24)",
    )

    return fig


if not DATA_FILE.exists():
    st.error(
        "O arquivo radar156.parquet não foi encontrado. "
        "Execute primeiro: python scripts/preparar_dados.py"
    )
    st.stop()


df = load_data()

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-brand-kicker">
            SP156 · Dados públicos
        </div>

        <div class="sidebar-brand-title">
            RADAR 156
        </div>

        <div class="sidebar-brand-line"></div>

        <div class="sidebar-brand-copy">
            Inteligência operacional sobre a demanda municipal.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
        filtered["tema"] == tema_selecionado
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
    ascending=[
        False,
        False,
        False,
    ],
)


if (
    pd.Timestamp(semana_selecionada)
    == pd.Timestamp("2026-06-29")
):
    st.warning(
        "A semana iniciada em 29/06/2026 é parcial: "
        "o conjunto do 2º trimestre possui dados apenas "
        "até 30/06/2026. Comparações de volume nessa semana "
        "devem ser interpretadas com cautela."
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

    fig_weekly.update_traces(
        line=dict(
            width=3,
            color="#FF5C35",
        ),
        marker=dict(
            size=7,
            color="#4D37FF",
            line=dict(
                width=1,
                color="#171717",
            ),
        ),
    )

    fig_weekly = standard_layout(
        fig_weekly,
        390,
    )

    fig_weekly.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        fig_weekly,
        width="stretch",
    )

    st.caption(
        "A última semana do período é parcial e "
        "não deve ser comparada diretamente com "
        "semanas completas."
    )


    if tema_selecionado == "Todos":
        chart_title = (
            "Temas com maior demanda"
        )
        category_column = "tema"

    else:
        chart_title = (
            "Serviços com maior demanda"
        )
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
            "solicitacoes":
            "Solicitações",
            "categoria_grafico":
            "",
        },
    )

    fig_categories = standard_layout(
        fig_categories,
        500,
    )

    fig_categories.update_traces(
        marker_color="#FF5C35",
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Solicitações: %{x}<extra></extra>"
        ),
    )

    fig_categories.update_yaxes(
        automargin=True,
        tickfont=dict(
            size=12,
            color="#D8D3DC",
        ),
    )

    fig_categories.update_xaxes(
        automargin=True
    )

    fig_categories.update_layout(
        showlegend=False,
        margin=dict(
            l=12,
            r=28,
            t=24,
            b=42,
        ),
        bargap=0.28,
    )

    st.plotly_chart(
        fig_categories,
        width="stretch",
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
        ranking_display = (
            ranking
            .head(15)
            .copy()
        )

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
            ]
            * 100
        )

        ranking_display[
            "Tempo médio"
        ] = ranking_display[
            "tempo_medio_dias"
        ]

        ranking_display[
            "Atípico"
        ] = np.where(
            ranking_display[
                "anomalia"
            ],
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
                    "distrito":
                    "Distrito",
                    "tema":
                    "Tema",
                    "servico":
                    "Serviço",
                    "solicitacoes":
                    "Solicitações",
                    "indice_atencao":
                    "Índice",
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
            ]
            * 100
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
            line_color="rgba(23,23,23,.28)",
        )

        fig_radar.add_hline(
            y=50,
            line_dash="dash",
            line_width=1,
            line_color="rgba(23,23,23,.28)",
        )

        fig_radar = standard_layout(
            fig_radar,
            650,
        )

        fig_radar.update_layout(
            coloraxis_colorbar=dict(
                title="Índice",
            ),
        )

        st.plotly_chart(
            fig_radar,
            width="stretch",
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
                "identificacao":
                "",
            },
        )

        fig_top.update_xaxes(
            range=[0, 100]
        )

        fig_top = standard_layout(
            fig_top,
            470,
        )

        fig_top.update_layout(
            showlegend=False,
        )

        st.plotly_chart(
            fig_top,
            width="stretch",
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
        .reset_index(drop=True)
    )

    option = st.selectbox(
        "Sinal para investigar",
        options=list(
            range(len(candidates))
        ),
        format_func=lambda i: (
            f"{candidates.iloc[i]['distrito']} | "
            f"{candidates.iloc[i]['servico']}"
        ),
    )

    selected = candidates.iloc[option]

    st.markdown(
        f"### {selected['distrito']}"
    )

    st.markdown(
        f"**{selected['servico']}**"
    )

    st.caption(
        f"Tema: {selected['tema']}"
    )

    c1, c2, c3, c4, c5 = (
        st.columns(5)
    )

    c1.metric(
        "Índice de Atenção",
        (
            f"{selected['indice_atencao']:.1f}"
            .replace(".", ",")
            + "/100"
        ),
    )

    c2.metric(
        "Solicitações",
        format_integer(
            selected["solicitacoes"]
        ),
    )

    c3.metric(
        "Variação",
        format_change(
            selected[
                "variacao_percentual"
            ]
        ),
    )

    c4.metric(
        "Pendentes",
        format_percent(
            selected["taxa_pendente"]
        ),
    )

    c5.metric(
        "Tempo médio",
        format_days(
            selected["tempo_medio_dias"]
        ),
    )

    if selected["anomalia"]:
        st.info(
            "Esta observação está entre o conjunto "
            "de maior atipicidade identificado pelo "
            "Isolation Forest."
        )


    history = df[
        (
            df["distrito"]
            == selected["distrito"]
        )
        &
        (
            df["tema"]
            == selected["tema"]
        )
        &
        (
            df["servico"]
            == selected["servico"]
        )
    ].copy()

    history = history.sort_values(
        "semana"
    )


    st.subheader(
        "Evolução da demanda"
    )

    fig_history = go.Figure()

    fig_history.add_trace(
        go.Scatter(
            x=history["semana"],
            y=history["solicitacoes"],
            mode="lines+markers",
            name="Solicitações",
            line=dict(
                width=3,
                color="#FF5C35",
            ),
            marker=dict(
                size=7,
                color="#4D37FF",
            ),
        )
    )

    fig_history.add_trace(
        go.Scatter(
            x=history["semana"],
            y=history["volume_baseline"],
            mode="lines",
            name="Baseline recente",
            line=dict(
                width=2,
                dash="dash",
                color="#68645D",
            ),
        )
    )

    fig_history = standard_layout(
        fig_history,
        470,
    )

    fig_history.update_layout(
        xaxis_title="",
        yaxis_title="Solicitações",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    st.plotly_chart(
        fig_history,
        width="stretch",
    )


    st.subheader(
        "Por que este sinal recebeu atenção?"
    )

    component_data = pd.DataFrame(
        {
            "Componente": [
                "Crescimento da demanda",
                "Pendência",
                "Tempo de atendimento",
            ],
            "Score": [
                selected[
                    "score_crescimento"
                ],
                selected[
                    "score_pendencia"
                ],
                selected[
                    "score_tempo"
                ],
            ],
            "Peso": [
                "40%",
                "35%",
                "25%",
            ],
        }
    )

    fig_components = px.bar(
        component_data,
        x="Score",
        y="Componente",
        orientation="h",
        text="Peso",
        labels={
            "Score":
            "Posição relativa no período",
            "Componente":
            "",
        },
    )

    fig_components.update_xaxes(
        range=[0, 100]
    )

    fig_components = standard_layout(
        fig_components,
        330,
    )

    fig_components.update_layout(
        showlegend=False,
    )

    st.plotly_chart(
        fig_components,
        width="stretch",
    )


    reasons = []

    if (
        selected["score_crescimento"]
        >= 75
    ):
        reasons.append(
            "crescimento da demanda "
            "está entre os valores mais "
            "elevados da base"
        )

    if (
        selected["score_pendencia"]
        >= 75
    ):
        reasons.append(
            "taxa de pendência está "
            "relativamente elevada"
        )

    if (
        selected["score_tempo"]
        >= 75
    ):
        reasons.append(
            "tempo médio de atendimento "
            "está relativamente elevado"
        )

    if reasons:

        if len(reasons) == 1:
            reason_text = reasons[0]

        else:
            reason_text = (
                ", ".join(
                    reasons[:-1]
                )
                + " e "
                + reasons[-1]
            )

        st.markdown(
            f"**Leitura do sinal**  \n"
            f"Nesta observação, {reason_text}. "
            "Esses fatores contribuíram para elevar "
            "o Índice de Atenção."
        )

    else:
        st.markdown(
            "**Leitura do sinal**  \n"
            "Nenhum componente isolado está no quartil "
            "superior da distribuição. O resultado decorre "
            "da combinação dos indicadores."
        )

    st.warning(
        "O Índice de Atenção não mede gravidade "
        "do problema e não determina automaticamente "
        "prioridades de política pública. Ele funciona "
        "como um sinal para apoiar investigação."
    )


elif pagina == "Metodologia":

    st.subheader(
        "Como funciona o Radar 156"
    )

    st.markdown(
        "O Radar 156 transforma registros operacionais "
        "do SP156 em sinais analíticos que podem ajudar "
        "equipes de gestão a identificar mudanças que "
        "merecem investigação."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
### Etapa 01 · Coleta

Dados públicos dos dois primeiros trimestres de 2026 do SP156.

### Etapa 02 · Tratamento

Padronização de datas, status, distritos e tratamento de valores ausentes ou não identificáveis.

### Etapa 03 · Agregação

Os registros são consolidados por semana, distrito, tema e serviço.
            """
        )

    with col2:
        st.markdown(
            """
### Etapa 04 · Indicadores

Volume, crescimento da demanda, pendência e tempo médio de atendimento.

### Etapa 05 · Índice

Combinação heurística dos indicadores para destacar pontos que merecem investigação.

### Etapa 06 · Anomalias

Isolation Forest identifica o conjunto de observações com maior atipicidade estatística.
            """
        )

    st.divider()

    st.subheader(
        "Índice de Atenção"
    )

    st.latex(
        r"I = 0.40C + 0.35P + 0.25T"
    )

    st.markdown(
        """
**Onde:**

**C** representa a posição relativa do crescimento da demanda.

**P** representa a posição relativa da taxa de pendência.

**T** representa a posição relativa do tempo médio de atendimento.

Os pesos foram definidos como uma **heurística para o protótipo**. Eles não representam critérios oficiais da Prefeitura e deveriam ser calibrados com especialistas e gestores em uma evolução da solução.
        """
    )

    st.subheader(
        "Detecção de anomalias"
    )

    st.markdown(
        "O Radar utiliza **Isolation Forest**, um algoritmo "
        "de aprendizado não supervisionado. Nesta versão, "
        "o parâmetro `contamination=0.03` define aproximadamente "
        "3% das observações territoriais como o conjunto de maior "
        "atipicidade. Portanto, a classificação de anomalia não "
        "significa automaticamente que existe um problema grave. "
        "Ela indica apenas um padrão estatístico menos comum em "
        "relação ao conjunto analisado."
    )

    st.subheader(
        "Qualidade e cobertura territorial"
    )

    total_dataset = int(
        df["solicitacoes"].sum()
    )

    total_territorial = int(
        df.loc[
            df["distrito_valido"],
            "solicitacoes",
        ].sum()
    )

    dataset_coverage = (
        total_territorial
        / total_dataset
    )

    qa1, qa2, qa3 = st.columns(3)

    qa1.metric(
        "Solicitações analisadas",
        format_integer(
            total_dataset
        ),
    )

    qa2.metric(
        "Com distrito identificado",
        format_integer(
            total_territorial
        ),
    )

    qa3.metric(
        "Cobertura territorial",
        format_percent(
            dataset_coverage
        ),
    )

    st.markdown(
        "Registros cujo campo Distrito estava vazio ou "
        "continha apenas um código numérico foram mantidos "
        "nos indicadores gerais, mas excluídos das análises "
        "territoriais. Essa decisão evita atribuir uma "
        "localização que não pode ser sustentada diretamente "
        "pelos dados."
    )

    st.subheader(
        "Limitações atuais"
    )

    st.markdown(
        "- O período histórico ainda é curto, cobrindo apenas o primeiro semestre de 2026.\n"
        "- Solicitações do SP156 não equivalem diretamente ao número de problemas existentes na cidade.\n"
        "- Uma mesma situação pode gerar mais de uma solicitação.\n"
        "- Serviços podem ser executados sem uma solicitação prévia no SP156.\n"
        "- Parte relevante dos registros não possui distrito nominal identificado.\n"
        "- Os pesos do Índice de Atenção ainda não foram validados com gestores municipais.\n"
        "- O baseline utiliza as observações anteriores disponíveis e ainda não modela explicitamente sazonalidade."
    )

    st.subheader(
        "Possíveis evoluções"
    )

    st.markdown(
        "- Atualização automatizada quando novos dados do SP156 forem publicados.\n"
        "- Incorporação de um histórico de vários anos.\n"
        "- Ajuste do índice em conjunto com gestores.\n"
        "- Modelos específicos por tipo de serviço.\n"
        "- Detecção de sazonalidade e mudanças estruturais.\n"
        "- Integração com dados demográficos do IBGE.\n"
        "- Integração geográfica com camadas do GeoSampa.\n"
        "- Alertas automáticos para áreas responsáveis.\n"
        "- Simulação de capacidade operacional e backlog.\n"
        "- Separação futura entre frontend e API analítica para uma arquitetura de produção."
    )

    st.info(
        "Fonte principal: Portal de Dados Abertos "
        "da Prefeitura de São Paulo, conjunto Dados do SP156."
    )
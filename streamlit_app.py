import streamlit as st

st.set_page_config(
    page_title="Radar 156",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1 {
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #E5E7EB;
            padding: 18px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Radar 156")
st.caption(
    "Inteligência de dados para identificar alterações relevantes "
    "na demanda por serviços municipais."
)

st.info("Ambiente configurado com sucesso.")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Solicitações", "Em processamento")
col2.metric("Distritos", "Em processamento")
col3.metric("Serviços", "Em processamento")
col4.metric("Sinais detectados", "Em processamento")
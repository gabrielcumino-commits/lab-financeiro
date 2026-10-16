import streamlit as st

from src.visualization import COR_RECEITA, COR_REGRESSAO

CSS = f"""
<style>
    /* Títulos de seção com faixa colorida */
    .stApp h3 {{
        border-left: 4px solid {COR_RECEITA};
        padding-left: 0.6rem;
        margin-top: 1.2rem;
    }}

    /* Cartões de métricas */
    [data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #E1E6ED;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
    }}
    [data-testid="stMetricLabel"] {{
        color: #5B6B7F;
    }}
    [data-testid="stMetricValue"] {{
        color: {COR_RECEITA};
    }}

    /* Abas */
    button[data-baseweb="tab"] p {{
        font-weight: 600;
    }}

    /* Cabeçalho */
    .banner {{
        background: linear-gradient(135deg, {COR_RECEITA} 0%, {COR_REGRESSAO} 100%);
        border-radius: 12px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
    }}
    .banner h1 {{
        color: #FFFFFF;
        margin: 0;
        padding: 0;
        font-size: 2rem;
    }}
    .banner p {{
        color: rgba(255, 255, 255, 0.9);
        margin: 0.3rem 0 0 0;
        font-size: 1.05rem;
    }}

    footer {{
        visibility: hidden;
    }}
</style>
"""


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def exibir_cabecalho(titulo, subtitulo):
    st.markdown(
        f'<div class="banner"><h1>{titulo}</h1><p>{subtitulo}</p></div>',
        unsafe_allow_html=True,
    )
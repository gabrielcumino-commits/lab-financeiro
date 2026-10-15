
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import calcular_indicadores


st.set_page_config(
    page_title="Lab Financeiro",
    page_icon="📊",
    layout="wide",
)

st.title("Lab Financeiro")
st.write("Análise quantitativa de fluxo de caixa")

caminho_dados = (
    Path(__file__).parent
    / "data"
    / "sample"
    / "fluxo_financeiro.csv"
)

dados = pd.read_csv(caminho_dados)

dados, indicadores = calcular_indicadores(dados)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Receita total",
    f"R$ {indicadores['receita_total']:,.2f}",
)

col2.metric(
    "Despesas totais",
    f"R$ {indicadores['despesas_totais']:,.2f}",
)

col3.metric(
    "Fluxo líquido",
    f"R$ {indicadores['fluxo_total']:,.2f}",
)

col4.metric(
    "Margem líquida média",
    f"{indicadores['margem_media']:.2f}%",
)

st.subheader("Evolução financeira mensal")

grafico = dados.set_index("data")[["receita", "despesas"]]
st.line_chart(grafico)

st.subheader("Base de dados")
st.dataframe(dados, use_container_width=True)

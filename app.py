
from pathlib import Path

import pandas as pd
import streamlit as st

from src.exporting import exportar_csv, exportar_excel


from src.report import gerar_relatorio


from src.analysis import (
    calcular_indicadores,
    calcular_estatisticas,
)
from src.preprocessing import limpar_dados , validar_dados
from src.forecasting import (
    avaliar_modelo,
    prever_proximos_meses,
    comparar_modelos,
)


st.set_page_config(
    page_title="Lab Financeiro",
    page_icon="📊",
    layout="wide",
)

st.title("Lab Financeiro")
st.write("Análise quantitativa de fluxo de caixa")

arquivo = st.file_uploader(
    "Carregue uma planilha financeira",
    type=["csv", "xlsx"],
)

if arquivo is not None:
    try:
        if arquivo.name.endswith(".csv"):
            dados_originais = pd.read_csv(arquivo)
        else:
            dados_originais = pd.read_excel(arquivo)

        dados = limpar_dados(dados_originais)

        if len(dados) < 4:
            st.error(
                "A planilha precisa ter pelo menos 4 registros válidos."
            )
            st.stop()

        st.success("Arquivo carregado e dados validados.")

    except Exception as erro:
        st.error(f"Não foi possível processar o arquivo: {erro}")
        st.stop()

else:
    caminho_dados = (
        Path(__file__).parent
        / "data"
        / "sample"
        / "fluxo_financeiro.csv"
    )

    dados = pd.read_csv(caminho_dados)
    dados = limpar_dados(dados)


    problemas = validar_dados(dados)

if problemas:
    st.warning("Foram encontrados problemas nos dados:")

    for problema in problemas:
        st.write(f"- {problema}")

    st.stop()

dados, indicadores = calcular_indicadores(dados)
estatisticas = calcular_estatisticas(dados)

st.subheader("Indicadores financeiros")

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
st.line_chart(dados.set_index("data")[["receita", "despesas"]])

st.subheader("Variação mensal da receita")
st.line_chart(dados.set_index("data")["variacao_receita"])

st.subheader("Análise estatística")

col1, col2, col3 = st.columns(3)

col1.metric("Receita média", f"R$ {estatisticas['receita_media']:,.2f}")
col2.metric("Receita mediana", f"R$ {estatisticas['receita_mediana']:,.2f}")
col3.metric(
    "Desvio padrão",
    f"R$ {estatisticas['variabilidade_receita']:,.2f}",
)

col4, col5, col6 = st.columns(3)

col4.metric("Fluxo mínimo", f"R$ {estatisticas['fluxo_minimo']:,.2f}")
col5.metric("Fluxo máximo", f"R$ {estatisticas['fluxo_maximo']:,.2f}")
col6.metric(
    "Crescimento da receita",
    f"{estatisticas['crescimento_receita']:.2f}%",
)

st.subheader("Previsão de receita")

meses_futuros = st.slider(
    "Meses para prever",
    min_value=1,
    max_value=6,
    value=3,
)

previsoes = prever_proximos_meses(
    dados,
    meses_futuros=meses_futuros,
)

st.line_chart(
    previsoes.set_index("data")["receita_prevista"]
)
st.dataframe(previsoes, use_container_width=True)

st.subheader("Avaliação do modelo")

metricas, resultados = avaliar_modelo(dados)

col1, col2 = st.columns(2)

col1.metric("MAE", f"R$ {metricas['mae']:,.2f}")
col2.metric("RMSE", f"R$ {metricas['rmse']:,.2f}")

st.dataframe(resultados, use_container_width=True)

st.subheader("Comparação de modelos")

metricas_comparacao, comparacao = comparar_modelos(dados)

col1, col2 = st.columns(2)

col1.metric(
    "MAE — Regressão linear",
    f"R$ {metricas_comparacao['mae_regressao']:,.2f}",
)
col2.metric(
    "MAE — Previsão ingênua",
    f"R$ {metricas_comparacao['mae_ingenua']:,.2f}",
)

st.line_chart(
    comparacao[
        ["receita_real", "regressao_linear", "previsao_ingenua"]
    ]
)

st.subheader("Dados analisados")
st.dataframe(dados, use_container_width=True)




st.subheader("Exportar resultados")

arquivo_csv = exportar_csv(dados)

st.download_button(
    label="Baixar dados em CSV",
    data=arquivo_csv,
    file_name="lab_financeiro_dados.csv",
    mime="text/csv",
)

arquivo_excel = exportar_excel(
    dados,
    indicadores,
    previsoes,
)

st.download_button(
    label="Baixar relatório em Excel",
    data=arquivo_excel,
    file_name="lab_financeiro_relatorio.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)



st.subheader("Relatório gerencial")

relatorio = gerar_relatorio(
    indicadores["receita_total"],
    indicadores["despesas_totais"]
)

st.text(relatorio)

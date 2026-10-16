from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import calcular_estatisticas, calcular_indicadores
from src.data_loader import carregar_dados
from src.estilo import aplicar_estilo, exibir_cabecalho
from src.exporting import exportar_csv, exportar_excel
from src.features import (
    adicionar_medias_moveis,
    calcular_correlacao,
    calcular_tendencia,
    verificar_normalidade,
)
from src.forecasting import (
    avaliar_modelo,
    comparar_modelos,
    prever_proximos_meses,
)
from src.preprocessing import (
    contar_linhas_removidas,
    detectar_meses_faltantes,
    limpar_dados,
    validar_dados,
)
from src.report import gerar_relatorio
from src.timeseries import (
    MINIMO_ADF,
    PERIODO_SAZONAL,
    TREINO_MINIMO,
    decompor_serie,
    prever_holt_winters,
    validar_walk_forward,
    verificar_estacionariedade,
)
from src.visualization import (
    COR_INGENUA,
    COR_REGRESSAO,
    COR_TEXTO,
    grafico_decomposicao,
    grafico_medias_moveis,
    grafico_previsao,
    grafico_receita_despesas,
    grafico_variacao_mensal,
    grafico_walk_forward,
)


def formatar_p(p_valor):
    if p_valor < 0.001:
        return "p < 0,001"
    return f"p = {p_valor:.3f}".replace(".", ",")


def formatar_percentual(valor):
    if pd.isna(valor):
        return "n/d"
    return f"{valor:.2f}%"


st.set_page_config(
    page_title="Lab Financeiro",
    page_icon="📊",
    layout="wide",
)

aplicar_estilo()
exibir_cabecalho(
    "Lab Financeiro",
    "Análise quantitativa de fluxo de caixa",
)

# ---------------------------------------------------------------- Carga
with st.container(border=True):
    st.markdown("**Fonte de dados**")

    col_decimal, col_arquivo = st.columns([1, 3])

    separador_decimal = col_decimal.radio(
        "Separador decimal (CSV)",
        options=[".", ","],
        horizontal=True,
    )

    arquivo = col_arquivo.file_uploader(
        "Carregue uma planilha financeira",
        type=["csv", "xlsx"],
    )

if arquivo is not None:
    try:
        dados_originais = carregar_dados(arquivo, decimal=separador_decimal)
        dados = limpar_dados(dados_originais)

        fonte = f"arquivo enviado ({arquivo.name})"

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

    dados_originais = carregar_dados(caminho_dados)
    dados = limpar_dados(dados_originais)

    fonte = "dados de exemplo (fictícios)"

# A validação roda nos dois casos (upload ou exemplo)
problemas = validar_dados(dados)

if problemas:
    st.warning("Foram encontrados problemas nos dados:")

    for problema in problemas:
        st.write(f"- {problema}")

    st.stop()

# Avisos que não bloqueiam a análise, mas afetam a confiança nos resultados
linhas_removidas = contar_linhas_removidas(dados_originais, dados)

if linhas_removidas > 0:
    st.warning(
        f"{linhas_removidas} linha(s) foram descartadas na limpeza por "
        f"terem data, receita ou despesas ausentes ou inválidas."
    )

meses_faltantes = detectar_meses_faltantes(dados)

if meses_faltantes:
    exibidos = ", ".join(meses_faltantes[:12])
    complemento = "..." if len(meses_faltantes) > 12 else ""

    st.warning(
        f"Há {len(meses_faltantes)} mês(es) ausente(s) na série: "
        f"{exibidos}{complemento}. Os modelos assumem meses consecutivos, "
        f"então as previsões podem ficar distorcidas."
    )

dados, indicadores = calcular_indicadores(dados)
estatisticas = calcular_estatisticas(dados)

st.caption(
    f"Fonte: {fonte} · {len(dados)} meses · "
    f"{dados['data'].min():%m/%Y} a {dados['data'].max():%m/%Y}"
)

(
    aba_geral,
    aba_estatistica,
    aba_previsao,
    aba_series,
    aba_dados,
) = st.tabs([
    "Visão geral",
    "Estatística",
    "Previsão",
    "Séries temporais",
    "Dados e exportação",
])

# ----------------------------------------------------------- Visão geral
with aba_geral:
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
        formatar_percentual(indicadores["margem_media"]),
    )

    st.subheader("Evolução financeira mensal")
    st.pyplot(grafico_receita_despesas(dados))

    st.subheader("Variação mensal da receita")
    st.pyplot(grafico_variacao_mensal(dados))

# ------------------------------------------------------------ Estatística
with aba_estatistica:
    st.subheader("Análise estatística")

    col1, col2, col3 = st.columns(3)

    col1.metric("Receita média", f"R$ {estatisticas['receita_media']:,.2f}")
    col2.metric(
        "Receita mediana",
        f"R$ {estatisticas['receita_mediana']:,.2f}",
    )
    col3.metric(
        "Desvio padrão",
        f"R$ {estatisticas['variabilidade_receita']:,.2f}",
    )

    col4, col5, col6 = st.columns(3)

    col4.metric("Fluxo mínimo", f"R$ {estatisticas['fluxo_minimo']:,.2f}")
    col5.metric("Fluxo máximo", f"R$ {estatisticas['fluxo_maximo']:,.2f}")
    col6.metric(
        "Crescimento da receita",
        formatar_percentual(estatisticas["crescimento_receita"]),
    )

    st.subheader("Análise estatística avançada")

    janela = st.slider(
        "Janela da média móvel (meses)",
        min_value=2,
        max_value=min(6, len(dados)),
        value=3,
    )

    dados_mm = adicionar_medias_moveis(dados, janela=janela)

    st.pyplot(grafico_medias_moveis(dados_mm, janela))

    correlacao = calcular_correlacao(dados)
    tendencia = calcular_tendencia(dados)
    normalidade = verificar_normalidade(dados["fluxo_liquido"])

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Correlação receita × despesas",
        f"{correlacao['correlacao']:.3f}",
    )
    col2.metric(
        "Tendência da receita",
        f"R$ {tendencia['inclinacao']:,.2f} / mês",
    )
    col3.metric("R² da tendência", f"{tendencia['r2']:.3f}")

    if tendencia["significativa"]:
        st.write(
            f"A tendência da receita é estatisticamente significativa "
            f"({formatar_p(tendencia['p_valor'])})."
        )
    else:
        st.write(
            f"Não há evidência estatística de tendência na receita "
            f"({formatar_p(tendencia['p_valor'])})."
        )

    if normalidade["normal"]:
        st.write(
            f"O fluxo líquido não rejeita a normalidade "
            f"(Shapiro-Wilk, {formatar_p(normalidade['p_valor'])})."
        )
    else:
        st.write(
            f"O fluxo líquido se desvia da normalidade "
            f"(Shapiro-Wilk, {formatar_p(normalidade['p_valor'])})."
        )

# --------------------------------------------------------------- Previsão
with aba_previsao:
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

    st.pyplot(grafico_previsao(dados, previsoes))
    st.dataframe(previsoes, use_container_width=True)

    st.subheader("Avaliação do modelo")

    metricas, resultados = avaliar_modelo(dados)

    col1, col2, col3 = st.columns(3)

    col1.metric("MAE", f"R$ {metricas['mae']:,.2f}")
    col2.metric("RMSE", f"R$ {metricas['rmse']:,.2f}")
    col3.metric("MAPE", formatar_percentual(metricas["mape"]))

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
        ],
        color=[COR_TEXTO, COR_REGRESSAO, COR_INGENUA],
    )

# -------------------------------------------------------- Séries temporais
with aba_series:
    st.subheader("Estacionariedade da receita (teste ADF)")

    if len(dados) > MINIMO_ADF:
        adf_nivel = verificar_estacionariedade(dados["receita"])
        adf_diferenca = verificar_estacionariedade(
            dados["receita"].diff().dropna()
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "ADF - receita original",
            formatar_p(adf_nivel["p_valor"]),
        )
        col1.caption(
            "Estacionária"
            if adf_nivel["estacionaria"]
            else "Não estacionária"
        )

        col2.metric(
            "ADF - receita diferenciada",
            formatar_p(adf_diferenca["p_valor"]),
        )
        col2.caption(
            "Estacionária"
            if adf_diferenca["estacionaria"]
            else "Não estacionária"
        )
    else:
        st.info(
            f"O teste ADF exige mais de {MINIMO_ADF} registros "
            f"para dar um resultado confiável."
        )

    st.subheader("Decomposição: tendência e sazonalidade")

    if len(dados) >= 2 * PERIODO_SAZONAL:
        st.pyplot(grafico_decomposicao(decompor_serie(dados)))
    else:
        st.info(
            f"A decomposição sazonal exige pelo menos "
            f"{2 * PERIODO_SAZONAL} meses de dados "
            f"(dois ciclos completos)."
        )

    st.subheader("Previsão com Holt-Winters x regressão linear")

    previsoes_hw = prever_holt_winters(dados, meses_futuros=meses_futuros)

    st.pyplot(grafico_previsao(dados, previsoes, previsoes_hw))

    st.subheader("Validação walk-forward (um mês à frente)")

    if len(dados) > TREINO_MINIMO:
        metricas_wf, tabela_wf = validar_walk_forward(dados)

        st.dataframe(
            pd.DataFrame(metricas_wf).T.round(2),
            use_container_width=True,
        )
        st.pyplot(grafico_walk_forward(tabela_wf))
    else:
        st.info(
            f"A validação walk-forward exige mais de {TREINO_MINIMO} "
            f"registros."
        )

# ---------------------------------------------------- Dados e exportação
with aba_dados:
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
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    st.subheader("Relatório gerencial")

    relatorio = gerar_relatorio(
        indicadores["receita_total"],
        indicadores["despesas_totais"],
    )

    st.text(relatorio)
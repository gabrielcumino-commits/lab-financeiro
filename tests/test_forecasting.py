
import pandas as pd

from src.forecasting import avaliar_modelo, prever_proximos_meses


def criar_dados_teste():
    return pd.DataFrame({
        "data": pd.date_range(
            "2026-01-01",
            periods=6,
            freq="MS",
        ),
        "receita": [1000, 1100, 1200, 1300, 1400, 1500],
    })


def test_avaliar_modelo():
    dados = criar_dados_teste()

    metricas, resultados = avaliar_modelo(dados)

    assert metricas["mae"] >= 0
    assert metricas["rmse"] >= 0
    assert len(resultados) == 2


def test_prever_proximos_meses():
    dados = criar_dados_teste()

    previsoes = prever_proximos_meses(dados, meses_futuros=3)

    assert len(previsoes) == 3
    assert previsoes["receita_prevista"].notna().all()
    assert previsoes["data"].iloc[0] == pd.Timestamp("2026-07-01")





from src.forecasting import comparar_modelos


def test_comparar_modelos():
    dados = criar_dados_teste()

    metricas, comparacao = comparar_modelos(dados)

    assert metricas["mae_regressao"] >= 0
    assert metricas["mae_ingenua"] >= 0
    assert len(comparacao) == 2
    assert "regressao_linear" in comparacao.columns
    assert "previsao_ingenua" in comparacao.columns

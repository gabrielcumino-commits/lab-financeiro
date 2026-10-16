import numpy as np
import pandas as pd
import pytest

from src.timeseries import (
    decompor_serie,
    prever_holt_winters,
    validar_walk_forward,
    verificar_estacionariedade,
)


def criar_dados(receitas):
    return pd.DataFrame({
        "data": pd.date_range("2026-01-01", periods=len(receitas), freq="MS"),
        "receita": receitas,
        "despesas": [0] * len(receitas),
    })


def serie_linear(n=10):
    return criar_dados([1000 + 100 * i for i in range(n)])


def test_decomposicao_com_24_meses():
    sazonal = np.tile([0, 50, -30, 20, 0, 10, -20, 40, 0, -10, 30, 5], 2)
    dados = criar_dados(1000 + np.arange(24) * 100 + sazonal)

    resultado = decompor_serie(dados)

    assert list(resultado.columns) == [
        "observado", "tendencia", "sazonalidade", "residuo",
    ]
    assert len(resultado) == 24


def test_decomposicao_com_poucos_dados_gera_erro():
    with pytest.raises(ValueError):
        decompor_serie(serie_linear(10))


def test_ruido_branco_e_estacionario():
    ruido = np.random.default_rng(42).normal(0, 1, 60)

    assert verificar_estacionariedade(ruido)["estacionaria"] is True


def test_tendencia_forte_nao_e_estacionaria():
    ruido = np.random.default_rng(1).normal(0, 1, 40)
    serie = np.arange(40) * 5 + ruido

    assert verificar_estacionariedade(serie)["estacionaria"] is False


def test_estacionariedade_poucos_valores_gera_erro():
    with pytest.raises(ValueError):
        verificar_estacionariedade([1, 2, 3])


def test_holt_winters_segue_tendencia_linear():
    previsoes = prever_holt_winters(serie_linear(10), meses_futuros=3)

    assert len(previsoes) == 3
    assert previsoes["data"].iloc[0] == pd.Timestamp("2026-11-01")
    assert previsoes["receita_prevista"].iloc[0] == pytest.approx(2000, rel=0.05)


def test_holt_winters_meses_invalidos():
    with pytest.raises(ValueError):
        prever_holt_winters(serie_linear(10), meses_futuros=0)


def test_walk_forward_estrutura():
    metricas, tabela = validar_walk_forward(serie_linear(10), treino_minimo=6)

    assert len(tabela) == 4
    assert set(metricas) == {"ingenua", "regressao_linear", "holt_winters"}
    assert {"mae", "rmse", "mape"} <= set(metricas["holt_winters"])


def test_walk_forward_tendencia_vence_previsao_ingenua():
    metricas, _ = validar_walk_forward(serie_linear(12), treino_minimo=6)

    assert metricas["regressao_linear"]["mae"] < metricas["ingenua"]["mae"]
    assert metricas["holt_winters"]["mae"] < metricas["ingenua"]["mae"]


def test_walk_forward_dados_insuficientes():
    with pytest.raises(ValueError):
        validar_walk_forward(serie_linear(6), treino_minimo=6)
import math

import pandas as pd
import pytest

from src.features import (
    adicionar_medias_moveis,
    calcular_correlacao,
    calcular_tendencia,
    verificar_normalidade,
)


def criar_dados(receita, despesas):
    return pd.DataFrame({
        "data": pd.date_range("2026-01-01", periods=len(receita), freq="MS"),
        "receita": receita,
        "despesas": despesas,
    })


def test_media_movel_de_3_meses():
    dados = criar_dados([1000, 2000, 3000, 4000], [100, 200, 300, 400])

    resultado = adicionar_medias_moveis(dados, janela=3)

    assert math.isnan(resultado["receita_mm"].iloc[0])
    assert resultado["receita_mm"].iloc[2] == 2000
    assert resultado["receita_mm"].iloc[3] == 3000
    assert resultado["despesas_mm"].iloc[3] == 300


def test_media_movel_janela_invalida():
    dados = criar_dados([1, 2, 3, 4], [1, 2, 3, 4])

    with pytest.raises(ValueError):
        adicionar_medias_moveis(dados, janela=1)


def test_correlacao_perfeita_positiva():
    dados = criar_dados([1000, 2000, 3000, 4000], [500, 1000, 1500, 2000])

    resultado = calcular_correlacao(dados)

    assert resultado["correlacao"] == pytest.approx(1)


def test_correlacao_perfeita_negativa():
    dados = criar_dados([1000, 2000, 3000, 4000], [2000, 1500, 1000, 500])

    resultado = calcular_correlacao(dados)

    assert resultado["correlacao"] == pytest.approx(-1)


def test_correlacao_serie_constante_retorna_nan():
    dados = criar_dados([1000, 1000, 1000, 1000], [500, 600, 700, 800])

    resultado = calcular_correlacao(dados)

    assert math.isnan(resultado["correlacao"])
    assert resultado["significativa"] is False


def test_tendencia_linear_exata():
    dados = criar_dados([1000, 1100, 1200, 1300], [0, 0, 0, 0])

    resultado = calcular_tendencia(dados)

    assert resultado["inclinacao"] == pytest.approx(100)
    assert resultado["intercepto"] == pytest.approx(1000)
    assert resultado["r2"] == pytest.approx(1)


def test_tendencia_sem_crescimento_nao_e_significativa():
    dados = criar_dados([1000, 1200, 1000, 1200, 1000, 1200], [0] * 6)

    resultado = calcular_tendencia(dados)

    assert resultado["significativa"] is False


def test_normalidade_retorna_p_valor_valido():
    resultado = verificar_normalidade([10, 12, 11, 13, 12, 11, 10, 14])

    assert 0 <= resultado["p_valor"] <= 1
    assert isinstance(resultado["normal"], bool)


def test_normalidade_poucos_valores_gera_erro():
    with pytest.raises(ValueError):
        verificar_normalidade([1, 2])
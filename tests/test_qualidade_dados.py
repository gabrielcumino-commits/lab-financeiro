import math

import pandas as pd

from src.analysis import calcular_estatisticas, calcular_indicadores
from src.preprocessing import (
    contar_linhas_removidas,
    detectar_meses_faltantes,
    limpar_dados,
)


def criar_dados(datas, receitas):
    return pd.DataFrame({
        "data": pd.to_datetime(datas),
        "receita": receitas,
        "despesas": [100] * len(receitas),
    })


def test_detectar_meses_faltantes():
    dados = criar_dados(
        ["2026-01-01", "2026-02-01", "2026-05-01"],
        [1000, 1100, 1200],
    )

    assert detectar_meses_faltantes(dados) == ["2026-03", "2026-04"]


def test_serie_completa_nao_tem_meses_faltantes():
    dados = criar_dados(
        ["2026-01-01", "2026-02-01", "2026-03-01"],
        [1000, 1100, 1200],
    )

    assert detectar_meses_faltantes(dados) == []


def test_meses_faltantes_em_dados_vazios():
    assert detectar_meses_faltantes(criar_dados([], [])) == []


def test_contar_linhas_removidas():
    originais = pd.DataFrame({
        "data": ["2026-01-01", "texto", "2026-03-01"],
        "receita": [1000, 1100, "abc"],
        "despesas": [700, 800, 900],
    })

    limpos = limpar_dados(originais)

    assert len(limpos) == 1
    assert contar_linhas_removidas(originais, limpos) == 2


def test_margem_com_receita_zero_nao_e_infinita():
    dados = criar_dados(
        ["2026-01-01", "2026-02-01", "2026-03-01"],
        [1000, 0, 2000],
    )

    resultado, indicadores = calcular_indicadores(dados)

    assert math.isnan(resultado["margem_liquida"].iloc[1])
    assert math.isfinite(indicadores["margem_media"])


def test_variacao_apos_receita_zero_e_nan():
    dados = criar_dados(
        ["2026-01-01", "2026-02-01", "2026-03-01"],
        [1000, 0, 2000],
    )

    resultado, _ = calcular_indicadores(dados)

    assert math.isnan(resultado["variacao_receita"].iloc[2])


def test_crescimento_com_primeira_receita_zero():
    dados = pd.DataFrame({
        "receita": [0, 500, 1000],
        "fluxo_liquido": [0, 100, 200],
    })

    assert math.isnan(calcular_estatisticas(dados)["crescimento_receita"])
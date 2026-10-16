import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from src.timeseries import decompor_serie, prever_holt_winters, validar_walk_forward
from src.visualization import (
    grafico_decomposicao,
    grafico_previsao,
    grafico_receita_despesas,
    grafico_walk_forward,
    salvar_figura,
)


def criar_dados(n=10):
    return pd.DataFrame({
        "data": pd.date_range("2026-01-01", periods=n, freq="MS"),
        "receita": [1000 + 100 * i for i in range(n)],
        "despesas": [700 + 50 * i for i in range(n)],
    })


def previsoes_futuras(meses=3):
    return pd.DataFrame({
        "data": pd.date_range("2026-11-01", periods=meses, freq="MS"),
        "receita_prevista": [2000, 2100, 2200][:meses],
    })


def test_grafico_receita_despesas():
    fig = grafico_receita_despesas(criar_dados())

    assert isinstance(fig, Figure)
    assert len(fig.axes[0].lines) == 2


def test_grafico_previsao_com_e_sem_holt_winters():
    dados = criar_dados()
    previsoes = previsoes_futuras()

    sem_hw = grafico_previsao(dados, previsoes)
    com_hw = grafico_previsao(dados, previsoes, prever_holt_winters(dados, 3))

    assert len(sem_hw.axes[0].lines) == 2
    assert len(com_hw.axes[0].lines) == 3


def test_grafico_walk_forward():
    _, tabela = validar_walk_forward(criar_dados())

    fig = grafico_walk_forward(tabela)

    # receita real + 3 modelos
    assert len(fig.axes[0].lines) == 4


def test_grafico_decomposicao_tem_tres_paineis():
    sazonal = np.tile([0, 50, -30, 20, 0, 10, -20, 40, 0, -10, 30, 5], 2)
    dados = criar_dados(24)
    dados["receita"] = 1000 + np.arange(24) * 100 + sazonal

    fig = grafico_decomposicao(decompor_serie(dados))

    assert len(fig.axes) == 3


def test_salvar_figura_cria_pasta_e_arquivo(tmp_path):
    destino = tmp_path / "subpasta" / "grafico.png"

    resultado = salvar_figura(grafico_receita_despesas(criar_dados()), destino)

    assert resultado.exists()
    assert resultado.stat().st_size > 0

import pandas as pd

from src.preprocessing import validar_dados


def test_identificar_receita_negativa():
    dados = pd.DataFrame({
        "data": pd.date_range("2026-01-01", periods=4, freq="MS"),
        "receita": [1000, -200, 1500, 1800],
        "despesas": [700, 800, 900, 1000],
    })

    problemas = validar_dados(dados)

    assert any("receitas negativas" in p for p in problemas)


def test_identificar_datas_duplicadas():
    dados = pd.DataFrame({
        "data": [
            "2026-01-01",
            "2026-01-01",
            "2026-03-01",
            "2026-04-01",
        ],
        "receita": [1000, 1100, 1500, 1800],
        "despesas": [700, 800, 900, 1000],
    })

    dados["data"] = pd.to_datetime(dados["data"])

    problemas = validar_dados(dados)

    assert any("datas duplicadas" in p for p in problemas)

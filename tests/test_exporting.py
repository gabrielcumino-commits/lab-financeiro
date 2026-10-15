
from io import BytesIO

import pandas as pd

from src.exporting import exportar_csv, exportar_excel


def test_exportar_csv():
    dados = pd.DataFrame({
        "receita": [1000, 2000],
        "despesas": [700, 1200],
    })

    resultado = exportar_csv(dados)

    assert isinstance(resultado, bytes)
    assert b"receita" in resultado
    assert b"despesas" in resultado


def test_exportar_excel():
    dados = pd.DataFrame({
        "receita": [1000, 2000],
        "despesas": [700, 1200],
    })

    indicadores = {"receita_total": 3000}

    previsoes = pd.DataFrame({
        "data": pd.to_datetime(["2026-03-01"]),
        "receita_prevista": [2500],
    })

    resultado = exportar_excel(
        dados,
        indicadores,
        previsoes,
    )

    planilha = pd.ExcelFile(BytesIO(resultado))

    assert planilha.sheet_names == [
        "Dados financeiros",
        "Resumo",
        "Previsoes",
    ]

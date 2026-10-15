
import pandas as pd

from src.analysis import calcular_indicadores


def test_calcular_fluxo_liquido():
    dados = pd.DataFrame({
        "data": ["2026-01-01", "2026-02-01"],
        "receita": [1000, 2000],
        "despesas": [700, 1000],
    })

    resultado, indicadores = calcular_indicadores(dados)

    assert resultado["fluxo_liquido"].tolist() == [300, 1000]
    assert indicadores["receita_total"] == 3000
    assert indicadores["despesas_totais"] == 1700
    assert indicadores["fluxo_total"] == 1300
    assert indicadores["margem_media"] == 40



# teste para ver se os calculos estao certos





from src.analysis import calcular_estatisticas


def test_calcular_estatisticas():
    dados = pd.DataFrame({
        "receita": [1000, 2000, 3000],
        "fluxo_liquido": [300, 1000, 1500],
    })

    resultado = calcular_estatisticas(dados)

    assert resultado["receita_media"] == 2000
    assert resultado["receita_mediana"] == 2000
    assert resultado["fluxo_minimo"] == 300
    assert resultado["fluxo_maximo"] == 1500
    assert resultado["crescimento_receita"] == 200

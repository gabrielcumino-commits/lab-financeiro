
import pandas as pd

from src.preprocessing import limpar_dados


def test_remover_linha_com_dados_invalidos():
    dados = pd.DataFrame({
        "data": ["2026-01-01", "data_invalida", "2026-03-01"],
        "receita": [1000, 2000, None],
        "despesas": [700, 1000, 500],
    })

    resultado = limpar_dados(dados)

    assert len(resultado) == 1
    assert resultado.iloc[0]["receita"] == 1000
    assert resultado.iloc[0]["despesas"] == 700

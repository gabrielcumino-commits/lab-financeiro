from io import BytesIO

import pandas as pd
import pytest

from src.data_loader import carregar_dados, padronizar_colunas


def test_padronizar_colunas_com_sinonimos_e_acentos():
    dados = pd.DataFrame(columns=[" Mês ", "Faturamento", "Custos"])

    resultado = padronizar_colunas(dados)

    assert list(resultado.columns) == ["data", "receita", "despesas"]


def test_carregar_csv_com_ponto_e_virgula():
    csv = "data;receita;despesas\n2026-01-01;1000;700\n2026-02-01;1100;800\n"

    resultado = carregar_dados(BytesIO(csv.encode("utf-8")), nome="x.csv")

    assert list(resultado.columns) == ["data", "receita", "despesas"]
    assert len(resultado) == 2


def test_carregar_csv_latin1_com_virgula_decimal():
    csv = "Período;Receita;Despesas\n2026-01-01;1000,50;700,25\n"

    resultado = carregar_dados(
        BytesIO(csv.encode("latin-1")), nome="x.csv", decimal=","
    )

    assert resultado["receita"].iloc[0] == 1000.50


def test_formato_nao_suportado():
    with pytest.raises(ValueError):
        carregar_dados(BytesIO(b"abc"), nome="dados.txt")


def test_carregar_csv_com_linha_em_branco_no_inicio():
    csv = "\ndata,receita,despesas\n2026-01-01,1000,700\n2026-02-01,1100,800\n"

    resultado = carregar_dados(BytesIO(csv.encode("utf-8")), nome="x.csv")

    assert len(resultado) == 2
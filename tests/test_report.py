
from src.report import gerar_relatorio


def test_relatorio_positivo():
    resultado = gerar_relatorio(10000, 7000)

    assert "positivo" in resultado
    assert "3000.00" in resultado


def test_relatorio_negativo():
    resultado = gerar_relatorio(5000, 7000)

    assert "negativo" in resultado
    assert "-2000.00" in resultado


def test_relatorio_equilibrado():
    resultado = gerar_relatorio(5000, 5000)

    assert "equilibrado" in resultado
    assert "0.00" in resultado


import pandas as pd


def calcular_indicadores(dados):
    dados = dados.copy()

    dados["data"] = pd.to_datetime(dados["data"])
    dados["fluxo_liquido"] = dados["receita"] - dados["despesas"]

    dados["margem_liquida"] = (
        dados["fluxo_liquido"] / dados["receita"]
    ) * 100

    indicadores = {
        "receita_total": dados["receita"].sum(),
        "despesas_totais": dados["despesas"].sum(),
        "fluxo_total": dados["fluxo_liquido"].sum(),
        "margem_media": dados["margem_liquida"].mean(),
    }

    return dados, indicadores

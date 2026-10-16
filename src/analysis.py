import numpy as np
import pandas as pd


def calcular_indicadores(dados):
    dados = dados.copy()

    dados["data"] = pd.to_datetime(dados["data"])
    dados["fluxo_liquido"] = dados["receita"] - dados["despesas"]

    # Receita zero deixa a margem indefinida (NaN) em vez de infinita
    receita_valida = dados["receita"].where(dados["receita"] != 0)

    dados["margem_liquida"] = (
        dados["fluxo_liquido"] / receita_valida
    ) * 100

    # Mês anterior com receita zero também gera infinito: vira NaN
    variacao = dados["receita"].pct_change() * 100
    dados["variacao_receita"] = variacao.replace([np.inf, -np.inf], np.nan)

    indicadores = {
        "receita_total": dados["receita"].sum(),
        "despesas_totais": dados["despesas"].sum(),
        "fluxo_total": dados["fluxo_liquido"].sum(),
        "margem_media": dados["margem_liquida"].mean(),
    }

    return dados, indicadores


def calcular_estatisticas(dados):
    receita = dados["receita"]
    fluxo = dados["fluxo_liquido"]

    primeira_receita = receita.iloc[0]

    if primeira_receita == 0:
        crescimento_receita = float("nan")
    else:
        crescimento_receita = (
            (receita.iloc[-1] / primeira_receita) - 1
        ) * 100

    estatisticas = {
        "receita_media": receita.mean(),
        "receita_mediana": receita.median(),
        "variabilidade_receita": receita.std(),
        "fluxo_minimo": fluxo.min(),
        "fluxo_maximo": fluxo.max(),
        "crescimento_receita": crescimento_receita,
    }

    return estatisticas
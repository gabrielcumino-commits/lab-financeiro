
import pandas as pd


def calcular_indicadores(dados):
    dados = dados.copy()

    dados["data"] = pd.to_datetime(dados["data"])
    dados["fluxo_liquido"] = dados["receita"] - dados["despesas"]

    dados["margem_liquida"] = (
        dados["fluxo_liquido"] / dados["receita"]
    ) * 100

    dados["variacao_receita"] = dados["receita"].pct_change() * 100

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

    crescimento_receita = (
        (receita.iloc[-1] / receita.iloc[0]) - 1
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

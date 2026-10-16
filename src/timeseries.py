import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

from src.evaluation import calcular_metricas

PERIODO_SAZONAL = 12  # dados mensais -> ciclo de 12 meses
MINIMO_ADF = 8
TREINO_MINIMO = 6
NIVEL_SIGNIFICANCIA = 0.05


def decompor_serie(dados, periodo=PERIODO_SAZONAL):
    """
    Separa a receita em tendência, sazonalidade e resíduo (modelo aditivo).
    Exige pelo menos dois ciclos completos (24 meses para dados mensais).
    """
    dados = dados.sort_values("data").reset_index(drop=True)

    if len(dados) < 2 * periodo:
        raise ValueError(
            f"A decomposição exige pelo menos {2 * periodo} registros."
        )

    serie = pd.Series(
        dados["receita"].to_numpy(dtype=float),
        index=pd.to_datetime(dados["data"]),
    )

    resultado = seasonal_decompose(serie, model="additive", period=periodo)

    return pd.DataFrame({
        "observado": resultado.observed,
        "tendencia": resultado.trend,
        "sazonalidade": resultado.seasonal,
        "residuo": resultado.resid,
    })


def verificar_estacionariedade(serie):
    """
    Teste ADF (Dickey-Fuller aumentado).
    Hipótese nula: a série tem raiz unitária (NÃO é estacionária).
    p-valor abaixo de 0,05 -> a série é estacionária.
    """
    valores = np.asarray(serie, dtype=float)

    if len(valores) < MINIMO_ADF:
        raise ValueError(
            f"O teste ADF exige pelo menos {MINIMO_ADF} observações."
        )

    if np.std(valores) == 0:
        return {
            "estatistica": float("nan"),
            "p_valor": float("nan"),
            "estacionaria": False,
        }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        estatistica, p_valor = adfuller(valores, autolag="AIC")[:2]

    return {
        "estatistica": float(estatistica),
        "p_valor": float(p_valor),
        "estacionaria": bool(p_valor < NIVEL_SIGNIFICANCIA),
    }


def _prever_ingenua(treino, passos):
    return np.repeat(treino[-1], passos)


def _prever_regressao(treino, passos):
    X = np.arange(len(treino)).reshape(-1, 1)
    X_futuro = np.arange(len(treino), len(treino) + passos).reshape(-1, 1)

    modelo = LinearRegression().fit(X, treino)

    return modelo.predict(X_futuro)


def _prever_holt(treino, passos):
    """Suavização exponencial com tendência (e sazonalidade se houver 24+ meses)."""
    sazonal = len(treino) >= 2 * PERIODO_SAZONAL

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        modelo = ExponentialSmoothing(
            treino,
            trend="add",
            seasonal="add" if sazonal else None,
            seasonal_periods=PERIODO_SAZONAL if sazonal else None,
            initialization_method="estimated",
        ).fit()

    return np.asarray(modelo.forecast(passos))


MODELOS = {
    "ingenua": _prever_ingenua,
    "regressao_linear": _prever_regressao,
    "holt_winters": _prever_holt,
}


def prever_holt_winters(dados, meses_futuros=3):
    """Previsão de receita futura com suavização exponencial (Holt-Winters)."""
    dados = dados.sort_values("data").reset_index(drop=True)

    if len(dados) < 4:
        raise ValueError("São necessários pelo menos 4 registros.")

    if meses_futuros < 1:
        raise ValueError("A quantidade de meses deve ser positiva.")

    receitas = dados["receita"].to_numpy(dtype=float)
    previstas = _prever_holt(receitas, meses_futuros)

    datas_futuras = pd.date_range(
        start=pd.to_datetime(dados["data"].iloc[-1]) + pd.DateOffset(months=1),
        periods=meses_futuros,
        freq="MS",
    )

    return pd.DataFrame({
        "data": datas_futuras,
        "receita_prevista": np.clip(previstas, 0, None),
    })


def validar_walk_forward(dados, treino_minimo=TREINO_MINIMO):
    """
    Validação walk-forward: para cada mês a partir de `treino_minimo`,
    treina só com o passado, prevê o mês seguinte e compara com o real.
    É mais confiável que um único corte treino/teste.
    """
    dados = dados.sort_values("data").reset_index(drop=True)

    receitas = dados["receita"].to_numpy(dtype=float)
    total = len(receitas)

    if treino_minimo < 3 or total <= treino_minimo:
        raise ValueError("Quantidade insuficiente de dados para validação.")

    reais = []
    previsoes = {nome: [] for nome in MODELOS}

    for t in range(treino_minimo, total):
        treino = receitas[:t]
        reais.append(receitas[t])

        for nome, funcao in MODELOS.items():
            previsoes[nome].append(float(funcao(treino, 1)[0]))

    tabela = pd.DataFrame({
        "data": pd.to_datetime(dados["data"].iloc[treino_minimo:]).to_numpy(),
        "receita_real": reais,
        **previsoes,
    })

    metricas = {
        nome: calcular_metricas(reais, previsoes[nome])
        for nome in MODELOS
    }

    return metricas, tabela
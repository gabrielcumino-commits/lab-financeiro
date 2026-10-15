
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def avaliar_modelo(dados, meses_teste=2):
    dados = dados.sort_values("data").reset_index(drop=True)

    if len(dados) <= meses_teste or meses_teste < 1:
        raise ValueError("Quantidade insuficiente de dados para avaliação.")

    dados["data"] = pd.to_datetime(dados["data"])

    X = np.arange(len(dados)).reshape(-1, 1)
    y = dados["receita"].to_numpy()

    X_treino = X[:-meses_teste]
    y_treino = y[:-meses_teste]

    X_teste = X[-meses_teste:]
    y_teste = y[-meses_teste:]

    modelo = LinearRegression()
    modelo.fit(X_treino, y_treino)

    previsoes = modelo.predict(X_teste)

    metricas = {
        "mae": mean_absolute_error(y_teste, previsoes),
        "rmse": np.sqrt(mean_squared_error(y_teste, previsoes)),
    }

    resultados = pd.DataFrame({
        "receita_real": y_teste,
        "receita_prevista": previsoes,
    })

    return metricas, resultados


def prever_proximos_meses(dados, meses_futuros=3):
    dados = dados.sort_values("data").reset_index(drop=True).copy()

    if len(dados) < 2:
        raise ValueError("São necessários pelo menos dois meses de dados.")

    if meses_futuros < 1:
        raise ValueError("A quantidade de meses deve ser positiva.")

    dados["data"] = pd.to_datetime(dados["data"])

    X = np.arange(len(dados)).reshape(-1, 1)
    y = dados["receita"].to_numpy()

    modelo = LinearRegression()
    modelo.fit(X, y)

    X_futuro = np.arange(
        len(dados),
        len(dados) + meses_futuros
    ).reshape(-1, 1)

    receitas_previstas = modelo.predict(X_futuro)

    datas_futuras = pd.date_range(
        start=dados["data"].iloc[-1] + pd.DateOffset(months=1),
        periods=meses_futuros,
        freq="MS",
    )

    previsoes = pd.DataFrame({
        "data": datas_futuras,
        "receita_prevista": receitas_previstas,
    })

    previsoes["receita_prevista"] = (
        previsoes["receita_prevista"].clip(lower=0)
    )

    return previsoes






def comparar_modelos(dados, meses_teste=2):
    dados = dados.sort_values("data").reset_index(drop=True)

    if len(dados) <= meses_teste or meses_teste < 1:
        raise ValueError("Quantidade insuficiente de dados para avaliação.")

    receitas = dados["receita"].to_numpy()

    treino = receitas[:-meses_teste]
    reais = receitas[-meses_teste:]

    X_treino = np.arange(len(treino)).reshape(-1, 1)
    X_teste = np.arange(
        len(treino),
        len(treino) + meses_teste,
    ).reshape(-1, 1)

    modelo = LinearRegression()
    modelo.fit(X_treino, treino)

    previsao_regressao = modelo.predict(X_teste)

    previsao_ingenua = np.repeat(treino[-1], meses_teste)

    comparacao = pd.DataFrame({
        "receita_real": reais,
        "regressao_linear": previsao_regressao,
        "previsao_ingenua": previsao_ingenua,
    })

    metricas = {
        "mae_regressao": mean_absolute_error(
            reais, previsao_regressao
        ),
        "mae_ingenua": mean_absolute_error(
            reais, previsao_ingenua
        ),
    }

    return metricas, comparacao

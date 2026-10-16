import numpy as np


def _preparar(reais, previstos):
    reais = np.asarray(reais, dtype=float)
    previstos = np.asarray(previstos, dtype=float)

    if reais.shape != previstos.shape:
        raise ValueError(
            "Valores reais e previstos precisam ter o mesmo tamanho."
        )

    if reais.size == 0:
        raise ValueError("Não há valores para avaliar.")

    return reais, previstos


def mae(reais, previstos):
    """Erro absoluto médio: quanto o modelo erra, em R$, em média."""
    reais, previstos = _preparar(reais, previstos)
    return float(np.mean(np.abs(reais - previstos)))


def rmse(reais, previstos):
    """Raiz do erro quadrático médio: como o MAE, mas pune erros grandes."""
    reais, previstos = _preparar(reais, previstos)
    return float(np.sqrt(np.mean((reais - previstos) ** 2)))


def mape(reais, previstos):
    """
    Erro percentual absoluto médio, em %.
    Ignora meses com valor real igual a zero (divisão impossível).
    Retorna NaN se todos os valores reais forem zero.
    """
    reais, previstos = _preparar(reais, previstos)

    validos = reais != 0

    if not validos.any():
        return float("nan")

    erros = np.abs((reais[validos] - previstos[validos]) / reais[validos])

    return float(np.mean(erros) * 100)


def calcular_metricas(reais, previstos):
    return {
        "mae": mae(reais, previstos),
        "rmse": rmse(reais, previstos),
        "mape": mape(reais, previstos),
    }
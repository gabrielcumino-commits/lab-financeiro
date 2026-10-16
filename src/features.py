import numpy as np
import statsmodels.api as sm
from scipy import stats

NIVEL_SIGNIFICANCIA = 0.05


def adicionar_medias_moveis(dados, janela=3):
    """Acrescenta receita_mm e despesas_mm (médias móveis) ao DataFrame."""
    if janela < 2:
        raise ValueError("A janela da média móvel deve ser de pelo menos 2.")

    dados = dados.copy()

    dados["receita_mm"] = dados["receita"].rolling(window=janela).mean()
    dados["despesas_mm"] = dados["despesas"].rolling(window=janela).mean()

    return dados


def calcular_correlacao(dados):
    """Correlação de Pearson entre receita e despesas, com p-valor."""
    if len(dados) < 3:
        raise ValueError("São necessários pelo menos 3 registros.")

    receita = dados["receita"].to_numpy(dtype=float)
    despesas = dados["despesas"].to_numpy(dtype=float)

    # Série constante não tem correlação definida
    if np.std(receita) == 0 or np.std(despesas) == 0:
        return {
            "correlacao": float("nan"),
            "p_valor": float("nan"),
            "significativa": False,
        }

    correlacao, p_valor = stats.pearsonr(receita, despesas)

    return {
        "correlacao": float(correlacao),
        "p_valor": float(p_valor),
        "significativa": bool(p_valor < NIVEL_SIGNIFICANCIA),
    }


def verificar_normalidade(serie):
    """
    Teste de Shapiro-Wilk. Hipótese nula: os dados seguem distribuição normal.
    p-valor acima de 0,05 -> não há evidência contra a normalidade.
    """
    valores = np.asarray(serie, dtype=float)

    if len(valores) < 3:
        raise ValueError("São necessários pelo menos 3 valores.")

    if np.std(valores) == 0:
        return {
            "estatistica": float("nan"),
            "p_valor": float("nan"),
            "normal": False,
        }

    estatistica, p_valor = stats.shapiro(valores)

    return {
        "estatistica": float(estatistica),
        "p_valor": float(p_valor),
        "normal": bool(p_valor > NIVEL_SIGNIFICANCIA),
    }


def calcular_tendencia(dados):
    """
    Regressão linear simples da receita contra o tempo (OLS).
    Hipótese nula: a inclinação é zero (receita sem tendência).
    """
    dados = dados.sort_values("data").reset_index(drop=True)

    if len(dados) < 3:
        raise ValueError("São necessários pelo menos 3 registros.")

    tempo = np.arange(len(dados))
    receita = dados["receita"].to_numpy(dtype=float)

    modelo = sm.OLS(receita, sm.add_constant(tempo)).fit()

    return {
        "inclinacao": float(modelo.params[1]),
        "intercepto": float(modelo.params[0]),
        "r2": float(modelo.rsquared),
        "p_valor": float(modelo.pvalues[1]),
        "significativa": bool(modelo.pvalues[1] < NIVEL_SIGNIFICANCIA),
    }
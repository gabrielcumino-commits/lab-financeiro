import math

import pytest
from sklearn.metrics import mean_absolute_error

from src.evaluation import calcular_metricas, mae, mape, rmse

REAIS = [100, 200]
PREVISTOS = [110, 180]


def test_mae_calculo_manual():
    # erros: 10 e 20 -> média 15
    assert mae(REAIS, PREVISTOS) == 15


def test_rmse_calculo_manual():
    # raiz de (10^2 + 20^2) / 2 = raiz de 250
    assert rmse(REAIS, PREVISTOS) == pytest.approx(math.sqrt(250))


def test_mape_calculo_manual():
    # erros percentuais: 10% e 10% -> média 10%
    assert mape(REAIS, PREVISTOS) == pytest.approx(10)


def test_previsao_perfeita_tem_erro_zero():
    metricas = calcular_metricas([100, 200, 300], [100, 200, 300])

    assert metricas == {"mae": 0, "rmse": 0, "mape": 0}


def test_mae_igual_ao_do_scikit_learn():
    reais = [1000, 1100, 1250, 1400]
    previstos = [1010, 1080, 1300, 1350]

    assert mae(reais, previstos) == pytest.approx(
        mean_absolute_error(reais, previstos)
    )


def test_rmse_nunca_menor_que_mae():
    assert rmse(REAIS, PREVISTOS) >= mae(REAIS, PREVISTOS)


def test_mape_ignora_valor_real_zero():
    # o mês com real = 0 é ignorado; sobra só 10%
    assert mape([0, 100], [50, 110]) == pytest.approx(10)


def test_mape_todos_zero_retorna_nan():
    assert math.isnan(mape([0, 0], [10, 20]))


def test_tamanhos_diferentes_geram_erro():
    with pytest.raises(ValueError):
        mae([1, 2, 3], [1, 2])


def test_listas_vazias_geram_erro():
    with pytest.raises(ValueError):
        rmse([], [])
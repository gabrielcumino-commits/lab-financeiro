"""
Gera as figuras do README a partir dos DADOS DE EXEMPLO (data/sample).

Uso, na raiz do projeto:
    py -m scripts.gerar_figuras

Não use dados reais aqui: as imagens ficam versionadas no GitHub.
"""
from pathlib import Path

from src.analysis import calcular_indicadores
from src.data_loader import carregar_dados
from src.forecasting import prever_proximos_meses
from src.preprocessing import limpar_dados
from src.timeseries import (
    PERIODO_SAZONAL,
    decompor_serie,
    prever_holt_winters,
    validar_walk_forward,
)
from src.visualization import (
    grafico_decomposicao,
    grafico_previsao,
    grafico_receita_despesas,
    grafico_walk_forward,
    salvar_figura,
)

RAIZ = Path(__file__).resolve().parent.parent
PASTA_FIGURAS = RAIZ / "reports" / "figures"


def main():
    caminho = RAIZ / "data" / "sample" / "fluxo_financeiro.csv"

    dados = limpar_dados(carregar_dados(caminho))
    dados, _ = calcular_indicadores(dados)

    previsoes = prever_proximos_meses(dados, meses_futuros=3)
    previsoes_hw = prever_holt_winters(dados, meses_futuros=3)
    _, tabela_wf = validar_walk_forward(dados)

    figuras = {
        "receita_despesas.png": grafico_receita_despesas(dados),
        "previsao.png": grafico_previsao(dados, previsoes, previsoes_hw),
        "walk_forward.png": grafico_walk_forward(tabela_wf),
    }

    if len(dados) >= 2 * PERIODO_SAZONAL:
        figuras["decomposicao.png"] = grafico_decomposicao(
            decompor_serie(dados)
        )
    else:
        print("Decomposição ignorada: são necessários 24 meses de dados.")

    for nome, figura in figuras.items():
        destino = salvar_figura(figura, PASTA_FIGURAS / nome)
        print(f"Figura salva: {destino}")


if __name__ == "__main__":
    main()
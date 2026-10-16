from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

COR_RECEITA = "#1f77b4"
COR_DESPESAS = "#d62728"
COR_REGRESSAO = "#2ca02c"
COR_HOLT = "#ff7f0e"
COR_INGENUA = "#7f7f7f"

NOMES_MODELOS = {
    "ingenua": ("Previsão ingênua", COR_INGENUA),
    "regressao_linear": ("Regressão linear", COR_REGRESSAO),
    "holt_winters": ("Holt-Winters", COR_HOLT),
}


def _formatar_reais(valor, _posicao=None):
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


def _formatar_eixos(ax, titulo):
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(FuncFormatter(_formatar_reais))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.grid(alpha=0.3)


def grafico_receita_despesas(dados):
    """Evolução mensal da receita e das despesas; a área entre elas é o fluxo líquido."""
    dados = dados.sort_values("data")

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        dados["data"], dados["receita"],
        marker="o", color=COR_RECEITA, label="Receita",
    )
    ax.plot(
        dados["data"], dados["despesas"],
        marker="o", color=COR_DESPESAS, label="Despesas",
    )
    ax.fill_between(
        dados["data"], dados["despesas"], dados["receita"],
        color=COR_RECEITA, alpha=0.12, label="Fluxo líquido",
    )

    _formatar_eixos(ax, "Receita e despesas mensais")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def grafico_previsao(dados, previsoes, previsoes_hw=None):
    """Histórico de receita com a previsão futura (e, opcionalmente, o Holt-Winters)."""
    dados = dados.sort_values("data")

    ultima_data = dados["data"].iloc[-1]
    ultimo_valor = dados["receita"].iloc[-1]

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        dados["data"], dados["receita"],
        marker="o", color=COR_RECEITA, label="Receita real",
    )

    def tracar(tabela, cor, rotulo, largura, transparencia):
        # começa no último ponto real para a linha ficar contínua
        datas = [ultima_data] + list(tabela["data"])
        valores = [ultimo_valor] + list(tabela["receita_prevista"])
        ax.plot(
            datas, valores,
            linestyle="--", marker="o", color=cor, label=rotulo,
            linewidth=largura, alpha=transparencia,
        )

    # a regressão fica mais grossa e translúcida: se o Holt-Winters
    # coincidir com ela, as duas linhas continuam visíveis
    tracar(previsoes, COR_REGRESSAO, "Previsão (regressão linear)", 5, 0.5)

    if previsoes_hw is not None:
        tracar(previsoes_hw, COR_HOLT, "Previsão (Holt-Winters)", 1.5, 1)

    _formatar_eixos(ax, "Previsão de receita")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def grafico_walk_forward(tabela):
    """Receita real contra a previsão de cada modelo, mês a mês."""
    tabela = tabela.sort_values("data")

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        tabela["data"], tabela["receita_real"],
        marker="o", color="black", linewidth=2, label="Receita real",
    )

    for coluna, (rotulo, cor) in NOMES_MODELOS.items():
        if coluna in tabela.columns:
            ax.plot(
                tabela["data"], tabela[coluna],
                linestyle="--", marker="o", color=cor, label=rotulo,
            )

    _formatar_eixos(ax, "Validação walk-forward (previsão um mês à frente)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def grafico_decomposicao(decomposicao):
    """Três painéis: série e tendência, sazonalidade e resíduo."""
    fig = Figure(figsize=(10, 8))
    topo, meio, base = fig.subplots(3, 1, sharex=True)

    topo.plot(
        decomposicao.index, decomposicao["observado"],
        color=COR_RECEITA, label="Observado",
    )
    topo.plot(
        decomposicao.index, decomposicao["tendencia"],
        color=COR_HOLT, linewidth=2, label="Tendência",
    )
    _formatar_eixos(topo, "Decomposição da receita")
    topo.legend()

    meio.plot(decomposicao.index, decomposicao["sazonalidade"], color=COR_REGRESSAO)
    _formatar_eixos(meio, "Sazonalidade")

    base.bar(
        decomposicao.index, decomposicao["residuo"],
        width=20, color=COR_INGENUA,
    )
    _formatar_eixos(base, "Resíduo")

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def salvar_figura(fig, caminho):
    """Salva a figura em PNG, criando a pasta se ela não existir."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(caminho, dpi=150, bbox_inches="tight")

    return caminho
from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

# Paleta do projeto (a mesma usada no tema do aplicativo)
COR_RECEITA = "#1F4E79"      # azul marinho
COR_DESPESAS = "#C44E52"     # vermelho
COR_REGRESSAO = "#2A9D8F"    # verde-azulado
COR_HOLT = "#E9A23B"         # âmbar
COR_INGENUA = "#8A94A6"      # cinza
COR_POSITIVO = "#2A9D8F"
COR_TEXTO = "#1B2B3A"
COR_TEXTO_SUAVE = "#5B6B7F"
COR_BORDA = "#C9D1DB"

NOMES_MODELOS = {
    "ingenua": ("Previsão ingênua", COR_INGENUA),
    "regressao_linear": ("Regressão linear", COR_REGRESSAO),
    "holt_winters": ("Holt-Winters", COR_HOLT),
}


def _formatar_reais(valor, _posicao=None):
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


def _formatar_percentual(valor, _posicao=None):
    return f"{valor:.0f}%"


def _formatar_eixos(ax, titulo, percentual=False):
    ax.set_title(
        titulo,
        fontsize=13,
        fontweight="bold",
        loc="left",
        color=COR_TEXTO,
        pad=12,
    )

    formato = _formatar_percentual if percentual else _formatar_reais
    ax.yaxis.set_major_formatter(FuncFormatter(formato))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(COR_BORDA)

    ax.tick_params(colors=COR_TEXTO_SUAVE)


def _finalizar(fig, ax):
    ax.legend(frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def grafico_receita_despesas(dados):
    """Evolução mensal da receita e das despesas; a área entre elas é o fluxo líquido."""
    dados = dados.sort_values("data")

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        dados["data"], dados["receita"],
        marker="o", color=COR_RECEITA, linewidth=2.2, label="Receita",
    )
    ax.plot(
        dados["data"], dados["despesas"],
        marker="o", color=COR_DESPESAS, linewidth=2.2, label="Despesas",
    )
    ax.fill_between(
        dados["data"], dados["despesas"], dados["receita"],
        color=COR_RECEITA, alpha=0.10, label="Fluxo líquido",
    )

    _formatar_eixos(ax, "Receita e despesas mensais")

    return _finalizar(fig, ax)


def grafico_variacao_mensal(dados):
    """Variação percentual da receita mês a mês (verde = alta, vermelho = queda)."""
    dados = dados.sort_values("data").dropna(subset=["variacao_receita"])

    cores = [
        COR_POSITIVO if valor >= 0 else COR_DESPESAS
        for valor in dados["variacao_receita"]
    ]

    fig = Figure(figsize=(10, 3.8))
    ax = fig.subplots()

    ax.bar(dados["data"], dados["variacao_receita"], width=20, color=cores)
    ax.axhline(0, color=COR_BORDA, linewidth=1)

    _formatar_eixos(ax, "Variação mensal da receita", percentual=True)

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def grafico_medias_moveis(dados_mm, janela):
    """Receita e despesas com a média móvel destacada."""
    dados_mm = dados_mm.sort_values("data")

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        dados_mm["data"], dados_mm["receita"],
        color=COR_RECEITA, linewidth=1.5, alpha=0.35,
    )
    ax.plot(
        dados_mm["data"], dados_mm["receita_mm"],
        color=COR_RECEITA, linewidth=3,
        label=f"Receita (média móvel de {janela} meses)",
    )
    ax.plot(
        dados_mm["data"], dados_mm["despesas"],
        color=COR_DESPESAS, linewidth=1.5, alpha=0.35,
    )
    ax.plot(
        dados_mm["data"], dados_mm["despesas_mm"],
        color=COR_DESPESAS, linewidth=3,
        label=f"Despesas (média móvel de {janela} meses)",
    )

    _formatar_eixos(ax, "Médias móveis")

    return _finalizar(fig, ax)


def grafico_previsao(dados, previsoes, previsoes_hw=None):
    """Histórico de receita com a previsão futura (e, opcionalmente, o Holt-Winters)."""
    dados = dados.sort_values("data")

    ultima_data = dados["data"].iloc[-1]
    ultimo_valor = dados["receita"].iloc[-1]

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        dados["data"], dados["receita"],
        marker="o", color=COR_RECEITA, linewidth=2.2, label="Receita real",
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

    return _finalizar(fig, ax)


def grafico_walk_forward(tabela):
    """Receita real contra a previsão de cada modelo, mês a mês."""
    tabela = tabela.sort_values("data")

    fig = Figure(figsize=(10, 4.5))
    ax = fig.subplots()

    ax.plot(
        tabela["data"], tabela["receita_real"],
        marker="o", color=COR_TEXTO, linewidth=2.2, label="Receita real",
    )

    for coluna, (rotulo, cor) in NOMES_MODELOS.items():
        if coluna in tabela.columns:
            ax.plot(
                tabela["data"], tabela[coluna],
                linestyle="--", marker="o", color=cor, label=rotulo,
            )

    _formatar_eixos(ax, "Validação walk-forward (previsão um mês à frente)")

    return _finalizar(fig, ax)


def grafico_decomposicao(decomposicao):
    """Três painéis: série e tendência, sazonalidade e resíduo."""
    fig = Figure(figsize=(10, 8))
    topo, meio, base = fig.subplots(3, 1, sharex=True)

    topo.plot(
        decomposicao.index, decomposicao["observado"],
        color=COR_RECEITA, linewidth=1.8, label="Observado",
    )
    topo.plot(
        decomposicao.index, decomposicao["tendencia"],
        color=COR_HOLT, linewidth=2.5, label="Tendência",
    )
    _formatar_eixos(topo, "Decomposição da receita")
    topo.legend(frameon=False)

    meio.plot(
        decomposicao.index, decomposicao["sazonalidade"],
        color=COR_REGRESSAO, linewidth=1.8,
    )
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
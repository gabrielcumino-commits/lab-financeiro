
def gerar_relatorio(receita_total, despesas_total):
    fluxo_liquido = receita_total - despesas_total

    if fluxo_liquido > 0:
        situacao = "positivo"
    elif fluxo_liquido < 0:
        situacao = "negativo"
    else:
        situacao = "equilibrado"

    relatorio = f"""
RELATÓRIO GERENCIAL FINANCEIRO

Receita total: R$ {receita_total:.2f}
Despesas totais: R$ {despesas_total:.2f}
Fluxo líquido: R$ {fluxo_liquido:.2f}

Situação financeira: {situacao}
"""

    return relatorio

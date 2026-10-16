import pandas as pd

COLUNAS_OBRIGATORIAS = ["data", "receita", "despesas"]


def limpar_dados(dados):
    dados = dados.copy()

    for coluna in COLUNAS_OBRIGATORIAS:
        if coluna not in dados.columns:
            raise ValueError(
                f"Coluna obrigatória ausente: {coluna}"
            )

    dados["data"] = pd.to_datetime(
        dados["data"],
        errors="coerce",
    )

    dados["receita"] = pd.to_numeric(
        dados["receita"],
        errors="coerce",
    )

    dados["despesas"] = pd.to_numeric(
        dados["despesas"],
        errors="coerce",
    )

    dados = dados.dropna(
        subset=COLUNAS_OBRIGATORIAS
    )

    dados = dados.sort_values("data").reset_index(drop=True)

    return dados


def contar_linhas_removidas(dados_originais, dados_limpos):
    """Quantas linhas a limpeza descartou (valores ausentes ou inválidos)."""
    return max(len(dados_originais) - len(dados_limpos), 0)


def detectar_meses_faltantes(dados):
    """
    Lista os meses ("AAAA-MM") que faltam entre o primeiro e o último mês
    da série. Os modelos assumem meses consecutivos.
    """
    if dados.empty:
        return []

    meses = pd.to_datetime(dados["data"]).dt.to_period("M")

    esperados = pd.period_range(meses.min(), meses.max(), freq="M")
    faltantes = esperados.difference(pd.PeriodIndex(meses.unique()))

    return [str(mes) for mes in faltantes]


def validar_dados(dados):
    problemas = []

    for coluna in COLUNAS_OBRIGATORIAS:
        if coluna not in dados.columns:
            problemas.append(
                f"Coluna obrigatória ausente: {coluna}"
            )

    if problemas:
        return problemas

    if dados.empty:
        problemas.append("A planilha não possui registros válidos.")
        return problemas

    if dados["data"].duplicated().any():
        problemas.append(
            "Existem datas duplicadas na planilha."
        )

    if (dados["receita"] < 0).any():
        problemas.append(
            "Existem receitas negativas que precisam ser verificadas."
        )

    if (dados["despesas"] < 0).any():
        problemas.append(
            "Existem despesas negativas que precisam ser verificadas."
        )

    if len(dados) < 4:
        problemas.append(
            "Existem menos de 4 registros para a análise."
        )

    return problemas
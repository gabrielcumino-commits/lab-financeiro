
import pandas as pd


def limpar_dados(dados):
    dados = dados.copy()

    colunas_obrigatorias = ["data", "receita", "despesas"]

    for coluna in colunas_obrigatorias:
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
        subset=colunas_obrigatorias
    )

    dados = dados.sort_values("data").reset_index(drop=True)

    return dados


def validar_dados(dados):
    problemas = []

    colunas_obrigatorias = ["data", "receita", "despesas"]

    for coluna in colunas_obrigatorias:
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



# teste de validaçao dos dados financeiros
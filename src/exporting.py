
from io import BytesIO

import pandas as pd


def exportar_csv(dados):
    return dados.to_csv(index=False).encode("utf-8-sig")


def exportar_excel(dados, indicadores, previsoes):
    arquivo = BytesIO()

    resumo = pd.DataFrame(
        list(indicadores.items()),
        columns=["Indicador", "Valor"],
    )

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        dados.to_excel(
            writer,
            sheet_name="Dados financeiros",
            index=False,
        )

        resumo.to_excel(
            writer,
            sheet_name="Resumo",
            index=False,
        )

        previsoes.to_excel(
            writer,
            sheet_name="Previsoes",
            index=False,
        )

    arquivo.seek(0)

    return arquivo.getvalue()

import unicodedata
from io import BytesIO
from pathlib import Path

import pandas as pd

EXTENSOES_ACEITAS = (".csv", ".xlsx")

# Nomes alternativos que planilhas reais costumam usar -> nome padrão do projeto
SINONIMOS = {
    "data": ["data", "mes", "periodo", "competencia", "date"],
    "receita": ["receita", "receitas", "faturamento", "entradas", "vendas"],
    "despesas": ["despesas", "despesa", "custos", "saidas", "gastos"],
}


def _normalizar_nome(nome):
    """Minúsculo, sem acento e sem espaços nas pontas: ' Mês ' -> 'mes'."""
    nome = unicodedata.normalize("NFKD", str(nome))
    nome = nome.encode("ascii", "ignore").decode("ascii")
    return nome.strip().lower()


def padronizar_colunas(dados):
    """Renomeia colunas para data / receita / despesas quando houver sinônimo."""
    dados = dados.copy()
    dados.columns = [_normalizar_nome(c) for c in dados.columns]

    renomear = {}
    for padrao, alternativas in SINONIMOS.items():
        if padrao in dados.columns:
            continue
        for alternativa in alternativas:
            if alternativa in dados.columns:
                renomear[alternativa] = padrao
                break

    return dados.rename(columns=renomear)


def _ler_csv(conteudo, decimal):
    conteudo = conteudo.lstrip()  # ignora linhas em branco no começo do arquivo

    # Excel brasileiro costuma salvar em latin-1; tentamos utf-8 primeiro
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(
                BytesIO(conteudo),
                sep=None,          # detecta ',' ou ';' sozinho
                engine="python",
                decimal=decimal,
                encoding=encoding,
            )
        except UnicodeDecodeError:
            continue
    raise ValueError("Não foi possível ler a codificação do arquivo CSV.")


def carregar_dados(origem, nome=None, decimal="."):
    """
    Carrega CSV ou XLSX a partir de um caminho ou de um arquivo enviado
    (como o do st.file_uploader) e devolve um DataFrame com colunas padronizadas.
    """
    if hasattr(origem, "read"):
        conteudo = origem.read()
        nome = nome or getattr(origem, "name", "")
    else:
        caminho = Path(origem)
        conteudo = caminho.read_bytes()
        nome = nome or caminho.name

    extensao = Path(nome).suffix.lower()

    if extensao not in EXTENSOES_ACEITAS:
        raise ValueError(
            f"Formato não suportado: '{extensao}'. Use CSV ou XLSX."
        )

    if extensao == ".csv":
        dados = _ler_csv(conteudo, decimal)
    else:
        dados = pd.read_excel(BytesIO(conteudo))

    return padronizar_colunas(dados)
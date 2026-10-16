# Metodologia — Lab Financeiro

**Autores:** Gabriel Vianna Cumino (Engenharia de Software, FIAP) e [PREENCHER: nome do colega] (Contabilidade)

> Campos marcados como **[PREENCHER]** dependem do contexto dos dados reais e devem ser completados com o colega de Contabilidade. Todo o restante descreve exatamente o que o código do projeto faz.

---

## 1. Problema de negócio

[PREENCHER: em 3 a 5 linhas, qual decisão ou pergunta a análise quer apoiar. Exemplos de formato: "Prever a receita dos próximos meses para planejar o caixa", "Entender se as despesas acompanham a receita", "Identificar sazonalidade para planejar capital de giro".]

**Pergunta central:** [PREENCHER]

**Quem usaria o resultado:** [PREENCHER: por exemplo, o gestor financeiro da empresa de origem dos dados]

## 2. Hipóteses

Cada hipótese é testada estatisticamente com nível de significância de 5% (α = 0,05).

| # | Hipótese nula (H0) | Hipótese alternativa (H1) | Método |
|---|---|---|---|
| H1 | A receita não tem tendência (inclinação = 0) | A receita tem tendência de crescimento ou queda | Regressão linear (OLS) da receita contra o tempo |
| H2 | Receita e despesas não são correlacionadas | Receita e despesas são correlacionadas | Correlação de Pearson |
| H3 | Os modelos de previsão não erram menos que a previsão ingênua | Pelo menos um modelo erra menos que a previsão ingênua | Comparação de MAE na validação walk-forward |
| H4 | Não há sazonalidade na receita | Há padrão sazonal de 12 meses | Decomposição sazonal (exige 24 meses ou mais) |

[PREENCHER: o colega de Contabilidade pode propor hipóteses de negócio adicionais, por exemplo sobre meses de fechamento, impostos ou datas comerciais.]

## 3. Dados

| Item | Descrição |
|---|---|
| Origem | [PREENCHER: tipo de organização e área, sem identificar a empresa] |
| Autorização de uso | [PREENCHER: quem autorizou e se a autorização cobre publicação de resultados agregados] |
| Anonimização | [PREENCHER: o que foi removido ou alterado] |
| Período | [PREENCHER: mês inicial e final] |
| Periodicidade | Mensal |
| Número de observações | [PREENCHER] |
| Variáveis | `data`, `receita`, `despesas` |
| Unidade | Reais (R$) |

**Os dados reais não são versionados no repositório.** Eles ficam em `data/raw/`, pasta ignorada pelo Git. O repositório contém apenas `data/sample/fluxo_financeiro.csv`, um conjunto **fictício** usado para demonstração e testes.

### 3.1 Carregamento (`src/data_loader.py`)

- Aceita CSV e XLSX, por caminho ou por upload.
- Detecta automaticamente o separador do CSV (vírgula ou ponto e vírgula) e tenta as codificações UTF-8 e Latin-1.
- Permite escolher o separador decimal (ponto ou vírgula).
- Padroniza os nomes das colunas (minúsculas, sem acento) e converte sinônimos comuns (por exemplo, `faturamento` para `receita` e `custos` para `despesas`).

### 3.2 Limpeza e validação (`src/preprocessing.py`)

- Converte `data` para data e `receita` e `despesas` para número. Valores que não podem ser convertidos viram vazios.
- **Remove as linhas com qualquer valor vazio** nas três colunas obrigatórias e ordena por data.
- A validação bloqueia a análise quando há: coluna obrigatória ausente, datas duplicadas, receita ou despesa negativa, ou menos de 4 registros.
- Dois avisos não bloqueiam a análise, mas aparecem na tela: a quantidade de linhas descartadas na limpeza e a lista de meses ausentes entre o primeiro e o último mês da série.

[PREENCHER: quantas linhas, se alguma, foram removidas na limpeza dos dados reais e o motivo.]

## 4. Indicadores e estatística descritiva (`src/analysis.py`)

| Indicador | Definição |
|---|---|
| Fluxo líquido | receita − despesas |
| Margem líquida (%) | fluxo líquido ÷ receita × 100 (indefinida quando a receita do mês é zero) |
| Variação mensal da receita (%) | variação percentual da receita em relação ao mês anterior (indefinida quando o mês anterior tem receita zero) |
| Crescimento da receita (%) | (receita do último mês ÷ receita do primeiro mês − 1) × 100 (indefinido quando a receita do primeiro mês é zero) |

Também são calculados média, mediana e desvio padrão da receita, e o mínimo e o máximo do fluxo líquido.

## 5. Análise estatística (`src/features.py`)

- **Média móvel** (janela de 2 a 6 meses) da receita e das despesas, para suavizar oscilações.
- **Correlação de Pearson** entre receita e despesas, com p-valor. Não é calculada quando uma das séries é constante.
- **Tendência da receita:** regressão linear simples (mínimos quadrados, `statsmodels`) da receita contra o índice do mês. Reporta a inclinação (R$ por mês), o R² e o p-valor da inclinação.
- **Normalidade do fluxo líquido:** teste de Shapiro-Wilk (H0: os dados seguem distribuição normal).

## 6. Séries temporais (`src/timeseries.py`)

- **Estacionariedade:** teste ADF (Dickey-Fuller aumentado). H0: a série tem raiz unitária, ou seja, não é estacionária. O teste é aplicado à receita original e à receita diferenciada (variação mês a mês). Exige mais de 8 observações.
- **Decomposição sazonal:** modelo aditivo com período de 12 meses, separando tendência, sazonalidade e resíduo. Exige pelo menos 24 meses (dois ciclos completos).
- **Suavização exponencial (Holt-Winters):** modelo aditivo com tendência. A componente sazonal de 12 meses só entra quando há 24 meses ou mais de histórico. Os parâmetros de suavização são estimados automaticamente.

## 7. Modelos de previsão e validação

### 7.1 Modelos comparados

| Modelo | Como prevê |
|---|---|
| Previsão ingênua | Repete o último valor observado (modelo de referência) |
| Regressão linear | Reta ajustada à receita contra o índice do mês |
| Holt-Winters | Suavização exponencial com tendência (e sazonalidade, quando há dados) |

### 7.2 Validação

- **Walk-forward (principal):** a partir do 6º mês, o modelo é treinado só com o passado, prevê o mês seguinte e o resultado é comparado com o valor real. O processo avança um mês por vez, o que simula o uso real da previsão e evita o vazamento de informação futura.
- **Hold-out (apoio):** o app também mostra uma avaliação simples, treinando com todos os meses menos os 2 últimos.

### 7.3 Métricas (`src/evaluation.py`)

| Métrica | Interpretação |
|---|---|
| MAE | erro médio absoluto, em R$ |
| RMSE | raiz do erro quadrático médio, em R$; penaliza mais os erros grandes |
| MAPE | erro percentual médio; meses com receita real zero são ignorados |

**Critério de decisão:** um modelo só é considerado útil se tiver MAE menor que o da previsão ingênua. Caso contrário, não agrega valor em relação a repetir o último mês.

## 8. Resultados

[PREENCHER depois de rodar com os dados reais. Não copie valores do conjunto de exemplo: ele é fictício.]

| Hipótese | Resultado | p-valor | Conclusão |
|---|---|---|---|
| H1 — tendência da receita | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| H2 — correlação receita × despesas | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| H3 — modelos x previsão ingênua | [PREENCHER] | — | [PREENCHER] |
| H4 — sazonalidade | [PREENCHER ou "não testável: menos de 24 meses"] | — | [PREENCHER] |

| Modelo | MAE | RMSE | MAPE |
|---|---|---|---|
| Previsão ingênua | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Regressão linear | [PREENCHER] | [PREENCHER] | [PREENCHER] |
| Holt-Winters | [PREENCHER] | [PREENCHER] | [PREENCHER] |

**Interpretação contábil:** [PREENCHER: o colega de Contabilidade explica o que os resultados significam para o negócio.]

## 9. Limitações

1. **Amostra pequena.** Com poucos meses, os testes estatísticos têm pouco poder: não rejeitar uma hipótese não prova que ela é verdadeira. Isso vale em especial para o teste de normalidade.
2. **Sazonalidade só é testável com 24 meses ou mais.** Com menos que isso, a decomposição é omitida e o Holt-Winters opera sem componente sazonal.
3. **Holt-Winters e regressão linear podem coincidir.** Em séries curtas, a estimação automática tende a zerar os parâmetros de suavização, e o modelo se reduz a uma reta de tendência. Isso foi observado no conjunto de exemplo.
4. **Correlação não é causalidade.** Receita e despesas costumam crescer juntas no tempo; a correlação alta pode refletir apenas a tendência comum.
5. **Os modelos usam a posição do mês, não a data.** Se houver meses ausentes na série, as previsões ficam deslocadas. O aplicativo detecta e lista os meses faltantes, mas não os preenche, para não inventar dados.
6. **Linhas inválidas são descartadas na limpeza.** O aplicativo informa quantas linhas foram removidas, e esse número deve ser conferido com a origem dos dados.
7. **Sem variáveis externas.** Inflação, calendário de impostos, campanhas e outros fatores não entram nos modelos.
8. **MAPE** ignora meses de receita zero. Nesses meses, a margem líquida e a variação mensal ficam indefinidas (n/d).
9. **Dados anonimizados** podem ter perdido informação relevante para a interpretação.

## 10. Arquitetura

| Módulo | Responsabilidade |
|---|---|
| `src/data_loader.py` | leitura de CSV e XLSX e padronização das colunas |
| `src/preprocessing.py` | limpeza e validação |
| `src/analysis.py` | indicadores e estatística descritiva |
| `src/features.py` | média móvel, correlação, tendência e normalidade |
| `src/timeseries.py` | ADF, decomposição, Holt-Winters e validação walk-forward |
| `src/forecasting.py` | regressão linear, previsão futura e comparação com a previsão ingênua |
| `src/evaluation.py` | MAE, RMSE e MAPE |
| `src/visualization.py` | gráficos |
| `src/exporting.py` e `src/report.py` | exportação em CSV e Excel e relatório gerencial |
| `app.py` | interface Streamlit |
| `scripts/gerar_figuras.py` | gera as figuras do README a partir dos dados de exemplo |
| `tests/` | testes automatizados (pytest) |

## 11. Divisão de tarefas

[AJUSTAR conforme o combinado entre vocês.]

| Área | Responsável |
|---|---|
| Pipeline de dados, modelos, testes e aplicativo | Gabriel |
| Contexto do negócio, definição do problema e das hipóteses | [PREENCHER: colega] |
| Conferência dos indicadores contábeis | [PREENCHER: colega] |
| Interpretação dos resultados | [PREENCHER: colega] |
| Redação da metodologia e do README | Ambos |

## 12. Reprodutibilidade

Na raiz do projeto:

- Instalar as dependências: `py -m pip install -r requirements.txt`
- Rodar os testes: `py -m pytest -q`
- Abrir o aplicativo: `py -m streamlit run app.py`
- Gerar as figuras do README (dados de exemplo): `py -m scripts.gerar_figuras`

Para analisar os dados reais, coloque o arquivo em `data/raw/` ou envie-o pelo aplicativo.
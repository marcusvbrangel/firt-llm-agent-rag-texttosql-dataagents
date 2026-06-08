# Relatório Executivo - Dados Reais de Produção Volve (Noruega)

**Data da Execução:** 2026-06-08 02:45:43

**Fonte de Dados CSV:** volve_ml_ready.csv
**Banco SQLite:** volve_ml_ready.db
**Tabela SQLite:** volve_ml_ready
**Shape do DataFrame:** (125, 58)

**Modelo Local (SQL):** qwen2.5-coder:7b-instruct via Ollama
**Modelo Remoto (Resposta Final):** anthropic/claude-sonnet-4.6 via OpenRouter

## 1. Fonte dos Dados

```text
BASE: volve_ml_ready.csv
PROVENIÊNCIA: versão preparada para analytics e machine learning derivada do Volve Field Dataset.
LIBERAÇÃO PÚBLICA ORIGINAL: Equinor (antiga Statoil).
CONTEXTO OPERACIONAL:
- Campo Volve, offshore da Noruega, no Mar do Norte, bloco 15/9.
- Produção histórica do campo entre 2008 e 2016.
- Unidade de produção associada: Mærsk Inspirer.
OBSERVAÇÕES:
- O CSV local usado neste notebook é uma versão tratada para analytics e ML.
- Parte das colunas clássicas do dataset Volve pode ter sido transformada, removida ou enriquecida durante a preparação.
- A família de dados Volve ficou conhecida por disponibilizar séries reais de produção e variáveis operacionais para pesquisa e indústria.
FONTES HISTÓRICAS ASSOCIADAS À FAMÍLIA DE DADOS:
- Volve Data Village.
- Base regulatória NPD, atualmente NOD.
- Espelhos públicos em GitHub usados por pesquisadores.
```

## 2. Dicionário de Dados Utilizado

```text
TABELA: volve_ml_ready
CONTEXTO: Serie temporal real de producao de um poco offshore do projeto Volve, no Mar do Norte da Noruega, carregada a partir de arquivo CSV e persistida em SQLite.

OBSERVACOES GERAIS:
- Esta tabela contem apenas as colunas disponiveis no CSV tratado volve_ml_ready.csv.
- Algumas colunas classicas do dataset bruto Volve nao estao presentes nesta versao tratada.
- Colunas prefixadas com oil_, water_ e gas_ sao features derivadas usadas para analytics e machine learning.
- Para SQL, use apenas os nomes de coluna listados abaixo exatamente como aparecem.

COLUNAS DISPONIVEIS NESTA TABELA:
- DATEPRD | sql_type=TEXT | classe=coluna original do dataset Volve | descricao=Data da producao/operacao diaria. | tipo_analitico=datetime | unidade=data | origem=Sistema operacional / historian | local_medicao=Centro de supervisao / banco operacional
- ON_STREAM_HRS | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Quantidade de horas em operacao/produzindo no dia. | tipo_analitico=float | unidade=horas | origem=Sistema supervisorio / producao | local_medicao=Status operacional do poco
- AVG_DOWNHOLE_PRESSURE | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Pressao media no fundo do poco. | tipo_analitico=float | unidade=bar(a) | origem=Gauge de fundo / sensor downhole | local_medicao=Fundo do poco / proximo da zona produtora
- AVG_DOWNHOLE_TEMPERATURE | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Temperatura media no fundo do poco. | tipo_analitico=float | unidade=graus C | origem=Sensor downhole | local_medicao=Fundo do poco / tubing inferior
- AVG_DP_TUBING | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Delta de pressao medio no tubing. | tipo_analitico=float | unidade=bar | origem=Sensores de pressao no tubing | local_medicao=Interior do tubing de producao
- AVG_CHOKE_SIZE_P | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Abertura media do choke em superficie. | tipo_analitico=float | unidade=% | origem=Atuador/sensor do choke | local_medicao=Choke na arvore de natal / superficie
- AVG_WHP_P | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Pressao media na cabeca do poco. | tipo_analitico=float | unidade=bar | origem=Sensor wellhead | local_medicao=Cabeca do poco / arvore de natal
- AVG_WHT_P | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Temperatura media na cabeca do poco. | tipo_analitico=float | unidade=graus C | origem=Sensor wellhead | local_medicao=Cabeca do poco / arvore de natal
- BORE_OIL_VOL | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Volume diario de oleo produzido. | tipo_analitico=float | unidade=Sm3/d | origem=Medidor multifasico / teste de producao | local_medicao=Linha de producao do poco
- BORE_WAT_VOL | sql_type=REAL | classe=coluna original do dataset Volve | descricao=Volume diario de agua produzida. | tipo_analitico=float | unidade=Sm3/d | origem=Medidor multifasico / separador | local_medicao=Linha de producao / separador
- WELL_TYPE | sql_type=TEXT | classe=coluna original do dataset Volve | descricao=Tipo do poco, por exemplo produtor ou injetor. | tipo_analitico=string | unidade=N/A | origem=Engenharia de producao | local_medicao=Configuracao operacional do poco
- oil_roll_30 | sql_type=REAL | classe=feature derivada - rolling | descricao=Feature rolling de 30 dias aplicada a serie de oleo. | tipo_analitico=feature derivada rolling | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_lag_1 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 1 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_lag_1 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 1 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_lag_3 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 3 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_lag_3 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 3 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_lag_7 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 7 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_lag_7 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 7 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_lag_14 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 14 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_lag_14 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 14 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_lag_30 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 30 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- gas_lag_30 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 30 dias da serie de gas derivada da familia BORE_GAS_VOL do dataset Volve original. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir da serie de gas do dataset fonte | local_medicao=Derivada em pipeline analitico / data science
- water_lag_30 | sql_type=REAL | classe=feature derivada - lag temporal | descricao=Valor defasado em 30 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada temporal | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_mean_3 | sql_type=REAL | classe=feature derivada - rolling mean | descricao=Media movel de 3 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_mean_7 | sql_type=REAL | classe=feature derivada - rolling mean | descricao=Media movel de 7 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_roll_mean_7 | sql_type=REAL | classe=feature derivada - rolling mean | descricao=Media movel de 7 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada rolling mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_mean_14 | sql_type=REAL | classe=feature derivada - rolling mean | descricao=Media movel de 14 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_roll_mean_30 | sql_type=REAL | classe=feature derivada - rolling mean | descricao=Media movel de 30 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada rolling mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_std_7 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 7 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_roll_std_7 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 7 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_std_14 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 14 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_roll_std_14 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 14 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roll_std_30 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 30 dias da serie de oleo derivada de BORE_OIL_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_roll_std_30 | sql_type=REAL | classe=feature derivada - rolling std | descricao=Desvio padrao movel de 30 dias da serie de agua derivada de BORE_WAT_VOL. | tipo_analitico=feature derivada rolling std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_delta_1d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de oleo derivada de BORE_OIL_VOL em relacao a 1 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_delta_1d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de agua derivada de BORE_WAT_VOL em relacao a 1 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_delta_3d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de oleo derivada de BORE_OIL_VOL em relacao a 3 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_delta_3d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de agua derivada de BORE_WAT_VOL em relacao a 3 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_delta_7d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de oleo derivada de BORE_OIL_VOL em relacao a 7 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_delta_7d | sql_type=REAL | classe=feature derivada - delta temporal | descricao=Diferenca da serie de agua derivada de BORE_WAT_VOL em relacao a 7 dias antes. | tipo_analitico=feature derivada delta | unidade=Sm3/d | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_pct_change_1d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de oleo derivada de BORE_OIL_VOL em relacao a 1 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_pct_change_1d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de agua derivada de BORE_WAT_VOL em relacao a 1 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_pct_change_7d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de oleo derivada de BORE_OIL_VOL em relacao a 7 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_pct_change_7d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de agua derivada de BORE_WAT_VOL em relacao a 7 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_pct_change_14d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de oleo derivada de BORE_OIL_VOL em relacao a 14 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_pct_change_14d | sql_type=REAL | classe=feature derivada - pct change | descricao=Variacao percentual da serie de agua derivada de BORE_WAT_VOL em relacao a 14 dias antes. | tipo_analitico=feature derivada percentual | unidade=% | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_expanding_mean | sql_type=REAL | classe=feature derivada - expanding mean | descricao=Media expansiva acumulada da serie de oleo ao longo do tempo. | tipo_analitico=feature derivada expanding mean | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_expanding_std | sql_type=REAL | classe=feature derivada - expanding std | descricao=Desvio padrao expansivo acumulado da serie de oleo ao longo do tempo. | tipo_analitico=feature derivada expanding std | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- water_cumulative | sql_type=REAL | classe=feature derivada - cumulativa | descricao=Acumulado historico da serie de agua produzida ao longo do periodo. | tipo_analitico=feature derivada cumulativa | unidade=Sm3 acumulado | origem=Feature engineering a partir de BORE_WAT_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_acceleration | sql_type=REAL | classe=feature derivada - aceleracao | descricao=Indicador derivado de aceleracao da dinamica da serie de oleo. | tipo_analitico=feature derivada de segunda ordem | unidade=unidade derivada do pipeline analitico | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_trend_strength | sql_type=REAL | classe=feature derivada - trend strength | descricao=Indicador derivado de forca de tendencia da serie de oleo. | tipo_analitico=feature derivada de tendencia | unidade=unidade derivada do pipeline analitico | origem=Feature engineering temporal | local_medicao=Derivada em pipeline analitico / data science
- water_trend_strength | sql_type=REAL | classe=feature derivada - trend strength | descricao=Indicador derivado de forca de tendencia da serie de agua. | tipo_analitico=feature derivada de tendencia | unidade=unidade derivada do pipeline analitico | origem=Feature engineering temporal | local_medicao=Derivada em pipeline analitico / data science
- oil_vs_trend | sql_type=REAL | classe=feature derivada - vs trend | descricao=Razao entre o valor corrente e a tendencia estimada da serie de oleo. | tipo_analitico=feature derivada de comparacao com tendencia | unidade=adimensional | origem=Feature engineering temporal | local_medicao=Derivada em pipeline analitico / data science
- water_vs_trend | sql_type=REAL | classe=feature derivada - vs trend | descricao=Razao entre o valor corrente e a tendencia estimada da serie de agua. | tipo_analitico=feature derivada de comparacao com tendencia | unidade=adimensional | origem=Feature engineering temporal | local_medicao=Derivada em pipeline analitico / data science
- oil_volatility_index | sql_type=REAL | classe=feature derivada - volatility index | descricao=Indice derivado de volatilidade da serie de oleo. | tipo_analitico=feature derivada de volatilidade | unidade=adimensional | origem=Feature engineering temporal | local_medicao=Derivada em pipeline analitico / data science
- oil_momentum_30d | sql_type=REAL | classe=feature derivada - momentum | descricao=Momentum de 30 dias da serie de oleo, comparando o valor corrente com a referencia de 30 dias antes. | tipo_analitico=feature derivada de momentum | unidade=Sm3/d | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_roc_30d | sql_type=REAL | classe=feature derivada - rate of change | descricao=Rate of change de 30 dias da serie de oleo. | tipo_analitico=feature derivada de taxa de variacao | unidade=fracao ou % conforme convencao do pipeline | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
- oil_zscore_30 | sql_type=REAL | classe=feature derivada - zscore | descricao=Z-score de 30 dias da serie de oleo. | tipo_analitico=feature derivada de padronizacao | unidade=adimensional | origem=Feature engineering a partir de BORE_OIL_VOL | local_medicao=Derivada em pipeline analitico / data science
```

## 3. Histórico de Execuções e Respostas Técnicas

### Caso de Teste 1: Em qual data ocorreu o maior BORE_OIL_VOL e qual foi o valor?
- Tempo Total: 54.65 segundos
- Tempo de Geração do SQL: 47.68 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 6.95 segundos
- Tamanho do Prompt Local Enviado: 22664 caracteres
- Tamanho do Prompt Remoto Enviado: 20770 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT DATEPRD, MAX(BORE_OIL_VOL) AS max_oil_volume FROM volve_ml_ready ORDER BY BORE_OIL_VOL DESC LIMIT 1
```

```text
   DATEPRD  max_oil_volume
2014-06-13          818.89
```

> ## Pico de Produção de Óleo — BORE_OIL_VOL

O maior volume diário de óleo produzido registrado na série histórica ocorreu em:

- **DATEPRD:** `2014-06-13`
- **BORE_OIL_VOL (max_oil_volume):** `818,89 Sm³/d`

Este valor representa o pico de produção diária de óleo do poço, medido na linha de produção via medidor multifásico/teste de produção, expresso em metros cúbicos padrão por dia (Sm³/d).

---

### Caso de Teste 2: Em qual data ocorreu o maior BORE_WAT_VOL e qual foi o valor?
- Tempo Total: 45.10 segundos
- Tempo de Geração do SQL: 39.60 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 5.49 segundos
- Tamanho do Prompt Local Enviado: 22664 caracteres
- Tamanho do Prompt Remoto Enviado: 20776 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT DATEPRD, MAX(BORE_WAT_VOL) AS max_water_volume FROM volve_ml_ready ORDER BY BORE_WAT_VOL DESC LIMIT 1
```

```text
   DATEPRD  max_water_volume
2015-06-26            765.45
```

> ## Maior Volume Diário de Água Produzida (BORE_WAT_VOL)

O pico de produção de água registrado no histórico do poço ocorreu em:

- **DATEPRD:** `2015-06-26`
- **BORE_WAT_VOL (max_water_volume):** `765,45 Sm³/d`

Este valor representa o maior volume diário de água produzida (BORE_WAT_VOL) medido na linha de produção/separador ao longo de toda a série temporal disponível na tabela `volve_ml_ready`.

---

### Caso de Teste 3: Qual foi a média de ON_STREAM_HRS?
- Tempo Total: 38.11 segundos
- Tempo de Geração do SQL: 33.38 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 4.70 segundos
- Tamanho do Prompt Local Enviado: 22637 caracteres
- Tamanho do Prompt Remoto Enviado: 20591 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT AVG(ON_STREAM_HRS) AS avg_on_stream_hrs FROM volve_ml_ready
```

```text
 avg_on_stream_hrs
           23.6488
```

> ## Média de ON_STREAM_HRS

A média de **ON_STREAM_HRS** para o poço offshore do projeto Volve é de **23,6488 horas/dia**.

> **ON_STREAM_HRS** representa a quantidade de horas em que o poço esteve em operação/produzindo ao longo de cada dia. O valor médio de **23,65 horas/dia** indica um alto fator de utilização operacional do poço ao longo do período analisado, próximo ao máximo teórico de 24 horas diárias.

---

### Caso de Teste 4: Em qual data ocorreu a maior AVG_DOWNHOLE_PRESSURE e qual foi o valor?
- Tempo Total: 72.39 segundos
- Tempo de Geração do SQL: 52.30 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 20.05 segundos
- Tamanho do Prompt Local Enviado: 22673 caracteres
- Tamanho do Prompt Remoto Enviado: 20812 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT DATEPRD, AVG_DOWNHOLE_PRESSURE AS max_avg_downhole_pressure FROM volve_ml_ready ORDER BY AVG_DOWNHOLE_PRESSURE DESC LIMIT 1
```

```text
   DATEPRD  max_avg_downhole_pressure
2014-11-24                 229.949538
```

> ## Maior AVG_DOWNHOLE_PRESSURE Registrada

A maior **AVG_DOWNHOLE_PRESSURE** ocorreu em **24/11/2014**, com valor de **229,95 bar(a)**, medida pelo gauge de fundo do poço, próximo à zona produtora.

---

### Caso de Teste 5: Qual foi o maior valor de water_cumulative e em qual data ocorreu?
- Tempo Total: 39.43 segundos
- Tempo de Geração do SQL: 34.22 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 5.17 segundos
- Tamanho do Prompt Local Enviado: 22669 caracteres
- Tamanho do Prompt Remoto Enviado: 20793 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT DATEPRD, MAX(water_cumulative) AS max_water_cumulative FROM volve_ml_ready
```

```text
   DATEPRD  max_water_cumulative
2015-06-26               96037.2
```

> ## Resultado: Maior valor de `water_cumulative`

O maior valor registrado de **water_cumulative** foi de **96.037,2 Sm³ acumulados**, ocorrido na data **2015-06-26** (26 de junho de 2015).

> `water_cumulative` representa o acumulado histórico da série de água produzida (derivada de `BORE_WAT_VOL`), expresso em **Sm³ acumulado**.

---

### Caso de Teste 6: Qual foi o maior valor de oil_roll_30 e em qual data ocorreu?
- Tempo Total: 49.26 segundos
- Tempo de Geração do SQL: 43.82 segundos
- Tempo de Execução SQL: 0.00 segundos
- Tempo de Resposta Remota: 5.43 segundos
- Tamanho do Prompt Local Enviado: 22664 caracteres
- Tamanho do Prompt Remoto Enviado: 20773 caracteres
- Tentativas de Correção (Retries): 0
- Status: Sem erros

```sql
SELECT DATEPRD, MAX(oil_roll_30) AS max_oil_roll_30 FROM volve_ml_ready ORDER BY oil_roll_30 DESC LIMIT 1
```

```text
   DATEPRD  max_oil_roll_30
2014-06-08       733.144333
```

> ## Resultado: Maior valor de `oil_roll_30`

O maior valor registrado para a feature **`oil_roll_30`** (média móvel de 30 dias da produção de óleo, derivada de `BORE_OIL_VOL`) foi:

| DATEPRD | max_oil_roll_30 |
|---|---|
| **2014-06-08** | **733,14 Sm³/d** |

**Conclusão técnica:** O pico da média móvel de 30 dias da produção de óleo ocorreu em **08 de junho de 2014**, atingindo **733,144333 Sm³/d**, representando o período de maior desempenho médio sustentado de produção de óleo no histórico analisado do poço Volve.

---

## 4. Sumário Executivo de Performance

- Total de Perguntas Submetidas: 6
- Casos com sucesso: 6
- Casos com falha: 0
- Tempo Total de Varredura: 298.99 segundos
- Média de Tempo por Requisição: 49.83 segundos
- Média de Tempo de Geração do SQL: 41.83 segundos
- Média de Tempo de Execução SQL: 0.00 segundos
- Média de Tempo de Resposta Remota: 7.96 segundos
- Média de Tamanho do Prompt Local: 22661.83 caracteres
- Média de Tamanho do Prompt Remoto: 20752.50 caracteres
- Status Geral do Sistema: Concluído com sucesso

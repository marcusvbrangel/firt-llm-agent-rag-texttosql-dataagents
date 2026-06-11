# Dashboard Volve

## Objetivo

Construir um dashboard em Streamlit para explorar a base `notebooks/volve_ml_ready.db`
com foco em:

- monitoramento de producao de oleo e agua
- analise de estabilidade operacional
- leitura de tendencia e volatilidade
- identificacao de anomalias com base nas features derivadas de ML

## Base utilizada

- Arquivo: `../../notebooks/volve_ml_ready.db`
- Tabela: `volve_ml_ready`
- Granularidade: diaria
- Perfil: serie temporal com variaveis operacionais e features derivadas

## Tipo de dashboard aprovado

O formato escolhido foi um cockpit analitico de producao e operacao, evitando um
dashboard BI generico. A base tem pouca variacao categorica, entao o valor maior
esta em filtros temporais, faixas operacionais e sinais de anomalia.

## Estrutura da tela

- Barra lateral com filtros agrupados
- Linha superior com KPIs
- Quatro abas principais:
  - Resumo executivo
  - Diagnostico operacional
  - Tendencias e alertas
  - Base filtrada

## Filtros previstos

- periodo
- tipo de poco
- faixa de producao de oleo
- faixa de producao de agua
- horas em operacao
- pressao downhole
- temperatura downhole
- diferencial de tubing
- choke size
- wellhead pressure
- limiar de anomalia via `oil_zscore_30`
- faixa de forca de tendencia
- faixa de volatilidade

## KPIs previstos

- oleo total
- oleo medio diario
- agua total
- agua media diaria
- water cut
- horas medias em operacao
- pressao media
- variacao de oleo em 7 dias
- quantidade de dias anomalos

## Visualizacoes aprovadas

### Aba 1: Resumo executivo

- serie temporal de oleo e agua
- medias moveis de 7d e 30d
- evolucao de water cut
- resumo rapido do periodo filtrado

### Aba 2: Diagnostico operacional

- dispersao entre pressao e oleo
- dispersao entre temperatura e oleo
- dispersao entre choke size e oleo
- dispersao entre diferencial de tubing e oleo
- heatmap de correlacao

### Aba 3: Tendencias e alertas

- linha de `oil_zscore_30`
- linha de `oil_trend_strength`
- barras de `oil_delta_7d`
- tabela com os dias mais criticos

### Aba 4: Base filtrada

- tabela detalhada com as colunas principais de producao, operacao e sinais derivados

## Primeira entrega implementada

A primeira versao deve:

- carregar o banco SQLite diretamente
- aplicar filtros pela barra lateral
- recalcular KPIs em cima do conjunto filtrado
- mostrar os principais graficos em abas
- expor a base filtrada para leitura e inspecao

## Como executar

Na raiz do repositorio:

```bash
streamlit run aplicacao/01-aplicacao/app.py
```

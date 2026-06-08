# Plano Tecnico - Consultas SQL versus Machine Learning

**Nome oficial:** `plano-tecnico-consultas-sql-versus-machine-learning`  
**Data:** 2026-06-08  
**Status:** proposta arquitetural detalhada  
**Escopo principal:** separacao formal entre trilha de consulta historica via SQL e trilha de previsao via machine learning para futura aplicacao em Streamlit

## 1. Resumo executivo

O sistema atual tenta responder perguntas historicas, analiticas e preditivas usando praticamente o mesmo fluxo:

`pergunta em linguagem natural -> geracao de SQL -> execucao SQLite -> resposta final`

Essa estrategia funciona razoavelmente para consultas historicas simples, mas comeca a falhar quando a pergunta exige previsao, inferencia temporal futura, mudanca de regime ou avaliacao de risco operacional. Nesses casos, tentar transformar tudo em SQL leva a:

- aumento de complexidade do prompt local;
- piora de latencia;
- degradacao de qualidade do SQL;
- ambiguidades semanticas;
- retrabalho tecnico em cima da camada errada.

Conclusao arquitetural:

- `SQLite/SQL` deve responder perguntas sobre fatos observados, series historicas, filtros, comparacoes, rankings, relatorios e dados para graficos;
- `ML` deve responder perguntas sobre previsao, tendencia futura, risco e comportamento esperado dos proximos dias;
- `LLM` deve atuar como camada de interface: entender a intencao, rotear a pergunta, compor a resposta final e explicar o resultado.

Esse plano formaliza a migracao da arquitetura atual para um modelo com duas trilhas principais:

1. `consulta_historica_sql`
2. `previsao_ml`

## 2. Contexto atual consolidado

## 2.1 Ativos ja existentes no repositorio

- Base SQLite pronta: `notebooks/volve_ml_ready.db`
- Dataset trabalhado: `notebooks/volve_ml_ready.csv`
- Notebook principal atual: `notebooks/07-exercicio-dados-reais-producao-volve-noruega.ipynb`
- Relatorio tecnico atual: `notebooks/relatorio_dados_reais_producao_volve_noruega.md`
- Planos e base de conhecimento de performance:
  - `notebooks/plano_acao_performance_fluxo_volve.md`
  - `notebooks/base_conhecimento_performance_fluxo_volve.md`

## 2.2 Diagnostico tecnico atual

Pelos experimentos mais recentes:

- o gargalo principal do fluxo atual esta no modelo local que traduz pergunta em SQL;
- o SQLite nao e o gargalo;
- a reducao do prompt remoto foi positiva para custo e latencia;
- previsoes e perguntas mais sofisticadas de serie temporal tendem a forcar a trilha errada.

## 2.3 Restricao critica do dataset

O dataset atual tem aproximadamente `125` linhas e `58` colunas.

Implicacoes:

- existe material suficiente para prototipar forecast, mas nao para assumir robustez de producao sem validacao forte;
- modelos mais complexos podem sobreajustar;
- qualquer modelo ML precisa competir contra baselines muito simples;
- a fase inicial precisa privilegiar transparencia e comparacao metodologica, nao sofisticacao gratuita.

## 3. Objetivo do plano

Construir uma arquitetura em que:

- perguntas historicas usem `SQL`;
- perguntas preditivas usem `ML`;
- a camada conversacional nao tente simular forecast via SQL;
- a futura aplicacao Streamlit consiga consumir as duas trilhas de forma clara, auditavel e performatica.

## 4. Principios de arquitetura

## 4.1 Separacao de responsabilidade

Cada camada deve ter um papel tecnico claro:

- `SQLite`: armazenamento e consulta de fatos observados;
- `SQL engine`: recuperacao estruturada de historico;
- `ML engine`: previsao e score de risco;
- `Router`: escolha de trilha;
- `LLM`: interpretacao da pergunta e explicacao do resultado;
- `Streamlit`: experiencia do usuario, graficos, tabelas, relatorios e depuracao.

## 4.2 Nao usar SQL para prever o futuro

Previsao nao deve ser implementada como gambiarra de SQL com `lags`, `rolling` e formulas soltas geradas por linguagem natural. Isso pode servir como baseline heuristico, mas nao como estrategia principal.

## 4.3 Baseline antes de modelo sofisticado

Antes de validar `XGBoost`, o sistema deve medir se ele realmente supera:

- ultimo valor observado;
- media movel curta;
- tendencia linear curta;
- heuristica operacional simples.

Se `XGBoost` nao superar isso de forma clara, ele nao entra na trilha principal.

## 4.4 Transparencia operacional

Toda resposta deve deixar claro:

- qual trilha foi usada;
- se o resultado veio de SQL historico ou ML;
- qual alvo foi previsto;
- qual horizonte foi usado;
- qual o nivel de confianca e limitacoes.

## 4.5 Otimizacao de custo com qualidade controlada

Diretriz mantida:

- nao aumentar novamente o prompt remoto como reacao padrao;
- manter o contrato remoto enxuto;
- melhorar primeiro a qualidade do contexto vindo da trilha SQL ou da trilha ML.

## 5. Arquitetura alvo

```text
Usuario / Streamlit
        |
        v
Router de Intencao
   |            |
   |            |
   v            v
Trilha SQL    Trilha ML
   |            |
   v            v
SQLite       Forecast Engine
   |            |
   +-----+------+ 
         |
         v
Camada de Explicacao / LLM
         |
         v
Resposta final + graficos + relatorio
```

## 5.1 Trilha SQL

Responsavel por:

- recuperar fatos historicos;
- montar tabelas e series para graficos;
- responder perguntas descritivas;
- alimentar dashboards e relatorios.

## 5.2 Trilha ML

Responsavel por:

- prever oleo e agua para horizontes futuros;
- estimar tendencia de curto prazo;
- detectar mudanca de regime;
- gerar score de risco operacional futuro.

## 5.3 Router de intencao

Responsavel por:

- classificar a pergunta;
- decidir a trilha;
- evitar que previsao caia em SQL;
- evitar que perguntas historicas simples paguem o custo de ML.

## 5.4 Camada de explicacao

Responsavel por:

- receber resultado estruturado;
- gerar resposta natural;
- explicar unidades, datas, limitacoes e contexto operacional;
- manter formato legivel para Streamlit e relatorios.

## 5.5 Stack tecnico recomendado

Camada por camada:

- persistencia: `SQLite`
- acesso a dados: `sqlite3` + `pandas`
- validacao de contratos: `pydantic` ou `TypedDict`
- roteamento: regras Python simples no inicio
- forecast baseline: `pandas`, `numpy`, `scikit-learn`
- forecast avancado: `xgboost`
- serializacao de artefatos: `joblib` ou `pickle`
- interface: `streamlit`
- observabilidade local: logs em arquivo + relatorios Markdown
- LLM local: `ollama`
- LLM remoto: fluxo atual via `OpenRouter`

Dependencias novas esperadas para a trilha ML:

- `xgboost`
- `scikit-learn`
- opcionalmente `joblib`

Observacao:

- `streamlit` e `pandas` ja estao no ambiente;
- `xgboost` ainda deve ser tratado como dependencia nova a ser incorporada quando a fase de modelagem comecar.

## 6. Taxonomia de perguntas

## 6.1 Categoria A - Consulta historica descritiva

Exemplos:

- "Quando ocorreu o maior volume diario de oleo?"
- "Qual foi a media de horas em operacao?"
- "Mostre a evolucao da agua produzida no periodo."
- "Quais foram os dias com maior pressao de fundo?"

Destino:

- `consulta_historica_sql`

## 6.2 Categoria B - Consulta historica analitica

Exemplos:

- "Em que periodo o oleo perdeu forca enquanto a agua aumentou?"
- "Quais dias ficaram mais acima do comportamento recente?"
- "Mostre as maiores divergencias em relacao a tendencia observada."

Destino:

- preferencialmente `consulta_historica_sql`
- com possibilidade de templates SQL especializados ou consultas analiticas predefinidas

## 6.3 Categoria C - Previsao quantitativa

Exemplos:

- "Qual a estimativa de oleo para amanha?"
- "Qual a previsao de agua para os proximos 3 dias?"
- "Como deve se comportar a producao no curtissimo prazo?"

Destino:

- `previsao_ml`

## 6.4 Categoria D - Risco ou mudanca de regime

Exemplos:

- "Ha sinal de piora da razao agua/oleo nos proximos dias?"
- "Existe risco de queda de desempenho no curto prazo?"
- "O sistema indica mudanca de regime operacional?"

Destino:

- `previsao_ml`

## 6.5 Categoria E - Ambigua

Exemplos:

- "Como esta a tendencia?"
- "A situacao esta melhorando ou piorando?"

Destino:

- primeiro tentar classificacao por regras;
- se ficar ambigua, chamar desambiguacao curta;
- se ainda ficar ambigua, responder com duas leituras:
  - leitura historica;
  - leitura preditiva;
  - ou pedir refinamento ao usuario.

## 7. Regras de roteamento

## 7.1 Estrategia recomendada

Implementar o router em tres niveis:

### Nivel 1 - Regras deterministicas

Usar dicionarios simples de padroes:

- palavras que indicam historico:
  - `ocorreu`
  - `aconteceu`
  - `foi`
  - `maior`
  - `menor`
  - `media`
  - `mostre`
  - `compare`
  - `evolucao`
  - `serie`
  - `historico`
- palavras que indicam previsao:
  - `previsao`
  - `estimativa`
  - `deve acontecer`
  - `proximos dias`
  - `amanha`
  - `D+1`
  - `D+3`
  - `tendencia futura`
  - `risco`
  - `mudanca de regime`

### Nivel 2 - Classificador leve

Se as regras forem insuficientes, usar:

- um classificador leve baseado em regras pontuadas;
- ou um LLM pequeno apenas para classificar intent, nao para gerar SQL nem forecast.

### Nivel 3 - Fallback seguro

Se a confianca ficar baixa:

- registrar `intent=ambiguous`;
- responder com pedido de refinamento;
- ou mostrar duas opcoes de leitura.

## 7.2 Contrato de saida do router

Exemplo de estrutura:

```json
{
  "intent_type": "forecast_ml",
  "confidence": 0.93,
  "target_metric": "oil",
  "forecast_horizon_days": 3,
  "requires_chart": true,
  "requires_narrative": true
}
```

## 8. Escopo funcional da trilha SQL

## 8.1 O que a trilha SQL deve fazer

- consultas de maximo, minimo, media, soma e contagem;
- rankings temporais;
- filtros por periodo;
- comparacao entre janelas historicas;
- resposta a perguntas sobre pressao, temperatura, horas em operacao, oleo e agua;
- alimentacao de graficos em Streamlit;
- insumos para relatorios executivos.

## 8.2 O que a trilha SQL nao deve fazer

- prever `D+1`, `D+3`, `D+7`;
- simular modelo preditivo usando formula improvisada dentro da pergunta;
- inventar risco futuro a partir de um unico snapshot sem metodo validado.

## 8.3 Evolucao recomendada da trilha SQL

Em vez de depender apenas de `NL -> SQL`, criar tres modos:

1. `template_sql_simples`
2. `template_sql_analitico`
3. `llm_sql_fallback`

### 1. template_sql_simples

Para perguntas altamente recorrentes:

- maior valor;
- menor valor;
- media;
- top N;
- serie no tempo.

### 2. template_sql_analitico

Para perguntas historicas mais sofisticadas, mas ainda deterministicas:

- maior desvio;
- comparacao com media movel;
- piora simultanea de oleo e agua;
- primeiros sinais de reversao;
- ranking de volatilidade historica.

### 3. llm_sql_fallback

Usar somente quando nao houver template claro.

Beneficio:

- reduz latencia;
- reduz dependencia do modelo local;
- melhora previsibilidade.

## 9. Escopo funcional da trilha ML

## 9.1 Objetivo inicial da trilha ML

Responder com metodo objetivo perguntas como:

- "Qual a previsao de oleo para amanha?"
- "Qual a previsao de agua para os proximos 3 dias?"
- "A tendencia de curtissimo prazo e de alta, queda ou estabilidade?"
- "Ha risco de water cut piorar?"

## 9.2 Ordem de prioridades recomendada

### Fase inicial

- previsao de `BORE_OIL_VOL`
- previsao de `BORE_WAT_VOL`
- horizontes `D+1` e `D+3`

### Fase intermediaria

- score de tendencia de curto prazo
- score de risco de piora de agua
- classificacao de regime

### Fase posterior

- previsoes multialvo mais complexas
- bandas de incerteza mais robustas
- cenario otimista/base/pessimista

## 9.3 Alvos recomendados

Iniciar somente com:

- `BORE_OIL_VOL`
- `BORE_WAT_VOL`

Motivo:

- sao os alvos mais intuitivos para operacao;
- ja existem features derivadas relacionadas;
- permitem valor pratico imediato na aplicacao Streamlit.

## 10. Estrategia de modelagem para series temporais

## 10.1 Baselines obrigatorios

Antes de usar `XGBoost`, implementar e medir:

### Baseline 1 - Ultimo valor

```text
y_hat(t+1) = y(t)
```

### Baseline 2 - Media movel curta

Exemplo:

```text
y_hat(t+1) = media dos ultimos 3 ou 7 pontos
```

### Baseline 3 - Tendencia linear curta

Regressao linear simples usando uma janela curta recente.

### Baseline 4 - Heuristica operacional

Por exemplo:

- repetir nivel recente quando a serie estiver estavel;
- aplicar inclinacao curta quando houver tendencia consistente.

## 10.2 Modelo candidato principal

`XGBoost Regressor`

Motivos:

- lida bem com dados tabulares e features temporais prontas;
- costuma funcionar melhor do que redes neurais em datasets pequenos;
- e relativamente interpretavel via importance e SHAP;
- tem boa relacao custo-beneficio para prototipo.

## 10.3 Modelos que nao devem ser prioridade agora

- LSTM
- Transformers de serie temporal
- Prophet como dependencia central
- ensembles grandes

Motivo:

- complexidade alta para pouco dado;
- custo de manutencao maior;
- chance alta de sobreajuste.

## 10.4 Configuracao inicial sugerida para XGBoost

Configuracao conservadora recomendada para o primeiro ciclo:

```python
XGBRegressor(
    n_estimators=80,
    max_depth=2,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.8,
    reg_alpha=0.0,
    reg_lambda=1.0,
    min_child_weight=2,
    objective="reg:squarederror",
    random_state=42
)
```

Racional:

- `max_depth` baixo para reduzir sobreajuste;
- `learning_rate` moderado para estabilidade;
- `n_estimators` pequeno porque o dataset e curto;
- regularizacao simples antes de tuning fino.

Regra:

- nao comecar com busca extensa de hiperparametros;
- primeiro provar que o modelo basico supera os baselines.

## 11. Features para a trilha ML

## 11.1 Features ja disponiveis

O dataset atual ja contem informacao util:

- lags de oleo e agua
- medias moveis
- desvios moveis
- deltas
- variacoes percentuais
- media expansiva
- cumulativo de agua
- trend strength
- momentum
- z-score
- volatility index

## 11.2 Features adicionais recomendadas

Adicionar explicitamente, se ainda nao estiverem no pipeline final:

- indice temporal sequencial
- dia da semana
- semana do mes
- mes
- contagem de dias desde inicio da serie
- water cut observado
- razao agua/oleo
- slope dos ultimos 3 e 7 dias
- sinal de aceleracao recente
- amplitude da janela recente

## 11.3 Cuidado importante

Somente usar features que estariam disponiveis no momento da previsao.

Regra:

- nenhuma feature pode vazar informacao do futuro;
- todo calculo deve respeitar causalidade temporal.

## 12. Validacao do modelo

## 12.1 Metodo recomendado

`walk-forward validation`

Exemplo:

1. treina em uma janela inicial;
2. testa no proximo ponto ou pequena janela;
3. avanca a fronteira temporal;
4. repete ate o fim da serie.

## 12.2 O que nao fazer

- `train_test_split` aleatorio;
- embaralhamento temporal;
- validacao cruzada tradicional sem ordem temporal.

## 12.3 Metricas obrigatorias

Para regressao:

- `MAE`
- `RMSE`
- `sMAPE`

Se fizer sentido operacional:

- erro absoluto medio por horizonte
- taxa de acerto de direcao

## 12.4 Criterio minimo para aceitar o XGBoost

O `XGBoost` so deve virar trilha principal se:

- superar pelo menos `2` dos principais baselines;
- tiver erro mais estavel no walk-forward;
- nao produzir comportamento erratico;
- for explicavel para uso operacional.

## 12.5 Criterio de rejeicao

Se o `XGBoost`:

- empatar com baselines simples;
- ganhar por margem irrelevante;
- ou perder em estabilidade,

entao o sistema deve permanecer com baseline simples como motor principal ate haver mais dados.

## 12.6 Matriz minima de avaliacao

Para cada alvo e horizonte, registrar no minimo:

```text
alvo: BORE_OIL_VOL
horizonte: D+1
modelo: naive_last_value
mae:
rmse:
smape:
directional_accuracy:
```

```text
alvo: BORE_OIL_VOL
horizonte: D+1
modelo: moving_average_3
mae:
rmse:
smape:
directional_accuracy:
```

```text
alvo: BORE_OIL_VOL
horizonte: D+1
modelo: xgboost_regressor
mae:
rmse:
smape:
directional_accuracy:
```

Repetir a mesma grade para:

- `BORE_OIL_VOL` em `D+3`
- `BORE_WAT_VOL` em `D+1`
- `BORE_WAT_VOL` em `D+3`

O relatorio comparativo deve mostrar:

- vencedor por metrica;
- vencedor geral por horizonte;
- estabilidade do erro ao longo do walk-forward.

## 13. Estrategia de horizontes

## 13.1 Horizonte inicial recomendado

- `D+1`
- `D+3`

## 13.2 Horizonte que deve esperar

- `D+7` ou superior

Motivo:

- dataset curto;
- incerteza rapidamente crescente;
- risco alto de vender falsa precisao.

## 13.3 Estrategia de saida

Para cada previsao, retornar:

- valor previsto;
- metodo usado;
- horizonte;
- ultima data observada;
- comparacao com ultimo valor real;
- observacao sobre confianca.

## 14. Estrategia de classificacao de tendencia e risco

Depois da regressao basica, o motor ML pode expor servicos derivados:

## 14.1 Classificacao de tendencia

Saidas:

- `alta`
- `queda`
- `estabilidade`

Base:

- comparacao entre forecast e nivel recente;
- ou classificador simples treinado com alvo derivado.

## 14.2 Score de risco de piora de agua

Saidas:

- `baixo`
- `medio`
- `alto`

Base:

- crescimento esperado de agua;
- piora na razao agua/oleo;
- volatilidade recente;
- inclinacao curta.

## 14.3 Mudanca de regime

Fase posterior:

- detectar ruptura de comportamento recente;
- usar regra heuristica primeiro;
- depois avaliar classificador especifico.

## 15. Contratos de dados internos

## 15.1 Contrato da trilha SQL

Entrada:

```json
{
  "question": "Quando ocorreu o maior volume diario de oleo?",
  "intent_type": "historical_sql",
  "expected_output": "table_or_scalar"
}
```

Saida:

```json
{
  "route": "sql",
  "sql": "SELECT DATEPRD, BORE_OIL_VOL FROM volve_ml_ready ORDER BY BORE_OIL_VOL DESC LIMIT 1",
  "rows": [{"DATEPRD": "2014-06-13", "BORE_OIL_VOL": 818.89}],
  "metadata": {
    "row_count": 1,
    "columns": ["DATEPRD", "BORE_OIL_VOL"],
    "units": {"BORE_OIL_VOL": "Sm3/d"}
  }
}
```

## 15.2 Contrato da trilha ML

Entrada:

```json
{
  "question": "Qual a previsao de oleo para amanha?",
  "intent_type": "forecast_ml",
  "target_metric": "BORE_OIL_VOL",
  "horizon_days": 1
}
```

Saida:

```json
{
  "route": "ml",
  "model_type": "xgboost_regressor",
  "target_metric": "BORE_OIL_VOL",
  "horizon_days": 1,
  "forecast_value": 735.4,
  "last_observed_date": "2015-06-26",
  "last_observed_value": 721.0,
  "validation_summary": {
    "mae": 18.2,
    "rmse": 24.7,
    "smape": 3.8
  },
  "confidence_note": "forecast experimental com base curta"
}
```

## 15.3 Contrato da camada de resposta final

Entrada:

- resultado estruturado da trilha SQL ou ML
- pergunta original
- contexto minimo de metadados

Saida:

- texto natural
- bloco tabular opcional
- sugestao de grafico opcional

## 16. Proposta de estrutura de codigo

```text
app/
  streamlit_app.py
  pages/
    01_overview.py
    02_consultas_historicas.py
    03_previsoes.py
    04_relatorios.py
    05_debug_tecnico.py

src/
  config/
    settings.py
  data/
    sqlite_repository.py
    dataframe_loader.py
  routing/
    intent_router.py
    intent_rules.py
    intent_schema.py
  sql/
    sql_templates.py
    sql_generator.py
    sql_validator.py
    sql_executor.py
    sql_metadata.py
  forecasting/
    feature_builder.py
    baseline_models.py
    xgboost_models.py
    walk_forward.py
    forecast_service.py
    forecast_schema.py
  llm/
    response_writer.py
    prompt_contracts.py
  reporting/
    markdown_reporter.py
    evaluation_reporter.py
  observability/
    metrics_logger.py
    run_registry.py

artifacts/
  models/
  reports/
  evaluations/
  prompts/
```

## 16.1 Artefatos recomendados

Padrao de nomes sugerido:

- modelo:
  - `artifacts/models/oil_d1_xgb.joblib`
  - `artifacts/models/water_d3_xgb.joblib`
- baseline report:
  - `artifacts/evaluations/baselines_oil_d1.md`
- comparativo final:
  - `artifacts/evaluations/model_comparison_oil_water.md`
- prompts e contratos:
  - `artifacts/prompts/sql_response_contract_v1.md`
  - `artifacts/prompts/forecast_response_contract_v1.md`

Metadados minimos por artefato:

- data de geracao;
- versao do dataset;
- alvo;
- horizonte;
- conjunto de features;
- metrica principal;
- observacao de limitacao.

## 16.2 Servicos recomendados

Servicos de mais alto nivel a implementar:

- `run_historical_query(question: str) -> HistoricalAnswer`
- `run_forecast(question: str, target: str | None = None, horizon: int | None = None) -> ForecastAnswer`
- `route_question(question: str) -> RoutedIntent`
- `render_final_answer(result: dict) -> str`

Beneficio:

- Streamlit, notebook e scripts futuros usam a mesma interface;
- reduz acoplamento a celulas do notebook.

## 17. Proposta para a aplicacao Streamlit

## 17.1 Pagina 1 - Visao geral

Conteudo:

- resumo do dataset;
- periodo coberto;
- principais metricas;
- estado do motor SQL;
- estado do motor ML.

## 17.2 Pagina 2 - Consultas historicas

Funcionalidades:

- caixa de pergunta em linguagem natural;
- tabela do resultado SQL;
- SQL gerado;
- grafico associado;
- resposta executiva.

## 17.3 Pagina 3 - Previsoes

Funcionalidades:

- pergunta em linguagem natural;
- escolha opcional de alvo;
- escolha opcional de horizonte;
- valor previsto;
- comparacao com ultimo observado;
- grafico historico + ponto previsto;
- metricas de validacao do modelo.

## 17.4 Pagina 4 - Relatorios

Funcionalidades:

- relatorios tecnicos;
- relatorios executivos;
- exportacao Markdown;
- consolidacao de experimentos.

## 17.5 Pagina 5 - Debug tecnico

Funcionalidades:

- rota escolhida;
- tempo por etapa;
- prompt local;
- prompt remoto;
- SQL gerado;
- features usadas no forecast;
- metrica do modelo utilizado.

## 18. Observabilidade recomendada

## 18.1 Para a trilha SQL

Registrar:

- pergunta original;
- intent classificado;
- rota;
- SQL gerado;
- tempo de geracao de SQL;
- tempo de execucao SQLite;
- numero de linhas retornadas;
- colunas retornadas;
- erros de validacao.

## 18.2 Para a trilha ML

Registrar:

- pergunta original;
- alvo;
- horizonte;
- modelo usado;
- versao do dataset;
- versao das features;
- tempo de inferencia;
- metricas de validacao;
- valor previsto;
- nota de confianca.

## 18.3 Para a camada LLM

Registrar:

- tamanho do prompt;
- tempo de resposta;
- trilha de origem;
- versao do contrato de prompt.

## 18.4 Para auditoria de previsao

Registrar por inferencia:

- data da inferencia;
- ultima data observada usada como fronteira;
- features de entrada relevantes;
- valor previsto;
- valor real futuro, quando existir e estiver disponivel;
- erro apos backfill de avaliacao.

Isso permite:

- medir degradacao do modelo ao longo do tempo;
- reprocessar historico de previsoes;
- comparar se o modelo esta melhorando ou piorando.

## 19. Roadmap de implementacao

## Fase 0 - Consolidacao arquitetural

Objetivo:

- fechar o desenho da solucao;
- congelar responsabilidades;
- definir contratos.

Entregaveis:

- este plano tecnico;
- taxonomia de perguntas;
- estrutura de pastas alvo.

## Fase 1 - Refatoracao da camada de dados

Objetivo:

- sair da dependencia do notebook como unico orquestrador.

Acoes:

- centralizar acesso ao `volve_ml_ready.db`;
- encapsular leitura e metadados;
- padronizar repositorio SQLite.

Critereos de aceite:

- consultas SQL podem ser executadas por funcoes reutilizaveis fora do notebook.

## Fase 2 - Endurecimento da trilha SQL

Objetivo:

- tornar a consulta historica confiavel e barata.

Acoes:

- templates SQL simples;
- templates SQL analiticos;
- manter `llm_sql_fallback` apenas para casos nao cobertos;
- validador de SQL;
- metadados das colunas retornadas.

Critereos de aceite:

- perguntas historicas comuns resolvidas sem depender do modelo local;
- latencia muito menor nos casos frequentes.

## Fase 3 - Implementacao do router de intencao

Objetivo:

- separar automaticamente historico de previsao.

Acoes:

- regras por palavras-chave;
- score de confianca;
- fallback para ambiguidades.

Critereos de aceite:

- perguntas preditivas nao caem mais na trilha SQL por acidente.

## Fase 4 - Baselines de forecast

Objetivo:

- estabelecer linha de base forte antes do `XGBoost`.

Acoes:

- ultimo valor;
- media movel curta;
- tendencia linear curta;
- avaliacao walk-forward.

Critereos de aceite:

- relatorio comparativo com metricas por alvo e horizonte.

## Fase 5 - Implementacao do XGBoost

Objetivo:

- testar se ha ganho real sobre os baselines.

Acoes:

- montar dataset supervisionado;
- treinar regressao para `BORE_OIL_VOL` e `BORE_WAT_VOL`;
- validar em `D+1` e `D+3`;
- comparar contra baselines.

Critereos de aceite:

- so avancar se houver ganho tecnico defensavel.

## Fase 6 - Servico de previsao

Objetivo:

- empacotar inferencia e contratos da trilha ML.

Acoes:

- classe `forecast_service`;
- funcoes por alvo e horizonte;
- saida padronizada;
- nota de confianca e limitacao.

Critereos de aceite:

- previsao pode ser chamada sem notebook.

## Fase 7 - Camada de explicacao

Objetivo:

- unificar a resposta final das duas trilhas.

Acoes:

- contrato de narrativa unico;
- prompts especificos para resultado SQL e resultado ML;
- explicacao mais curta, objetiva e consistente.

Critereos de aceite:

- respostas finais deixam claro se vieram de historico ou de previsao.

## Fase 8 - Streamlit

Objetivo:

- disponibilizar uso pratico em interface.

Acoes:

- paginas de exploracao;
- pagina de previsao;
- pagina de debug;
- graficos e exportacao de relatorios.

Critereos de aceite:

- usuario consegue consultar historico e pedir previsao pela mesma aplicacao.

## Fase 9 - Validacao operacional

Objetivo:

- testar se a experiencia faz sentido para engenharia de producao.

Acoes:

- revisar linguagem das perguntas;
- revisar utilidade dos graficos;
- revisar interpretabilidade das previsoes;
- ajustar thresholds e textos.

Critereos de aceite:

- perguntas operacionais comuns sao respondidas sem expor nome de coluna ao usuario.

## 20. Riscos tecnicos e mitigacoes

## Risco 1 - Dataset curto demais para forecast robusto

Mitigacao:

- usar baselines fortes;
- limitar horizonte;
- rotular forecast como experimental;
- nao prometer precisao de producao.

## Risco 2 - Sobreajuste do XGBoost

Mitigacao:

- usar parametros conservadores;
- reduzir numero de features se necessario;
- validar com walk-forward;
- comparar contra baselines em toda iteracao.

## Risco 3 - Router classificar errado

Mitigacao:

- regras simples e transparentes primeiro;
- logs de classificacao;
- fallback em caso ambiguo.

## Risco 4 - SQL continuar central demais

Mitigacao:

- templates primeiro, LLM depois;
- medir porcentagem de perguntas resolvidas sem LLM local.

## Risco 5 - Explicacao final misturar historico com previsao

Mitigacao:

- contrato de resposta com campo `route`;
- prompts separados por trilha;
- debug visivel no Streamlit.

## 21. Criterios de sucesso do programa

O programa sera considerado bem sucedido se atingir os pontos abaixo:

- a rota `historico` responder bem perguntas descritivas e analiticas comuns;
- a rota `forecast` responder previsoes `D+1` e `D+3` com metodo claro;
- a aplicacao Streamlit apresentar graficos e tabelas confiaveis;
- o usuario nao precisar conhecer nomes de colunas para perguntar;
- o `XGBoost` so entrar em producao se superar baselines com evidencia;
- a camada LLM permanecer focada em interface e explicacao, nao em inventar previsao.

## 22. Decisoes recomendadas para agora

## Decisao 1

Parar de tratar perguntas de previsao como problema principal de `text-to-sql`.

## Decisao 2

Separar o projeto em duas trilhas formais:

- `consulta_historica_sql`
- `previsao_ml`

## Decisao 3

Implementar `baselines` antes de `XGBoost`.

## Decisao 4

Usar `XGBoost` apenas se ele realmente superar os baselines.

## Decisao 5

Planejar a aplicacao Streamlit desde ja como consumidora de duas trilhas tecnicas independentes.

## 23. Proximos passos imediatos

1. Extrair a camada SQLite do notebook para modulo reutilizavel.
2. Implementar taxonomia de perguntas e router por regras.
3. Criar baselines de forecast para oleo e agua.
4. Montar avaliacao walk-forward.
5. Medir se o dataset sustenta `D+1` e `D+3`.
6. So depois testar `XGBoost`.
7. Em paralelo, preparar a estrutura do app Streamlit.

## 24. Conclusao

O caminho mais tecnico, limpo e sustentavel para este projeto nao e insistir em fazer previsao pela trilha SQL. O caminho correto e:

- `SQL` para passado e exploracao;
- `ML` para futuro e risco;
- `LLM` para interpretar, rotear e explicar;
- `Streamlit` como camada de uso operacional.

Essa separacao reduz retrabalho, melhora a qualidade tecnica das respostas e cria uma base muito mais solida para evolucao do sistema.

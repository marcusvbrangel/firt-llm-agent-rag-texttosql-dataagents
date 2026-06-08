# Plano de Acao - Melhoria Gradual das Execucoes no Projeto Volve

**Data:** 2026-06-08

**Escopo:** melhoria gradual do fluxo `pergunta -> SQL local -> execucao SQLite -> resposta remota`, sem buscar otimização extrema nem mudança de arquitetura.

## Objetivo

Melhorar de forma incremental:

1. Observabilidade da execucao.
2. Qualidade e estabilidade do SQL gerado.
3. Qualidade da interpretacao da LLM remota.
4. Qualidade do relatorio final de execucao.

## Diagnostico atual

Os principais problemas observados no fluxo atual sao:

- o relatorio mostra apenas tempo total por pergunta;
- nao ha separacao entre tempo de geracao de SQL, tempo de execucao do banco e tempo de resposta remota;
- alguns SQLs ainda usam padroes frageis para `MAX/MIN` com data associada;
- aliases nem sempre sao legiveis;
- a resposta remota ainda pode usar linguagem vaga para unidades e conceitos;
- o relatorio ainda informa pouco para depuracao e comparacao entre execucoes.

## Estrategia de melhoria

### Etapa 1 - Medir melhor

Adicionar ao notebook:

- `sql_generation_time`
- `sql_execution_time`
- `remote_response_time`
- `total_time`
- tamanho do prompt local enviado
- tamanho do prompt remoto enviado

**Objetivo da etapa:** descobrir com precisao onde esta o gargalo do pipeline.

**Resultado esperado:**

- distinguir gargalo do `SQLite` versus gargalo do modelo local ou remoto;
- comparar perguntas simples e perguntas mais lentas;
- criar base para otimizacoes posteriores sem adivinhacao.

### Etapa 2 - Estabilizar o SQL gerado

Melhorias sugeridas:

- padrao obrigatorio para `max/min + data`: usar `ORDER BY ... DESC/ASC LIMIT 1`;
- evitar `SELECT DATEPRD, MAX(...)` com coluna nao agregada solta;
- exigir alias claros para agregacoes;
- validar automaticamente padroes SQL indesejados;
- permitir uma reescrita automatica quando o SQL vier ruim.

**Objetivo da etapa:** melhorar robustez, legibilidade e previsibilidade das consultas.

### Etapa 3 - Melhorar a semantica da resposta remota

Melhorias sugeridas:

- sempre enviar o dicionario de dados para o modelo remoto;
- enviar tambem o contexto das colunas retornadas pela consulta;
- reforcar regras para:
  - uso correto de unidades;
  - diferenca entre coluna medida e feature derivada;
  - interpretacao de series temporais;
  - interpretacao de metricas de producao offshore.

**Objetivo da etapa:** fazer a resposta remota entender melhor conceitos de producao de petroleo e variaveis derivadas de analytics.

### Etapa 4 - Enriquecer o relatorio de execucao

Melhorias sugeridas:

- mostrar tempos por etapa;
- mostrar tamanho dos prompts;
- mostrar colunas retornadas;
- mostrar numero de linhas retornadas;
- mostrar observacoes sobre padrao do SQL;
- mostrar media por etapa no sumario final.

**Objetivo da etapa:** transformar o relatorio em ferramenta de auditoria tecnica e comparacao entre execucoes.

## Ordem recomendada de implementacao

1. Instrumentacao de tempos e tamanho de prompts.
2. Guardrails e padroes de SQL.
3. Melhorias do contexto semantico para a LLM remota.
4. Relatorio mais rico e mais auditavel.

## O que nao fazer agora

Para manter a melhoria gradual, nao priorizar neste momento:

- Streamlit;
- fine-tuning;
- troca de modelo;
- arquitetura mais complexa;
- otimizacoes prematuras sem medicao.

## Implementacao imediata

Implementar agora a **Etapa 1 - Medir melhor**, incluindo:

- tempo de geracao do SQL;
- tempo de execucao da consulta SQL;
- tempo de resposta da LLM remota;
- tempo total por pergunta;
- tamanho do prompt local;
- tamanho do prompt remoto.

# Base de Conhecimento - Performance do Fluxo Volve

**Ultima atualizacao:** 2026-06-08

## Problema

O fluxo de geracao de SQL para o dataset Volve pode levar muitos minutos para concluir um lote pequeno de perguntas, mesmo com banco local muito pequeno.

## Sintoma observado

- execucao interrompida manualmente apos cerca de 10 minutos;
- `KeyboardInterrupt` ocorreu durante `ollama_client.chat(...)`;
- o relatorio em disco mostrava sucesso de uma execucao anterior, nao da tentativa interrompida.

## Causa raiz confirmada

O gargalo principal e a etapa de geracao de SQL local com `Ollama`.

Evidencias:

- a maior parte do tempo medio do pipeline estava em `sql_generation_time`;
- o `SQLite` executa rapido e nao explica a demora;
- o prompt local estava grande demais para perguntas muito simples;
- o prompt remoto tambem estava maior do que o necessario.

## O que nao e o gargalo principal

- `SQLite` local
- volume de linhas da tabela atual
- agregacoes simples como `MAX`, `AVG` e `ORDER BY ... LIMIT 1`

## Decisoes tecnicas aplicadas

### Diretriz fixa

Manter o prompt remoto reduzido.

Interpretacao consolidada:

- se a resposta remota perder qualidade, a primeira suspeita deve ser o contrato de contexto vindo do SQL local;
- nao aumentar novamente o prompt remoto como primeira reacao;
- corrigir primeiro alias, metadado de coluna retornada e mapeamento entre coluna de saida e coluna de origem.

### Decisao 1

Nao enviar o dicionario completo para o modelo local em todas as perguntas.

Aplicacao:

- usar contexto local enxuto por pergunta;
- destacar apenas colunas relevantes ou fallback pequeno.

### Decisao 2

Diminuir o budget de geracao local.

Aplicacao:

- `LOCAL_SQL_NUM_PREDICT=80` por padrao.

### Decisao 3

Nao enviar o dicionario completo para o modelo remoto.

Aplicacao:

- usar apenas metadados das colunas retornadas pela consulta.

## Arquivos envolvidos

- notebook alvo:
  - `notebooks/07-exercicio-dados-reais-producao-volve-noruega.ipynb`
- relatorio avaliado:
  - `notebooks/relatorio_dados_reais_producao_volve_noruega.md`
- plano especifico:
  - `notebooks/plano_acao_performance_fluxo_volve.md`

## Risco residual apos a otimização

Otimizar prompt e budget pode reduzir latencia, mas ha dois riscos:

- perda de contexto em perguntas mais ambiguas;
- resposta local curta demais se `num_predict` ficar apertado para algum caso fora do conjunto atual.

## Como diagnosticar rapidamente nas proximas execucoes

Verificar nesta ordem:

1. `Tempo de Geracao do SQL`
2. `Tempo de Resposta Remota`
3. `Tamanho do Prompt Local`
4. `Tamanho do Prompt Remoto`
5. SQL gerado
6. resposta final

Interpretacao:

- se `Tempo de Geracao do SQL` dominar, o gargalo continua local;
- se o prompt local subir muito, ha regressao de contexto;
- se a resposta remota piorar sem ganho de tempo, o corte de contexto remoto ficou agressivo.

## Regra operacional importante

Se a execucao for interrompida antes do fim do loop, o relatorio final pode nao representar a tentativa interrompida. Antes de confiar no Markdown em disco, conferir se a execucao chegou ao ponto de gravacao do arquivo.

## Proximos passos recomendados

- medir novamente os 6 casos apos as mudancas;
- se ainda houver demora alta, testar `qwen2.5-coder:3b-instruct`;
- se a interrupcao humana continuar frequente, salvar relatorio incremental apos cada caso.

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

## Ajustes aplicados ate aqui

### Ajuste 1

Reducao forte do contexto enviado ao modelo local.

Objetivo:

- parar de mandar dicionario completo em toda pergunta;
- focar nas colunas mais relevantes para cada caso.

### Ajuste 2

Reducao do budget de geracao local.

Aplicacao:

- `LOCAL_SQL_NUM_PREDICT=80`

### Ajuste 3

Normalizacao do SQL gerado.

Objetivo:

- remover alias ruins em colunas base;
- preservar o nome original das colunas medidas;
- melhorar o contrato semantico com a etapa remota.

### Ajuste 4

Mapeamento entre alias e coluna de origem.

Objetivo:

- fazer a resposta remota entender corretamente unidade e significado da coluna;
- reduzir interpretacoes erradas por parte do modelo remoto.

### Ajuste 5

Criacao de `fast path` deterministico para perguntas simples.

Objetivo:

- tirar perguntas triviais do caminho do `Ollama`;
- reduzir custo de tempo onde nao ha necessidade de inferencia generativa.

## Resultado importante ja obtido

Em uma rodada validada de perguntas simples:

- 6 de 6 perguntas tiveram sucesso;
- media aproximada de 4 segundos por pergunta;
- tempo de geracao de SQL praticamente zerado nesses casos;
- prompt remoto ficou muito menor do que no fluxo antigo.

## Historico dos nossos sofrimentos

### Sofrimento 1 - Interrupcao por demora excessiva

Fato observado:

- a execucao foi interrompida manualmente depois de cerca de 10 minutos;
- o `KeyboardInterrupt` ocorreu no meio do `ollama_client.chat(...)`.

Licao:

- antes de pensar em trocar banco ou reescrever tudo, era necessario confirmar o gargalo real;
- o gargalo real foi a etapa local de SQL.

### Sofrimento 2 - Tentar resolver tudo com a mesma trilha

Problema:

- perguntas simples, analiticas e preditivas estavam pressionando a mesma arquitetura `pergunta -> SQL -> resposta`;
- isso fez o sistema parecer mais geral do que realmente era.

Licao:

- historico e previsao nao devem ser tratados como o mesmo tipo de problema.

### Sofrimento 3 - Culpar o prompt remoto pela coisa errada

Problema potencial:

- havia risco de aumentar novamente o prompt remoto toda vez que a qualidade caia.

Conclusao consolidada:

- a qualidade remota nao deve ser corrigida primeiro por aumento de contexto;
- a primeira suspeita deve ser contexto ruim vindo do SQL local.

### Sofrimento 4 - Perguntas irreais de avaliacao

Problema:

- parte das perguntas de teste usava nomes de colunas e formulas como se um operador falasse em linguagem de banco.

Impacto:

- o teste ficou artificial;
- a avaliacao deixou de representar linguagem natural de engenharia de producao.

Licao:

- perguntas precisam ser operacionais e naturais;
- schema e formulas devem ficar dentro do sistema.

## Erros e desafios ainda abertos

### Desafio 1

Perguntas historicas analiticas ainda podem exigir demais do modelo local quando nao existe template nem `fast path`.

### Desafio 2

Perguntas de previsao continuam sendo o ponto de maior risco arquitetural se forem tratadas como extensao do `text-to-sql`.

### Desafio 3

O dataset atual tem cerca de 125 linhas, o que exige muita disciplina antes de adotar `XGBoost` como solucao principal.

### Desafio 4

O notebook ainda concentra responsabilidades demais:

- acesso a dados;
- definicao de schema;
- geracao de SQL;
- execucao;
- resposta final;
- relatorio.

## Virada arquitetural registrada

Ficou consolidado que:

- `SQL` deve responder passado, exploracao, relatorios, comparacoes e graficos;
- `ML` deve responder previsao, tendencia futura, risco e mudanca de regime;
- `LLM` deve servir como camada de interface, roteamento e explicacao.

Documento principal dessa virada:

- `plano-tecnico-consultas-sql-versus-machine-learning.md`

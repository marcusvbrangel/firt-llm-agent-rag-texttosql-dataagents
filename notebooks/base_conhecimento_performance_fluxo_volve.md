# Base de Conhecimento - Performance do Fluxo Volve

**Ultima atualizacao:** 2026-06-10

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

## Atualizacao operacional - Notebook 09 - 2026-06-10

### O que virou verdade tecnica no notebook 09

O `notebooks/09-exercicio.ipynb` consolidou uma trilha remota mais barata e mais observavel:

- SQL remoto via `deepseek/deepseek-chat`
- resposta final remota via `google/gemini-2.5-flash`
- banco local `SQLite` em modo somente leitura
- contexto SQL com ordem preparada para favorecer caching estrutural
- resposta final curta e operacional
- instrumentacao de tempo e tamanho de contexto

### Configuracao oficial dos modelos

No notebook 09, a configuracao oficial deve ficar no topo e sem camadas intermediarias:

- `REMOTE_SQL_MODEL = "deepseek/deepseek-chat"`
- `REMOTE_TEXT_MODEL = "google/gemini-2.5-flash"`

Regra de manutencao:

- se o usuario quiser trocar modelos, a mudanca deve acontecer somente nessas duas linhas;
- o restante do notebook deve consumir exatamente essas variaveis.

### Causa raiz de uma falha cara que foi eliminada

Foi confirmado que a primeira tentativa de SQL falhava por inducao do proprio contexto:

- o few-shot usava `oil_roll_mean_30`;
- a coluna existente na base e `oil_roll_30`.

Impacto:

- falha em `SQLite`;
- segunda chamada paga ao modelo;
- aumento de latencia;
- ruido na avaliacao.

Regra consolidada:

- qualquer ajuste futuro em exemplos de prompt deve ser conferido contra o schema real da tabela `volve_ml_ready`.

### Perguntas de teste deixaram de ser artificiais

O banco de perguntas foi reescrito para linguagem humana de operador.

Antes:

- perguntas citavam nomes de colunas SQL;
- a avaliacao era artificial.

Agora:

- perguntas falam em producao, pressao de fundo, horas em operacao, risco de agua, oscilacao e instabilidade;
- o sistema interno faz o mapeamento para colunas e indicadores.

Licao:

- schema pertence ao sistema;
- linguagem operacional pertence ao usuario.

### Contrato novo da resposta final

A resposta final do notebook 09 deve obedecer ao seguinte contrato:

- primeira linha em formato `Diagnóstico: ...`
- no maximo 2 paragrafos curtos depois disso
- sem saudacao
- sem tom de relatorio executivo
- sem bloco de codigo
- se houver tabela, ela deve ser compacta
- se houver recomendacao, ela deve ser concreta e operacional

### Ajuste importante no contexto da resposta

Os dados enviados ao modelo final passaram a ser formatados para leitura humana.

Exemplo importante:

- `oil_pct_change_1d = 0.15129` deve entrar como `15.13%`

Motivo:

- reduz ambiguidade;
- melhora a qualidade da resposta;
- evita que o operador veja um valor fracionario cru que exige interpretacao.

### Instrumentacao obrigatoria do fluxo

O notebook 09 passou a carregar rastros internos com dois interruptores:

- `DEBUG_METHOD_TRACE = True`
- `TRACE_OPERATION_METRICS = True`

Esses rastros passaram a ser parte do desenho do sistema, nao detalhe opcional.

O que medir a partir deles:

1. tempo total do pipeline
2. tempo de geracao do SQL
3. tempo de execucao do SQLite
4. tempo da resposta remota
5. tamanho do prompt SQL
6. tamanho do prompt da resposta final
7. tamanho do SQL gerado
8. tamanho da resposta final

### Leitura correta dos rastros

Se o custo ou a latencia piorarem, investigar nesta ordem:

1. se o prompt SQL cresceu demais
2. se o contexto da resposta final cresceu demais
3. se houve retry por erro de schema
4. se o SQL remoto ficou mais verboso ou menos disciplinado
5. se a resposta final voltou a ficar explicativa demais

### Regra de log confiavel

Foi corrigido um erro de observabilidade:

- o log dizia `Claude` mesmo quando o modelo ativo era outro.

Regra nova:

- log deve sempre refletir `REMOTE_SQL_MODEL` ou `REMOTE_TEXT_MODEL` reais;
- diagnostico por log so vale se o log disser a verdade.

### Regra de apresentacao terminal

Antes da resposta final impressa ao usuario, o notebook agora emite uma linha separadora.

Motivo:

- separar rastros tecnicos de mensagem operacional;
- melhorar legibilidade em execucao terminal.

### Regra de higiene do arquivo ipynb

Para preservar leitura e versionamento:

- limpar `outputs`
- zerar `execution_count`
- nao commitar residuos de respostas antigas dentro do notebook

### Checklist de manutencao futura do notebook 09

Sempre que houver mudanca relevante:

1. validar o JSON do notebook
2. extrair a celula e compilar o codigo
3. checar se os modelos do topo ainda sao os usados de fato
4. verificar se o few-shot continua alinhado ao schema real
5. rodar pelo menos uma pergunta real e observar os traces

### Regra final de paz

Para manter o notebook 09 barato, confiavel e menos sofrido:

- nao reintroduzir nomes de colunas errados no contexto;
- nao deixar a resposta final crescer sem necessidade;
- nao voltar a escrever perguntas como se o usuario fosse DBA;
- nao aceitar logs mentirosos;
- nao discutir custo sem olhar tempo e tamanho de contexto.

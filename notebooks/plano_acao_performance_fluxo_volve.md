# Plano de Acao - Performance do Fluxo Volve

**Data:** 2026-06-08

**Escopo:** `notebooks/07-exercicio-dados-reais-producao-volve-noruega.ipynb`

## Objetivo

Reduzir a latencia do fluxo `pergunta -> SQL local -> SQLite -> resposta remota` sem trocar a arquitetura agora.

## Diagnostico confirmado

Evidencias do relatorio atual:

- tempo medio total por pergunta: `49.83 s`
- tempo medio de geracao de SQL local: `41.83 s`
- tempo medio da resposta remota: `7.96 s`
- tempo medio de execucao SQL: `0.00 s`
- prompt local medio: `22661.83` caracteres
- prompt remoto medio: `20752.50` caracteres

Conclusao:

- o gargalo principal esta no `Ollama`, nao no `SQLite`;
- o prompt local esta grande demais para a complexidade das perguntas;
- o prompt remoto tambem esta carregando contexto demais.

## Acoes implementadas hoje

### 1. Contexto local enxuto por pergunta

Mudanca aplicada:

- o prompt local nao envia mais o dicionario completo em toda pergunta;
- o notebook agora monta um contexto enxuto com colunas mais relevantes para a pergunta;
- quando nao houver match claro, o notebook usa um conjunto pequeno de colunas de fallback.

Resultado esperado:

- reduzir tokens processados pelo modelo local;
- manter a precisao semantica para SQL simples;
- diminuir latencia media da etapa local.

### 2. Reducao do budget de geracao no Ollama

Mudanca aplicada:

- `num_predict` local caiu de `220` para `80`;
- a configuracao ficou exposta via `LOCAL_SQL_NUM_PREDICT`.

Resultado esperado:

- reduzir o tempo gasto para produzir uma query curta;
- evitar que o modelo desperdice geracao em texto inutil.

### 3. Prompt remoto sem dicionario completo

Mudanca aplicada:

- a etapa remota agora recebe apenas:
  - pergunta;
  - metadados das colunas retornadas;
  - dados retornados pelo banco.

Resultado esperado:

- reduzir latencia remota;
- diminuir custo e ruido semantico;
- manter as unidades corretas a partir do contexto realmente usado na resposta.

## Validacao recomendada

Executar nesta ordem:

1. Rodar `TEST_QUESTIONS_LIMIT=1` com uma pergunta simples.
2. Confirmar que o SQL continua correto.
3. Registrar novo tamanho de prompt local e remoto.
4. Rodar os 6 casos novamente.
5. Comparar com o relatorio antigo:
   - media de tempo de geracao SQL;
   - media de tempo remoto;
   - media de tamanho dos prompts;
   - taxa de acerto do SQL.

## Criterios de sucesso

- queda visivel do tempo medio de geracao de SQL;
- queda visivel no tamanho do prompt local;
- queda visivel no tamanho do prompt remoto;
- nenhuma regressao de acuracia nos 6 casos de teste atuais.

## Proximas acoes se ainda ficar lento

### Prioridade alta

- salvar relatorio parcial por caso para nao perder resultado em `KeyboardInterrupt`;
- adicionar timeout por etapa com mensagem mais objetiva;
- comparar `qwen2.5-coder:7b-instruct` com `qwen2.5-coder:3b-instruct`.

### Prioridade media

- criar cache do contexto local por pergunta;
- manter um resumo compacto do schema em vez do schema inteiro;
- separar perguntas simples de perguntas analiticas mais pesadas.

### Prioridade baixa

- avaliar troca de arquitetura apenas depois de medir as melhorias acima.


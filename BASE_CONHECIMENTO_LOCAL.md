# Base de Conhecimento Local

Ultima consolidacao: 2026-06-08

## Objetivo

Este arquivo registra as correcoes, evolucoes, requisitos atuais, melhorias aplicadas, sugestoes e erros aprendidos nos notebooks do projeto. O foco e evitar retrabalho, reduzir erros recorrentes e manter um ponto unico de referencia tecnica.

## Escopo Atual

Arquivos principais envolvidos:

- `notebooks/05-exercicio-open-router.ipynb`
- `notebooks/05-exercicio-open-router-corrigido.ipynb`
- `notebooks/06-exercicio-modelo-local-e-remoto.ipynb`
- `notebooks/07-exercicio-dados-reais-producao-volve-noruega.ipynb`
- `notebooks/relatorio_estresse.md`
- `notebooks/relatorio_modelo_local_e_remoto.md`
- `notebooks/relatorio_dados_reais_producao_volve_noruega.md`
- `notebooks/base_conhecimento_performance_fluxo_volve.md`
- `plano-tecnico-consultas-sql-versus-machine-learning.md`

## Dependencias e Ambiente

Dependencias operacionais relevantes:

- `nbformat` para leitura e regravacao segura de notebooks.
- `ollama` para inferencia local.
- Cliente Python `openai` para acesso ao OpenRouter.
- Banco SQLite local para execucao do SQL.

Comandos importantes:

- Instalar `nbformat`: `pip install nbformat`
- Iniciar Ollama: `ollama serve`
- Baixar modelo local: `ollama pull qwen2.5-coder:7b-instruct`

Observacao operacional:

- Em maquina sem GPU dedicada ou com CPU mais modesta, `qwen2.5-coder:7b-instruct` pode ficar mais lento.
- Nessa situacao, a alternativa manual mais segura e testar `qwen2.5-coder:3b-instruct`.

## Estado Estavel Consolidado

### Notebook 05 - OpenRouter

Estado esperado:

- Geracao de SQL e resposta final usando OpenRouter.
- Modelo atual fixado em `anthropic/claude-sonnet-4.6`.
- Relatorio salvo em `notebooks/relatorio_estresse.md`.
- Existe uma copia protegida em `notebooks/05-exercicio-open-router-corrigido.ipynb` para reduzir risco de sobrescrita.

Decisoes atuais:

- Nao usar lista de fallback de modelos.
- Usar apenas uma variavel de modelo para previsibilidade operacional.
- Integracao feita com cliente `openai.OpenAI` apontando para `https://openrouter.ai/api/v1`.

### Notebook 06 - Modelo local + remoto

Arquitetura atual:

- SQL gerado localmente com `Ollama`.
- SQL executado localmente no SQLite.
- Resposta final redigida remotamente pelo OpenRouter.

Modelos atuais:

- `LOCAL_SQL_MODEL = qwen2.5-coder:7b-instruct`
- `REMOTE_RESPONSE_MODEL = anthropic/claude-sonnet-4.6`

Motivacao:

- Reduzir consumo de creditos remotos.
- Manter a etapa mais cara de raciocinio tecnico simples e local.
- Usar o modelo remoto apenas na etapa de redacao final.

## Correcoes e Evolucoes Aplicadas

### 1. Reorganizacao estrutural do notebook 05

Antes:

- Notebook mal formatado.
- Blocos grandes e pouco legiveis.
- Indentacao irregular distorcendo a logica condicional.
- Alto risco de erros ao editar.

Depois:

- Notebook reorganizado em secoes mais claras.
- Separacao entre configuracao, funcoes, grafo e geracao de relatorio.
- Melhor legibilidade para depuracao e manutencao.

### 2. Correcao de indentacao irregular

Problema:

- Havia varios pontos com indentacao inconsistente que alteravam o fluxo do Python.

Impacto:

- Condicionais e tratamentos de erro ficavam semanticamente incorretos.
- O notebook podia aparentar estar "rodando rapido" apenas porque falhava cedo.

Correcao:

- Reestruturacao dos blocos Python.
- Revisao da logica condicional para refletir o fluxo esperado.

### 3. Correcao da integracao com OpenRouter

Problema encontrado:

- Erro semelhante a `'str' object has no attribute 'model_dump'`.

Causa provavel:

- Incompatibilidade entre o wrapper usado anteriormente e o formato de resposta recebido do OpenRouter.

Correcao aplicada:

- Substituicao da integracao anterior por `openai.OpenAI`.
- Base URL padronizada para `https://openrouter.ai/api/v1`.

### 4. Correcao de modelo remoto invalido

Problema encontrado:

- Uso anterior de nome de modelo sem endpoint disponivel.
- Exemplo de falha: `anthropic/claude-3.5-sonnet`.

Erro observado:

- Resposta `404` com ausencia de endpoint valido.

Correcao aplicada:

- Modelo consolidado em `anthropic/claude-sonnet-4.6`.

### 5. Remocao do mecanismo de fallback remoto

Problema:

- Fallback multiplo torna custo, latencia e diagnostico menos previsiveis.

Correcao aplicada:

- Substituicao por uma configuracao de modelo unico.
- Isso simplifica rastreabilidade e facilita saber exatamente qual modelo funcionou.

### 6. Melhorias no relatorio de erro

Melhorias:

- Mensagens mais explicitas.
- Registro de tipo de excecao.
- Maior clareza quando o erro e de API, modelo, autenticacao ou conectividade.

### 7. Correcao do caminho de saida do relatorio

Estado atual:

- O relatorio do notebook 05 deve ser salvo em `notebooks/relatorio_estresse.md`.
- O relatorio do notebook 06 deve ser salvo em `notebooks/relatorio_modelo_local_e_remoto.md`.

### 8. Protecao contra sobrescrita percebida

Problema:

- Houve indicio de que o notebook corrigido estava sendo regravado ou sobrescrito por outra alteracao.

Acao tomada:

- Criacao de uma copia de referencia: `notebooks/05-exercicio-open-router-corrigido.ipynb`.

### 9. Migracao para arquitetura hibrida no notebook 06

Nova regra:

- Geracao de SQL: local.
- Execucao do SQL: local.
- Resposta final: remota.

Beneficios:

- Menor uso de credito.
- Melhor controle do pipeline.
- Separacao clara entre raciocinio estruturado e redacao final.

## Novos Requisitos Consolidados

### Requisito 1. Modelo remoto fixo

- Usar `anthropic/claude-sonnet-4.6`.
- Nao usar fallback de modelos no notebook 05 e no notebook 06.

### Requisito 2. Modelo local fixo por padrao

- Usar `qwen2.5-coder:7b-instruct` no `Ollama`.
- Se a CPU ficar lenta, usar `qwen2.5-coder:3b-instruct` como opcao manual.

### Requisito 3. Separacao de responsabilidades

- Modelo local gera SQL.
- Banco local executa SQL.
- Modelo remoto redige a resposta final.

### Requisito 4. Persistencia de relatorios

- Sempre salvar os relatorios em arquivo Markdown.
- Os relatorios sao parte do diagnostico, nao apenas saida auxiliar.

## Erros Aprendidos e Como Nao Repetir

### Erro recorrente 1. Notebook visualmente baguncado

Sintoma:

- Celulas grandes, fluxo dificil de seguir, blocos misturados.

Risco:

- Facilita erro de indentacao.
- Aumenta chance de mexer em parte errada do notebook.

Prevencao:

- Separar o notebook em secoes pequenas.
- Isolar configuracao, funcoes, grafo, execucao e relatorio.

### Erro recorrente 2. Indentacao irregular alterando a logica

Sintoma:

- `if`, `try`, `except`, `for` e `return` fora do nivel correto.

Risco:

- Fluxo condicional muda sem que isso fique obvio.
- O notebook pode parar cedo e parecer rapido.

Prevencao:

- Revisar blocos Python apos toda grande edicao.
- Validar a celula como codigo Python antes de considerar a correcao concluida.

### Erro recorrente 3. Quebra de strings ao editar `.ipynb`

Sintoma:

- Strings como `"\n"` ficam quebradas em varias linhas dentro do JSON do notebook.

Risco:

- Gera erro de sintaxe.
- Gera markdown ou relatorio corrompido.

Prevencao:

- Evitar edicoes manuais desestruturadas dentro do JSON do notebook.
- Validar as celulas com parse Python depois de regravar o `.ipynb`.

### Erro recorrente 4. Nome de modelo incorreto no provedor

Sintoma:

- O nome do modelo existe em outro contexto, mas nao no endpoint usado.

Exemplos importantes:

- Nome remoto estavel: `anthropic/claude-sonnet-4.6`
- Nome local no Ollama: `qwen2.5-coder:7b-instruct`
- Nao confundir com nome estilo Hugging Face: `Qwen2.5-Coder-7B-Instruct`

Prevencao:

- Sempre usar o nome exato aceito pelo provedor que vai atender a requisicao.

### Erro recorrente 5. Wrapper inadequado para a API

Sintoma:

- Erros de serializacao ou acesso a propriedades que nao existem.

Prevencao:

- Para OpenRouter neste projeto, usar `openai.OpenAI` com `base_url` explicito.

### Erro recorrente 6. Interpretar falha rapida como boa performance

Sintoma:

- Execucao antiga parecia mais rapida.

Causa provavel:

- O fluxo falhava antes de chamar corretamente o modelo remoto ou antes de concluir todas as etapas.

Licao:

- Tempo baixo com erro precoce nao significa pipeline eficiente.

### Erro recorrente 7. Resposta final inventando conclusoes

Sintoma:

- O texto afirma exclusividade ou comparacoes nao suportadas pelo resultado SQL.

Exemplo:

- Dizer que `FIELD-X` era o unico campo apenas porque a consulta usou `LIMIT 1`.

Prevencao:

- A resposta final deve se limitar ao que esta nos resultados retornados.
- Se a pergunta exigir exclusividade, a consulta precisa comprovar isso.

### Erro recorrente 8. Dependencia local nao disponivel

Sintoma:

- `Ollama` desligado.
- Modelo local nao baixado.
- Falha ao conectar no host local.

Prevencao:

- Rodar `ollama serve`.
- Baixar o modelo com `ollama pull qwen2.5-coder:7b-instruct`.
- Confirmar que o modelo esta disponivel antes da execucao principal.

## Checklists Operacionais

### Checklist antes de rodar o notebook 05

1. Confirmar `OPENROUTER_API_KEY` configurada.
2. Confirmar que o modelo remoto esta definido como `anthropic/claude-sonnet-4.6`.
3. Reiniciar o kernel.
4. Executar as celulas de cima para baixo.
5. Verificar se o relatorio foi salvo em `notebooks/relatorio_estresse.md`.

### Checklist antes de rodar o notebook 06

1. Iniciar `ollama serve`.
2. Garantir que `qwen2.5-coder:7b-instruct` foi baixado.
3. Confirmar `OPENROUTER_API_KEY` configurada.
4. Reiniciar o kernel.
5. Executar as celulas de cima para baixo.
6. Verificar se o relatorio foi salvo em `notebooks/relatorio_modelo_local_e_remoto.md`.

## Melhorias Recomendadas

### Curto prazo

- Adicionar uma celula de pre-check no inicio dos notebooks para validar:
  - chave da OpenRouter
  - acesso ao banco
  - disponibilidade do Ollama
  - presenca do modelo local

- Endurecer o prompt da resposta final para proibir conclusoes nao sustentadas pelos dados retornados.

- Salvar relatorios com timestamp opcional para historico de execucoes.

### Medio prazo

- Extrair funcoes reutilizaveis dos notebooks para um modulo `.py`.
- Centralizar configuracoes de modelo e caminhos em um arquivo unico.
- Criar uma rotina automatica de validacao estrutural dos notebooks apos cada alteracao relevante.

### Longo prazo

- Implementar cache de esquema e contexto para reduzir latencia.
- Comparar `qwen2.5-coder:7b-instruct` com `qwen2.5-coder:3b-instruct` em custo x qualidade x tempo.
- Avaliar uma camada de guardrails para validar SQL e resposta final antes de gravar relatorio.

## Sugestoes de Governanca

- Manter sempre uma copia corrigida quando houver suspeita de sobrescrita.
- Nao editar celulas longas sem revalidar o notebook inteiro.
- Quando um erro for resolvido, registrar neste arquivo a causa raiz e a regra de prevencao.
- Tratar relatorio de execucao como evidencia tecnica.

## Resumo das Licoes Principais

- Notebook mal estruturado aumenta erro logico, nao apenas erro visual.
- Falha rapida pode mascarar baixa cobertura do fluxo real.
- Modelo correto e nome correto sao parte critica da estabilidade.
- SQL local + resposta final remota e uma boa estrategia para reduzir credito e manter qualidade.
- Sem registro de causa raiz, o projeto tende a repetir os mesmos erros.

## Consolidacao Volve - 2026-06-08

### 1. Sofrimento principal confirmado

No caso Volve, o sofrimento tecnico principal nao estava no `SQLite`. O gargalo dominante passou a ser a etapa local de geracao de SQL com `Ollama`, especialmente quando o sistema tentava responder perguntas de series temporais mais sofisticadas usando a mesma trilha de perguntas simples.

### 2. Diagnostico correto da queda de qualidade

Foi consolidada uma diretriz importante:

- manter o prompt remoto reduzido;
- nao culpar automaticamente a reducao do prompt remoto por qualquer perda de qualidade;
- tratar a qualidade do contexto local como suspeita principal.

Em outras palavras:

- se a resposta remota piorar, a primeira investigacao deve recair sobre SQL, aliases, metadados retornados e contexto enviado ao modelo remoto.

### 3. Ajustes efetivamente aplicados no notebook 07

Os principais ajustes feitos no fluxo Volve foram:

- contexto local enxuto por pergunta;
- reducao de `LOCAL_SQL_NUM_PREDICT` para `80`;
- normalizacao do SQL gerado;
- preservacao de nomes de colunas base sem alias desnecessario;
- mapeamento entre alias e coluna de origem;
- `fast path` deterministico para perguntas simples de maximo, minimo e media.

Esses ajustes reduziram latencia e melhoraram a consistencia sem precisar inflar novamente o prompt remoto.

### 4. Resultado tecnico importante obtido

Em uma rodada validada de perguntas simples:

- 6 de 6 casos tiveram sucesso;
- a media ficou por volta de 4 segundos por pergunta;
- a geracao de SQL ficou praticamente zerada nesses casos por causa do `fast path`;
- o prompt remoto ficou muito menor do que nas execucoes antigas.

### 5. Erro de avaliacao descoberto

Foi identificado um erro importante no desenho das perguntas de teste:

- perguntas estavam centradas em nomes de colunas e formulas;
- esse estilo nao representa a linguagem de um engenheiro de producao ou operador;
- o teste passou a medir familiaridade com schema, e nao aderencia a linguagem natural operacional.

Licao consolidada:

- perguntas de usuario real devem ser escritas em linguagem natural operacional;
- nomes de colunas devem ficar escondidos dentro do sistema.

### 6. Mudanca de direcao arquitetural

Foi consolidada uma conclusao mais estrutural:

- continuar tentando empurrar perguntas de previsao para dentro da trilha `linguagem natural -> SQL` consumiria muito tempo com retorno tecnico ruim;
- perguntas historicas e analiticas devem permanecer na trilha `SQL`;
- perguntas de previsao, tendencia futura, risco e mudanca de regime devem migrar para uma trilha `ML`.

Essa virada gerou o documento:

- `plano-tecnico-consultas-sql-versus-machine-learning.md`

### 7. Regra nova de arquitetura

Separacao recomendada a partir deste ponto:

- `SQL` para passado, exploracao, filtros, ranking, graficos e relatorios;
- `ML` para previsao de `D+1`, `D+3`, tendencia futura, risco e mudanca de regime;
- `LLM` para classificar intencao, rotear e explicar.

### 8. Desafios que permanecem abertos

- tirar a orquestracao principal de dentro do notebook;
- criar `router` de intencao confiavel;
- montar baselines de forecast antes de testar `XGBoost`;
- validar se um dataset com cerca de 125 linhas sustenta previsoes uteis de curto prazo;
- construir uma aplicacao Streamlit sem misturar responsabilidades.

## Regra de Memoria do Projeto

Este projeto nao deve guardar apenas a versao final das solucoes. A base de conhecimento precisa registrar:

- tentativas ruins;
- erros de arquitetura;
- interrupcoes;
- causas raiz;
- mudancas de direcao;
- e os sofrimentos tecnicos que levaram as decisoes atuais.

Sem esse historico, o projeto tende a repetir o mesmo custo em ciclos futuros.

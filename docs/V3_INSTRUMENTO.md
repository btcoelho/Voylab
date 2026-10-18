# TRONCO-01 v3: validar o instrumento antes de medir modelos

Pedido do Bruno a 18/10/2026, 06:43. Fases 1 a 5. Regras: sem treino; sem sementes reservadas; desenvolvimento, validação e cega separados; históricos intocados; até 3 rondas por fase; previsões escritas antes de cada corrida; descargas, APIs e merges só com aprovação caso a caso.

## Fase 1. A tarefa está bem posta?

### Previsões ex-ante (escritas a 18/10, antes de qualquer cálculo desta fase)
- **F1-a.** O prompt atual comunica apenas a leitura **só-cartas**: não há no texto nenhuma menção ao espaço de hipóteses nem ao suporte ≤ 2.
- **F1-b.** Sobre a árvore completa de estados de informação (todas as consultas possíveis com todas as respostas compatíveis com o estado inicial, e não só as respostas verdadeiras), a divergência entre as duas leituras fica entre 50% e 75% dos estados. A maior parte é `undetermined` (70) → `supported` (cartas).
- **F1-c.** Com o espaço comunicado, o veredicto de referência é função **apenas** do estado de informação: estados com a mesma vista pública canónica nunca recebem veredictos diferentes (0 colisões).
- **F1-d.** O **alvo**, pelo contrário, não é função do estado de informação, porque depende das respostas verdadeiras. Há estados de informação iguais (no início) com alvos diferentes. Isto não é um defeito: o alvo é uma referência do avaliador. Mas tem de constar da definição e não pode ser usado como "a resposta que o agente devia saber".
- **F1-e.** A consulta decisiva de k passos e a de 1 passo coincidem em toda a árvore completa (0 divergências). Prevejo isto porque o orçamento é 2 e as respostas são binárias, mas não está provado.
- **F1-f.** Uma implementação independente noutra linguagem (Node.js, enumeração das 2^16 funções, sem código partilhado) dá 0 divergências nos veredictos de toda a árvore.
- **Critérios de aceitação da fase 1:** F1-c e F1-f com 0 colisões ou divergências; a correção do enunciado provada por enumeração. Se falhar, há nova ronda (máximo 3).

### 1.1 Formalização
**Estado de informação** s = (O, C, W, T, M, b, Q, y_Q):
- O: observações iniciais (entrada, saída);
- C: as três cartas, como tabelas;
- W ∈ C: a carta de trabalho;
- T: 4 entradas retidas;
- M: o menu;
- b = 2: o orçamento;
- (Q, y_Q): as consultas feitas e as respostas obtidas.

O agente vê exatamente isto. O mecanismo oculto h e as respostas por consultar nunca são visíveis.

**Ações.** Na exploração: `query(q ∈ M \ Q)` enquanto |Q| < b, `commit(veredicto, cartas, previsões)` e `suspend`. Na revisão, depois de chegar o bloco E: `keep` ou `revise(veredicto, cartas)`.

**Regra de veredicto, leitura 70 (a da especificação).** H = funções de {0,1}^4 em {0,1} com suporte essencial ≤ 2 (|H| = 70); A(s) = {h ∈ H : h reproduz O ∪ y_Q}.
- inconsistent se A = ∅;
- rejected se W ∉ A;
- supported se ∀h ∈ A, ∀t ∈ T: h(t) = W(t);
- undetermined nos restantes casos.

**Leitura só-cartas.** A mesma regra, mas com A_C(s) = {c ∈ C : c reproduz O ∪ y_Q}.

**O que o prompt v3 comunica: só a leitura só-cartas.** O texto diz "três cartas que descrevem possíveis regras" e "uma carta é admissível se reproduz todas as observações". O espaço H nunca é mencionado. **F1-a confirmada.**

**Alvo** (do avaliador, não do agente): o veredicto obtido com as consultas ótimas e as **respostas verdadeiras** de h (`generator_v3.determination`). **Consulta decisiva** (do agente): existe uma sequência de até b − |Q| consultas e um conjunto de respostas compatíveis com A(s) que leva a um veredicto diferente de `undetermined`.

### 1.2 Enumeração completa (`instrument/enumerate_states.py`; `results/instrumento/F1_ENUMERACAO.json`)
Os 267 mundos de desenvolvimento (sementes 91xxx, equilibrados; o piloto é subconjunto). Para cada mundo: todos os subconjuntos Q do menu com |Q| ≤ 2 e todas as respostas compatíveis com alguma hipótese admissível no início. Os estados com respostas impossíveis são excluídos.

- **35 209 estados**, todos com vista pública distinta. Ficheiro de estados com sha256 `a9de653b…`; não fica no repositório (21 MB), regenera-se com o script.
- **Divergência entre as leituras: 86,4% dos estados.** **F1-b refutada** (a previsão era 50–75%).

| Leitura 70 → só-cartas | Estados |
|---|---|
| rejected → **inconsistent** | 20 880 |
| undetermined → **supported** | 9 526 |
| rejected → rejected | 2 479 |
| undetermined → undetermined | 1 266 |
| supported → supported | 1 058 |

A maior divergência não era a prevista. Quando uma consulta contradiz W, na leitura só-cartas muitas vezes nenhuma carta sobrevive, e o veredicto seria `inconsistent`. Esse veredicto nem sequer é permitido na fase de exploração. Esta combinação de "só-cartas" com "inconsistent não permitido" pode explicar parte da ausência total de `rejected` nos modelos. É uma hipótese, a testar na fase 3.

- **Veredicto como função do estado de informação (F1-c).** 0 colisões, mas o teste **não tem poder**: os 35 209 estados são todos distintos, por isso não há pares para colidir. A prova real é a da §1.4: o veredicto é recalculado só a partir da vista pública e da definição de H. F1-c fica **confirmada pela §1.4**, não por este teste.
- **Alvo (F1-d), confirmada.** Em **267/267** raízes, o alvo depende do h oculto. Para cada h ainda admissível no início, o oráculo dá mais do que um alvo possível. O alvo não é função do estado de informação. Por isso a grelha só o usa para classificar acertos *ex post*, e as categorias "sorte" e "prematuro" existem para separar a decisão fundamentada (função do estado) do resultado.
- **Consulta decisiva (F1-e), confirmada.** A versão de 1 passo e a de k passos coincidem nos **2 537** estados `undetermined` com orçamento por gastar (0 divergências), agora na árvore completa e não só nas respostas verdadeiras.

### 1.3 Correção do enunciado (prompt v3.1, `pilot_harness.SYSTEM_PROMPT_V31`; o v3 fica intacto)
O texto novo diz explicitamente que as regras possíveis são as funções que dependem de no máximo dois atributos (70 ao todo), que as cartas são só exemplos e que a regra verdadeira pode não estar entre elas. Define "admissível" para as regras (as 70) e não para as cartas, e reescreve `supported` e `undetermined` em termos das 70. Pede `admissible_cards` como as cartas admissíveis.

**Prova de que, com v3.1, a referência é função apenas do estado de informação:** o verificador da §1.4 recebe só a vista pública canónica (observações e consultas como entradas legíveis, tabelas das cartas, tabela de W, entradas retidas) e a frase do v3.1 que define H. A partir disso reproduz o veredicto de referência nos 35 209 estados. Nenhum dado oculto entra no cálculo.

### 1.4 Segunda via independente (`instrument/verify_states.mjs`, Node.js 22)
O Z3 não pôde ser instalado, porque este ambiente bloqueia o PyPI e o npm; instalá-lo no WSL do Bruno seria uma descarga que precisa de aprovação. A segunda via usa uma linguagem e um método diferentes, sem código partilhado:
- enumera as 65 536 funções booleanas e filtra por suporte essencial ≤ 2 (calculado de raiz);
- descodifica as cartas pelas chaves das tabelas;
- recalcula as duas leituras.

Resultado: **|H| = 70** (obtido de forma independente) e **0 divergências em 35 209 estados nas duas leituras**. **F1-f confirmada.**

Poder do verificador: com 36 rótulos v70 trocados de propósito, os 36 foram detetados. Das 24 observações trocadas, foram detetadas as que mudam o veredicto, como é de esperar.

### Decisão da fase 1 (ronda 1 de 3): **avançar**
- Critérios de aceitação cumpridos: 0 divergências com a via independente, e a correção do enunciado provada por enumeração.
- F1-b refutada, e a forma da divergência (`rejected` → `inconsistent`) dá uma hipótese nova para a fase 3.
- Fica registado que as corridas R1–R3 e L1–L3 usaram o enunciado ambíguo. As pontuações mantêm-se; a interpretação é a da `PILOTO_LOCAL.md` §12.
- **Fase 1: 100%. Plano do instrumento: 20%** (1 de 5 fases, sem pesar o esforço; as fases 2 e 3 são as mais pesadas).

### Ronda 2 da fase 1 (reaberta durante o desenho da fase 3, antes de qualquer corrida com v3.1)
**Falha encontrada.** O v3, e o próprio v3.1 da ronda 1, definem `inconsistent` como "a evidência nova contradiz as observações anteriores". A referência diz `inconsistent` quando **nenhuma das 70 regras** reproduz tudo junto. Na árvore completa de revisão (um estado pós-evidência por cada estado pré-compromisso, 35 209), há **24 396** `inconsistent` e **8 805 (36%) não têm nenhuma contradição direta** (nenhuma entrada com duas saídas). Só nas respostas verdadeiras, a proporção é 1 840/6 244 (29%). Um agente que siga o enunciado à letra responderia mal em todos esses casos.

**Correção (v3.1, revisto).** Na revisão aplicam-se as mesmas definições a todas as observações juntas. `inconsistent` = nenhuma das 70 regras reproduz todas as observações; inclui a mesma entrada com saídas diferentes, mas pode acontecer sem isso.

**Verificação.** A enumeração passa a incluir os estados de revisão (`results/instrumento/F1_ronda2/`; estados com sha256 `c8c1fd9c…`, 70 418 no total). O verificador Node.js dá **0 divergências em 70 418 estados**, nas duas leituras.

**Decisão (ronda 2 de 3): avançar.** Ficam registados dois defeitos de enunciado no v3: o espaço não é dito, e `inconsistent` está mal definido. Ambos estão corrigidos no v3.1, e nenhuma corrida com o v3.1 aconteceu antes desta correção.

## Fase 2. A métrica deteta o que diz detetar?

### Previsões ex-ante (escritas antes de correr a fase 2)
- **F2-a.** As políticas com defeitos plantados, corridas pelo ambiente real (`env_v3.Episode`), são classificadas pela grelha (`instrument/grid.py`) exatamente no rótulo que a sua construção implica, em todos os 267 mundos de desenvolvimento: matriz de confusão diagonal, 0 erros.
- **F2-b.** A grelha nova aplicada às transcrições R1–R3 e L1–L3 reproduz os números do script provisório (`pilot/grelha_itt.py`, `results/ESCADA_GRELHA_ITT.txt`) sem diferenças.
- **F2-c.** Nos testes de mutação a `grid.py` e às funções de `scoring.py` que a grelha usa, ≥ 90% das mutações são mortas pelos testes das políticas plantadas. As sobreviventes são equivalentes ou ficam explicadas uma a uma.
- **F2-d.** Com a métrica "revisão final correta", a ordenação dos modelos na revisão muda face ao tipo I. Os resultados históricos não são reescritos: o efeito fica num ficheiro novo.
- **Critérios de aceitação:** F2-a com 0 erros; F2-c ≥ 90% com as sobreviventes explicadas.

## Fase 3. Testes de comportamento (desenho e previsões, escritos antes de construir os itens e de correr modelos)

### Método
- **Só mundos de desenvolvimento** (sementes 91xxx). Nenhuma semente reservada é aberta.
- **Medição por escolha forçada.** Para cada item calcula-se a log-probabilidade de cada resposta candidata, dado o prompt (chat template do Qwen, texto tokenizado guardado). A resposta do modelo é a de maior probabilidade; a distribuição normalizada sobre as candidatas é a "probabilidade do modelo". Isto evita a descodificação gananciosa e a gramática.
- **Prompt v3.1** (espaço explícito) em todos os itens de veredicto.
- **Itens:**
  1. *Pares mínimos.* Dois estados do mesmo mundo, com o mesmo conjunto de consultas, que diferem na resposta de uma só consulta, e cujos veredictos (leitura 70) diferem. Orçamento restante 0, para isolar a inferência. Uma amostra estratificada por tipo de transição (por exemplo, undetermined↔supported, undetermined↔rejected, supported↔rejected).
  2. *Metamorfoses* de estados de base: (i) ordem do menu invertida; (ii) cartas renomeadas; (iii) ordem do enum de veredictos permutada; (iv) atributos renomeados (nomes e valores). A resposta correta não muda.
  3. *Sondas* (resposta exata calculada por código; acaso indicado):
     - **célula**: saída de uma carta numa entrada (acaso 0,5);
     - **compatibilidade**: a carta reproduz todas as observações? (acaso 0,5; reporta-se a exatidão equilibrada);
     - **separa**: uma consulta dá saídas diferentes em duas cartas? (0,5);
     - **veredicto dado o conjunto**: dados explicitamente "W é/não é admissível" e as saídas das regras admissíveis nas retidas, qual é o veredicto? (1/3);
     - **contradição**: a evidência nova contradiz alguma observação? (0,5).
     O resolvedor exato acerta 100% por construção; isto é verificado.
- **Incerteza:** IC 95% por bootstrap agrupado por `structure_group` (2 000 reamostragens).
- **Potência (calculada antes):** com n = 200 itens binários, a diferença 0,60 vs 0,50 tem potência ≈ 0,8 (α = 0,05) sem agrupamento. Com ~140 grupos de estrutura, o efeito de desenho reduz-se ao n efetivo, que será reportado. Nos pares mínimos, uma política constante tem sensibilidade 0, pelo que qualquer sensibilidade ≥ 0,10 é detetável com ~150 pares.

### Previsões ex-ante da fase 3
- **F3-a (leitura).** A sonda *célula* é a mais fácil. 3B e 7B ≥ 0,80; 0,5B e 1,5B entre 0,55 e 0,75.
- **F3-b (compatibilidade).** É o primeiro ponto de rotura, como sugerem os 0 `rejected`. Exatidão equilibrada ≤ 0,70 em todos os modelos, e pelo menos 0,10 abaixo da *célula* em cada modelo.
- **F3-c (veredicto dado o conjunto).** Com o conjunto dado de bandeja, o 7B ≥ 0,60 e os restantes ≤ 0,50. Acaso 1/3.
- **F3-d (pares mínimos).** Sensibilidade à evidência (veredicto escolhido muda dentro do par): 0,5B ≤ 0,15; 7B entre 0,20 e 0,50. Nenhum modelo acerta os dois membros do par em mais de 30% dos pares.
- **F3-e (probabilidades).** A massa de probabilidade em `rejected` sobe dentro do par quando a evidência passa a rejeitar W em ≥ 60% desses pares no 7B. É uma deslocação na direção certa, mesmo que insuficiente para mudar a escolha.
- **F3-f (metamorfoses).** A invariância do veredicto escolhido fica abaixo de 0,90 em todos os modelos para a permutação do enum e para a ordem do menu (enviesamento de posição). A renomeação de cartas e atributos é a mais estável (≥ 0,85 no 7B).
- **F3-g (contradição).** Melhor do que o acaso em 3B e 7B (≥ 0,65), em linha com serem os únicos que reveem.
- **Critérios de aceitação da fase 3 (do instrumento, não dos modelos):** o resolvedor exato tem 100% em todas as sondas; cada sonda e cada metamorfose tem ≥ 150 itens; os textos tokenizados e as distribuições ficam guardados; a análise é repetível a partir dos ficheiros guardados.

### 3.1–3.3 Construção dos itens (`instrument/items.py`; `results/instrumento/F3/ITENS.jsonl.gz`)
- **2 304 itens** de 259 mundos de desenvolvimento e 138 grupos de estrutura. Ficheiro descomprimido com sha256 `e168021b…`.
  - pares mínimos: 200 pares (400 itens);
  - metamorfoses de veredicto: 154 bases × 4 (original, cartas renomeadas, enum permutado, atributos renomeados);
  - escolha de consulta: 160 raízes × 2 (menu original e invertido);
  - sondas: célula 200, compatibilidade 200, separa 200, veredicto dado o conjunto 168, contradição 200. Respostas equilibradas por construção, exceto no veredicto: 66/36/66.
- **Limitação de construção dos pares mínimos.** Com as mesmas consultas, mudar uma resposta nunca leva de `supported` para `undetermined`: as duas respostas não podem coincidir ambas com W. Por isso os pares cobrem só `rejected`↔`supported` (100) e `rejected`↔`undetermined` (100). A transição `supported`↔`undetermined` mede-se nas metamorfoses e nas sondas, não nos pares.
- **Verificação independente das respostas a partir do texto apresentado ao modelo** (`instrument/verify_items.mjs`, Node.js; lê os atributos, as observações, as cartas, W e as retidas do próprio texto, incluindo os atributos renomeados): **0 divergências em 1 984 itens**. Os itens de escolha de consulta não têm resposta única.
- **Validação das métricas com respostas sintéticas**, antes de qualquer modelo. Um "oráculo" tem 1,00 em todas as sondas, sensibilidade 1,00 nos pares e invariância 1,00. A política "primeira candidata" tem 0,50 nas sondas binárias, 0,33 de exatidão equilibrada no veredicto, sensibilidade 0 e recall só em `rejected`. As métricas distinguem os dois extremos.
- **Problema encontrado e corrigido nesta validação.** A marca "consulta informativa" (existe uma resposta que decide) vale para 89% das consultas do menu e não separa boas escolhas de más. Foi substituída por um **valor numérico**: a probabilidade, com prior uniforme sobre A, de o veredicto ficar decidido depois da consulta e da melhor segunda consulta (o que o bayes_ig otimiza). Os itens não relacionados com consultas ficaram idênticos.
- **Achado sobre o instrumento.** Mesmo com o valor numérico, a alavanca da escolha de consulta é pequena: valor médio da melhor consulta 0,885, média uniforme do menu 0,798, `q1` 0,793. Em 130 das 160 raízes a diferença entre a melhor e a pior consulta passa de 0,05. "Escolher consultas" é por isso medido com pouca margem nesta tarefa, e isto tem de pesar na fase 5.
- **Executor** (`instrument/run_items.py`): escolha forçada por soma de log-probabilidades, um forward por item com as candidatas em lote; guarda o contexto exato (texto e ids) e assinala quando a fronteira entre contexto e candidata funde tokens. **Análise** (`instrument/analyse_items.py`): fixada antes de qualquer resultado, com bootstrap agrupado.

### Resultados da fase 2
- **F2-a confirmada.** As 9 políticas com defeitos plantados (e, na ronda 2, uma 10.ª: "compromete-se e falha a revisão") jogadas pelo ambiente real nos 267 mundos de desenvolvimento ficam sempre no rótulo que a construção implica: **0 erros em 2 403 episódios**, com todas as categorias exercitadas e a revisão final também certa (`instrument/planted.py`). Na construção da política "fundamentado", a precondição "o bayes_ig chega ao alvo" falhou (97% no desenvolvimento, já registado); passou a usar as consultas do oráculo, e a precondição ficou verificada por asserção.
- **F2-b confirmada.** A grelha nova reproduz o script provisório nas seis corridas, com 0 diferenças (`results/instrumento/F2_GRELHA_HISTORICOS.json`).
- **F2-c: ronda 1 refutada, ronda 2 confirmada.**
  - Ronda 1 (`F2_MUTACOES.json`): 31/36 mortos (86% < 90%). Os sobreviventes eram duas lacunas reais: nenhuma política se comprometia e falhava a revisão; os testes não passavam pelos estados `undetermined` com orçamento e sem consulta decisiva, que só existem 8 vezes no desenvolvimento.
  - Correção: uma política plantada nova (`sem_revisao`) e um teste exaustivo da consulta decisiva de 1 passo contra a de k passos em toda a árvore do desenvolvimento, exigindo que os estados não decisivos apareçam.
  - Ronda 2 (`F2_MUTACOES_R2.json`): **35/36 mortos (97%)**, um deles por erro. O único sobrevivente muda `should_revise` em `revision_reference`. É equivalente para a grelha, porque esta usa o veredicto pós-evidência e não esse campo (o defeito da `PILOTO_LOCAL.md` §10).
- **F2-d refutada.** Revisão final correta: 0,5B 7/48, 1,5B 8/48, 3B 16/48, 7B 16/48. A ordenação é a mesma do tipo I (3B e 7B à frente). A métrica nova não reordena, mas passa a contar os casos em que o compromisso estava errado.
- **Decisão da fase 2: avançar** (2 rondas de 3). **Fase 2: 100%. Plano do instrumento: 40%.**

## Fase 4. Âncoras externas: propostas para aprovação (nada executado)

### 4.1 Referência humana
- **Objetivo:** saber se a tarefa, tal como o v3.1 a enuncia, é resolúvel por pessoas. Se não for, o problema está no enunciado e não nos modelos.
- **Desenho:** 2 a 3 pessoas (podes ser tu e uma ou duas pessoas que não conheçam o projeto), **20 episódios** de desenvolvimento, iguais para todas: 7/7/6 por alvo, e 8 dos 20 com mudança na revisão. Mais 20 itens de sonda (célula, compatibilidade, contradição), para separar a leitura do raciocínio.
- **Interface:** uma página privada (Artifact) que mostra o prompt v3.1 e o estado exatamente como o modelo os vê, recolhe as ações e guarda as respostas. Precisa de aprovação para a criar.
- **Medidas:** grelha ITT e revisão final correta por pessoa; **kappa de Cohen** entre pessoas e contra a referência; tempo por episódio.
- **Esforço estimado:** 1,5 a 3 horas por pessoa.
- **Critério:** se as pessoas atingirem o macro fundamentado ≥ 0,8 e um kappa com a referência ≥ 0,7, o enunciado está bem posto. Abaixo disso, volta-se à fase 1.

### 4.2 Teto com um modelo de fronteira via API
- **Objetivo:** com o mesmo prompt v3.1 e o mesmo arnês, um modelo forte chega perto do bayes_ig? Se não chegar, a tarefa pode ser difícil por razões do enunciado ou do formato, e não por falta de capacidade.
- **Âmbito:** os 48 episódios do piloto (cerca de 200 chamadas) e as sondas em modo de geração (cerca de 1 000 chamadas). A escolha forçada por probabilidades não é possível em APIs que não as devolvem.
- **Volume estimado:** cerca de 1,3 M tokens de entrada e 0,1 M de saída, contados pelos prompts reais (~1 000 tokens cada). O custo depende do preço do modelo escolhido, que confirmo na altura com a tabela oficial, sem inventar valores.
- **O que precisa de ti:** escolher o modelo e configurares tu a chave da API. Eu não introduzo chaves.

### 4.3 Benchmark externo (validade convergente)
- **Objetivo:** ver se a ordenação dos modelos aqui concorda com a de outra tarefa que meça o mesmo tipo de competência (escolher experiências e usar a evidência).
- **Candidatos:**
  - **DiscoveryWorld** (Apache-2.0, código verificado na síntese de 17/10);
  - **HypoSpace** (conjuntos admissíveis; licença por esclarecer);
  - **LUCA** (o código está numa ligação anónima de revisão, inacessível);
  - **ACED-Bench** (não encontrei código).
  - Recomendação: um subconjunto pequeno do DiscoveryWorld com os mesmos 4 modelos locais.
- **Medida:** correlação de postos (Spearman) entre a ordenação nas duas tarefas; com 4 modelos é só indicativa. Exige descarregar o repositório, o que precisa de aprovação.

### Ronda 1 da fase 3 (corrida 18/10, 07:39–09:49): defeito do instrumento encontrado
- Os quatro modelos correram os 2 304 itens: `results/instrumento/F3/{0.5B,1.5B,3B,7B}/`, todos com o mesmo sha dos itens.
- **Lentidão no 3B, resolvida.** O executor pedia os logits de todas as posições, cerca de 2 GB por item. A GPU de 12 GB ficou sem memória (aviso de OOM) e o Windows passou à memória partilhada (7 itens/min em vez de ~100). Correção: `logits_to_keep` (commit 9b02b34). Verificação no 0,5B: em 60 itens, diferença máxima 0,00000 e a mesma escolha em 60/60. O 3B retomou a partir do que estava gravado.
- **Defeito: enviesamento de comprimento na escolha forçada.** "não" ocupa 2 tokens e "sim" 1; `undetermined"` ocupa 3 e `rejected"`/`supported"` 2. A soma das log-probabilidades penaliza as candidatas mais longas. Em **todos** os modelos, as três sondas de sim/não deram "sim" em ~100% dos itens. Isto não distingue um modelo que nada sabe de um instrumento enviesado. **Os resultados das sondas sim/não e das famílias de veredicto da ronda 1 não são interpretáveis como capacidade.** As sondas célula (0/1, 1 token cada) e veredicto com o conjunto dado de bandeja (1/1/2 tokens) são menos afetadas, mas também são repetidas.
- **Correção da ronda 2, registada antes de voltar a correr.** O executor passa a guardar a log-probabilidade de cada token e o id do primeiro token. **Medida principal:** a candidata com maior log-probabilidade do **primeiro** token, quando os primeiros tokens das candidatas são distintos (é o que a descodificação gananciosa decide). Verifica-se que são distintos e reportam-se as colisões. **Medida secundária:** a soma. Na escolha de consulta (`q1` e `q10` partilham o primeiro token) mantém-se a soma, com a nota de que `q10"` tem mais um token. A análise da ronda 1 continua reproduzível com a regra `sum`.
- As previsões F3-a a F3-g mantêm-se e são avaliadas sobre a ronda 2.

### Ronda 2 da fase 3 (corrida 18/10, 09:52–11:05; código 3b9033f; regra do primeiro token)
- Os quatro modelos sobre os mesmos 2 304 itens (sha `e168021b…`) e **os mesmos tokens de entrada** (hash das ids de contexto `a6707c4b…`, igual nos quatro). Saídas em `results/instrumento/F3R2/{modelo}/`: pontuações, log-probabilidades por token, contextos tokenizados e análise.
- **0 colisões de primeiro token** e **0 fronteiras fundidas** em todos os modelos.
- **Validade por item: massa das candidatas no primeiro token** (mediana; abaixo de 0,5, o modelo queria responder outra coisa e o item não mede a escolha):

| | célula | compat. | separa | contrad. | veredicto dado | pares | metamorfoses |
|---|---|---|---|---|---|---|---|
| 0,5B | 1,00 | **0,16** | **0,01** | **0,02** | 0,93 | 0,87 | 0,87 |
| 1,5B | 1,00 | 0,75 | 0,53 | 0,66 | 0,95 | 0,93 | 0,93 |
| 3B | 1,00 | 0,98 | 0,99 | 1,00 | 0,98 | 0,95 | 0,96 |
| 7B | 1,00 | 0,56 | 0,98 | 0,91 | 0,99 | 1,00 | 1,00 |

As sondas sim/não do 0,5B **não são interpretáveis**. As restantes células são.

**Resultados (escolha pelo primeiro token; IC 95% por bootstrap agrupado; acaso entre parênteses):**

| | célula (0,50) | compat. equil. (0,50) | separa (0,50) | contrad. (0,50) | veredicto dado, equil. (0,33) | pares: sensib. / ambos certos | veredicto completo, exatidão | 1.ª posição na consulta |
|---|---|---|---|---|---|---|---|---|
| 0,5B | 0,535 [0,47; 0,61] | (inválida) | (inválida) | (inválida) | 0,33, sempre `undetermined` | 0,00 / 0,00 | 0,30, sempre `supported` | 0,94 |
| 1,5B | 0,535 [0,47; 0,60] | 0,50, sempre "sim" | 0,50, sempre "sim" | 0,50, sempre "sim" | 0,33, sempre `supported` | 0,175 / 0,00 | 0,22 | 1,00 |
| 3B | 0,59 [0,52; 0,66] | 0,50, sempre "sim" | 0,50, sempre "sim" | 0,50, sempre "sim" | **0,93 [0,87; 0,98]** | 0,00 / 0,00 | 0,35, sempre `undetermined` | 1,00 |
| 7B | 0,615 [0,56; 0,67] | 0,53 [0,50; 0,57] | 0,50, sempre "sim" | 0,50, sempre "sim" | **0,66 [0,59; 0,73]** | 0,03 / 0,00 | 0,34 | 1,00 |

- **Uso da evidência nos pares mínimos.** Nenhum modelo acerta os dois membros de um par (0/200 nos quatro). A probabilidade de `rejected` sobe no lado certo do par em 0,47–0,55 dos pares, o que é indistinguível do acaso.
- **Escolha de consulta.** Posição 1 em 94–100% dos casos, com o menu original ou invertido. A invariância do *input* escolhido é 0,00: a escolha é puramente posicional. O valor da consulta escolhida (0,79) é igual ao de escolher ao acaso no menu (0,80); a melhor dá 0,885.
- **Metamorfoses.** A invariância é alta (0,83–1,00) mas, nos modelos de resposta constante (0,5B, 3B), é vazia. A variação total das probabilidades é maior na permutação do enum (0,5B 0,34; 3B 0,13; 7B 0,14) do que na renomeação das cartas (0,02–0,10): o texto do modelo de ação mexe mais do que o conteúdo.

### Previsões da fase 3 (avaliadas sobre a ronda 2)
- **F3-a refutada.** Célula: 3B 0,59 e 7B 0,615, abaixo de 0,80; 0,5B e 1,5B 0,535, abaixo de 0,55. A leitura de uma célula está perto do acaso em todos.
- **F3-b refutada em parte.** A compatibilidade fica ≤ 0,70 em todos (confirmado), mas não fica 0,10 abaixo da célula, porque a própria célula está perto do acaso.
- **F3-c refutada.** O 7B tem 0,66 (≥ 0,60, confirmado), mas o **3B tem 0,93**, não ≤ 0,50. A relação com o tamanho não é monótona.
- **F3-d refutada em parte.** 0,5B ≤ 0,15 e "ambos certos" ≤ 30% confirmados; mas o 7B fica em 0,03, não entre 0,20 e 0,50.
- **F3-e refutada.** 7B 0,55 [0,48; 0,62], não ≥ 0,60.
- **F3-f mista.** A ordem do menu mostra um enviesamento de posição total (confirmado). O enum só é < 0,90 nos modelos não constantes. A renomeação no 7B fica ≥ 0,85 (confirmado).
- **F3-g refutada.** Contradição 0,50 (sempre "sim") no 3B e no 7B.

**Critérios de aceitação do instrumento:**
- resolvedor exato 100%, verificado de forma independente a partir do texto: 0/1 984 divergências;
- ≥ 150 itens por família;
- textos tokenizados e distribuições guardados;
- análise repetível a partir dos ficheiros;
- e ainda a validade por item (massa das candidatas).

**Decisão da fase 3 (2 rondas de 3): avançar**, com a máscara de validade aplicada. **Fase 3: 100%.**

## Fase 5. Decisão

**O que os números permitem concluir sobre os acertos.** Os acertos registados na escada (16/48, 17/48 e semelhantes) vêm de **políticas constantes** que coincidem com alvos equilibrados (1/3). Com o enunciado corrigido e medição por escolha forçada:
- nenhum dos quatro modelos lê uma tabela de forma fiável (célula 0,535–0,615);
- nenhum distingue compatível de incompatível, contradição de não contradição, ou consultas que separam de consultas que não separam;
- nenhum muda corretamente de veredicto quando a evidência muda (0/200 pares em todos);
- todos escolhem a consulta pela posição.

**A única competência acima do acaso é aplicar a regra do veredicto quando o conjunto admissível é dado** (3B 0,93; 7B 0,66). O estrangulamento está na **construção do conjunto admissível**: ler tabelas e verificar a compatibilidade. Não está na regra, e não se resolve com tamanho: do 3B para o 7B, a célula sobe 0,025 e o veredicto dado desce 0,27.

**Recomendação: execução de código, mais uma correção da tarefa.** Não recomendo subir de modelo, caderno, especialistas nem revisor por agora.
1. **Execução de código (trilha `com_codigo`).** O passo que falha (calcular A(H) a partir de tabelas) é exatamente o que o código faz de forma exata. O agente escreve ou chama o código que verifica a compatibilidade e calcula o conjunto; o LLM aplica a regra e decide. É também a arquitetura da decisão de 18/10: o enquadramento produz uma especificação executável.
2. **Corrigir a tarefa para que C3 seja mensurável.** A alavanca da escolha de consulta é pequena: a melhor consulta vale 0,885 e o acaso 0,798. Mesmo um agente perfeito na escolha mostraria pouco. Antes de medir C3, é preciso um gerador com mais alavanca: menus maiores, consultas com valores mais espalhados, orçamento maior ou várias rondas.
3. **Caderno, especialistas e revisor** resolvem falhas de planeamento e coordenação, que não se conseguem observar enquanto a perceção falha primeiro. Ficam para depois.

**O que tornaria a recomendação errada:**
- (a) Um modelo de fronteira, com o mesmo prompt v3.1 e só texto, resolver a tarefa perto do teto. Nesse caso o problema era escala, e a âncora 4.2 decide isto.
- (b) Com o conjunto admissível calculado por código, os modelos continuarem a falhar a decisão nos pares mínimos. Nesse caso o estrangulamento não era só perceção.
- (c) As pessoas da âncora 4.1 também falharem. Nesse caso o enunciado continua mal posto.

**Resultado na partição cega que confirmaria ou refutaria** (a pré-registar antes de gerar a cega por drand, dividida por grupos de estrutura):
- com A(H) calculado por código, o 3B atinge macro fundamentado ≥ 0,80 e "ambos certos" ≥ 0,80 nos pares mínimos;
- só com texto, o mesmo 3B fica ≤ 0,40.
A recomendação fica **refutada** se a versão só com texto atingir ≥ 0,60, ou se a versão com código ficar ≤ 0,60.

**Progresso.**
- Plano do instrumento: fases 1, 2, 3 e 5 a 100%; fase 4 a 100% como propostas, com a execução à espera de aprovação.
- Global: cerca de 40% (7 de 17 etapas fechadas, sem pesar o esforço: objetivo, auditoria M17, gerador v3 e auditorias, políticas, piloto, escada, validação do instrumento).

**O que preciso do Bruno:**
1. aprovar ou não as âncoras 4.1 (pessoas), 4.2 (API, com o modelo e a chave configurados por ti) e 4.3 (descarregar o DiscoveryWorld);
2. aprovar a direção: trilha `com_codigo` e correção da alavanca de C3 antes de mais corridas de modelos;
3. merge do ramo `tronco01-v3-instrumento` (e de `tronco01-v3-escada`), só com a tua autorização.

## Adenda (18/10, revisão; não altera resultados históricos)

**Alcance das conclusões sobre a escolha de consultas.** Na tarefa usada nas fases 1–3, a diferença entre a melhor consulta do menu e a média é de 0,087 (mediana). Com essa margem, a métrica de consultas não separa uma política competente de uma aleatória, por isso **as conclusões desta fase sobre a escolha de consultas não medem capacidade**. A escolha de consulta passa a ser medida só na V4 (docs/V3_CONSULTAS.md §10–12: gap mediano 0,438). As conclusões sobre leitura do estado, inferência do veredicto e revisão continuam válidas, porque não dependem dessa margem. Os números acima ficam como estavam.

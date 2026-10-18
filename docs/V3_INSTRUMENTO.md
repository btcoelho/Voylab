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

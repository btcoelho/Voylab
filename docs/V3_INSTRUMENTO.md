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

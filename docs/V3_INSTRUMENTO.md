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

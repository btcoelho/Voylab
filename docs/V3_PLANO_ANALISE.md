# TRONCO-01 v3 — plano de análise e protocolo de resposta (rascunho a congelar)

**17 de outubro de 2026.** Fixa, antes do piloto e do congelamento, as escolhas que ficaram abertas. Nada aqui usa reservas.

## 1. Escolhas fixadas
1. **Análise principal = conjunto equilibrado** (`balance_trim`: alvos iguais em cada grupo dificuldade × família × nº de linhas iniciais).
   O conjunto completo é só sensibilidade. A escolha foi feita depois de ver o desequilíbrio nas sementes 93xxx; fica registado.
2. **Sementes 93001/93003/93009 estão gastas**: serviram para a confirmação das previsões Q1–Q11 e para decidir o equilíbrio. Nunca voltam a servir de confirmação.
   Também estão gastas as 91xxx (desenho) e 92xxx (substitutos de desenho).
3. **Quota de `change_indirect` = quota de `change`** (81 e 81 nas três sementes de confirmação). Já se verificava; nada a alterar.
4. **Sem ferramentas e com código** reportam-se em separado (ver `docs/DECISOES_2026-10-17.md`).

## 2. Protocolo de resposta do agente (implementado em `v3/env_v3.py`)
Ações JSON. Fase **explore**: `query {query_id}` (≤ orçamento), `commit {verdict, admissible_cards[ids], predictions{"1".."4"}}`, `suspend`.
Fase **revision** (depois de comprometer ou suspender, com a nova evidência visível): `keep`, `revise {verdict, admissible_cards}`.
Veredictos: `rejected | supported | undetermined`; `inconsistent` só na revisão (o histórico deixou de caber em qualquer hipótese).
Ação inválida: erro devolvido e contado; 3 inválidas seguidas terminam o episódio (episódio incompleto, conta como falha).
O teste de equivalência (3 696 comparações, 0 divergências) mostra que o protocolo reproduz o avaliador direto para as 11 políticas de referência.
*Defeito corrigido durante o teste:* o alfabeto de veredictos não tinha `inconsistent`, logo a mudança de regime era inexprimível na revisão.

**`suspend` é correto** quando o veredicto do próprio histórico é `undetermined` e nenhuma consulta pública restante (dentro do orçamento) pode alguma vez
determiná-lo. `commit` com `undetermined` enquanto uma consulta ainda o podia determinar é **paragem prematura**. O oráculo fica fora da métrica de paragem
(usa conhecimento privado).

## 3. Objetivos primários, secundários e multiplicidade
**Primários (3), Holm a α = 0,05:** (P-a) alcance do veredicto; (P-b) erro de inferência; (P-c) erro de revisão tipo I nos mundos `change` e `change_indirect`.
**Secundários (sem confirmar hipóteses):** erro de procura, evidência ignorada, paragem prematura / suspensão correta, validade e exatidão das previsões em T,
cartas admissíveis exatas, consultas gastas, ações inválidas, resultados por família e por dificuldade.
Comparações pareadas por mundo; IC 95% por aproximação normal da diferença média; Wilson para proporções.

## 4. Critérios de passagem (sem afinação posterior)
- Ações inválidas ≤ 1% e respostas que cumprem o esquema ≥ 98% (condição de elegibilidade, não de desempenho).
- Um modelo «bate» a referência X se o IC 95% da diferença de alcance for > 0. Referências de comparação: aleatória, rival, sem_consultas.
- Nenhuma conclusão sobre competência por família com menos de 180 mundos nessa família.

## 5. Tamanho das partições (corrige uma estimativa minha anterior)
Estimei antes «cerca de 400 mundos para detetar 0,05». O cálculo com os desvios observados em dev (`results/POTENCIA.json`; sd da diferença pareada 0,35–0,48; 80% de potência, α = 0,05)
dá **~710–730 mundos para 0,05** e **~180 para 0,10**.
Decisão: **720 mundos equilibrados por partição** (240 por veredicto): 0,05 no global e 0,10 por família (240 por família).
Duas partições: **VALIDAÇÃO** (pode usar-se uma vez por degrau da escada, com limiares pré-registados) e **CEGA** (abre-se uma única vez, no fim).
Sem consultas do mesmo mundo entre partições (verificado por estado público canónico).

## 6. Exclusões
Nenhuma exclusão de mundos depois de gerados. Episódios incompletos contam como falha. Mundos inviáveis (células vazias) ficam listados no manifesto.

## 7. O que este plano ainda não decide
Modelo e meio do piloto (local ou API); pista com código (só especificada); nível «difícil»; ruído; enquadramento (tarefa separada).

# TRONCO-01 v3: tarefa de escolha de consultas com alavanca suficiente

Decisão do Bruno, 18/10/2026, 12:10. Meta inicial de discriminação **0,25**, tratada como **critério de desenho**, não como resultado a garantir por ajustes sucessivos. Sem corridas de modelos nesta fase. A partição cega não se usa.

## 1. Referência determinística (fixada antes de mexer no gerador)
- `instrument/reference_manifest.py`: hashes do código de referência e dos artefactos, mais um resumo recalculável (267 mundos de desenvolvimento, sha do conteúdo `e17a3cac…`, piloto `cdf24285…`, |H| = 70). Gravado em `results/instrumento/REFERENCIA.json`.
- Teste `FrozenReference` em `tests/test_instrument.py`: falha se algum artefacto ou o resumo recalculado mudar. O gerador atual fica como modo por omissão; as variantes entram como opções novas, sem alterar o que existe.

## 2. Métrica (única para a linha de base e para as variantes; `instrument/query_leverage.py`)
- **v2(q)** = probabilidade, com h uniforme sobre A₀ (as hipóteses admissíveis na raiz), de o veredicto ficar determinado depois de q e da melhor segunda consulta. Com orçamento 1 (se uma variante o usar), a mesma definição reduz-se a "depois de q".
- **gap(mundo)** = max_q v2(q) − média_q v2(q), sobre **todo** o menu desse mundo, com peso uniforme. É a mesma métrica, nos mesmos mundos e com a mesma distribuição de consultas, em todas as comparações.
- Reportam-se sempre:
  - a distribuição de gap (média, mediana, quartis, mínimo e máximo, histograma de 0,05 em 0,05);
  - a proporção de mundos com gap ≥ 0,25;
  - a qualidade da evidência: média de max v2;
  - a dificuldade: 1 − média de v2 no menu;
  - a posição normalizada da melhor consulta no menu, e a proporção de mundos em que é a primeira.

## 3. Linha de base (gerador atual, 267 mundos de desenvolvimento; `results/instrumento/CONSULTAS_LINHA_DE_BASE.json`)
| | valor |
|---|---|
| gap média / mediana | 0,085 / 0,072 |
| quartis; mínimo e máximo | 0,031–0,136; 0,000–0,389 |
| mundos com gap ≥ 0,25 | **3%** (8/267) |
| qualidade da evidência (max v2) | 0,894 |
| dificuldade (1 − média v2) | 0,191 |
| posição normalizada média da melhor | 0,12 |
| **melhor consulta é a primeira do menu** | **58%** |

**Achado: pista de posição no gerador.** O menu é ordenado pelo índice das entradas, e a melhor consulta (o primeiro empate) aparece em primeiro lugar em 58% dos mundos. Escolher sempre `q1`, como fizeram os quatro modelos na fase 3, é uma heurística razoável nesta tarefa. A leitura "escolha puramente posicional" da fase 3 continua certa quanto ao comportamento, mas o instrumento não penalizava esse comportamento. Fica corrigido em qualquer variante.

## 4. Critérios de aceitação de uma variante (fixados antes de desenhar e de medir variantes)
Todos medidos nos mundos de desenvolvimento (sementes 91xxx), com a métrica da §2:
1. **mediana de gap ≥ 0,25 e ≥ 50% dos mundos com gap ≥ 0,25.** A meta não pode ser cumprida por uma cauda de casos extremos.
2. **Sem pista de posição:** a ordem do menu é baralhada por mundo; posição normalizada média da melhor em [0,40; 0,60]; melhor consulta em primeiro lugar em ≤ 1,5/|menu| dos mundos.
3. **Tarefa resolúvel:** qualidade da evidência (média de max v2) ≥ 0,80.
4. **Escolher ao acaso é claramente pior:** valor médio do menu ≤ 0,60.
5. **Equilíbrio dos alvos mantido:** 1/3 por veredicto no conjunto equilibrado, como hoje.
6. **Sem pista de superfície simples:** um preditor trivial (número de atributos em que a consulta difere das observações; distância de Hamming mínima às observações) não identifica a melhor consulta em mais do que o dobro do acaso. É um diagnóstico reportado.

## 5. Regra contra ajustar até parecer bem (fixada antes)
- **No máximo 3 variantes**, definidas aqui antes de qualquer medição e avaliadas por esta ordem (da mais simples para a mais construída). Escolhe-se a **primeira** que cumprir todos os critérios. Não se afinam parâmetros entre medições.
- Se nenhuma cumprir, regista-se o falhanço e decide-se com o Bruno. Nem a meta nem os critérios mudam depois de ver números.
- **V1, mais observações iniciais:** k₀ ∈ {5, 6, 7} em vez de {2, 3, 4}. Com A₀ mais pequeno, muitas entradas deixam de separar hipóteses e só algumas decidem. Orçamento 2.
- **V2, orçamento 1:** o gerador atual com uma só consulta. Sem segunda consulta para compensar, a escolha pesa mais.
- **V3, menu curto construído:** 6 consultas por mundo, com exatamente 1 a 2 de valor alto (as melhores do menu completo) e as restantes escolhidas entre as de valor mais baixo. Orçamento 2.
- Todas com a ordem do menu baralhada por mundo, numa semente derivada do uid.

## 6. Previsões ex-ante (antes de implementar as variantes)
- **C-a.** V1 não cumpre o critério 1 (mediana de gap entre 0,12 e 0,25): mais observações também tornam mais mundos triviais.
- **C-b.** V2 cumpre o critério 1 (mediana ≥ 0,25), mas pode falhar o critério 3 (qualidade < 0,80), porque com uma só consulta muitos mundos ficam por decidir.
- **C-c.** V3 cumpre os critérios 1 a 4 por construção; o risco está no critério 6 (pistas de superfície), porque as consultas de valor baixo podem ter um padrão reconhecível.
- **C-d.** Com o menu baralhado, a posição normalizada da melhor fica em [0,40; 0,60] nas três variantes.
- **C-e.** A primeira variante a cumprir tudo será a V2 ou a V3, e não a V1.

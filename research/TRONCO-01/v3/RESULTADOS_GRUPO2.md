# v3 — grupo 2: resultados contra a segunda série de previsões

**17 de outubro de 2026.** Previsões em `docs/V3_PREVISOES_EXANTE_2.md` (commit 3109b6a), escritas antes do código.
Sementes de confirmação-dev 93001/93003/93009 (414 mundos; 270 na variante equilibrada), usadas uma vez. Sem modelos, sem reservas.
Resultados: `results/POLITICAS_CONFIRMACAO.json`, `results/TEXTO_RONDA_2.json`, `results/TEXTO_RONDA_1_SEM_EQUILIBRIO.json`.

## Políticas (alcance, conjunto completo pré-registado)
sem_consultas 21,7% · aleatória 56,3% · simples 56,5% · primeiro_do_menu 58,5% · rival 68,6% · greedy_a 68,8% · bayes_ig 99,0% · oráculo 100%.

| | Previsão | Resultado |
|---|---|---|
| Q1 | P3 generaliza | **Confirmada**: bayes_ig − aleatória +0,427 (IC 0,387–0,467). |
| Q2 | simples ≈ aleatória | **Confirmada**: +0,002 (IC −0,033 a 0,036). |
| Q3 | bayes_ig − sem_consultas ≥ 0,25 | **Confirmada**: +0,773. |
| Q4 | rival bate simples e aleatória | **Confirmada**, mas pouco: +0,121 e +0,123 (ICs > 0). |
| Q5 | rival < bayes_ig | **Confirmada**: bayes_ig − rival +0,304 (IC 0,258–0,351). |
| Q6 | rival ≈ bayes_ig com `need = 1`; rival < bayes_ig com `need = 2` | **Parcialmente REFUTADA.** `need = 2`: confirmada (+0,82). `need = 1`: **refutada**, diferença +0,149 (IC 0,09–0,20). A heurística falha também quando uma consulta chega, logo a vantagem do bayes_ig não é só planeamento a dois passos. |
| Q7 | primeiro_do_menu ≈ aleatória | **Confirmada**: +0,021 (IC −0,017 a 0,059). Não há atalho de posição. |
| Q8 | cega_pegajosa falha toda a revisão exigida | **Confirmada**: tipo I = taxa de `should_revise` em cada tipo (100% em `stable_informative` e nas mudanças; 32% em `stable_uninformative`); tipo II = 0. |
| Q9 | mudança indireta | **Confirmada**: 0 entradas do bloco repetem linhas iniciais ou consultas do oráculo (testado por família); bayes_ig e sem_consultas tipo I = 0; pegajosa 1,0. |
| Q10 | decomposição de erros | **Confirmada**: erro de inferência 0 nas políticas de referência; erro de procura = 1 − alcance; ignora_evidencia: erro de inferência e evidência ignorada 78% (previsto 77% ± 3). |
| Q11 | auditoria do texto sem fugas | **Refutada na primeira execução; corrigida na segunda (ver abaixo).** |

## Q11: duas falhas, uma minha
**Ronda 1 do texto (414 mundos, sem equilíbrio).** Rejeições Holm: `chars`, `lines` (p = 0,003 e 0,006), mais o «rank da primeira consulta do oráculo», com p ≈ 1e-91 e 43,5% de consultas na posição 0 contra «acaso» 11%.
1. O rank do oráculo era um **artefacto da minha métrica**: o oráculo devolve o primeiro conjunto mínimo encontrado (viés para o início do menu) e o rank −1 é definido pelo próprio alvo. A medida foi substituída pela **posição de todas as consultas úteis** (as que pertencem a algum conjunto mínimo determinante) contra a expectativa `|úteis| / |menu|`.
2. O comprimento do texto reflete um **desequilíbrio real**: o alvo `undetermined` tem células inviáveis com 2 linhas iniciais, logo menos mundos curtos. Correção: `balance_trim` iguala os alvos dentro de cada grupo (dificuldade, família, nº de linhas iniciais), sem olhar a resultados.

**Ronda 2 do texto (270 mundos, equilibrada).** 0 rejeições Holm (menor p = 0,043 sem correção para `chars`). Posição 0 do menu é útil em 43,9% dos mundos (IC 36,8–51,2%) contra 41,9% esperado se uniforme. Posições úteis distribuídas sem viés (79, 81, 77, 65, 85, 82, 80, 58, 44, 13 pelas posições 0–9, decrescendo no fim por o menu ser mais curto).
**Aceitação:** cumprida. **Limite:** o equilíbrio foi escolhido depois de ver o desequilíbrio, nas mesmas sementes; para o conjunto pré-registado completo, `chars/lines` continuam a associar-se ao alvo. Os resultados das políticas estão por isso apresentados nas duas variantes, e as conclusões são as mesmas (equilibrada: bayes_ig − aleatória +0,364; rival − aleatória +0,101; bayes_ig − rival +0,263).

## O que se implementou
- `scoring.py`: previsão em T (validade e exatidão), conjunto de cartas admissíveis, paragem prematura, consultas gastas depois de o veredicto estar determinado, e a decomposição **erro de procura / erro de inferência / evidência ignorada**.
- Gerador: tipo `change_indirect`; `balance_trim` (opcional).
- Políticas: `rival`, `primeiro_do_menu` (sondas), `cega_pegajosa`, `ignora_evidencia` (controlos negativos).
- `text_audit_v3.py`: renderização determinista do prompt e auditoria do texto.

## Limitações (novas)
- `premature_stop` assinala sem_consultas a 100% e o oráculo a 9%: o oráculo para por conhecimento privado; nenhum agente consegue saber isso a partir do estado público.
- Em mundos estáveis a revisão só testa agentes sem consultas prévias: bayes_ig tem `should_revise` = 0 em `stable_informative`.
- A previsão em T tem exatidão limitada pela ambiguidade (bayes_ig 84%, oráculo 81%); a validade é 100%.
- `change_indirect` tem poucos mundos por semente (27 em 93001).
- Pista com código e o texto para modelos de linguagem **não foram avaliados** com nenhum modelo.

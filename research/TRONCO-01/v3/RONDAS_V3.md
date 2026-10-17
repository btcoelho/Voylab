# Gerador v3 — registo de rondas (dev apenas; sem reservas, sem modelos)

**17 de outubro de 2026.** Sementes dev 91001/91003/91009. Resultados em `results/RONDA_0.json` e `results/RONDA_1.json`.

## Decisões de desenho tomadas por sondagem em dev (declaradas, não escondidas)
- Orçamento **B = 2** e **4 entradas retidas** (T). Com B ≥ 3 ou |T| = 2 o oráculo determina quase sempre o veredicto e `undetermined` deixa de ser alcançável. Alterado face ao rascunho (≤ 4, |T| = 2).
- A carta de trabalho **ajusta-se sempre às linhas iniciais** (pode ser um engodo). Em mundos aleatórios, 2/3 começavam já `rejected`, sem necessidade de consultar.
- `rejected` é absorvente (mais evidência nunca o desfaz), logo a revisão só ocorre de `undetermined` para determinado, ou por contradição (mudança). A referência de revisão é recalculada com o histórico real do agente (`revision_reference`).
- `T` fora do menu: se se pudesse consultar T, qualquer veredicto ficava determinado com 2 consultas.
- Dificuldade "difícil" (latente) **não implementada**; fácil e médio apenas.

## Ronda 0 (n = 234, sem estratificação do número de linhas iniciais)
| Falha | Evidência |
|---|---|
| Número de linhas iniciais prediz o veredicto-alvo | `n_obs`, `menu_len`, `distinct_in`: p ≈ 6e-11; `obs_id_sorted` (efeito indireto de `n_obs`) |
| Regra "só estado" acima da maioria | 52,6% (IC 46–59%) vs 38,5% |
Correção: número de linhas iniciais estratificado por índice (2, 3, 4 em rotação) dentro de cada célula.
Critério de aceitação da ronda 1: nenhuma rejeição Holm nas características de superfície/distribuição; naive Bayes ≤ maioritária + IC.

## Ronda 1 (n = 332)
| Medida | Resultado |
|---|---|
| Rejeições Holm (11 testes) | **0** (menor p = 0,073) |
| Naive Bayes superfície+distribuição | 43,4% (IC 38–49%) vs maioritária 40,7% |
| Veredicto-alvo | rejected 135, supported 135, undetermined 62 (máx. 40,7% ≤ 60%) |
| Consultas necessárias (oráculo) | 1: 174 · 2: 96 · não alcançável: 62 |
| Recomputação do veredicto só com informação pública | 0 divergências (332) |
| Duplicados | 0 |
| Células inviáveis (registadas) | 7: `undetermined` com bloco não informativo, k0 = 2 (todas as famílias, fácil e médio) e k0 = 3 (pair, médio) |
| Regra "só estado" (A0, cartas ajustadas, n_obs; leave-one-out) | 53,6% (IC 48–59%) vs maioritária 40,7% |

**Aceitação:** R3, R4, R5 e equilíbrio cumpridos. **R1 em aberto, não declarado cumprido:** a regra "só estado" ainda
bate a maioria. Parte é estrutura legítima (um A0 grande dificulta a determinação). O critério passa a ser comparativo:
cada política que consulta tem de superar a política **sem consultas** com margem fixada antes de correr (passo das
políticas de referência). Esta definição foi adotada **depois** de ver 53,6%; fica registado.

## Limitações
Fácil e médio apenas; sem ruído; |T| = 4 e B = 2 escolhidos em dev; `undetermined` só com bloco não informativo
(informativo é logicamente impossível nesse alvo); 7 células inviáveis; amostra pequena por célula (≈ 3 por semente).

## Reproduzir
```bash
python -m unittest discover -s tests -v
python audit_v3.py --no-stratify --output results/RONDA_0.json
python audit_v3.py --output results/RONDA_1.json
```

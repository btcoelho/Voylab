# v3 — políticas de referência: resultados contra as previsões ex-ante

**17 de outubro de 2026.** Previsões commitadas em `docs/V3_PREVISOES_EXANTE.md` (commit 4679da7) **antes** de
`policies.py` existir. Dev: sementes 91001/91003/91009 (332 mundos). Substituto: 92001/92003/92009 (333 mundos).
Sem modelos. Resultados completos em `results/POLITICAS_RONDA_1.json`. Alcance = veredicto comprometido igual ao
alvo atingível; diferenças pareadas com IC 95%.

| Política | Alcance dev | Alcance substituto | Consultas (média) |
|---|---|---|---|
| sem_consultas | 18,7% | 18,9% | 0 |
| aleatória (5 repetições) | 56,6% | 56,8% | 2 |
| simples | 56,9% | 56,2% | 2 |
| greedy_a (*acrescentada depois, ver P5*) | 63,6% | 67,3% | 2 |
| bayes_ig | 97,0% | 99,1% | 1,7 |
| pegajosa (só revisão; consultas de bayes_ig) | 97,0% | 99,1% | 1,7 |
| oráculo | 100% | 100% | 1,1 |

## Veredicto sobre cada previsão
| | Resultado |
|---|---|
| P1 oráculo 100% | **Confirmada** (dev e substituto). |
| P2 sem_consultas = fração `undetermined` | **Confirmada** (18,7% / 18,9%). |
| P3 bayes_ig bate aleatória e sem_consultas; maior diferença onde são precisas 2 consultas | **Confirmada**: +0,40 e +0,78 (dev); em `need = 2` bayes_ig 100% vs aleatória 9–10%. |
| P4 empate geral em alvos `undetermined` | **Confirmada**: todas 100%, incluindo sem_consultas. |
| P5 simples ≈ bayes_ig em `single`; bayes_ig > simples em `pair` | **REFUTADA.** Em `single`, simples 58% vs bayes_ig 96% (dif. +0,39, IC 0,29–0,49). Simples ≈ aleatória em todas as famílias. A heurística de discordância entre cartas não identifica o suporte nestes mundos. |
| P6 simples ≈ aleatória | **Confirmada** (dif. +0,004, IC −0,04 a 0,04; substituto −0,006). |
| P7 pegajosa falha `change` e os `stable_informative` que exigem revisão; os outros 0 | **Confirmada**: tipo I = 1,0 em `change`; nos estáveis coincide com `should_revise` (1–3%); bayes_ig 0. |
| P8 zero ações inválidas | **Confirmada**. |
| P9 bayes_ig − sem_consultas ≥ 0,25 | **Confirmada**: +0,78 (dev) e +0,80 (substituto). **Fecha o R1** na forma comparativa. |

## Consequências e limitações
- **A tarefa distingue profundidade de planeamento**, não só "consultar": a política gananciosa de um passo (greedy_a, 64–67%) fica
  30 pontos abaixo do planeamento exato (bayes_ig, 97–99%). greedy_a foi acrescentada **depois** de P5 ser refutada, para perceber porquê;
  fica sinalizada como post hoc e não entra nas previsões.
- **A refutação de P5 pesa na interpretação:** a política «simples» não é um bom padrão de heurística barata; não se pode afirmar
  que «a tarefa só se resolve com raciocínio sobre A(H)» sem uma heurística simples melhor. Fica por testar.
- **Revisão fraca nos mundos estáveis:** um agente competente já consultou, por isso só 1–3% dos blocos `stable_informative` exigem revisão.
  A revisão é testada sobretudo pelos mundos `change` (e por agentes que consultam pouco). Para modelos, convém um conjunto adicional
  de revisão sem consultas prévias — por desenhar.
- bayes_ig não é oráculo: 93–98% em alvo `rejected` (não pode saber qual consulta separa W de h sem conhecer h). Diferença para o oráculo 3 pontos (dev, IC 1–5) e 0,9 (substituto, IC −0,1 a 1,9).
- O prior uniforme em A de bayes_ig não é a distribuição do gerador.
- Os mundos substitutos usam o mesmo gerador; não são reservas.

## Reproduzir
```bash
python -m unittest discover -s tests -v
python run_policies.py --output results/POLITICAS_RONDA_1.json   # ~1 min
```

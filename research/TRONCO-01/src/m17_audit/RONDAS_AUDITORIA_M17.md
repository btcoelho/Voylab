# Auditoria M17 v2 — registo de rondas (alternativa (a))

**Data:** 17 de outubro de 2026. Sem chamadas de modelo. **Nenhuma semente reservada foi gerada**
(`guard.py` recusa-as, incluindo a cadeia de repetições `seed + 7919·k`; testado).
Conjuntos: dev (53001/53003/53009, 300 mundos) e substituto (200003/200009/200017/200023, 400 mundos,
quatro famílias). Resultados agregados em `results/RONDA_1.json` e `results/RONDA_2.json`; sem IDs de mundos.

## Ronda 1 — taxonomia inicial das características
| Falha encontrada | Evidência |
|---|---|
| Associações fortes entre categoria e características "de superfície" | 45 (dev) e 48 (substituto) testes rejeitados após Holm; naive Bayes S+D 71% e 63% (acaso 20%) |
| Erro meu de classificação | `menu_informative_count` e `menu_first_informative_pos` são calculadas a partir da evidência, não são superfície |

Correções: mover essas duas para o grupo de evidência (E); acrescentar o teste que importa — só no subconjunto em que a
evidência inicial não decide a categoria (NORMAL vs CHANGE).
Critério de aceitação da ronda 2: nesse subconjunto, nenhuma rejeição após Holm e naive Bayes S+D não superior à classe maioritária.

## Ronda 2
| Medida | dev | substituto |
|---|---|---|
| Testes rejeitados (todas as categorias, S+D) | 31 | 34 |
| Naive Bayes S+D, 5 classes | 51,7% | 46,5% |
| Controlo positivo (E) | 99,3% | 97,8% |
| Subconjunto ambíguo: n (NORMAL/CHANGE) | 74 (14/60) | 103 (23/80) |
| Subconjunto ambíguo: rejeições Holm | 0 | 0 |
| Subconjunto ambíguo: NB S+D vs maioritária | 81,1% vs 81,1% | 76,7% vs 77,7% |
| Calibração nula (permutação de rótulos, 5 vias) | 4% com alguma rejeição | 5% |
| Potência (sintética, 60 mundos/categoria) | 5% a 10% de fuga; 87% a 20%; 100% a 30% | — |
| Fuga plantada de ponta a ponta no dev | detetada a partir de 20% | — |
| Duplicados dentro/entre conjuntos | 0 / 0 | 0 / 0 |
| Transferência dev → famílias substitutas (NB S+D) | 36%–52% | — |

**Aceitação:** cumprida para o critério da ronda 2. Nenhuma característica de superfície ou de distribuição prediz a
categoria *onde a evidência não a decide*, com potência para fugas de cerca de 20% ou mais.

## O que fica por resolver (falhas do gerador, não do auditor)
1. **A categoria quase sempre é decidida pelo estado inicial.** Uma regra que só olha para o conjunto de categorias
   compatíveis acerta 95,3% (dev) e 94,3% (substituto); transfere entre famílias (92%–96%). Só NORMAL vs CHANGE precisa de consulta.
   O gerador mal testa "escolher consultas úteis".
2. **Desequilíbrio no caso ambíguo:** 77%–81% são CHANGE. "Responder sempre CHANGE quando ambíguo" já dá esse valor.
3. **INSUFFICIENCY** (menu sem informação) é incompatível com o contrato v2; precisa de definição própria pré-registada.
4. As rejeições restantes (D.rows_*, json_length) refletem a estrutura da evidência (p. ex. linhas contraditórias);
   não são atalhos para além de E, mas não foram eliminadas.

## Decisão após 2 rondas (limite: 3)
**Reformular, não avançar.** O M17 como está não serve de critério de sucesso do tronco: o gerador é identificável e sem
fuga de superfície detetável, mas demasiado fácil de resolver sem consultas e desequilibrado no único caso que as exige.
O v3 deve (a) equilibrar os casos ambíguos, (b) exigir consultas em mais categorias, (c) definir INSUFFICIENCY a priori.
Não foi usada a terceira ronda; não há falha adicional que ela corrigisse com os dados disponíveis.

## Limitações
Famílias substitutas são sementes novas do mesmo gerador, não as reservadas; conclusões sobre a lógica do gerador
transferem-se, as sobre distribuições reservadas não. Identificabilidade ao nível das três explicações listadas.
Potência só para fugas ≳20%. Análise de consultas não adaptativa.

## Reproduzir
```bash
python -m unittest discover -s tests -v
python audit_m17_v2.py --round 1 --output results/RONDA_1.json
python audit_m17_v2.py --round 2 --output results/RONDA_2.json
```

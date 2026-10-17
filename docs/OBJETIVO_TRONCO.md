# TRONCO-01 — objetivo numa página

**Versão 1 · 17 de outubro de 2026 · aprovado por Bruno em 17/10/2026 (20:38, Europe/Lisbon)**

## Âmbito
Construir e **demonstrar experimentalmente** um *tronco* de investigação geral, reutilizável e verificável. O tronco deve descobrir e enquadrar problemas, não apenas executar uma política dada. O manuscrito Voynich é uma **aplicação futura**; não é dado de treino, nem critério de sucesso, nem fonte para escolher parâmetros nesta fase.

## Capacidades que a próxima versão tem de demonstrar
| # | Capacidade | Medida primária (definida no pré-registo v3) |
|---|---|---|
| C1 | Reconhecer um problema (contradição, mudança de regra, hipótese ausente) e distingui-lo de ruído ou de insuficiência | sensibilidade e especificidade por categoria, com IC 95% |
| C2 | Enquadrar sem assumir a solução, incluindo hipóteses **fora** da lista declarada | recuperação e validade do conjunto de respostas admissíveis |
| C3 | Identificar a informação em falta | fração das entradas ainda em aberto que o agente nomeia corretamente |
| C4 | Pedir informação útil dentro de um orçamento | ganho de informação realizado por consulta, face às referências |
| C5 | Rever conclusões perante evidência contrária e manter a conclusão perante contestação inválida | revisão correta com contestação válida; manutenção correta com contestação inválida, irrelevante ou contraditória |
| C6 | Saber parar | regra de paragem pré-registada cumprida; sem consultas a mais nem a menos |
| C7 | Reconhecer casos não identificáveis | taxa de resposta "não resolvido" com incerteza residual correta |

Perda de treino, JSON válido e imitação de uma política de referência **não** contam como competência científica.

## Fora de âmbito
Voynich, imagens, fine-tuning novo, árvore multiagente completa e especialistas, benchmarks externos antes da validação interna (BoxingGym, HypoSpace), ruído de medição e causalidade geral (a v3 é determinística e finita; é um limite declarado), alterar ou apagar os adaptadores M16 e M17.

## Critérios de sucesso e de insucesso
- **Porta da tarefa (antes de qualquer modelo candidato):** (i) as quatro referências (oráculo, ganho de informação, regra simples, aleatória) comportam-se como **previsto ex-ante** em cada classe de cenário, com IC 95% e por família; (ii) a auditoria de pistas acidentais não encontra associação inexplicada; (iii) os casos não identificáveis estão excluídos e contados à parte.
- **Porta do agente:** supera a melhor referência não-oráculo na métrica primária, com o limite inferior do IC 95% acima da margem δ fixada no pré-registo, em pelo menos duas das três famílias e sem regressão em nenhuma. Taxa de ações inválidas ≤ 1% e relatório explícito em ≥ 98% dos episódios, como condições técnicas.
- **Insucesso:** qualquer porta falhada. Não se compensa uma porta com outra.

## Previsões ex-ante das referências (a hierarquia não é assumida)
| Classe de cenário | Previsão |
|---|---|
| S1: a verdade está na lista declarada e as consultas diferem em informação | ganho de informação > aleatória; ganho de informação ≥ regra simples; oráculo ≥ todas |
| S2: a verdade está fora da lista declarada | regra simples de sondagem de contradições pode igualar ou superar o ganho de informação; oráculo ≥ todas |
| S3: todas as consultas são igualmente informativas, ou o caso não é identificável | todas empatam; pontuação por conjunto |
| S4: orçamento suficiente para esgotar o menu | todas empatam em resposta final; diferem só em custo |

Cada previsão é testada com IC 95% e por família. Uma previsão falhada marca a **tarefa** como não apta, não o agente. As previsões numéricas exatas são fixadas no pré-registo v3 antes de qualquer execução.

## Orçamento de auditoria
**Três rondas por etapa.** Cada ronda produz: lista explícita de falhas, correções e critérios de aceitação. Esgotadas as três, regista-se uma decisão fundamentada entre **avançar, reformular ou suspender**. Nunca se declara sucesso por falta de tempo.

## Condições que impedem a progressão
1. Manifesto, equivalência `src/`↔ZIPs ou CI falham.
2. Alguma reserva cega aberta, reutilizada ou gerada antes do congelo do protocolo.
3. Auditoria de pistas com associação inexplicada, ou sem controlo de potência (pista plantada).
4. Definição de insuficiência do M17 sem pré-registo próprio.
5. Referências que não se distinguem como previsto.
6. Ensaio de modelo sem ficha fechada (hipótese, métrica, orçamento, condição de sucesso) e sem análise anterior fechada.
7. Qualquer artefacto histórico alterado.

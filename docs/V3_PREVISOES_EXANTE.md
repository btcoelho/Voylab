# TRONCO-01 v3 — políticas de referência e previsões ex-ante

**17 de outubro de 2026.** Escrito e commitado **antes** de existir o código das políticas e antes de qualquer corrida.
Não se assume oráculo > ganho de informação > simples > aleatória em todos os cenários. Cada previsão abaixo é uma
hipótese que a corrida pode refutar; se for refutada, regista-se como refutada (não se reescreve).

## Episódio e métricas
Cada política vê só o estado público, pode fazer até B = 2 consultas do menu, compromete-se com um veredicto calculado
**de A(H) sobre o seu próprio histórico** (todas calculam A exatamente, logo o veredicto é coerente com o histórico), e
na fase 2 recebe o bloco de evidência e decide manter ou rever.
- **alcance** (`reach`): o veredicto final igual ao `target_verdict` do mundo (o melhor atingível com B consultas).
- **consultas gastas**; **ações inválidas** (esperado 0).
- **erro de revisão**: não reviu quando `revision_reference` exige (tipo I) ou reviu sem necessidade (tipo II).
- Comparações pareadas por mundo; IC 95% da diferença média (aproximação normal; n ≥ 100); por família, dificuldade e alvo.
- «A bate B» = IC 95% da diferença de alcance estritamente > 0. «Empate» = IC inclui 0 e |diferença| < 0,05.

## Políticas
1. **sem_consultas**: não consulta; compromete-se com A(H₀).
2. **aleatória**: 2 consultas uniformes do menu (sem repetição).
3. **simples**: regra fixa, sem raciocinar sobre A: consulta as entradas do menu onde a carta de trabalho W discorda do maior número das outras cartas declaradas (desempate pela ordem do menu).
4. **bayes_ig**: recursão exata sobre A com prior uniforme em A: minimiza a probabilidade esperada de acabar `undetermined`, profundidade = orçamento restante, replaneando depois de cada resposta.
5. **oráculo**: usa h; escolhe o conjunto mínimo que determina o veredicto.
6. **pegajosa** (controlo negativo, só revisão): consultas de bayes_ig, mas nunca revê depois de comprometida.

## Previsões (todas por refutar)
- **P1.** oráculo: alcance 100% em todas as células (por construção; se falhar, há erro no avaliador).
- **P2.** sem_consultas: alcance = fração de alvos `undetermined` (≈ 19% no dev), ± IC; é o piso.
- **P3.** bayes_ig bate aleatória e sem_consultas no alcance global; maior diferença em mundos de alvo `supported` com 2 consultas necessárias.
- **P4.** Em alvos `undetermined`, **todas** as políticas empatam, **incluindo sem_consultas**: não há veredicto melhor para atingir.
- **P5.** Família `single`: simples ≈ bayes_ig (empate), porque discordância entre cartas identifica o suporte. Família `pair`: bayes_ig bate simples. *Se não se verificar, a diferença entre simples e bayes_ig não vem do raciocínio sobre A e a tarefa não distingue o que queremos.*
- **P6.** aleatória pode empatar com simples no global. **Não se prevê** simples > aleatória.
- **P7.** Revisão: bayes_ig, simples, aleatória, oráculo, sem_consultas têm erro de revisão 0 (recalculam A); **pegajosa** falha todos os mundos `change` e todos os `stable_informative` em que a fase 2 altera o veredicto no seu histórico, e acerta os restantes. Isto valida que a métrica de revisão deteta quem não revê.
- **P8.** Nenhuma ação inválida em nenhuma política.
- **P9 (fecha R1).** bayes_ig supera sem_consultas por ≥ 0,25 de alcance (margem fixada agora) em dev e substitutos. Se não, a tarefa é considerada demasiado fácil de resolver sem consultas e volta-se ao desenho.

## Refutação
Uma previsão refutada exige ronda de auditoria com lista de falhas, correção e critérios (limite de 3 rondas por etapa).

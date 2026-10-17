# TRONCO-01 v3 — previsões ex-ante, segunda série (grupo 2)

**17 de outubro de 2026, antes de existir o código.** Sementes de confirmação-dev **novas** (93001/93003/93009), usadas uma só vez.
Não são reservas. As escolhas de desenho do v3 foram feitas em dev; esta série verifica se P3, P6, P9 generalizam e testa o que se acrescenta.
Mesma regra de comparação: «A bate B» = IC 95% pareado da diferença de alcance > 0; «empate» = IC inclui 0 e |dif| < 0,05.

## Políticas e sondas novas
- **rival** (heurística barata, definida agora): entre as cartas declaradas ≠ W que ajustam todas as linhas, consulta a primeira entrada do menu onde W e o rival diferem; sem rival ajustado, consulta a entrada do menu mais afastada (Hamming) das já observadas. Não enumera A(H).
- **primeiro_do_menu** (sonda de atalho): consulta as 2 primeiras entradas do menu.
- **cega_pegajosa**: compromete-se sem consultas e nunca revê (controlo negativo da revisão sem consultas prévias).
- **ignora_evidencia**: consulta como bayes_ig, mas compromete-se sempre `undetermined` (controlo negativo da métrica «evidência ignorada»).

## Previsões
- **Q1.** P3 generaliza: bayes_ig bate aleatória e sem_consultas na confirmação-dev. **Q2.** P6 generaliza: simples ≈ aleatória. **Q3.** P9: bayes_ig − sem_consultas ≥ 0,25.
- **Q4.** rival bate simples e aleatória no global (dif. > 0). **Q5.** rival fica abaixo de bayes_ig no global (IC da diferença > 0). **Q6.** Por alvo/necessidade: rival ≈ bayes_ig em `need = 1`, rival < bayes_ig em `need = 2`.
  *Se Q6 falhar, a diferença bayes_ig vs heurística não é planeamento a 2 passos.*
- **Q7.** primeiro_do_menu ≈ aleatória (sem atalho de posição). Se bater a aleatória, a ordem do menu é uma fuga.
- **Q8.** cega_pegajosa: erro de revisão tipo I = taxa de `should_revise` de cada célula (100% em `stable_informative` e em `change*`); tipo II = 0.
- **Q9.** Mudança indireta (`change_indirect`): nenhuma entrada do bloco repete uma entrada das linhas iniciais nem das consultas do oráculo; bayes_ig e sem_consultas têm tipo I = 0; pegajosa tipo I = 1,0.
- **Q10.** Decomposição de erros: nas políticas de referência, erro de inferência = 0; erro de procura = 1 − alcance. ignora_evidencia: erro de inferência e evidência ignorada = fração de mundos cujo veredicto do próprio histórico é determinado (≈ alcance de bayes_ig − fração `undetermined`, ± 0,03).
- **Q11.** Auditoria do texto: nenhuma característica do prompt (comprimento, posição da carta de trabalho, ordem das cartas, rank da consulta do oráculo no menu) prediz o alvo (0 rejeições Holm); a posição da primeira consulta do oráculo no menu não difere do acaso.

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

~~**Achado: pista de posição no gerador.**~~ **Retirado na §7.** O valor de 58% vinha de um defeito da medição: com empates, contava-se a posição do primeiro empate. Não há mundos com uma melhor consulta única no gerador atual, e com a posição média dos empates a melhor fica a 0,50.

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

## 7. Resultados das variantes (ronda 1; `results/instrumento/CONSULTAS_VARIANTES.json`)

| | V1 (k₀ 5–7) | V2 (orçamento 1) | V3 (menu curto) | critério |
|---|---|---|---|---|
| mundos (equilibrados) | 324 | 270 | 324 | |
| gap mediana | 0,000 | **0,346** | 0,083 | ≥ 0,25 |
| mundos com gap ≥ 0,25 | 4% | **74%** | 5% | ≥ 50% |
| qualidade da evidência | 0,780 | **0,783** | 0,875 | ≥ 0,80 |
| valor médio do menu | 0,748 | 0,406 | 0,774 | ≤ 0,60 |
| alvos equilibrados | sim | sim | sim | sim |
| pista de superfície (melhor preditor / acaso) | 1,03× | 1,39× | 1,31× | ≤ 2× |
| células inviáveis | 0 | 24 | 19 | |

**Defeito da medição de posição, encontrado e corrigido** (`results/instrumento/CONSULTAS_POSICAO_CORRIGIDA.json`). A posição da melhor consulta era a do *primeiro* empate. Na linha de base, na V1 e na V3, **nenhum mundo tem uma melhor consulta única**: há sempre vários empates. Por isso "a melhor está em primeiro" valia 58% (linha de base) e 92% (V1) mesmo com o menu baralhado. A correção é uma definição, não um limiar, e aplica-se a todos por igual:
- posição média dos empates;
- e, nos mundos com melhor única, a posição dessa.

| | mundos com melhor única | posição (média dos empates) | posição (melhor única) | melhor única em 1.º lugar |
|---|---|---|---|---|
| linha de base | 0 | 0,50 | — | — |
| V1 | 0 | 0,50 | — | — |
| V2 | 140/270 | 0,47 | 0,44 | 0,171 (limite: 1,5/8,8 = 0,170) |
| V3 | 0 | 0,51 | — | — |

**Consequência:** a pista de posição de 58% anunciada na §3 é retirada. Não existe no gerador. Em ~60% dos mundos `q1` está entre as melhores, mas isso é o acaso de acertar numa das melhores com tantos empates (0,596). A conclusão da fase 3 de que os modelos escolhem pela posição mantém-se; a de que o instrumento os favorecia por posição, não.

**Critérios:**
- **V1:** falha 1, 3 e 4.
- **V3:** falha 1 e 4.
- **V2:** cumpre 1 (mediana 0,346; 74% ≥ 0,25), 2 (posição 0,44–0,47; a taxa em 1.º lugar fica no limite, 0,171 contra 0,170), 4, 5 e 6. **Falha o 3: qualidade 0,783 < 0,80.**
- Nenhuma variante cumpre todos.

**Previsões:**
- C-a confirmada quanto ao falhanço da V1, mas a mediana (0,000) ficou abaixo do intervalo previsto.
- **C-b confirmada exatamente:** a V2 cumpre o critério 1 e falha o 3.
- **C-c refutada:** a V3 não cumpre o critério 1. Ao reduzir o menu, a segunda consulta continua a compensar uma má primeira escolha.
- **C-d:** com a medição corrigida, a posição fica em [0,40; 0,60] em todas (confirmada).
- **C-e refutada:** nenhuma cumpre tudo.

**Achado estrutural:** com orçamento 2, a segunda consulta neutraliza a escolha da primeira (V1 e V3 têm gap ≈ 0). A alavanca só aparece quando a escolha não pode ser corrigida depois (V2).

**Decisão: segundo a regra da §5, registar o falhanço e decidir com o Bruno.** Não se mexe nos critérios nem se afina nenhuma variante sem essa decisão.

## 8. Ronda 2: pré-registo (decisão do Bruno, 18/10, 12:45; escrito antes de implementar e de medir)
Máximo de três variantes novas. Os critérios, os limiares e a métrica não mudam. **Se nenhuma passar, para-se e reavalia-se o desenho da tarefa**, sem criar mais variantes.

### Construção exata
Todas usam os mundos de desenvolvimento (sementes 91xxx), a mesma grelha de células de `audit_v3.dev_set`, k₀ ∈ {2, 3, 4} estratificado como hoje, o conjunto equilibrado por `balance_trim`, o menu baralhado por mundo com uma semente derivada do uid, e o alvo recalculado pelo mesmo oráculo (`determination`) sobre o menu da variante.
- **V4: uma consulta, menu completo.** Orçamento 1. O menu tem as **16 entradas**, incluindo as já observadas (consultá-las não traz informação) e as 4 retidas (consultá-las revela a saída numa entrada retida).
- **V5: duas consultas sequenciais, menu completo.** O mesmo menu de 16 entradas da V4; orçamento 2. A segunda consulta é escolhida depois de ver a resposta da primeira. A diferença para a linha de base atual é só o menu completo, por isso V4 e V5 diferem **apenas** na possibilidade de se adaptar.
- **V6: uma consulta, menu reduzido por um critério independente.** Orçamento 1. Menu = 6 consultas tiradas **ao acaso** do menu atual (semente do uid), sem usar o valor de nenhuma consulta. Testa se a discriminação da V2 vem da estrutura (uma só consulta) ou do menu.

### Métrica (a da §2, sem alterações)
- **v2(q)** com o orçamento da variante: com orçamento 1, a probabilidade de ficar determinado depois de q; com orçamento 2, depois de q e da melhor segunda consulta escolhida conforme a resposta.
- **gap** = max − média sobre o menu completo da variante, com peso uniforme.
- **Posição com a correção da §7:** média da posição dos empates, e posição da melhor nos mundos com melhor única.
- **Só na V5, medidos à parte** (precaução do Bruno):
  - **valor da 1.ª consulta sozinha**: v1(q), a probabilidade de ficar determinado só com q, e o respetivo gap1;
  - **ganho da 2.ª**: v2(q) − v1(q), em média no menu e na melhor consulta.
  Assim não se confunde a qualidade da seleção inicial com o que a adaptação acrescenta. O critério de aceitação aplica-se ao v2, como em todas as outras.

### Critérios (iguais para as três)
1. mediana do gap ≥ 0,25 **e** ≥ 50% dos mundos com gap ≥ 0,25;
2. sem pista de posição: posição média dos empates em [0,40; 0,60]; nos mundos com melhor única, a melhor fica em 1.º lugar em ≤ 1,5/|menu|;
3. valor da melhor consulta (média de max v2) ≥ 0,80;
4. valor de uma consulta ao acaso (média do menu) ≤ 0,60;
5. alvos equilibrados (1/3 cada);
6. sem pista de superfície: nenhum preditor trivial identifica a melhor consulta acima do dobro do acaso. Os preditores são:
   - distância de Hamming às observações (máxima e mínima);
   - "a consulta é uma entrada retida" (novo, porque V4 e V5 incluem as retidas no menu);
   - "a consulta não é uma entrada já observada".

**Regra de escolha:** avalia-se pela ordem V4, V5, V6. A primeira que cumprir os seis critérios é a escolhida. Se nenhuma cumprir, para-se.

### Previsões ex-ante
- **D-a (V4).** Cumpre 1, 3 e 4: as entradas já observadas valem 0 e baixam a média, e as retidas sobem a melhor. **Risco no critério 6:** "consultar uma retida" pode identificar a melhor acima do dobro do acaso. Prevejo que a V4 **falha o 6**.
- **D-b (V5).** Falha o critério 1 (mediana < 0,25), pela mesma razão da V1 e da V3: a segunda consulta compensa. O ganho médio da segunda (v2 − v1) é ≥ 0,15.
- **D-c (V6).** Gap semelhante ao da V2 (mediana entre 0,25 e 0,40), mas falha o critério 3 (< 0,80), porque escolher o máximo entre 6 opções ao acaso baixa a melhor.
- **D-d.** Prevejo que **nenhuma** das três cumpre os seis critérios, e que a ronda termina com a paragem e a reavaliação do desenho.

## 9. Ronda 2: resultados (`results/instrumento/CONSULTAS_VARIANTES_R2.json`)

| | V4 (1 consulta, menu de 16) | V5 (2 adaptativas, menu de 16) | V6 (1 consulta, 6 ao acaso) | critério |
|---|---|---|---|---|
| mundos (equilibrados) | 225 | **48** | 300 | |
| gap mediana (quartis) | **0,438** (0,344–0,638) | 0,090 (0,072–0,177) | 0,324 (0,205–0,500) | ≥ 0,25 |
| mundos com gap ≥ 0,25 | **91%** | 2% | 66% | ≥ 50% |
| valor da melhor (média de max v2) | **0,806** | 0,942 | 0,762 | ≥ 0,80 |
| valor médio do menu | **0,332** | 0,824 | 0,413 | ≤ 0,60 |
| posição média dos empates | 0,49 | 0,50 | 0,50 | [0,40; 0,60] |
| melhor única em 1.º lugar | 0,044 (90 mundos com melhor única; limite 0,094) | sem mundos com melhor única | 0,175 (limite 0,25) | ≤ 1,5/\|menu\| |
| pista de superfície mais forte (acerto / acaso) | 1,47× (Hamming máx.); retida 1,27×; não observada 1,25× | 1,52× | 1,29× | ≤ 2× |
| alvos equilibrados | sim | sim | sim | |
| **todos os critérios** | **sim** | não (1, 4) | não (3) | |

- **V5, medidas separadas.** A 1.ª consulta sozinha tem gap mediano 0,284. O ganho médio da 2.ª consulta é 0,444 sobre o menu e 0,429 na melhor. A adaptação acrescenta muito valor, e é por isso que, com duas consultas, a escolha da primeira deixa de discriminar. Além disso, com o menu completo e duas consultas quase tudo fica determinado: só 48 mundos sobrevivem ao equilíbrio dos alvos.
- **Previsões:**
  - D-a confirmada nos critérios 1, 3 e 4, mas **refutada no 6**: a pista "consultar uma retida" fica em 1,27×, não acima de 2×;
  - **D-b confirmada** (falha o 1; ganho da 2.ª ≥ 0,15);
  - **D-c confirmada exatamente** (gap 0,32, falha o 3 com 0,762);
  - **D-d refutada**: a V4 cumpre tudo.
- **Decisão pela regra da §8: a V4 é a variante escolhida** (a primeira, pela ordem, a cumprir os seis critérios).

### Sensibilidade da V4 (relatada, não usada para afinar; `CONSULTAS_V4_SENSIBILIDADE.json`)
- **A discriminação é estrutural, não vem das opções sem valor.** Sem as entradas já observadas no menu, a mediana do gap é 0,359 e 80% dos mundos ficam ≥ 0,25. Sem as observadas nem as retidas, 0,340 e 73%.
- **A qualidade passa pela média, mas é heterogénea.** Média 0,806, com o critério cumprido por pouco: 55,6% dos mundos têm a melhor consulta abaixo de 0,80 (percentil 10 = 0,60), e a média é sustentada pelos mundos em que a melhor decide sempre. Isto fica registado como ponto fraco do instrumento. Ao validar a tarefa V4 completa, reporta-se o resultado por estrato de qualidade.

### Próximos passos (sem corridas de modelos, sem partição cega)
1. Implementar a V4 como tarefa completa no ambiente (orçamento 1, menu de 16; consultar uma entrada já observada é uma ação válida que não traz informação). Repetir sobre ela as validações das fases 1 e 2: verificador independente, políticas plantadas e mutação.
2. Piloto humano sobre a V4.
3. Modelo de fronteira, só depois.

## 10. V4 como tarefa completa: validação (pré-registo, 18/10 13:05, antes de correr)
O que se repete sobre os 225 mundos V4 de desenvolvimento, com o mesmo ambiente (`env_v3.Episode`, orçamento 1, menu de 16 entradas):
1. **Verificador independente** (Node.js): árvore completa (todas as consultas do menu e todas as respostas possíveis, mais o estado de revisão de cada uma). Veredicto da leitura 70 recalculado só a partir da vista pública.
2. **Políticas com defeitos plantados** (as 10 da fase 2), jogadas pelo ambiente nos mundos V4. A grelha classifica cada uma no rótulo que a construção implica.
3. **Mutação** da grelha e da pontuação, com os testes estendidos aos mundos V4.

**Previsões:**
- **E-a.** 0 divergências no verificador.
- **E-b.** 0 erros nas políticas plantadas, com todas as categorias exercitadas.
- **E-c.** ≥ 90% de mutantes mortos.
- **E-d.** Consultar uma entrada já observada é aceite pelo ambiente e não altera o veredicto do próprio histórico, o que é verificado à parte.

**Critério:** E-a, E-b e E-c cumpridos. Caso contrário, há ronda de correção (máximo 3), sem tocar no gerador nem nos critérios da §8.

## 11. Piloto humano sobre a V4: protocolo (pré-registo; aprovado pelo Bruno a 18/10, 11:21, como piloto e não como amostra representativa)
- **Participantes:** 2 a 3 pessoas (o Bruno e uma ou duas que não conheçam o projeto). Sem treino prévio além do enunciado.
- **Episódios:** 20 mundos V4 de desenvolvimento, iguais para todos e na mesma ordem, escolhidos de forma determinística (semente fixa) e estratificados assim:
  - alvo: 7 `supported`, 7 `rejected`, 6 `undetermined`;
  - qualidade da melhor consulta (o ponto fraco da §9): 10 com max v2 ≥ 0,80 e 10 com < 0,80;
  - pelo menos 8 com mudança na revisão.
- **Interface:** uma página privada que mostra exatamente o prompt v3.1 (com orçamento 1) e o estado como o modelo o vê:
  1. escolher 1 das 16 consultas;
  2. ver a resposta;
  3. comprometer-se com um veredicto, as cartas admissíveis e as 4 previsões;
  4. ver a evidência nova;
  5. manter ou rever.
  - Tudo é registado: a ação, o momento e o participante.
  - As respostas ocultas estão no código da página. Num piloto de pessoas colaborativas isto é aceitável, mas fica dito.
- **Medidas** (com o código de análise já existente):
  - grelha ITT;
  - revisão final correta;
  - valor v2 da consulta escolhida, comparado com a melhor e com a média do menu;
  - **kappa de Cohen** entre pessoas e de cada pessoa contra a referência (o veredicto do próprio histórico);
  - tempo por episódio;
  - tudo também separado por estrato de qualidade.
- **Critério (da fase 4.1):** macro fundamentado ≥ 0,80 e kappa contra a referência ≥ 0,70 significam que o enunciado está bem posto. Abaixo disso, volta-se ao enunciado e não aos modelos.
- **Previsões:**
  - H-a: as pessoas escolhem uma consulta de valor acima da média do menu em ≥ 70% dos episódios;
  - H-b: o macro fundamentado fica entre 0,6 e 0,9, com mais erros no estrato de qualidade baixa e em `undetermined`;
  - H-c: kappa contra a referência ≥ 0,6;
  - H-d: tempo mediano por episódio entre 2 e 6 minutos.

## 12. V4: resultados da validação da tarefa completa
- **E-a confirmada:** 0 divergências em 12 836 estados (6 418 pré-compromisso e 6 418 de revisão), com |H| = 70 obtido de forma independente (`results/instrumento/V4_F1/`).
- **E-b confirmada:** 10 políticas plantadas × 225 mundos = 2 250 episódios, **0 erros**, todas as categorias exercitadas e a revisão certa em todos.
- **E-c confirmada:** **36/36 mutantes mortos** (2 por erro), `results/instrumento/V4_MUTACOES.json`. O mutante de `should_revise`, que sobrevivia antes, morre agora com os testes da V4.
- **E-d confirmada:** consultar uma entrada já observada é aceite (225/225) e não muda o veredicto (225/225).
- **Decisão: a V4 fica validada como tarefa** (ronda 1 de 3). Segue-se o piloto humano da §11.

### Página do piloto humano (publicada a 18/10)
- Página privada no claude.ai, gerada a partir de `instrument/piloto_humano_template.html` e de `results/instrumento/PILOTO_HUMANO_EPISODIOS.json` (sha `fc56988c…`).
- Cada participante grava um documento em `respostas/<id>`. Regras: leitura do conjunto só para editores; cada participante lê e escreve apenas o seu.
- Verificação funcional: com acesso de participante, uma listagem do conjunto não mostra o documento de outra pessoa (sonda gravada e apagada).
- Ressalva já registada na §11: as respostas certas estão no código da página.

## 13. Piloto humano: protocolo revisto (aprovado pelo Bruno, 18/10, 16:16, antes de qualquer resposta)
**Porquê.** O v3.1 pede um raciocínio sobre 70 regras invisíveis. Uma pessoa sem ferramenta pode falhar só por isso, e então não saberíamos se o enunciado está mal posto ou se a tarefa é só impraticável de cabeça.

**Duas condições, dentro de cada pessoa:**
- **A, sem ajuda:** exatamente como na §11.
- **B, com ajuda:** a página mostra, calculado a partir do que a pessoa vê, o número de regras (das 70) ainda admissíveis, se W é admissível, quais das três cartas são admissíveis e os padrões de saída das regras admissíveis nas 4 entradas retidas, com contagens. A ajuda atualiza-se no início, depois da consulta e depois da evidência nova. Com a ajuda, o veredicto fica quase mecânico. O que a condição B mede é **a escolha da consulta e a revisão**, com o cálculo de A feito por código, que é o desenho recomendado na fase 5.

**Atribuição:**
- os 20 episódios dividem-se em dois conjuntos de 10, equilibrados por alvo e por estrato de qualidade (conjuntos X e Y, fixados por `human_pilot.split`);
- participantes com código ímpar (P1, P3) fazem X sem ajuda e Y com ajuda; os de código par (P2), o contrário;
- a ordem dos episódios é sempre 1 a 20 e cada episódio diz em que condição está;
- o código tem de ter a forma P1, P2, P3.

**Leitura dos resultados (ponto 3 da revisão).** Com 10 episódios por pessoa e condição, os intervalos são largos. Cada critério é lido como **passa** (limite inferior do IC 95% ≥ limiar), **falha** (limite superior < limiar) ou **inconclusivo**:
- proporção de episódios fundamentados: intervalo de Wilson;
- kappa: bootstrap sobre episódios, 2 000 reamostragens.

Os limiares da §11 mantêm-se: fundamentado ≥ 0,80 e kappa contra a referência ≥ 0,70.

**Estratos obrigatórios (ponto 6).** O código de análise reporta sempre todos os resultados separados por estrato de qualidade (melhor consulta ≥ 0,80 ou < 0,80) e por condição. Não há resultado agregado sem a respetiva desagregação.

**Previsões adicionais:**
- **H-e.** Na condição B, fundamentado ≥ 0,80 (passa ou inconclusivo, nunca falha) e kappa contra a referência ≥ 0,7.
- **H-f.** Na condição A, fundamentado < 0,80: as pessoas falham sem ajuda, o que confirma que o estrangulamento é o cálculo de A, tal como nos modelos.
- **H-g.** A escolha de consulta (valor v2 da escolhida acima da média do menu) não difere mais de 0,15 entre condições, porque a ajuda não mostra o valor das consultas.

**Análise escrita e testada antes de haver respostas reais:** `instrument/analyse_human.py`, testada com participantes sintéticos (§14).

### 13.1 Ressalva de desenho (revisão, 18/10)
Com as capacidades atuais da página não é possível esconder as respostas: os episódios e a referência ficam num documento partilhado (`db`) que a análise lê e que, por isso, os participantes também conseguem ler. O piloto é feito só com pessoas colaborativas que aceitam não consultar o código nem os dados; esta ressalva acompanha qualquer resultado do piloto, que não serve como prova contra um participante adversarial.

## 14. Piloto humano: segunda revisão do protocolo (aprovada pelo Bruno, 18/10, 16:55, antes de qualquer resposta)

Feita depois de uma revisão crítica; nenhum resultado humano existia. Substitui o que §11 e §13 dizem em contrário.

1. **Natureza do piloto: descritiva (opção b).** Com 3 pessoas × 10 episódios por condição, o agregado só passaria com 29 ou 30 em 30 (com taxa verdadeira de 90%, P(passa) ≈ 0,18). O piloto serve para encontrar defeitos na tarefa, na página e na grelha, e para estimar o tempo e a taxa de acerto. As leituras passa/falha/inconclusivo continuam a ser calculadas e reportadas, mas **a decisão sobre a resolubilidade humana fica para uma amostra posterior**, dimensionada com as estimativas deste piloto. Os limiares (0,80 e 0,70) não mudam.
2. **Participantes: 4 (P1–P4)**, 2 de código ímpar e 2 de código par, para o contrabalanço ficar 2 contra 2.
3. **Ordem intercalada:** os episódios passam a seguir a ordem fixa X, Y, X, Y, … (sha do ficheiro `eeaffd9e…`). Cada participante alterna as condições (ímpares A,B,A,B…; pares B,A,B,A…), e a aprendizagem deixa de se confundir com a ajuda. A seleção dos 20 e a partição X/Y não mudaram.
4. **Leitura da condição B:** a ajuda mostra as regras admissíveis, os seus padrões nas retidas e o de W; o veredicto lê-se quase diretamente. A condição B é **um teto e um teste de compreensão da tarefa**, não uma medida de raciocínio com apoio.
5. **Defeito corrigido:** a ajuda da condição B no passo da revisão estava calculada mas não era mostrada; passa a ser.
6. **Treino:** 2 episódios de treino (um com alvo `rejected`, outro `supported`), do mesmo conjunto de desenvolvimento da V4 e fora dos 20, o primeiro sem ajuda e o segundo com ajuda, com a resposta de referência no fim. Não entram na análise (`results/instrumento/PILOTO_HUMANO_TREINO.json`).
7. **Concordância simples** reportada ao lado do kappa (contra a referência e entre pessoas), porque com veredictos desequilibrados o kappa pode ser baixo com muita concordância.
8. **Fuga:** além do documento `db`, as respostas estão no código da página; a introdução pede explicitamente para não o abrir. Ressalva de §13.1 mantém-se.
9. **Verificação ponta a ponta** (`tests/test_pilot_page_e2e.py`): um participante simulado clica a página real no Chromium; o registo gravado, passado por `analyse_human`, dá exatamente as mesmas linhas que o mesmo comportamento escrito à mão (P1 e P2); confirma a alternância das condições, a ajuda na revisão só em B e o retorno do treino. Com a linha da ajuda na revisão retirada, o teste falha (mutação apanhada). Corre localmente com TRONCO_SLOW=true; no CI é saltado, porque o Playwright não está instalado lá.
10. **Ensaio do Bruno (P0)** antes dos participantes, com 3–4 episódios, para medir o tempo e a clareza das instruções. Não conta para a análise; o código P0 fica reservado para isso.

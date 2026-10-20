# TEXTO-01: agente de análise de texto e manuscritos (especificação, 19/10/2026)

Mudança de rumo decidida pelo Bruno (19/10, 06:08): antes de avançar com mais experiências na V4, o agente tem de saber analisar texto. Tem de identificar características linguísticas e padrões, questionar hipóteses de cifra e reportar. Enquanto isto não estiver assente, o resto fica parado: a validação drand (§22) e o Strands Decider (§25) ficam em pausa, sem nada gerado nem descarregado.

Mantêm-se as regras do projeto: não treinar modelos; o Voynich é aplicação futura, nunca dado de desenvolvimento nem critério de sucesso; previsões escritas antes de cada corrida; partição cega só para a validação final; descargas e chamadas a APIs só com aprovação caso a caso.

## 1. O que se aproveita da V3/V4

- **A lição de §24:** tudo o que pode ser código é código. O modelo nunca calcula números; pede medidas e interpreta-as. Cada afirmação numérica do relatório é recalculada por um verificador de código, e uma afirmação falsa é uma falha, não um detalhe.
- **A estrutura epistémica da V3:** cada hipótese recebe `rejeitada`, `compatível` ou `indeterminada`, com a evidência que a sustenta. Não basta dizer "parece cifra": tem de citar o teste que a distingue das alternativas.
- **A disciplina:** pré-registo congelado por sha256, retoma sem chamadas duplicadas, referências obrigatórias (constante e regra simples), intervalos Wilson, resultados por família.
- **O código:** `deepseek_backend.py`, o padrão de `Logged`/retoma, `analyse_human.wilson`.

## 2. Entrada

Um texto transcrito numa sequência de **glifos**, com fronteiras de **palavra** (espaço), **linha** e **secção** quando existirem. O alfabeto é arbitrário: letras latinas, um alfabeto de transcrição com glifos de vários caracteres (como o EVA) ou símbolos inventados. A tokenização usa uma lista explícita de glifos (o mais longo primeiro) e fica registada com o texto.

## 3. Medidas (código determinístico, `research/TRONCO-01/texto/medidas.py`)

| Medida | O que dá | Para que serve |
|---|---|---|
| `alfabeto` | glifos distintos, contagens, cobertura dos 10 mais frequentes | tamanho e forma do inventário |
| `entropia` | h0, h1, h2 condicional (glifo dado o anterior), dentro da palavra e no fluxo | previsibilidade; h2 baixo aponta para estrutura rígida ou codificação verbosa |
| `coincidencia` | índice de coincidência; IC por período 1–20 (Friedman) | substituição simples conserva o IC da língua; polialfabética aproxima-o do uniforme |
| `kasiski` | distâncias entre trigramas repetidos e os seus divisores mais comuns | período de uma cifra polialfabética |
| `palavras` | distribuição e média de comprimentos, tipos/ocorrências em janelas fixas, hapax | vocabulário |
| `zipf` | declive e R² da reta log-frequência contra log-posição | distribuição de palavras de língua natural (declive perto de −1) |
| `posicional` | por glifo, fração em início, meio e fim de palavra; e por palavra, em início e fim de linha | restrições posicionais |
| `repeticoes` | palavras repetidas seguidas, quase-repetições (distância de edição 1), n-gramas de glifos repetidos | padrões de repetição |
| `dependencia` | informação mútua entre palavras consecutivas (último glifo → primeiro glifo seguinte; palavra → palavra) contra a mesma medida com a ordem baralhada (100 permutações, semente fixa) | distingue texto com ordem com significado de palavras em ordem aleatória ou geradas por tabela |
| `sukhotin` | classificação vogal/consoante pelo algoritmo de Sukhotin | estrutura silábica |
| `perfil` | distância (Jensen-Shannon) entre a distribuição de glifos ordenada e a de línguas de referência | proximidade a línguas conhecidas, invariante a substituição |

Todas devolvem números com os parâmetros usados. Nenhuma lê a verdade escondida.

## 4. Afirmações e verificação (`texto/verificador.py`)

Cada afirmação do relatório tem uma forma que o código consegue verificar:

```json
{"id": "A3", "texto": "h2 é muito menor que h1",
 "medida": "entropia", "parametros": {}, "campo": "h2_fluxo",
 "op": "<", "outra": {"medida": "entropia", "parametros": {}, "campo": "h1"}, "margem": 0.5}
```

ou com um valor fixo (`"op": "≈", "valor": 3.9, "tolerancia": 0.05`). O verificador recalcula a medida e responde verdadeira ou falsa. Uma afirmação sem medida associada é marcada como **interpretação** e só pode aparecer como razão de um veredicto que cite afirmações verificadas. Se alguma afirmação for falsa, o agente recebe só os factos que falharam e corrige, até 2 rondas (§24). As falsas que sobrarem ficam no relatório, marcadas, e contam como falha.

## 5. Hipóteses que o agente tem de questionar

| Código | Hipótese | Teste esperado que a distingue |
|---|---|---|
| `LN` | língua natural sem cifra | perfil próximo de uma língua de referência; Zipf perto de −1; dependência entre palavras acima do baralhado |
| `SUB` | substituição simples de uma língua natural | perfil ordenado e IC de língua, mas glifos não coincidem com nenhuma língua |
| `POL` | polialfabética (Vigenère) | IC perto do uniforme; pico do IC num período; Kasiski |
| `TRA` | transposição | frequências de língua, mas h2 perto de h1 (dependência local destruída) |
| `VER` | cifra verbosa (uma letra → vários glifos) | h2 baixo; palavras longas; restrições posicionais fortes |
| `NUL` | nulos inseridos | um ou mais glifos sem dependência do contexto |
| `BAR` | palavras reais em ordem aleatória | estatística dentro das palavras de língua; dependência entre palavras igual à do baralhado |
| `TAB` | gerado por tabela ou grelha, sem significado | estrutura interna forte; dependência entre palavras igual à do baralhado; Zipf atípico |
| `ALE` | glifos ao acaso | h1 perto de h0; sem restrições posicionais |

Para cada hipótese o agente dá `rejeitada`, `compatível` ou `indeterminada`, cita as afirmações verificadas e diz o que mudaria a sua conclusão. O agente tem também de listar o que não consegue distinguir com as medidas disponíveis: por exemplo, `SUB` e `LN` numa língua sem referência.

## 6. Corpus de desenvolvimento com verdade conhecida

- **Textos simples:** obras de domínio público em várias línguas, com a obra (não o excerto) como unidade de partição, para não haver fuga entre partições. As fontes e a descarga precisam da aprovação do Bruno; até lá, os testes usam textos gerados.
- **Transformações com chave conhecida (`texto/transformacoes.py`):** substituição simples, Vigenère (períodos 3–12), transposição colunar (com fronteiras de palavra reaplicadas aos comprimentos originais), nulos (taxa 5–15%), cifra verbosa (tabela fixa de 1–3 glifos por letra), baralhar palavras, gerador de tabela (prefixo-meio-sufixo com grelha) e glifos ao acaso. Cada exemplar regista a família, a chave e a semente; o agente vê só o texto.
- **Partições por semente e por obra:** desenvolvimento, validação e cega, escolhidas antes de qualquer corrida.

## 7. Como se avalia

- **Afirmações:** fração de afirmações numéricas verificadas como verdadeiras. Meta: 100% depois das rondas de correção. Qualquer falsa que sobre é falha.
- **Hipóteses:** a família verdadeira nunca pode ser `rejeitada`. Acerto da família mais provável indicada pelo agente, por família, com Wilson.
- **Questionamento:** quando duas famílias não se distinguem com as medidas (definido por código antes da corrida), o agente tem de dizer que ficam indeterminadas e não escolher uma às cegas.
- **Referências obrigatórias:** constante (sempre `LN`), regra simples por limiares fixos sobre as medidas, e acaso. O agente só vale a pena se igualar a regra simples na classificação **e** acrescentar um relatório verificado; se não a igualar, a regra simples fica como resultado.
- **Desempenho não é validade:** um bom resultado no corpus sintético não diz nada sobre o Voynich. Diz só que o agente lê bem estas medidas nestas transformações.

## 8. Ordem de trabalho

1. Medidas, transformações e verificador, com testes (sem chamadas a modelos).
2. Agente com backend falso, testado ponta a ponta.
3. Aprovação do Bruno para as fontes de texto e a sua descarga.
4. Pré-registo da primeira corrida (modelo, orçamento, previsões), congelado.
5. Corrida no desenvolvimento, com aprovação; análise; no máximo 3 rondas de ajuste nesta fase.
6. Validação e, só no fim, a partição cega.

## 9. Prova de conceito (pedida pelo Bruno, 19/10, 06:29: testes só os suficientes para verificar a credibilidade; escrito antes de correr a regra e o agente)

**Dados.** 8 obras do Perseus (CC BY-SA 3.0 US; 4 em latim: César *BG*, Cícero, Ovídio *Met.*, Virgílio *En.*; 4 em inglês: César *BG*, *Ilíada*, *Odisseia*, Heródoto), checksums em `SHA256SUMS.txt` junto dos ficheiros (fora do repositório). Um excerto de 2000 palavras por obra (só a–z, com fronteiras de palavra), cifrado nas 9 famílias: 72 amostras, sementes fixas (`texto/poc.py`). `NUL` = substituição com 12% de glifos nulos do próprio alfabeto dentro das palavras; `TAB` = prefixo+meio+sufixo escolhidos por uma grelha que avança.
**Agente.** `deepseek-chat` sem raciocínio, temperatura 0, até 8 medidas, até 2 rondas de correção pelo verificador de código; indica `mais_provavel`.
**Regra simples.** `poc.regra`, limiares fixados agora: alfabeto ≤ 10 → VER (h2 < h1 − 0,3) ou ALE; IC < 0,05 → POL; h2 do fluxo > h1 − 0,25 → TRA; dependência entre palavras não significativa → TAB (Zipf > −0,7) ou BAR; 5 dos 6 glifos mais frequentes entre `etaoinsrhul` → LN; IC < 0,058 → NUL; senão SUB.
**Previsões.**
- **P1:** regra ≥ 43/72 (60%).
- **P2:** o agente acerta menos do que a regra em `mais_provavel`.
- **P3:** afirmações numéricas falsas no relatório final ≤ 5%.
- **P4:** família verdadeira `rejeitada` em ≤ 7/72.
- **P5:** relatório válido em ≥ 65/72 (90%).
**Leitura.** Exploratória e pequena (8 por família, Wilson muito largo). Serve para decidir se vale a pena investir mais, não para afirmar capacidade. Custo previsto < 2 USD.
**Desvio de execução (registado durante a corrida).** Após 11 de 72 amostras, uma afirmação do agente com um valor não numérico fez o verificador lançar uma exceção e parou a corrida. Correção: afirmações não verificáveis contam como **falsas e malformadas** (antes não estavam previstas). As 11 amostras feitas mantêm-se; a corrida retoma nas restantes 61. Nada mais muda (regra, previsões, medidas, prompt).

### 9.1 Resultados da prova de conceito (`texto/resultados/poc/ANALISE.json`)

72/72 relatórios válidos; 0 falhas de execução depois da correção; custo ≈ 0,05 USD (saldo 6,05 → 6,00).

| | Agente (DeepSeek sem raciocínio) | Regra simples |
|---|---|---|
| Acerto da família | 13/72 [0,11; 0,29] | 49/72 [0,57; 0,78] |
| LN / SUB / POL / TRA / VER / NUL / BAR / TAB / ALE (de 8) | 8 / 2 / 2 / 0 / 0 / 0 / 0 / 0 / 1 | 8 / 7 / 8 / 8 / 6 / 0 / 4 / 0 / 8 |
| Respondeu "indeterminada" | 43/72 | — |

**Afirmações:** 13/180 falsas na primeira versão; depois do verificador, **3/174 = 1,7%** [0,6%; 4,9%]. **Família verdadeira rejeitada:** 2/72 (duas `ALE` dadas como POL). **Investigação:** 2,3 medidas por amostra (sempre `alfabeto` e `entropia`; `coincidencia` em 17, `kasiski` em 5; **nunca** `dependencia`, `zipf`, `posicional`, `palavras`).

**Previsões:** P1 confirmada (49 ≥ 43); P2 confirmada (13 < 49); P3 confirmada (1,7% ≤ 5%); P4 confirmada (2 ≤ 7); P5 confirmada (72/72).

**Leitura.** (1) A cadeia é credível: as medidas, as transformações e o verificador funcionam, e o verificador apanha e faz corrigir as afirmações falsas (7% → 1,7%). (2) O agente não investiga: pára ao fim de duas medidas e responde "indeterminada" em 60% dos casos, mesmo quando a medida que distinguia estava disponível e não foi pedida. É a mesma falha da V4 (§17, §24): o problema é recolher a evidência, não lê-la. (3) A regra simples falha NUL e TAB (dá SUB a todos) e metade de BAR: as medidas atuais não chegam para essas três famílias, o que é um limite das medidas, não do agente.

### 9.2 Teste pequeno: bateria completa em código, o modelo só interpreta (aprovado pelo Bruno, 19/10, 06:50; escrito antes de correr)

**Base nos outros projetos** (`docs/TEXTO_FONTES.md`): ms408 (bateria fixa aplicada sempre; o LLM fica fora do cálculo), Data Interpreter (plano explícito: 0,37 → 0,85 na ablação), "Agents Explore but Agents Ignore" (os modelos não usam o que têm disponível, mas usam-no quando o recebem pronto). Medidas novas com fonte: `gaskell` (comprimento de palavra, autocorrelação, compressão; Gaskell & Bowern 2022) e `amancio` (razão contra versões baralhadas; Amancio et al. 2013).
**Mudança.** `Analista(bateria=True)`: o código corre as 12 medidas e entrega-as todas no primeiro pedido; o modelo responde logo com o relatório. Tudo o resto igual (modelo, temperatura, verificador, 2 rondas).
**Amostras.** 18: obras 0 (inglês, César) e 1 (latim, César), as 9 famílias, as mesmas amostras de §9. Nessas 18, antes: agente 2/18, "indeterminada" 12/18; regra 12/18.
**Previsões.** **B1:** agente ≥ 6/18. **B2:** "indeterminada" ≤ 6/18. **B3:** afirmações falsas finais ≤ 5%. **B4:** o agente continua abaixo da regra (≤ 12/18), porque NUL e TAB não se distinguem com estas medidas. **B5:** 18/18 relatórios válidos.
**Decisão depois:** se B1 e B2 se confirmarem, o problema era de recolha de evidência e alarga-se às 72; se não, o problema é de interpretação e a próxima base a estudar é a falsificação sequencial (POPPER) ou o raciocínio ligado.

**Resultados de §9.2** (`resultados/poc/ANALISE_BATERIA.json`). 18/18 relatórios válidos. **Acerto 8/18** (antes 2/18; regra 12/18). **"Indeterminada" 0/18** (antes 12/18). Afirmações falsas: 46/228 (20%) na primeira versão; **16/157 (10%) no fim**. Família verdadeira rejeitada: 4/18.
Por família (agente | regra): LN 2|2, SUB 2|1, POL 2|2, ALE 2|2, NUL 0|0 (ambos SUB), TAB 0|0 (ambos SUB), TRA 0|2 (agente SUB), VER 0|2 (agente POL), BAR 0|1 (agente LN).
**Previsões:** B1 confirmada (8 ≥ 6); B2 confirmada (0 ≤ 6); **B3 refutada** (10% > 5%); B4 confirmada (8 ≤ 12); B5 confirmada.
**Leitura.** A recolha de evidência era um dos problemas: com a bateria entregue, o agente deixa de fugir para "indeterminada" e o acerto quadruplica. Mas continua abaixo da regra, e os erros são de interpretação: tem os números que separam TRA (h2 do fluxo perto de h1), VER (alfabeto de 6 glifos) e BAR (razão de Amancio perto de 1) e não os usa. Com mais números no pedido, também inventa mais (20% de afirmações falsas na primeira versão). NUL e TAB continuam indistinguíveis para o agente e para a regra.

### 9.3 Teste pequeno: o modelo escreve a função que decide e cita números por referência (aprovado pelo Bruno, 19/10, 06:59; escrito antes de correr)

**Base** (`docs/TEXTO_FONTES.md`, pesquisa de 06:55): Program of Thoughts (+12% sobre raciocínio em texto), TableBench (o código só ganha se correr: esqueleto fixo), Number Cookbook (comparar números em texto é uma fraqueza do modelo), Proof-Carrying Numbers (números por referência), Huang et al. 2024 (só o retorno externo corrige).
**Mudança** (`texto/programa.py`). O modelo recebe as 98 medidas da bateria como dicionário `m` e devolve `classificar(m)` e uma lista de justificações (expressões booleanas sobre `m`). O código executa a função num ambiente restrito por AST (só if/return, comparações, aritmética, abs/min/max/round/len); a família é o que a função devolve. Justificações falsas ou função que não corre voltam ao modelo, até 2 rondas. Mesmo modelo, temperatura 0, mesmas 18 amostras de §9.2.
**Previsões.** **C1:** acerto ≥ 11/18 (§9.2: 8/18; regra 12/18). **C2:** a função corre em ≥ 17/18 no fim. **C3:** justificações falsas no fim ≤ 5%. **C4:** pelo menos 2 dos 3 erros-tipo de §9.2 desaparecem (TRA dado como SUB, VER como POL, BAR como LN), contando por amostra (6 amostras). **C5:** NUL e TAB continuam errados (0/4).
**Decisão depois:** se C1 se confirmar, alarga-se às 72; se não, a opção seguinte é o código decidir e o modelo só explicar.

**Resultados de §9.3** (`resultados/poc/ANALISE_PROGRAMA.json`). **Acerto 9/18** (§9.2: 8/18; regra 12/18). A função correu em **18/18** (1 erro de execução na primeira versão, corrigido na ronda seguinte). Justificações falsas: 2/155 na primeira versão, **0/153 no fim**.
Por amostra: TRA 1/2 (0-TRA continua SUB); VER 0/2 (já não POL, agora TAB e BAR); BAR 0/2 (continua LN); NUL 0/2 (LN e VER); TAB 1/2; LN, POL e ALE 2/2; SUB 1/2.
**Previsões:** **C1 refutada** (9 < 11); C2 confirmada (18/18); C3 confirmada (0%); **C4 refutada** contando por amostra: o erro-tipo desaparece em 3 das 6 amostras (VER→POL nas 2, TRA→SUB em 1, BAR→LN em 0), mas as duas VER continuam erradas; **C5 refutada** (1/4: uma TAB certa).
**Leitura.** (1) Citar números por referência e avaliá-los por código **resolve as afirmações inventadas** (de 20%/10% em §9.2 para 0,0% no fim), o que confirma o desenho do Proof-Carrying Numbers. (2) **Não resolve a classificação**: o acerto fica no ruído de §9.2. A função que o modelo escreve não é um classificador; é a sua conclusão escrita como código (por exemplo, `m['alfabeto.glifos_distintos'] > m['sukhotin.letras']` → VER, que nunca é verdade), e as justificações verdadeiras não garantem que sejam as que distinguem as famílias. (3) Pela regra escrita antes de correr, a opção seguinte é o código decidir e o modelo só explicar.

### 9.4 Teste pequeno: modo programa com raciocínio ligado (aprovado pelo Bruno, 19/10, 07:03; escrito antes de correr)

**Base:** V4 §21 (o mesmo modelo com raciocínio: 15/45 → 37/45 fundamentados); "Do Reasoning Models Ask Better Questions?" (2026; com CoT 0,94 contra 0,08 de vitórias); "Agents Explore but Agents Ignore" (2026; raciocínio alto ≈ 3× mais uso do que o agente tem disponível).
**Mudança:** só o modo de raciocínio (`thinking: enabled`, limite 32 000 tokens). Tudo o resto como em §9.3: as mesmas 18 amostras, a mesma bateria, `classificar(m)` executada pelo código, justificações por referência, 2 rondas.
**Previsões.** **R1:** acerto ≥ 12/18 (iguala a regra). **R2:** justificações falsas no fim ≤ 5%. **R3:** a função corre em ≥ 17/18. **R4:** pelo menos 1 de 4 NUL/TAB certa. **R5:** respostas cortadas pelo limite ≤ 1/18.
**Decisão depois:** se R1 se confirmar, alarga-se às 72 com raciocínio; se não, passa-se ao código a decidir e o modelo a explicar.

**Resultados de §9.4** (`resultados/poc/ANALISE_PROGRAMA_RACIOCINIO.json`). Custo ≈ 0,40 USD (saldo 6,00 → 5,60). **Acerto 15/18** [0,61; 0,94] (regra 12/18; §9.3 sem raciocínio 9/18). A função correu em 18/18. Justificações falsas no fim **0/239**. 2 respostas inválidas em rondas intermédias, recuperadas na ronda seguinte; 18/18 com relatório final.
Por família (raciocínio | regra): LN 2|2, SUB 2|1, POL 2|2, TRA 2|2, VER 2|2, TAB **2|0**, NUL **1|0**, BAR 1|1, ALE 1|2. Erros: 1-ALE → TAB, 1-BAR → LN, 0-NUL → TAB.
**Previsões:** R1 confirmada (15 ≥ 12); R2 confirmada (0%); R3 confirmada (18/18); R4 confirmada (3 de 4 NUL/TAB certas); R5: o registo não separa respostas cortadas de respostas inválidas; houve 2 rondas inválidas (≤ 1/18 por amostra no fim: 0), por isso fica **por verificar**, não confirmada.
**Leitura.** Com raciocínio e as comparações executadas por código, o agente passa a regra simples (15 contra 12), não inventa números (0/239) e acerta em famílias que a regra não distingue (TAB 2/2, NUL 1/2). Isto confirma, com outro tipo de tarefa, o que a V4 mostrou: o que faltava ao modelo era espaço de raciocínio, e o código tem de fazer as contas. **Ressalvas:** 18 amostras (o IC vai de 0,61 a 0,94 e cruza o da regra), duas obras, sem partição de validação, e o modelo vê as 12 primeiras palavras (o que ajuda em LN). É prova de conceito, não resultado.

## 10. Fase 1: reproduzir resultados publicados (decidido pelo Bruno, 20/10, 06:02; escrito antes de correr)

**Objetivo.** Antes de procurar dados novos, confirmar que conseguimos reproduzir de forma idêntica dados dados como adquiridos. Imagens: aproveitar o que existe, sem investir mais (decisão do Bruno).
**10.1 Gaskell & Bowern 2022** (repositório `danielgaskell/voynich`, commit `d076a7d`, licença MIT modificada com citação obrigatória; fora do nosso repositório). Os textos Voynich do repositório **não** são usados. Passo A: o código deles, sobre os textos deles (38 gibberish, 74 com significado), reproduz a tabela publicada `results/metrics_paperv1.csv` nas 42 métricas? Passo B (depois): a nossa implementação independente das métricas que já temos reproduz os mesmos valores. Passo C (depois): um modelo open source, a partir da descrição do método, escreve o código que os reproduz.
**Critério de coincidência, fixado agora:** contagens exatas; restantes com diferença relativa ≤ 1% (ou absoluta ≤ 1e-6 quando o valor publicado é 0). A linha 203 de `stats.py` usa `random.randint` sem semente, por isso as métricas que dependem dela podem variar entre execuções: registam-se à parte.
**Previsão A:** ≥ 95% dos pares texto × métrica coincidem; os desvios concentram-se nas métricas que usam o sorteio sem semente.

**Resultado do passo A (10.1).** O código deles, nos 38 textos sem significado, coincide em **861/1596 pares (54%)** com o critério de 1%. **Previsão A refutada**, e pela razão que importa: todas as 42 métricas são médias de 100 subconjuntos de 200 palavras tirados ao acaso sem semente (`stats.py`, linhas 198–206), não só algumas. A tabela publicada tem, portanto, ruído de amostragem; a diferença relativa mediana fica em 1–4% na maioria das métricas, com caudas maiores em `wordbias_lines_skew`, `zipf`, `wordlen_autocorr`, `repeated_words` e `tripled_words`. O critério de 1% foi mal escolhido para dados com ruído; fica registado como erro meu, não se reescreve.
**Teste seguinte (pequeno, escrito antes de correr):** correr o código deles mais 2 vezes em 8 dos 38 textos (os primeiros por ordem alfabética), para medir o ruído entre execuções. O valor publicado conta como **reproduzido** se estiver dentro de 3 desvios-padrão da média das 3 execuções (a de cima mais estas duas). **Previsão A2:** ≥ 90% dos pares texto × métrica reproduzidos assim.
**Resultado do teste de ruído.** Por engano corri 6 dos 8 textos previstos (DC_01, 03, 04, 05, 06, 08; ficaram de fora DA_01 e DA_02). Nesses 6, **202/252 (80%)** dentro de 3 desvios-padrão de 3 execuções: **A2 refutada**. Mas não há viés: nos 38 textos, a diferença média para o publicado é ≤ 0,2% (por exemplo `wordlen_mean` −0,12%, `entropy` +0,07%), com sinais equilibrados (cerca de 50% acima e 50% abaixo). Os desvios são ruído de amostragem, e 3 execuções subestimam esse ruído.
**Leitura.** A tabela publicada é **reprodutível sem viés, com precisão de cerca de 2% por valor**; casas decimais além disso não têm significado, e métricas como `wordbias_lines_skew` (variação ~7% entre execuções), `repeated_words` (~6%), `zipf` e `wordlen_autocorr` (~4%) só servem para diferenças grandes. Isto é enquadramento que o artigo não dá.

### 10.2 Que dados dão uma resposta determinante: língua, cifra ou artificial? (pedido do Bruno, 20/10, 06:08; escrito antes de calcular)

**Dados:** as tabelas publicadas por Gaskell & Bowern: `metrics_paperv1.csv` e `metrics_enciphered.csv` (este do artigo "Enciphered after all?", CEUR Vol-3313), sem recalcular nada. Classes: **língua** = Modern + Historical + Conlangs (74 textos); **artificial** = Gibberish (38); **cifrado** = Enciphered (814 variantes). Voynichese e Random excluídos.
**Medida:** para cada uma das 42 métricas e cada par de classes, a AUC (probabilidade de uma métrica ordenar corretamente um texto de cada classe; 0,5 = inútil, 1 = separa sempre). "Determinante" = AUC ≥ 0,95 (ou ≤ 0,05).
**Previsões.** **D1:** nenhuma métrica é determinante entre língua e artificial (os autores dizem que o gibberish imita a língua em quase todas). **D2:** pelo menos uma é determinante entre língua e cifrado. **D3:** a melhor métrica entre língua e artificial é de informação ou repetição (`entropy`, `compression`, `repeated_*`), como dizem os autores.
**Ressalva já conhecida:** as 814 variantes cifradas saem de poucos textos de origem; não são independentes, o que tende a inflacionar a AUC entre língua e cifrado.

**Resultados de 10.2** (`texto/resultados/fase1/auc.json`). Nenhuma das 42 métricas é determinante em nenhum par.
- **Língua vs artificial:** melhor AUC 0,83 (`charbias_mean`, maior no artificial), depois `wordlen_autocorr` 0,80 e `wordbias_mean` 0,80. `entropy` 0,64, `compression` 0,67, `repeated_chars` 0,75.
- **Língua vs cifrado:** melhor 0,74 (`wordunique_skew`); `entropy` 0,52 (inútil).
- **Cifrado vs artificial:** melhor 0,79 (`wordbias_std`).
**Previsões:** D1 **confirmada** (0 determinantes); D2 **refutada** (0 determinantes, máximo 0,74); D3 **refutada** (as melhores são de viés de posição e de autocorrelação do comprimento, não de informação nem repetição).
**Leitura.** Com estas 42 métricas, isoladas, nenhum número decide sozinho se um texto é língua, cifra ou artificial. As cifras deste conjunto (29 textos de origem, 814 variantes) foram desenhadas para imitar o Voynich, o que as torna mais difíceis do que as nossas famílias sintéticas, onde o IC e o h2 separavam bem POL e TRA. Fica por testar se uma **combinação** pequena de métricas é determinante.

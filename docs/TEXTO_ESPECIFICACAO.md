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

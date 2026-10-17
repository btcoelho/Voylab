# TRONCO-01 v2.7 — ensaio real e análise obrigatória

**Resultado principal: 0/10 sucessos conjuntos.** O lote foi executado uma vez com o checkpoint Qwen2.5-0.5B-Instruct de quatro bits já disponível. Foram feitas dez chamadas, sem retries, consultas ou falhas técnicas. As dez respostas são JSON completo e terminam em EOS; só três passam a validação da ação. Nenhuma dessas três acerta o veredicto ou o conjunto de candidatos.

**Decisão após o lote: a configuração não demonstrou a capacidade-alvo e permanece inadequada para avançar para M17 ou para uma avaliação maior.** Há agora um defeito de integração da gramática reproduzível e há erros científicos independentes desse defeito. O ensaio fica preservado como resultado negativo de desenvolvimento. O ponto obrigatório de análise foi atingido; nenhuma configuração foi alterada nem houve nova inferência após o lote.

## Execução e proveniência

- O candidato v2.7 original foi preservado. Foi criada uma cópia de execução distinta, com pré-registo e manifesto congelados antes de carregar o checkpoint.
- Congelamento: `2026-10-17T16:19:37.423130+00:00`; início do processo: `16:19:44.837809+00:00`; fim: `16:20:49.896119+00:00`.
- Manifesto congelado: SHA-256 `3486e64c702a1d71ca936cc9855c99c07f60bb80c6ff9683b81f73b38e4f5216`.
- Pré-registo congelado: SHA-256 `8a4b547767c82b6c074029e217bbce6fde073071e447643c9d68e0ecb4f9977b`.
- Modelo: `unsloth/Qwen2.5-0.5B-Instruct-bnb-4bit`, revisão `216d96b52c97a3c8294776df8477592f6828981c`; sem adaptador. Hardware: NVIDIA RTX 4070.
- Configuração: greedy, 256 tokens novos no máximo, contexto 2048, gramática LMFE, uma chamada por episódio, orçamento de consultas zero e ordem fixa. Os prompts tinham 630–723 tokens; as saídas, 48–92 tokens.
- O código executável, o prompt e a agenda são idênticos aos do candidato revisto. Apenas o estado de congelamento e a documentação de decisão foram acrescentados à cópia de execução.
- A verificação posterior confirmou os 25 ficheiros internos congelados e os 11 artefactos externos. O ambiente coincidiu com as seis versões pré-registadas. Não houve fine-tuning, modelo maior, utilização de reservas ou inferência no manuscrito.

## Resultado medido

| Indicador | Resultado |
|---|---:|
| Episódios executados / planeados | 10/10 |
| Chamadas aprendidas | 10 |
| JSON completo | 10/10 |
| Terminação em EOS | 10/10 |
| Truncagem ao limite | 0/10 |
| Ações aceites | 3/10 |
| Falhas de saída / validação | 7/10 |
| Falhas técnicas | 0 |
| Sucessos conjuntos | **0/10** |

As falhas de saída são de forma ou referências públicas; não são erros de parsing JSON neste lote. O rótulo `reported` significa que a ação foi aceite para avaliação. Não significa que o seu conteúdo seja verdadeiro. `pilot_09` e `pilot_10`, por exemplo, passam a forma e falham a alegação de localização e os critérios científicos.

O modelo repetiu a mesma combinação em todos os episódios: `supported / [A] / none_fit / no_observations`. O histórico e os candidatos públicos variavam, mas essa combinação principal não mudou. É uma observação deste ensaio; não demonstra por si só qual mecanismo interno provocou o comportamento.

## Conferência por episódio

| Episódio | Veredicto esperado | Veredicto produzido | Estado da ação | Tokens | Problema observado |
|---|---|---|---|---:|---|
| 01 | undetermined | supported | Rejeitada | 48 | Cita A como observação e usa valor de localização inexistente |
| 02 | undetermined | supported | Rejeitada | 48 | Idêntico ao episódio 01 |
| 03 | supported | supported | Rejeitada | 92 | Valores de localização repetidos; diagnóstico e suficiência errados |
| 04 | supported | supported | Rejeitada | 92 | Valores de localização repetidos; diagnóstico e suficiência errados |
| 05 | supported | supported | Rejeitada | 59 | Valores de localização repetidos; diagnóstico e suficiência errados |
| 06 | supported | supported | Rejeitada | 59 | Valores de localização repetidos; diagnóstico e suficiência errados |
| 07 | rejected | supported | Rejeitada | 56 | Valores de localização repetidos e veredicto errado |
| 08 | rejected | supported | Aceite | 51 | Veredicto, candidatos, diagnóstico e suficiência errados |
| 09 | rejected | supported | Aceite | 59 | Veredicto, candidatos e suficiência errados; `none` com valores não vazios |
| 10 | rejected | supported | Aceite | 59 | Veredicto, candidatos e suficiência errados; `none` com valores não vazios |

A agenda contém nove estados públicos distintos. Os episódios vazios 01 e 02 são idênticos e produziram exatamente a mesma resposta. Não se devem tratar os dez episódios como dez problemas independentes novos.

## Verificação independente

`analyze_run.py` reconstituiu os registos, validou os hashes de prompts e schemas, conferiu a ordem e o limite de uma chamada e comparou os resultados guardados com um cálculo separado. A referência de rótulos estava escrita e incluída no manifesto antes da inferência. A reanálise não importou as funções semânticas do scorer primário. As pontuações recalculadas coincidem com as guardadas; não foram encontrados rótulos privados nos prompts.

Entre as três ações aceites: veredicto 0/3, candidatos 0/3, diagnóstico 2/3 e suficiência 0/3. O indicador de certificado marca 3/3 porque as respostas `supported` citam todas as linhas públicas; esse componente verifica a cobertura exigida para a forma alegada. Como o veredicto é falso, **não significa que existam três conclusões sustentadas pela evidência**. O sucesso conjunto mantém essa distinção e vale zero.

Como diagnóstico retrospectivo adicional, lemos os campos das dez respostas JSON, incluindo as sete ações rejeitadas. O veredicto isolado coincide em 4/10, candidatos em 2/10, diagnóstico em 2/10 e suficiência em 2/10. **Nenhuma resposta acerta os quatro campos simultaneamente.** Estes valores não substituem o resultado primário e não transformam ações ilegais em sucessos. Mostram que a correção do formato, sozinha, não bastaria para validar as respostas já produzidas.

## Defeito reproduzível da integração da gramática

Nos estados vazios, o nosso schema gera `items.enum: []` e `maxItems: 0` para a evidência. A integração assumia que isto impediria qualquer citação. No LMFE 0.11.3 instalado, essa garantia não se verifica:

| Caso mínimo | Contrato pretendido | Observado no parser real |
|---|---|---|
| Array com `maxItems: 0`, item limitado a `o1`, saída `["o1"]` | Rejeitar | Aceita |
| String com lista de IDs vazia, saída `"A"` | Não permitir um ID | Aceita |
| Array com `uniqueItems: true`, saída `["A","A"]` | Rejeitar repetição | Aceita |
| Array vazio `[]` | Aceitar | Aceita |

O primeiro caso isola o limite zero sem depender de enum vazio. O parser cria um ramo de primeiro item ao abrir o array, mesmo quando o máximo é zero. A lista vazia de strings permitidas é tratada como ausência de restrição de strings. A nossa adaptação tem de tratar estes casos explicitamente, em vez de presumir que o schema é integralmente aplicado pelo motor.

O replay offline, com tokenizer e callback LMFE reais, confirmou que **todos os tokens das dez respostas eram permitidos pelo callback utilizado**, incluindo as sete saídas depois rejeitadas pelo validador. Não houve inferência aprendida adicional neste diagnóstico. A terminação EOS foi também conferida contra o tokenizer.

A não aplicação de unicidade na gramática já estava explicitada antes do ensaio; o validador final detectou corretamente os duplicados. A novidade demonstrada é a insuficiência do caminho de listas vazias e do respetivo pré-teste negativo. O smoke anterior testava uma resposta válida; não demonstrava o bloqueio de respostas inválidas nestas fronteiras. A conclusão anterior sobre o âmbito efetivamente restringido pela gramática foi demasiado ampla.

O validador e o scorer não concederam sucesso conjunto indevido. O defeito limita a promessa de geração conforme ao contrato e contribui para a taxa de ações rejeitadas. Não explica os erros científicos presentes em todas as combinações centrais.

## Efeito das alterações e estado geral

Comparado descritivamente com v2.3, os episódios com falha JSON passaram de quatro para zero, e os dez terminaram em EOS. Os relatórios aceites mantiveram-se em três e o sucesso conjunto em zero. As chamadas passaram de 19 para 10 por força do novo limite de uma chamada; isso não prova maior eficiência de raciocínio. Prompt, interface, gramática e política de chamadas mudaram em conjunto, pelo que o ensaio não identifica a contribuição causal de cada mudança.

O progresso concreto está na execução auditável, na distinção entre classes de erro e no contraexemplo agora disponível. Não há evidência de progresso da capacidade científica do checkpoint nesta configuração. O alvo amplo do analista autónomo, a aquisição de informação e M17 continuam por validar. Não há base para atribuir uma percentagem global de conclusão ao projeto a partir destes dez casos.

## Próximo bloco delimitado

1. Preservar este resultado negativo e os registos; nenhuma repetição deste lote para procurar uma saída melhor.
2. Corrigir apenas a fronteira de representação das listas vazias na adaptação ao motor real e acrescentar os contraexemplos positivos e negativos ao percurso tokenizer/callback. Manter o validador final. Qualquer garantia sobre duplicados deve corresponder ao que o motor realmente faz.
3. Como localização não é o alvo deste protocolo, propor um ensaio diagnóstico que a fixe publicamente a `none / []` ou a omita. Isto tem de constar de um novo pré-registo e não pode ser aplicado retrospectivamente ao resultado atual. A gramática deve continuar a permitir todas as escolhas científicas legais, sem usar o rótulo esperado para restringir a resposta.
4. Preparar um diagnóstico mínimo do veredicto com o mesmo checkpoint, separado do relato multicomponente, para distinguir a dificuldade de interface da leitura das tabelas. Antes de nova inferência, explicitar o contraste, os casos de desenvolvimento, o resultado que mudaria a decisão e o novo limite de chamadas. Não abrir reservas M17 nem iniciar treino ou modelos maiores.

**Paragem desta execução: análise do lote concluída, antes de qualquer alteração de prompt, orçamento, gramática ou modelo.** O próximo avanço deve resolver estes contraexemplos e formular esse diagnóstico pequeno. Ampliar a arquitetura ou o benchmark não é justificado pelos dados atuais.

## Reproduzir a análise sem modelo

Na raiz da entrega extraída:

```powershell
python work/TRONCO01_V27_MODEL_RUN/analyze_run.py
```

O replay da gramática e a verificação dos artefactos externos usam o ambiente WSL e o snapshot locais declarados:

```bash
python work/TRONCO01_V27_MODEL_RUN/grammar_replay.py
python work/TRONCO01_V27_MODEL_RUN/postrun_integrity.py
```

O launcher tem um diretório de execução e um lock de tentativa já existentes. Está preservado como prova do lançamento único; não deve ser usado para repetir este lote. A entrega contém os prompts, tokens, respostas brutas, diário, outcomes, summary, log do processo, pré-registo, manifesto congelado, scripts e reanálises. Os pesos não estão incluídos.

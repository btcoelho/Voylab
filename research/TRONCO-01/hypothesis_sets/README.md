# TRONCO-01 — passo 4: conjuntos de hipóteses admissíveis

**Data:** 17 de outubro de 2026
**Natureza:** implementação independente e auditoria offline. Sem chamadas de modelo, sem dados novos, sem acesso às reservas. Não altera resultados históricos.

## O que foi implementado

Este diretório implementa o passo 4 do relatório de estado: uma enumeração independente de conjuntos de hipóteses admissíveis, inspirada no método descrito para o HypoSpace ([arXiv:2510.15614](https://arxiv.org/abs/2510.15614v3)). Nenhum código do HypoSpace foi copiado ou importado, porque a licença continua por esclarecer.

A ideia central é que um histórico público H não define uma resposta escondida única. Define um conjunto A(H): as hipóteses que reproduzem todas as observações. Dois mundos que o agente não consegue distinguir têm de receber o mesmo A(H). Só evidência discriminante pode reduzir esse conjunto.

| Ficheiro | Função |
|---|---|
| `hypothesis_sets.py` | Domínio finito, enumeração por extensão, A(H), descodificação das cartas, rótulos do contrato v2 e métricas de resposta em conjunto |
| `worlds.py` | Lado do avaliador: mundo = mecanismo oculto + vista pública; pares indistinguíveis; identificabilidade de uma pergunta |
| `audit_v27.py` | Auditoria dos dez estados v2.7, lidos do ZIP arquivado depois de verificar o hash |
| `tests/` | 20 testes, incluindo leis exaustivas |
| `mutation_check.py` | Seis defeitos injetados, cada um corrido num interpretador limpo |
| `results/` | Saídas guardadas da auditoria e das mutações |

## Decisões de desenho

- **Identidade por extensão.** Uma hipótese é a sua tabela completa sobre as 16 entradas, não a sua descrição. "Depende só de glyph" com tabela constante é a mesma hipótese que a constante.
- **Espaço de hipóteses explícito.** O espaço é o das funções com suporte essencial de no máximo 2 atributos: 70 hipóteses. É uma escolha declarada, não uma verdade. Com suporte 4, o espaço tem 65 536 funções.
- **A vista pública nunca recebe o mecanismo oculto.** `admissible` só aceita evidência pública. O mecanismo oculto só existe em `worlds.py`.
- **As cartas são lidas pelas chaves da tabela, não pelo texto.** O enunciado serve apenas de verificação cruzada: se não coincidir com as chaves, é um erro, não uma tentativa de adivinhar. Uma tabela incompleta não é completada.
- **Contradição não é `none_fit`.** Linhas contraditórias dão `inconsistent_observations`: nenhuma função sem ruído encaixa, qualquer que seja a lista de candidatos.

## Verificações

- **Enumeração por duas vias.** A construção por suporte coincide com a filtragem das 65 536 funções pelo tamanho do suporte essencial, para k = 0 a 4.
- **Lei dos mundos indistinguíveis.** Testada de forma exaustiva para os 697 conjuntos de até 3 entradas observadas e as 70 hipóteses. A(H) é exatamente a classe de mundos com a mesma evidência pública, calculada por uma via independente.
- **Pares e separação.** O número de pares coincide com a soma de C(n, 2) por classe de n mundos. Uma entrada discriminante separa cada par; uma entrada não discriminante mantém-no junto.
- **Invariâncias.** A ordem e os IDs das observações não alteram as conclusões. Mais evidência nunca alarga A(H).
- **Mutações: 6/6 mortas, nenhuma por crash.** Os defeitos injetados foram: fuga do mecanismo oculto na vista pública, última observação ignorada, identidade sintática, chave em falta completada, contradições ignoradas e enunciado confiado em vez das chaves.

Para reproduzir (Python 3.12 ou superior, só biblioteca padrão):

```bash
python -m unittest discover -s tests -v
python mutation_check.py
python audit_v27.py --output results/AUDITORIA_CONJUNTOS_V2_7_2026-10-17.json
```

## Resultado da auditoria v2.7

A coluna "Diagnóstico v2" é calculada só sobre os candidatos declarados. A coluna "Hipóteses admissíveis" conta os elementos de A(H) no espaço de 70.

| Episódio | Diagnóstico v2 | Cartas admissíveis | Hipóteses admissíveis | Entradas ainda em aberto |
|---|---|---|---|---|
| pilot_01, pilot_02 | ambiguous | A, B, C | 70 | 16 |
| pilot_03, pilot_04 | ambiguous | A, B, C | 35 | 15 |
| pilot_05, pilot_06 | identified | A | 17 | 13 |
| pilot_07, pilot_08 | identified | B | 10 | 14 |
| pilot_09, pilot_10 | none_fit | — | 2 | 4 |

1. **Os rótulos do contrato v2 são identificáveis.** O descodificador independente reproduz a referência privada nos 10 episódios. Os rótulos dependem só do estado público, por isso nenhum par indistinguível recebe rótulos diferentes.
2. **Há um duplicado.** pilot_01 e pilot_02 têm exatamente o mesmo estado público, com rótulos privados iguais. São 9 estados distintos, como já indicava o relatório.
3. **`identified` não significa mecanismo identificado.** Em pilot_05–08 resta um único candidato declarado, mas continuam admissíveis 10 a 17 mecanismos no espaço. A pergunta "a carta X é o mecanismo verdadeiro?" não é identificável em nenhum destes quatro episódios.
4. **`none_fit` não significa "não existe explicação".** Em pilot_09–10 nenhuma carta declarada encaixa, mas duas funções simples de glyph e setting (XOR e OR) explicam todas as observações.
5. A pergunta sobre o mecanismo oculto só é identificável em 2 dos 10 episódios, e mesmo aí apenas porque nenhuma carta declarada é admissível.

## O que isto autoriza e o que não autoriza

O passo 4 está implementado e verificado para o domínio v2.7: tabelas binárias, sem ruído, entradas completas e espaço de suporte ≤ 2. Os resultados confirmam que o contrato v2 é bem definido quando lido literalmente. Mostram também que qualquer pontuação sobre o **mecanismo** (e não sobre o ajuste aos candidatos) teria de aceitar conjuntos, não um rótulo único.

Não autoriza conclusões sobre a competência do modelo, sobre o M17, sobre ruído, nem sobre outros domínios. O espaço de hipóteses é uma escolha. Com outro espaço, os tamanhos de A(H) mudam, mas as leis testadas continuam a valer.

## Próximo passo sugerido

Aplicar a mesma verificação ao gerador M17, que atribui o veredicto esperado pela categoria oculta. Por exemplo, `INSUFFICIENCY` exige `undetermined` mesmo quando W encaixa em todas as observações. É preciso confirmar se dois mundos M17 de categorias diferentes podem ter a mesma informação pública, ou a mesma informação a menos de renomeações. Se puderem, o veredicto esperado não é identificável e esses casos não podem pontuar o agente.

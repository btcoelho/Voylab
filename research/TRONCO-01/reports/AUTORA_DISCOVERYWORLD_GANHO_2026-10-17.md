# AutoRA + DiscoveryWorld: comparação de seleção de medições

**Data:** 17-10-2026
**Decisão:** ganho demonstrado contra amostragem aleatória num benchmark estreito; vantagem incremental do AutoRA sobre uma regra direta não demonstrada.

## Pergunta e critério

Testei se a seleção de uma amostra de solo com base na observação pública permite identificar, após uma única medição com o medidor de nutrientes, qual nutriente é necessário ao crescimento. O critério primário foi o número de hipóteses causais que permanecem após a medição; também verifiquei se o conjunto final continha a resposta oculta do benchmark.

Cada seed foi executado em três braços emparelhados:

1. **AutoRA desacordo:** `model_disagreement_sample` seleciona entre seis solos observados, usando dois modelos de utilidade especificados antes do ensaio. Um pressupõe que uma amostra com crescimento visível deixa uma hipótese; o outro prevê quatro hipóteses em ambos os casos.
2. **AutoRA aleatório:** `random_pool` seleciona uniformemente uma das mesmas seis amostras públicas.
3. **Regra pública direta:** escolhe a primeira amostra que tem um sinal público de crescimento.

Todos os braços receberam uma medição de solo por seed. A teletransportação para junto da amostra foi um atalho do harness para posicionamento, não uma ação científica nem parte do orçamento de medição. O scorecard/oráculo do DiscoveryWorld foi consultado apenas depois da escolha e da leitura, para pontuação posterior.

## Amostra reforçada

A execução inicial com 30 seeds consecutivos foi mantida como piloto, mas não é a base da conclusão inferencial: o código de `Plant Nutrients Easy` faz o nutriente oculto depender de `seed % 5`, repetindo cinco respostas em sequência. Para reduzir essa pseudorreplicação, o ensaio final usou **100 seeds inteiros, únicos e não consecutivos**, sorteados sem reposição de 1 000 a 99 999 com `NumPy default_rng(20261017)`. A lista integral está no JSON para reprodução.

Ambiente registado: Python 3.12.10; AutoRA 4.2.0; `autora-experimentalist-model-disagreement` 2.2.0; DiscoveryWorld commit `fd591323920be0d3786ef350955de1945aa571e5`.

## Resultados

| Braço | Hipótese única e correta | Hipóteses restantes, média | Medições válidas |
|---|---:|---:|---:|
| AutoRA desacordo | 100/100 | 1,00 | 100/100 |
| AutoRA aleatório | 34/100 | 2,98 | 100/100 |
| Regra pública direta | 100/100 | 1,00 | 100/100 |

As 300 leituras foram bem-sucedidas e cada uma indicou exatamente um nutriente em nível alto. Em todas as 100 execuções, os seis solos foram identificáveis pela observação pública e havia exatamente dois sinais públicos de crescimento. Os três braços conservaram a resposta oculta no conjunto de hipóteses final em todos os episódios.

Face ao braço aleatório, o AutoRA por desacordo reduziu em média **1,98 hipóteses** adicionais por medição. A regra direta produziu exatamente o mesmo tamanho de conjunto e identificação em todos os 100 seeds. O aleatório acertou a amostra com sinal público em 34/100, perto do valor mecânico de 2/6 esperado ao escolher uniformemente entre seis amostras das quais duas têm sinal positivo. Assim, a vantagem observada decorre de escolher uma amostra informativa, não de qualquer superioridade comprovada do algoritmo AutoRA sobre uma heurística simples.

O teste de sinais emparelhado registado no JSON dá `p = 2,71e-20`, mas não o trato como evidência independente de generalização: os resultados são quase determinados pela regra do cenário e pela diferença entre amostragem uniforme e escolha do sinal positivo. A leitura apropriada é descritiva e limitada ao benchmark e às seeds amostradas.

## O que ficou demonstrado

- **Sim:** a integração pode conduzir uma escolha de amostra usando observação pública, executar uma medição real do DiscoveryWorld e reduzir incerteza, neste cenário determinístico, com orçamento de uma medição.
- **Sim:** nesta tarefa, o critério informado alcança 100% de identificação, comparado com 34% da seleção uniforme.
- **Não:** não se demonstrou que o AutoRA, enquanto framework, melhora o resultado face à regra pública simples. Ambos os métodos escolheram uma amostra com sinal de crescimento e tiveram resultados iguais.
- **Não:** isto não valida TRONCO-01/M17, G1 ou G2; não demonstra descoberta causal geral, aprendizagem a partir de dados brutos ou transferência para tarefas mais difíceis. O modelo de utilidade do braço ativo inclui explicitamente a hipótese estrutural de uma causa e aproveita o sinal de crescimento visível.
- O marcador `task_completed` ficou falso nos episódios: a avaliação mede identificação da hipótese por uma medição, não conclusão da missão inteira do DiscoveryWorld.

## Conclusão e próximo ensaio

**Há ganho mensurável, mas apenas no critério de resolução de hipóteses deste benchmark:** selecionar a amostra com crescimento visível é melhor que escolher aleatoriamente. **Não há ganho específico do AutoRA** em relação à regra simples. A combinação AutoRA + DiscoveryWorld mostrou um caminho técnico funcional; a justificativa para manter AutoRA é a interface reutilizável de desenho experimental, ainda não uma vantagem empírica própria.

O próximo ensaio que pode decidir o valor adicional do framework deve ser pré-registado e sair da estrutura fácil determinística: usar `Plant Nutrients Normal`/`Challenge` ou outra tarefa com amostras, variáveis e resultados não codificados na regra de seleção; comparar AutoRA, heurísticas simples e aleatório sob o mesmo orçamento; pontuar pela evidência pública e manter o oráculo apenas para auditoria posterior. Antes disso, convém inspecionar o mecanismo de tarefa e verificar se uma associação pública de crescimento continua identificável sem consultar estados ocultos. Não inferir resultados de dificuldade normal/desafio a partir deste ensaio.

## Reprodução

A reprodução requer o checkout do DiscoveryWorld no commit indicado e ambiente com Python/AutoRA instalados. O script executa 300 episódios e grava o JSON junto de si. No PowerShell, a partir da raiz deste projeto:

```powershell
$repo = (Resolve-Path 'work/autora_smoke/discoveryworld').Path
$python = (Resolve-Path 'work/autora_smoke/.venv/Scripts/python.exe').Path
$script = (Resolve-Path 'outputs/compare_autora_active_random_discoveryworld.py').Path
$env:PYTHONPATH = $repo
$env:SDL_VIDEODRIVER = 'dummy'
$env:PYGAME_HIDE_SUPPORT_PROMPT = '1'
Push-Location $repo
try { & $python $script }
finally { Pop-Location }
```

O código versiona a seed de amostragem e regista a lista final. A saída gerada deve ser comparada com `AUTORA_DISCOVERYWORLD_RESULTADOS_100_SEEDS.json`.

## Artefactos

- Script de reprodução: `compare_autora_active_random_discoveryworld.py`
- Resultados completos (300 episódios): `AUTORA_DISCOVERYWORLD_RESULTADOS_100_SEEDS.json`
- Piloto anterior de 30 seeds consecutivos, preservado como histórico: `AUTORA_DISCOVERYWORLD_PILOTO_30_SEEDS.json`

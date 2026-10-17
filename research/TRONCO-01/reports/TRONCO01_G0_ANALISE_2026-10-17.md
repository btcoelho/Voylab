# TRONCO-01 — avaliação operacional G0

**Data:** 17/10/2026  
**Protocolo:** TRONCO01-G0-v0.1  
**Estado:** concluída; paragem obrigatória para análise.

## Resultado

Foram feitas as 16 gerações previstas, com amostras de desenvolvimento e validação M16. Não houve retentativas. Todas as respostas terminaram por EOS; nenhuma atingiu o limite de 192 tokens.

| Modelo | Tarefas curtas: prompt M17 atual | Tarefas curtas: instrução de sistema | Exemplos nativos M16 |
|---|---:|---:|---:|
| Qwen base | 0/3 válidas | 0/3 válidas | 0/2 válidas |
| Adaptador M16 | 0/3 válidas | 0/3 válidas | 2/2 válidas |

O gate de comunicação explícita exigia 6/6 respostas válidas nas tarefas curtas sob instrução de sistema. O resultado foi 0/6; **G0 falha**. Nenhuma competência científica foi medida.

## O que os resultados permitem concluir

- A instrução de sistema direta não corrigiu o contrato novo: o modelo base devolveu estruturas JSON diferentes das pedidas; M16 devolveu campos incompletos ou ações incompatíveis. Houve também saídas sem objeto JSON válido.
- M16 consegue emitir ações `query` e `commit` válidas em dois exemplos retirados de `validation.jsonl` do próprio protocolo M16. Isso mostra que o checkpoint e a descodificação funcionam no contrato nativo nestes dois casos.
- A diferença entre 2/2 nativos e 0/6 tarefas curtas para M16 aponta para incompatibilidade de interface/transferência de contrato. São apenas dois exemplos nativos, portanto o resultado é diagnóstico de engenharia, não uma estimativa geral.
- O modelo base falhou também nos dois exemplos M16; neste ensaio, a falha não pode ser explicada apenas pelo esquema M17. As saídas incluíram recusas em prosa e JSON fora do esquema.
- O parser de M17 procura o primeiro objeto JSON dentro do texto. Assim, uma resposta com vários objetos pode ser classificada como JSON analisável, mas continua inválida para a ação pedida. O relatório conserva a saída bruta e o erro da validação para distinguir as duas situações.

## Uma intervenção proposta

Na próxima etapa de desenvolvimento, construir um **adaptador de contrato determinístico** que apresente ao M16 um estado no formato nativo de treino (`task`, `allowed_actions`, opções disponíveis e dados públicos) e traduza apenas campos de ação de forma explícita e verificável. O adaptador não deve escolher consultas, inferir conclusões nem reparar semanticamente a resposta. Primeiro, testar a ida e volta do mapeamento com dados sintéticos de desenvolvimento; depois, fazer uma única comparação curta e previamente fixada. Se não existir correspondência inequívoca entre uma ação M16 e uma ação M17, a tradução deve rejeitar a ação e registar o motivo.

Não abrir ainda o diagnóstico reservado. A intervenção altera a interface, por isso precisa de uma condição experimental própria e de nova revisão do gate antes de qualquer avaliação científica.

## Integridade e reprodutibilidade

- A sequência contém 21 eventos: cinco registos de pergunta e 16 gerações. A verificação independente confirmou a cadeia SHA-256 evento a evento e o hash final declarado.
- As cinco fontes M17 monitorizadas antes e depois mantiveram os mesmos hashes. O adaptador M16 original e as reservas não foram modificados.
- Modelos: `unsloth/Qwen2.5-0.5B-Instruct-bnb-4bit` com revisão local registada no manifesto; adaptador M16 preservado em `m16-l4l5-r1` (hash da árvore registado).
- Os exemplos nativos vieram das linhas 0 (`query`) e 2 (`commit`) do conjunto `validation.jsonl` M16. Não foram usados rótulos de verdade oculta.
- Execução local na RTX 4070; duração observada: cerca de 70 segundos. Não foram avaliados custos monetários.
- A compilação sintática do executor foi verificada. Não foram executadas suites de testes nem avaliação M17 diagnóstica/reservada.

Os prompts exatos, estados, saídas brutas, contagens de tokens, erros, manifesto, registo de perguntas e diário encadeado estão no pacote reproduzível.

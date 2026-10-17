# TRONCO-01 G0b — protocolo operacional pré-registado

Data: 17/10/2026. Estado: congelado antes das gerações. Área de trabalho: `work/TRONCO01_G0B`. Limite absoluto: 20 gerações, sem retentativas. Não usar diagnóstico ou confirmação M17.

## Pergunta operacional

Uma instrução M17 mais explícita, com exemplos completos do contrato, permite transportar ações M17 válidas para fora do modelo? A verificação separa validade do JSON, validade da ação, correspondência ao pedido e correspondência ao professor nos dois controlos nativos M16. Não avalia raciocínio, adequação de hipóteses ou descoberta científica.

## Condições e orçamento

| Bloco | Condições | Chamadas |
|---|---|---:|
| Quatro fixtures de transporte no formato público M17 | Base e M16 × estado M17 atual só como utilizador e novo prompt de sistema com exemplos | 16 |
| JSON canónico | Dois pedidos, só base | 2 |
| Contrato nativo M16 | M16, um estado L4 de consulta e um estado L5 de compromisso, sem novo sistema | 2 |
| **Total máximo** | Sem repetição automática | **20** |

As quatro fixtures pedem, de forma explícita, uma consulta `qB`, um relatório `supported`, um `rejected` e um `undetermined`. Os campos referenciados existem nos próprios estados. Os exemplos do novo sistema usam IDs fictícios e não contêm as respostas das fixtures. Os estados, ações pedidas, prompts renderizados, hashes e critérios são gravados antes da inferência.

Os exemplos M16 vêm de `validation.jsonl`, não do treino nem das reservas científicas: linha 3, mundo L4 `09a8f893de5142a6`, consulta; linha 66, mundo L5 `11231cfece4ced99`, compromisso. São mundos diferentes e estados não usados no G0 anterior. O alvo do professor é conservado apenas para pontuar concordância e nunca é incluído no prompt.

## Medidas por chamada

Guardar prompt e hash, texto bruto, tokens de entrada e saída, EOS/limite, JSON estrito de objeto único, erro de parser, validação da ação e referências, correspondência ao pedido e, para M16, concordância com o professor. Falha de carga ou geração fica explícita. Limite de contexto 2048, geração greedy com `max_new_tokens=192` e `do_sample=false`. Não se corrige saída nem se tenta outra vez.

## Gate de engenharia

Para cada modelo avaliado para seguir no contrato M17, exigir 4/4 saídas estritamente JSON, 4/4 ações válidas com referências públicas válidas e 4/4 correspondências aos valores pedidos, sem truncamento. Este resultado apenas autoriza um pequeno piloto M17 em desenvolvimento. Não autoriza métricas científicas, abrir reservas, confirmar resultados ou treinar.

Os controlos canónicos base e a comparação M16 nativa ajudam a localizar a falha; não são contados no gate M17. Se o base falhar ambos os controlos canónicos, parar e verificar carregamento/descodificação antes de atribuir o resultado a capacidade. Se M16 só passar no contrato nativo, reportar falha de transferência de interface e não fabricar uma tradução semântica.

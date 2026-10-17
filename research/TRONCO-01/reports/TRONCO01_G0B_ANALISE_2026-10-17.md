# TRONCO-01 — análise da avaliação operacional G0b

**Data:** 17/10/2026  
**Protocolo:** TRONCO01-G0b-v0.1  
**Estado:** 20 gerações concluídas; gate de engenharia falhou para ambos os modelos.

## Resultados

| Bloco | JSON estrito | Ação válida | Correspondência exata |
|---|---:|---:|---:|
| Base — quatro fixtures M17, prompt atual | 0/4 | 0/4 | 0/4 |
| Base — quatro fixtures M17, sistema com exemplos | 1/4 | 0/4 | 0/4 |
| M16 — quatro fixtures M17, prompt atual | 4/4 | 0/4 | 0/4 |
| M16 — quatro fixtures M17, sistema com exemplos | 4/4 | 0/4 | 0/4 |
| Base — controlos JSON canónicos | 1/2 | 0/2 exatos | 0/2 |
| M16 — contrato nativo, L4 query e L5 commit | 2/2 | 2/2 | 2/2 do professor |

O gate exigia, por modelo, quatro respostas de transporte JSON estritas, válidas e correspondentes ao pedido. **Nenhum modelo passou.** O base falhou também os dois controlos canónicos. O M16 emitiu JSON estrito em todas as fixtures M17, mas as ações foram inválidas; em ambas as condições respondeu `report` ao pedido de `query`. No contrato nativo, acertou exatamente as duas ações de validação: uma consulta L4 e um compromisso L5, em mundos diferentes.

Uma resposta do base no caso `undetermined` chegou ao limite de 192 tokens sem EOS. As outras 19 chamadas terminaram por EOS. Não se fizeram retentativas, diagnóstico M17, treino ou consulta a reservas científicas.

## Limitação da comparação de prompts

O prompt de sistema pré-registado tinha um exemplo `query` e três exemplos `report` (um por veredicto). A condição ficou desequilibrada por tipo de ação e pode ter favorecido `report`; de facto, o M16 escolheu `report` até para a fixture de consulta. Assim, G0b mostra que esta intervenção completa falhou o gate, mas não estima isoladamente o efeito de uma instrução de sistema equilibrada. Os resultados do gate mantêm-se: nenhuma saída cumpriu a ação solicitada.

As fixtures testam transporte de campos e IDs conhecidos; não testam seleção científica, diagnóstico ou adequação de hipóteses. A concordância nativa M16 é evidência operacional limitada a dois estados de desenvolvimento. Ela confirma o caminho de inferência e a resposta no contrato nativo nesses estados, sem demonstrar competência geral.

## Decisão

Parar antes do piloto de mundos M17. Para o base, investigar primeiro o carregamento e a geração, dado que falhou também os controlos canónicos. Para o M16, manter a evidência de que executa o contrato nativo nestes dois exemplos, e tratar a transferência para o esquema M17 como não demonstrada.

A próxima avaliação operacional deve separar sintaxe de ação: primeiro comparar JSON estrito com descodificação restrita, depois testar a instrução com exemplos equilibrados entre `query` e `report`. Usar fixtures novos e fixados antes da chamada. Se esses gates passarem, avançar para um piloto pequeno apenas em desenvolvimento. Qualquer adaptação semântica de `commit` para os relatórios M17 precisa de uma regra explícita e avaliação própria; o adaptador não deve preencher campos científicos em falta.

## Integridade

- 20 gerações realizadas, iguais ao orçamento pré-registado; 20/20 prompts coincidem por hash com o ficheiro de agenda escrito antes da inferência.
- Pré-registo SHA-256 verificado; cadeia de 28 eventos verificada até ao hash final declarado.
- Os exemplos M16 são a linha 3 (mundo L4 `09a8f893de5142a6`) e linha 66 (mundo L5 `11231cfece4ced99`) do conjunto de validação. Os alvos do professor foram excluídos dos prompts.
- Os hashes dos cinco ficheiros M17 monitorizados são iguais antes e depois.
- O modelo base usou a revisão local `216d96b52c97a3c8294776df8477592f6828981c`; o adaptador manteve o hash de árvore `b5d6ab418b2c683e759c373d2d20e19e2deaed237e4e29dd9b33c4ef112c548f`.
- Verificação sintática do executor concluída; não foram executadas suites de testes.

Os prompts renderizados, saídas brutas, erros, hashes, agenda, diário, registo das perguntas e resumo estão no pacote reproduzível.

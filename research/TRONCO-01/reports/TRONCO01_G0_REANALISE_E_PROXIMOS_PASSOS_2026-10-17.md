# TRONCO-01 — reanálise de G0 e próximos passos

Data: 17/10/2026. Esta nota analisa as 16 saídas já gravadas; não executa novos modelos. Preserva o relatório e o pacote G0 originais.

## Leitura corrigida

| Condição | JSON estrito, objeto único | Ação válida |
|---|---:|---:|
| Base, estado como utilizador | 0/3 | 0/3 |
| Base, instrução de sistema | 2/3 | 0/3 |
| M16, estado como utilizador | 2/3 | 0/3 |
| M16, instrução de sistema | 3/3 | 0/3 |
| Base, exemplos nativos M16 | 0/2 | 0/2 |
| M16, exemplos nativos M16 | 2/2 | 2/2 |

O parser usado em G0, como o de M17, extrai o primeiro objeto JSON completo mesmo quando a resposta inteira não é um único objeto JSON. Por isso, 10/16 respostas tinham um objeto extraível, mas apenas 9/16 eram um objeto JSON completo. A diferença veio da resposta `base:cite_conflict:direct_system_instruction`, que contém vários fragmentos. Em todo o ensaio, só as duas respostas M16 no contrato nativo eram ações válidas.

A mensagem de sistema foi efetivamente renderizada no prompt. Melhorou a forma de algumas respostas: nos seis casos curtos, JSON estrito passou de 2/6 para 5/6. Não corrigiu os campos, valores e referências exigidos: validade permaneceu 0/6. Todas as 16 saídas terminaram por EOS e ficaram abaixo do limite de geração; a causa observada não é truncamento.

Os dois exemplos nativos M16 são passos da **mesma trajetória L4**: uma consulta e um compromisso posterior. Foram escolhidos pelo tipo de ação do professor, e a validação G0 verificou apenas se a ação produzida tinha campos e referências permitidos. O resultado 2/2 confirma compatibilidade de formato nestes dois estados; não constitui duas réplicas independentes nem demonstra decisão correta em novos mundos.

## Revisão da intervenção anteriormente sugerida

O relatório G0 sugeria construir um adaptador determinístico do contrato M16 para M17. Essa sugestão é prematura. No M16, `query` escolhe um inteiro `x`, `commit` escolhe uma hipótese e `abstain` encerra. No M17, `query` escolhe um `query_id` que aponta para uma medição estruturada; `report` exige `verdict` e confiança para ser aceite pelo ambiente, enquanto modelos candidatos, evidências e localização são necessários para sustentar os diagnósticos. Uma transformação de sintaxe não produz esses juízos e referências. Preencher campos ausentes com regras seria uma política científica adicional, que exigiria uma condição experimental própria. Primeiro é necessário demonstrar uma correspondência semântica explícita para cada ação; quando ela faltar, o adaptador deve rejeitar a tradução.

Os três exercícios curtos G0 foram construídos para testar comunicação e não reproduzem um estado M17 completo. Portanto, 0/6 diagnostica falha nesse contrato curto, mas não mede diretamente a taxa de validade que um prompt M17 melhor definido obteria num episódio real. As recusas e textos alheios à tarefa do modelo base também justificam uma verificação independente do carregamento e da inferência antes de atribuir a falha à capacidade do modelo.

## Sequência até à próxima avaliação obrigatória

1. **Congelar G0 como evidência.** Manter o manifesto, 16 saídas, diário e hashes. Registar a distinção entre JSON estrito, objeto extraível, ação válida e decisão correta. Não promover os dois exemplos nativos a uma métrica de competência.
2. **Auditar os contratos sem geração.** Especificar as ações e os campos obrigatórios de M16 e M17 numa tabela, indicando mapeamentos totais, parciais ou impossíveis. Rever o template, tokens especiais, configuração de geração, limites e validação; produzir um validador estrito que rejeite texto com objetos adicionais e registe o primeiro erro concreto.
3. **Preparar uma única intervenção de prompt M17.** Usar estado público no formato real M17, com ações permitidas e um exemplo de saída completo para cada tipo de ação. Manter modelo, parser estrito e parâmetros fixos. Os exemplos destinam-se a testar transporte de ações; não devem conter a solução dos casos avaliados.
4. **Fazer um ensaio G0b limitado a 20 gerações de desenvolvimento, sem retentativas.** Comparar prompt M17 atual e novo em quatro situações de transporte (`query`, `report supported`, `report rejected`, `report undetermined`) para base e M16: 16 chamadas emparelhadas. Acrescentar duas tarefas JSON canónicas no base para verificar a inferência e dois estados nativos M16 de mundos independentes, incluindo L5: quatro chamadas. Pré-registar IDs, estados, ordem, limites e critérios antes da primeira chamada. Guardar cada saída bruta e motivo de falha.
5. **Parar e avaliar G0b.** Gate de engenharia proposto para o novo prompt: 4/4 objetos JSON estritos e ações válidas por modelo, com zero truncamentos; 8/8 só se os dois modelos forem seguir no mesmo contrato M17. Reportar separadamente se os valores escolhidos são os solicitados. Se o base falhar tarefas canónicas, investigar carregamento/descodificação ou usar uma referência de maior capacidade antes de testar raciocínio. Se apenas M16 falhar o novo contrato, mantê-lo como comparação nativa e não inferir transferência. Para cada modelo que passar, fazer um piloto pequeno de mundos M17 de desenvolvimento com orçamento e interrupção na primeira ação inválida por episódio.

Esse novo piloto ainda seria validação operacional. Só depois de comunicação e fluxo de episódios funcionarem se deve congelar um protocolo científico novo, com famílias independentes, critérios de adequação, controlos e custos iguais. As reservas M17 e a confirmação permanecem fechadas; treino novo não é indicado por G0.

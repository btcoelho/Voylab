# Revisão do piloto v2.3 e próximo bloco

A conferência voltou aos eventos originais, aos prompts efetivamente enviados e ao JSON bruto. Não executou inferência nem alterou os resultados históricos. Os 13 controlos deste bloco passaram: sequência do diário, episódios únicos, hashes, correspondência dos 19 prompts com o estado público, correspondência das 15 ações descodificadas com o JSON bruto, componentes da pontuação, truncações, repetições e integridade do arquivo. O resultado é uma análise retrospectiva de desenvolvimento.

Os números anteriores estão corretos depois de reconciliar o rótulo de `pilot_01`: dez episódios, 19 chamadas, quatro saídas truncadas, três episódios sem relatório terminal legal e três relatórios legais, com zero sucessos conjuntos. Nas quatro truncações houve exatamente 256 tokens gerados e ausência de EOS. Houve 15 tentativas de relatório descodificadas; 12 foram rejeitadas por citarem evidência não observada. Não houve ações de consulta.

Nos três relatórios legais, o veredicto e o certificado de evidência falharam em 3/3. O conjunto de candidatos acertou em 2/3; diagnóstico e suficiência acertaram cada um em 1/3. Estes componentes ajudam a localizar o erro, mas não substituem o resultado conjunto de 0/10. O painel intencional não sustenta uma estimativa geral de desempenho nem conclusões sobre o Voynich.

## As alterações surtiram efeito?

| Alteração | Efeito verificado | Limite |
|---|---|---|
| Diário bruto e retoma | O lote terminou; cada episódio foi iniciado uma vez; saídas brutas e tokens ficaram guardados | O rótulo antigo de `pilot_01` e o histórico da sentinela não foram reconciliados no resumo |
| Tratamento específico de erro JSON | Os episódios posteriores com JSON incompleto foram classificados como falha de saída | Outros erros de descodificação, como chaves repetidas ou texto adicional, continuam no ramo genérico de exceções do runner |
| Gramática de saída | As 15 ações completas foram JSON descodificável; o ambiente rejeitou referências ilegais | Não impediu quatro truncações, nem decisões erradas; não houve comparação que isolasse o efeito causal da gramática |
| Avaliação por componentes | Recalculada a partir dos estados públicos, sem divergência nas ações deste lote | A concordância cobre estes estados e relatórios; não demonstra validade universal |

O avanço demonstrado está na observabilidade e na capacidade de localizar erros. Não há evidência de melhoria científica do modelo. A tarefa, o prompt e o protocolo deste piloto diferem das experiências históricas; comparar diretamente as percentagens não isolaria o efeito de uma alteração.

## Correções à interpretação anterior

**O runner repetiu o mesmo pedido após o erro.** Em `pilot_03`, `pilot_07` e `pilot_08`, as quatro chamadas de cada episódio têm um único prompt distinto e uma única saída distinta. O runner descartou o resultado de rejeição ao construir o pedido seguinte: enviou novamente só o estado, que permaneceu igual. A geração era determinística. Estes 12 eventos não demonstram quatro tentativas informadas de recuperação por episódio; contêm nove chamadas redundantes. O relatório anterior atribuiu demasiado desse comportamento ao modelo.

**As consultas eram opcionais e desnecessárias para atingir a pontuação.** Construí um relatório correto diretamente a partir de cada um dos dez estados iniciais; todos satisfazem o contrato sem consultar. Isto inclui `undetermined` no histórico vazio e `supported` com diagnóstico ambíguo quando várias tabelas ajustam os dados. Assim, zero consultas não é, por si só, falha. O painel não testa a necessidade de aquisição de informação nem a qualidade de uma política de consulta. A interação de consulta também não foi exercida pelo modelo neste lote.

**O contrato de ação não estava integralmente visível.** O prompt explica vários critérios científicos, mas omite a sintaxe exata de `{"action":"query","query_id":"..."}` e não apresenta o esquema completo de resposta. O descodificador conhece o esquema; isso não equivale a explicá-lo ao modelo. É uma deficiência de interface demonstrada pela fonte, cujo impacto causal no desempenho ainda não foi isolado.

**Desempenho baixo não demonstra invalidade do avaliador.** O replay confirma que as respostas científicas erradas observadas receberam insucesso, inclusive quando eram ações legais. A frase anterior de que o instrumento não estava apto, justificada principalmente por 0/10, foi demasiado ampla. A decisão delimitada é: o núcleo pontuou corretamente estes casos; o sistema integrado exige correções de execução, interface e análise antes de outro ensaio. Este lote não obriga a redefinir a semântica da tarefa.

## Limites encontrados no próprio verificador

O verificador retrospectivo anterior não é uma segunda implementação completa do ambiente: trata a localização `none`, não valida toda a estrutura JSON e compara ações já descodificadas. Nesta revisão, fiz também a ligação ao JSON bruto e exigi presença e igualdade de todos os campos de pontuação dos relatórios legais; isso não mudou os números.

Há dois defeitos concretos no seu código: a taxa principal é escrita como `0.0` em vez de calculada; e a comparação de pontuações considera apenas chaves presentes nos dois lados. Se a avaliação guardada fosse `{}`, a expressão `all(...)` sobre a interseção vazia aceitaria concordância. Os campos necessários existem neste lote e a comparação completa passou, portanto estes defeitos não alteram o 0/10 atual; impedem reutilizar o verificador como gate geral sem correção.

O pacote preserva apenas o hash do pré-registo inicial, não o seu conteúdo original nem uma cópia independente do runner anterior à emenda. É possível verificar o estado emendado atual e o diário; não é possível demonstrar retrospectivamente a integridade de um ficheiro inicial ausente. Essa ausência deve continuar explícita. O arquivo de evidências está íntegro, mas o procedimento do verificador depende de repor a estrutura de pastas do workspace; ainda não é reprodução autónoma com um comando numa pasta limpa.

## Próximo bloco que pode ser feito seguido

1. **Consolidar o estado a partir do diário.** Criar uma nova versão do runner e do analisador; preservar v2.3. Derivar resultados e taxas dos eventos, distinguir falha de saída, ação ilegal e falha de infraestrutura, preservar o histórico da sentinela e retomar sem duplicar chamadas concluídas. Incluir IDs de episódio/chamada nos eventos que hoje dependem da sua posição. Guardar o conteúdo e o hash de cada pré-registo e versão de código antes da execução.

2. **Explicitar e compactar o contrato.** Apresentar ao modelo a sintaxe pública de consulta e relatório, com um esquema curto; retirar a explicação livre do payload pontuado e limitar tamanhos de listas. Se forem restringidos IDs aos já visíveis, declarar isso como assistência de interface numa nova condição experimental. A gramática deve permitir decisões semânticas erradas: não deve calcular candidatos compatíveis, veredicto ou diagnóstico para os impor na resposta. Esta condição não pode ser apresentada como continuação inalterada do piloto anterior.

3. **Definir o comportamento após ações ilegais.** Usar uma política escrita: por exemplo, devolver um erro público de legalidade e o estado atual na chamada seguinte, dentro do mesmo limite de chamadas. O erro não deve revelar a conclusão científica esperada. Verificar com respostas simuladas que o pedido realmente muda após a rejeição e que orçamentos e terminação continuam corretos. Os relatórios cientificamente errados mas legais devem continuar a terminar e a contar como insucesso.

4. **Verificar as correções sem inferência.** Reproduzir o histórico deste lote, testar retoma interrompida e resumo desatualizado; introduzir resultados ausentes, falsos sucessos, chaves repetidas, referências ilegais e consultas fora do orçamento. O verificador deve rejeitar a avaliação vazia e produzir taxa 1.0 para um lote manual inteiramente correto. Testar os campos de diagnóstico, suficiência e localização independentemente. Conferir trajetos da gramática com o tokenizer até EOS e a compatibilidade do contrato compacto com o limite de tokens; continuar a classificar explicitamente qualquer truncação.

5. **Entregar um pacote de replay autónomo e o ponto de análise.** A partir de uma pasta limpa, um comando deve reconstruir o resumo a partir dos eventos, verificar hashes e executar os casos manuais e mutações relevantes. Encerrar este bloco com uma decisão sobre a integração corrigida. Só depois desta análise deve ser definido um novo piloto, com novo congelamento. Se houver interesse em testar consultas necessárias, isso exige um objetivo e métrica próprios; não se deve transformar a ausência de consultas deste painel em falha retrospectiva.

Este bloco é delimitado a correções e testes sem modelo. Fine-tuning, modelos maiores, expansão da amostra e reservas M17 continuam fora do bloco. G1/G2 e o piloto v2.3 conservam o estatuto histórico.

Registo verificável desta conferência: `TRONCO01_CONFERENCIA_PILOTO_v2_3_2026-10-17.json`. O script de conferência foi guardado em `work/verify_pilot_v23_review.py`.

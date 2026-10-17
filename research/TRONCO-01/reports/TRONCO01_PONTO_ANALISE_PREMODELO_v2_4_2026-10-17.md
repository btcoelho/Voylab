# Ponto de análise obrigatório — preparação v2.4

Este bloco concluiu a reparação offline da integração e a reprodução histórica. **Não carreguei pesos nem fiz chamadas ao modelo.** A análise obrigatória antes de uma nova inferência chegou agora ao seu ponto de decisão.

## O que passou

- 16 testes automatizados passaram; os módulos e testes passaram por compilação Python.
- A reprodução independente, só com biblioteca padrão, leu os registos arquivados de v2.3 e recalculou: 10 episódios, 19 chamadas, quatro saídas JSON truncadas no limite de 256 tokens, 12 ações ilegais, três relatórios legais, zero consultas e zero sucessos conjuntos. Reconciliou pilot_01 como falha de saída a partir do JSONDecodeError guardado, sem editar os ficheiros históricos.
- O resumo novo é derivado dos eventos: recupera o stop da sentinela, calcula a taxa a partir do número de sucessos e deixa a taxa planeada sem valor enquanto houver episódios por executar.
- O harness recusa retomar episódios interrompidos ou duplicados sem revisão; regista prompt, hash, esquema dinâmico, chamada, saída bruta, ação e resultado. Uma falha no gate de hashes produz zero chamadas.
- O feedback após rejeição muda o pedido seguinte e não inclui resposta científica esperada. A gramática elimina a ação de consulta quando o orçamento chega a zero.
- Com o tokenizer Qwen local e LM Format Enforcer, sem carregar pesos: 4 caminhos válidos chegaram a EOS; 7 casos inválidos foram bloqueados; um relatório semanticamente errado continuou estruturalmente permitido. Um relatório no maior formato representado terminou em 70 tokens, abaixo do limite histórico de 256.

Durante a verificação surgiu um defeito real na gramática para histórico vazio: a combinação de uma enumeração vazia sem tipo explícito quebrava o parser do LM Format Enforcer. Acrescentei o tipo string aos itens dinâmicos e voltei a executar a pré-verificação; o relatório vazio agora chega a EOS. Também limitei os valores de localização aos valores observados e testei que valores inventados sejam bloqueados.

## O que isto demonstra

As correções propostas para retoma, contagem, feedback e restrições estruturais funcionam nos testes simulados e no replay do diário antigo. O resultado v2.3 permanece igual: 0/10 sucessos conjuntos. Isso continua a ser uma medição da configuração antiga; a nova interface e o feedback mudam a condição experimental.

A nova gramática restringe identificadores e valores aos que já aparecem no estado público. Isso é assistência de interface, documentada no protocolo. A gramática não impõe veredicto, conjunto de candidatos, diagnóstico ou suficiência: o caso de controlo errado foi aceite até EOS. Portanto, uma pontuação futura mede o modelo com esta assistência explícita.

O gate offline passou no âmbito testado, mas ainda não existe um adaptador de geração ligado a um checkpoint, nem um modelo, parâmetros ou agenda novos congelados. A verificação de EOS percorreu o tokenizer e o TokenEnforcer; não executou a geração do modelo. O pacote também não recupera o conteúdo do pré-registo original de v2.3, que só sobrevive pelo hash.

## Decisão neste ponto

**Apto para encerrar a preparação offline; ainda não pronto para iniciar outra inferência.** O núcleo determinístico não precisou de redefinição neste bloco. A próxima avaliação deve ter uma pré-registração própria para a interface v2.4, fixar modelo e geração, congelar a agenda e integrar o backend com o esquema público dinâmico e o gate de hashes. Tem de declarar se mede resposta científica direta, recuperação após rejeição ou política de consulta; o piloto v2.3 só mede o primeiro objetivo de forma indireta e não exige consulta.

Depois de fixados esses itens, repete-se o ponto de análise. Até lá, G1/G2 e o lote v2.3 mantêm o estatuto histórico, e as reservas M17 permanecem fechadas. Não houve fine-tuning nem expansão de modelo.

Reprodução: executar python replay.py e python -m unittest discover -s tests -v dentro do pacote. A pré-verificação do tokenizer requer o ambiente documentado no resultado JSON; não requer nem carrega pesos.

# Contrato TRONCO-01 v2.1 — ensaio determinístico delimitado

## Âmbito e afirmações

O alvo primário é o ajuste observacional do modelo de trabalho `W` ao histórico público `H`:

- `supported`: H tem pelo menos uma observação e W prevê todas as saídas de H.
- `rejected`: existe uma observação pública que W não prevê.
- `undetermined`: H está vazio.

Em campos separados, o agente devolve o conjunto dos candidatos compatíveis com **todo** H e o diagnóstico da classe declarada: `none_fit`, `identified` ou `ambiguous`. O campo `sufficiency` comunica suficiência para identificar um candidato: `no_observations`, `no_candidate_fits`, `identity_ambiguous` ou `identity_resolved`. Isso não torna uma classe de candidatos completa nem prova uma causa externa.

Nenhum rótulo escondido do gerador define as respostas esperadas. Dois episódios com o mesmo estado público têm as mesmas respostas esperadas. Não se avalia causalidade nem previsão fora da classe e do domínio explicitamente observado.

## Camadas

1. **Descodificação:** exatamente um objeto JSON; chaves repetidas, NaN/Infinity, texto antes/depois e JSON incompleto são rejeitados. O texto bruto é gravado e sincronizado antes da descodificação.
2. **Estrutura:** schema fixo Draft 2020-12; objetos de ação e localização têm campos conhecidos; IDs nas listas são únicos. Respostas falsas mas bem formadas continuam representáveis.
3. **Legalidade:** consulta tem de estar no menu e o orçamento ser positivo; evidência tem de apontar para observações existentes; candidatos têm de pertencer à lista pública. Ação ilegal não pode obter aprovação final.
4. **Sustentação:** W é comparado com todo H. `supported` requer certificado que cubra cada conteúdo observacional distinto; duplicatas idênticas não criam novo conteúdo. `rejected` requer pelo menos um contraexemplo citado, e todas as referências têm de ser legais. `undetermined` só vale com H vazio e evidência vazia.
5. **Diagnóstico:** candidatos declarados têm de coincidir exatamente com os sobreviventes que acertam todo H; `diagnosis` e `sufficiency` têm de coincidir com a cardinalidade desse conjunto.
6. **Localização opcional:** usa feature "none" e lista de valores vazia quando não há alegação. Só se pontua um contraste direto: os outros campos ficam fixos, a saída muda, e os dois valores afirmados coincidem exatamente com os observados. Não é uma alegação causal.

Legalidade e sustentação são registadas separadamente. A aprovação conjunta exige ambas. A saída do sistema apresenta cada falha, sem esconder uma referência ilegal sob um veredicto certo.

## Ações e estado

Uma consulta aceite retira o ID do menu, acrescenta uma observação com ID novo e diminui o orçamento em um. Rejeição não muda o estado. Relatório legal termina o episódio, mesmo se a ciência estiver errada. Ações posteriores à terminação falham. Estados novos começam independentes.

## Portão pré-modelo

O ensaio de modelo fica bloqueado até schema, parser, validador, máquina de estados, diário bruto, avaliador e gramática passarem o pré-teste reproduzível. O pré-teste valida proveniência dos ficheiros congelados, menu e orçamento. A bateria inclui enumeração finita, propriedades, defeitos históricos e mutações. Esta aprovação permite apenas considerar um ensaio pequeno pré-registado; não permite fine-tuning, modelos maiores ou uso de reservas M17.

## Limites

O contrato assume tabelas determinísticas, observações completas e sem ruído, e modelos de candidato codificados corretamente. Generalização para ruído, hipótese omitida, manuscritos ou inferência causal exige outra tarefa e outro modelo de observação.

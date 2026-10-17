# TRONCO-01 — análise de integridade da execução G0e

**Data:** 17/10/2026  
**Estado:** 32 gerações concluídas; instrumento com alvos de consulta inválidos.  
**Decisão:** não abrir o piloto M17. A execução não serve para aprovar nem rejeitar o gate operacional.

## Falha encontrada

O pré-registo G0e tinha dois alvos de consulta (`qM` e `qT`) que não existiam nos respetivos menus. Para o estado A, os IDs públicos eram `qAM` e `qAT`; para o estado B, `qBM` e `qBT`. O executor adicionou o alvo esperado diretamente à trie e verificou apenas se o alvo pertencia à trie. Não verificou se o alvo respeitava as referências públicas do estado. Por isso, o alvo impossível passou o teste de alcance, mas foi corretamente rejeitado pelo validador de ações.

Esta falha invalida o gate global G0e. As consultas não testaram uma ação válida do protocolo, e a condição restrita incluiu deliberadamente uma opção inválida. Nenhum piloto científico deve depender destas contagens.

## O que os registos permitem dizer

| Modelo e condição | JSON estrito | Ação válida | Correspondência exata | Limite/EOS |
|---|---:|---:|---:|---:|
| Base, livre | 7/8 | 0/8 | 0/8 | uma saída atingiu o limite sem EOS |
| Base, trie | 8/8 | 6/8 | 4/8 | 8/8 EOS |
| M16, livre | 6/8 | 0/8 | 0/8 | 8/8 EOS |
| M16, trie | 8/8 | 6/8 | 5/8 | 8/8 EOS |

Nas seis fixtures de relatório, as saídas restritas foram válidas. A correspondência foi 4/6 para o base e 5/6 para o M16. Estes valores são descritivos do conjunto finito de opções daquela trie; não aprovam competência científica. Nas consultas, o base copiou `qM` e `qT`, ambos inválidos nos menus. O M16 escolheu um relatório `undetermined` em vez de consulta. O braço livre não produziu ações válidas nos oito casos de cada modelo.

O conjunto restrito continha o objeto alvo como opção explícita. A correspondência mostra a seleção desse objeto entre as opções fornecidas; não demonstra que o modelo construiu autonomamente o objeto. O teste é de seguimento de pedido e interface.

## Integridade e limites

- 32/32 chamadas foram feitas; não houve retentativas.
- Agenda e hashes dos prompts foram gravados antes da inferência. A cobertura literal do alvo foi verificada, mas a validação semântica do alvo contra o estado foi omitida.
- O resumo por modelo e condição foi calculado no fim; o gate de avanço não passou.
- Não houve piloto, treino, alteração do adaptador ou acesso a dados reservados.

## Próximo bloco, a executar sem paragens intermédias

1. Corrigir o construtor de fixtures e validar cada ação alvo com o mesmo validador usado pelo ambiente. Para cada alvo, exigir simultaneamente: ID em menu/lista pública, ação autorizada, campos e tipos corretos, e igualdade com o alvo após validação. Se um alvo falhar, parar antes de carregar qualquer modelo.
2. Corrigir a geração de alternativas da trie para usar apenas ações válidas no estado. Manter `query` e `report` disponíveis quando ambos forem legais. Gravar o conjunto permitido e os resultados da validação de cada candidato no pré-registo.
3. Congelar uma nova versão do protocolo e oito fixtures de transporte. Exigir duas consultas com alvos retirados literalmente dos respetivos menus e seis relatórios cujos alvos passam o validador. Verificar cobertura dos alvos e que cada estado permite as opções que o ensaio pretende comparar.
4. Executar no máximo 32 gerações: base e M16, geração livre e restrita, sem retentativas. Pontuar condições separadamente. O gate por condição exige 8/8 ações e valores de alvo corretos, zero referências inválidas, zero falhas de geração e zero truncamentos.
5. Se pelo menos uma condição/modelo passar o gate, fazer o sentinela de cinco mundos de desenvolvimento e, se os cinco tiverem relatório explícito sem erro operacional, seguir automaticamente para 25 mundos. Caso contrário, parar.
6. Ponto de análise obrigatório depois do gate ou do piloto. Nenhuma partição reservada é aberta e nenhum fine-tuning ocorre neste bloco.

Esta execução atingiu o ponto de análise previsto. Como a auditoria encontrou uma falha no instrumento, o próximo protocolo precisa de nova versão e novo pré-registo; não se devem acrescentar chamadas retroativamente ao G0e.

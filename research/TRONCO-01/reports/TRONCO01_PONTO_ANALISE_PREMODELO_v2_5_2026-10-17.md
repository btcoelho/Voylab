# Ponto de análise obrigatório antes do modelo — TRONCO-01 v2.5

## Decisão

**A preparação offline está pronta para análise humana; o ensaio de modelo ainda não começou.** O manifesto e a pré-registração permanecem em rascunho, e o guard impede que o carregador Qwen aceite esse estado. Nenhum peso foi carregado, nenhuma inferência foi executada, e não houve fine-tuning ou mudança para modelo maior.

## O que foi corrigido e demonstrado

- O diário agora grava uma identidade de ensaio que liga a agenda canónica, o limite de chamadas e o hash da pré-registração. O guard é verificado à entrada, mesmo se todos os episódios estiverem concluídos. Retoma com agenda, pré-registração ou ficheiro externo alterado é bloqueada.
- O backend Qwen2.5 foi extraído do executor histórico para um adaptador lazy. Antes de importar Unsloth ou carregar pesos, exige manifesto congelado e confirma hash da pré-registração, pesos, tokenizer e configuração do tokenizer. Testes mostraram que manifesto em rascunho e hash incorreto param antes de qualquer chamada.
- A gramática LMFE 0.11.3 aceita as três formas de listas duplicadas testadas. Isso ficou explicitamente declarado: a validação Python rejeita as duplicações e regista a saída como falha, sem deduplicar nem pontuar. O teste do tokenizer confirmou os dois lados da regra.
- A integração simulada usou tokenizer e template de chat Qwen reais, manifesto de teste, gramática LMFE, executor de ensaios e diário. Uma ação de consulta acrescentou uma observação e o relatório seguinte encerrou o episódio em duas chamadas. A resposta é fixa e não-oracular; não é evidência de capacidade do modelo.
- Passaram 25 testes (0.237s); três mutações dirigidas foram detetadas; os módulos compilaram. O SHA-256 local de `model.safetensors`, `tokenizer.json` e `tokenizer_config.json` coincide com os valores registados no pré-registo v2.3, verificados lendo ficheiros sem carregar pesos.

## Resultado histórico

O replay independente permanece em **0/10 sucessos conjuntos**: 19 chamadas, quatro saídas truncadas sem EOS, 12 ações ilegais, três relatórios legais e zero consultas. A nova interface teria recusado as 12 ações antigas que citavam IDs inexistentes, mas isso é uma verificação sobre saídas guardadas, não uma previsão de uma nova geração.

## Ensaio candidato e alcance

A pré-registração em rascunho propõe o mesmo checkpoint e os mesmos parâmetros recuperáveis — Qwen2.5-0.5B Instruct quantizado, `do_sample=false`, 256 tokens novos e contexto 2048 — num modo de resposta direta sem consultas. Reusa os dez estados públicos de v2.3. Como já foram expostos, serviria apenas para diagnosticar a alteração de interface; não seria teste cego, confirmatório ou medida de generalização.

## Ponto que requer decisão humana

Antes da primeira inferência, decidir se este painel exposto ainda é útil para desenvolvimento. Se sim, congelar uma agenda identificada como desenvolvimento, mudar o manifesto para `frozen_before_inference`, confirmar os hashes ativos e registar a decisão. O manifesto atual está em `draft_not_frozen` e o carregador bloqueia esse estado. A geração real e o comportamento do adaptador Qwen só poderão ser avaliados depois desse gate; a simulação não os substitui.

G1/G2, os registos v2.3 e as reservas M17 permanecem intactos.

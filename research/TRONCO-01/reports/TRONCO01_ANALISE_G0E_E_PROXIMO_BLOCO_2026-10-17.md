# TRONCO-01 — análise G0e e próximo bloco contínuo

> **Atualização após execução (17/10/2026):** o bloco corrigido G0g foi executado; o gate válido ficou em 7/8 no base restrito e 6/8 no M16 restrito, pelo que o piloto não avançou. Ver [análise G0g](TRONCO01_G0G_ANALISE_E_GATE_2026-10-17.md).

**Data:** 17/10/2026  
**Estado atual:** G0e concluiu as 32 chamadas, mas não pode decidir o gate porque os dois alvos de consulta não existiam nos menus. Nenhum piloto M17 foi executado.

## Leitura correta do G0e

As fixtures A ofereciam `qAM` e `qAT`, mas pediam `qM`; as fixtures B ofereciam `qBM` e `qBT`, mas pediam `qT`. O executor inseriu os alvos diretamente na trie e verificou que estavam presentes, sem confirmar a validade no estado. O validador rejeitou as consultas do base; o M16 escolheu relatórios nos dois casos de consulta. Isso invalida o gate global.

Nas seis fixtures de relatório, os alvos estavam disponíveis e passaram o validador. Sob a trie, a correspondência foi 4/6 no base e 5/6 no M16. Na condição livre, nenhum dos modelos produziu ação válida em oito casos. Estes resultados descrevem apenas a interface e este pequeno conjunto de cópia; não medem capacidade científica nem aprovam um agente M17.

O G0e também evidencia que “o alvo está na trie” é uma verificação insuficiente. O critério deve ser: **o alvo passa o validador do ambiente e é permitido pela gramática**, ambos antes de qualquer chamada ao modelo.

## Bloco seguinte — uma execução até à análise obrigatória

### Fase 1 — corrigir e auditar fixtures, sem chamar modelos

1. Gerar os IDs de consulta escolhendo diretamente um item de `query_menu`; nunca escrever o ID alvo manualmente.
2. Para cada uma das oito fixtures, validar o alvo com a mesma função do ambiente M17 e confirmar a correspondência exata com o item público. Fazer o mesmo para todos os candidatos admitidos pela descodificação.
3. Confirmar duas fixtures de consulta e duas de cada veredicto; IDs únicos; referências públicas existentes; ações legais; prompts abaixo do limite de contexto; ambas as ações (`query` e `report`) disponíveis onde o estado permite ambas.
4. Verificar que a condição livre e a restrita usam o mesmo estado e prompt. Na condição restrita, verificar automaticamente que um prefixo que sai da trie falha explicitamente e não continua sem restrição.
5. Validar o pontuador em exemplos sintéticos: alvo correto, ID inexistente, veredicto trocado, evidência ausente, resposta truncada e saída fora de JSON. Nenhum modelo é carregado nesta fase.

**Gate pré-inferência:** zero alvos inválidos, zero referências inexistentes, todos os alvos alcançáveis, e os erros injetados nos exemplos sintéticos são classificados corretamente. Se falhar, corrigir e repetir apenas esta verificação local.

### Fase 2 — congelar uma nova avaliação de transporte

Criar uma versão nova do protocolo, com oito fixtures e 32 chamadas máximas: dois modelos (base e M16), duas condições (livre e restrita) e oito fixtures. Guardar pré-registo, código, hashes da árvore de modelos/adaptador, agenda e respostas permitidas antes da primeira inferência. Sem retentativas.

Pontuar separadamente: JSON estrito, tipo de ação, ID/veredicto, referências e campos obrigatórios. Na cópia literal, comparar os valores pedidos campo a campo; apresentar igualdade integral como medida adicional. A descodificação restrita nunca deve decidir o tipo de ação quando ambos são legais.

**Gate operacional:** analisar cada condição separadamente. Uma condição candidata ao piloto precisa de 8/8 ações e valores discretos corretos, referências válidas, zero erros de geração e zero truncamentos. Se a condição restrita passar, ela define o formato usado no piloto. A condição livre é comparação e não precisa passar para a restrita avançar. Se nenhuma condição passar, encerrar no ponto de análise sem repetir com novos prompts.

### Fase 3 — piloto em desenvolvimento, só se uma condição passar

Executar cinco mundos de desenvolvimento, um por categoria, até quatro ações por mundo e parar o episódio na primeira ação inválida. Prosseguir automaticamente para 25 mundos (cinco por categoria) apenas se os cinco episódios iniciais terminarem com relatório explícito e sem erro de parser, geração, ação inválida ou truncamento. Comparar com controlos determinísticos nos mesmos mundos e orçamento de consultas.

Registar resultados por episódio: veredicto, decisão correta, reconhecimento de insuficiência, relatório explícito ou fim forçado, evidências, consultas, custo e falhas operacionais. Não tratar ações sucessivas do mesmo mundo como amostras independentes. Os resultados permanecem exploratórios.

### Fase 4 — ponto único de análise

Parar após falha do gate operacional ou após o piloto de 25 mundos. Rever saídas brutas, resultados por categoria, diferença para os controlos e integridade das partições. Só então decidir se é necessário um modelo de referência mais capaz ou uma intervenção de treino. Reservas diagnósticas e de confirmação permanecem fechadas; nenhum fine-tuning ocorre neste bloco.

## Regra de continuidade

As Fases 1 e 2 decorrem sem interrupção entre correções locais. O bloco de modelo executa uma vez com o pré-registo congelado. A única paragem científica é a Fase 4, além de um bloqueio técnico que impeça validar a integridade antes da inferência.

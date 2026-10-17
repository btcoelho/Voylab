# TRONCO-01 — revisão G0c/G0d e bloco seguinte

> **Atualização após execução (17/10/2026):** o bloco G0e de 32 gerações terminou, mas duas consultas usavam IDs fora do menu. O gate global ficou inválido e o piloto não começou. Ver [análise de integridade G0e](TRONCO01_G0E_ANALISE_DE_INTEGRIDADE_2026-10-17.md) antes de reutilizar o plano abaixo.

**Data:** 17/10/2026  
**Estado:** revisão dos dados e do executor; plano pronto para execução contínua até novo ponto de análise.

## Correção dos resultados anteriores

O gate G0c/G0d de descodificação restrita tinha um erro de desenho. Para cada fixture `report`, a trie continha apenas `explanation` igual a `short statement` ou `fixture statement`. Os alvos pediam `Transport fixture.` ou `Held-out fixture.`. Além disso, o alvo `rejected` de G0d pedia confiança `0.9`, ausente da lista permitida; o alvo `rejected` de G0c usava uma localização também ausente. Assim, **os três relatórios exatos de cada conjunto eram impossíveis de gerar**. A melhor pontuação exata possível era 1/4, mesmo para um modelo ideal. O base alcançou esse único caso possível; o M16 não acertou o ID da consulta.

Uma auditoria direta do código e dos pré-registos confirmou a cobertura: em G0c e G0d, o alvo da consulta pertence às duas saídas permitidas; cada alvo de relatório está ausente das 3456 saídas permitidas no respetivo estado. A auditoria não fez chamadas a modelos.

A função `action_candidates` também lia `requested_action` para permitir somente `query` nas fixtures de consulta e somente `report` nas restantes. Logo, os 4/4 de ações válidas sob restrição são produzidos pela interface; não medem a escolha de tipo de ação pelo modelo. A comparação de 1/4 versus 0/4 não sustenta a conclusão de que ambos falharam um gate de 4/4. O relatório anterior fica assinalado como corrigido, preservando-se as saídas brutas.

Há uma observação mais estreita que continua válida: com esta trie, ambos escolheram `supported` nos três pedidos de relatório de G0c e nos três de G0d, incluindo pedidos `rejected` e `undetermined`. Isto sugere uma preferência de saída neste ensaio de transporte. Não mede diagnóstico científico. Na geração livre G0c, o base produziu 1/4 ações válidas e o M16 0/4; estas quatro fixtures já tinham sido usadas em G0b, portanto são diagnóstico de desenvolvimento, não validação independente.

G0d mudou IDs e valores, mas manteve a mesma estrutura de estado e inseriu a resposta pretendida em `requested_action`. Não constitui um teste de decisão autónoma. Os dois carregadores carregaram o checkpoint; o controlo JSON aninhou a instrução num campo `task`, limitando o que se pode concluir sobre diferenças de inferência.

## Bloco de trabalho a executar de seguida

O bloco abaixo pode decorrer sem paragens para aprovação entre fases. Só se interrompe antes do piloto se o gate operacional pré-registado falhar, ou no ponto de análise final. A avaliação reservada e o fine-tuning continuam fora deste bloco.

### 1. Reparar o instrumento antes de novas gerações

- Criar um descodificador ou enumerador cujo conjunto de saídas contenha **todas** as ações alvo de transporte. Auditar automaticamente `target ∈ outputs_permitidos` para cada fixture antes de carregar um modelo.
- Nas tarefas de transporte e de decisão, permitir `query` **e** `report` no mesmo estado quando ambos são legalmente possíveis; a gramática só restringe sintaxe, tipos e referências públicas. O tipo pedido continua a ser escolhido pelo modelo.
- Separar pontuações: JSON estrito, tipo de ação, ID, veredicto, referências, localização e conformidade com o pedido. Uma explicação com palavras diferentes não deve reprovar uma ação semanticamente equivalente. Para a tarefa de cópia literal, pontuar também igualdade integral, depois de verificar que o alvo é alcançável.
- Rejeitar qualquer prefixo gerado fora da trie como falha explícita; não deixar a descodificação continuar sem restrição. Guardar tokens, texto bruto, prompt e causa de rejeição.

**Gate interno:** todos os alvos alcançáveis, nenhum tipo de ação decidido pelo descodificador na tarefa de decisão, e avaliador de campos consistente em exemplos com respostas equivalentes e erradas. Falhando este gate, corrigir o instrumento sem gastar gerações de modelo.

### 2. Congelar dois conjuntos distintos

**Transporte:** oito fixtures novas, com dois pedidos de consulta e dois de cada veredicto. Variar ordem dos IDs, orçamento e evidências. O pedido explícito aparece apenas neste conjunto. Congelar estados, alvos aceitáveis, prompts, hashes, modelo/revisão, limite de tokens e orçamento antes da primeira geração.

**Decisão:** estados de desenvolvimento M17 sem `requested_action`. Preparar uma rubrica a partir de evidência pública e regra de paragem, admitindo várias ações justificáveis. O rótulo oculto só entra no avaliador depois da ação. Incluir os cinco tipos de mundo, exemplos identificáveis e exemplos em que a evidência impõe `undetermined`. Verificar fugas por nomes, ordem e comprimento.

### 3. Executar avaliação operacional limitada

Executar as oito fixtures de transporte em base e M16, cada um em geração livre e com restrição corrigida: **máximo de 32 gerações**, sem retentativas. Pontuar por campo, guardar todas as saídas e falhas. O adaptador M16 continua como braço exploratório de transferência; o seu desempenho não bloqueia a avaliação do base.

**Gate por modelo para avançar:** 8/8 tipos de ação, IDs, veredictos e outras referências discretas pedidas corretos; campos obrigatórios presentes; zero truncamentos e zero falhas de geração. Pontuar a confiança pedida com tolerância fixada previamente e a explicação pela presença e relação com as evidências, separadamente. A igualdade textual integral é apresentada à parte. Se nenhum passar, parar e produzir a análise obrigatória com as falhas por campo; não repetir automaticamente com novos prompts.

### 4. Piloto de decisão em desenvolvimento, apenas para modelos que passaram

Começar por cinco mundos, um por categoria, com até quatro ações por mundo e paragem após a primeira ação inválida. Prosseguir automaticamente para **25 mundos de desenvolvimento**, cinco por categoria, somente se os cinco episódios terminarem com relatório explícito, sem ação inválida, erro de parser, erro de geração ou truncamento. Usar o mesmo limite de quatro ações e mundos não apresentados nos exemplos de prompt. Executar os controlos determinísticos sobre os mesmos mundos, com igual orçamento de consultas.

Relatar por mundo: veredicto, reconhecimento explícito de insuficiência, relatório versus fim forçado, evidências citadas, consultas e custo. Não usar ações de um mundo como réplicas independentes. Estes números são exploratórios e não aprovam M17.

### 5. Ponto único de análise obrigatório

Parar após falha do gate operacional ou após o piloto de 25 mundos. Rever saídas brutas, erros de interface, diferenças face aos controlos, casos de insuficiência e integridade das partições. Decidir então se faz sentido testar um modelo de referência mais capaz, mudar a interface ou propor treino específico. Congelar novo protocolo antes de qualquer avaliação diagnóstica ou confirmação reservada.

## Regra de interpretação

Um descodificador que impõe JSON e IDs válidos resolve parte da interface. Não demonstra que o modelo escolhe uma consulta útil, reconhece insuficiência ou sustenta um veredicto. O próximo gate e o piloto medem essas capacidades em etapas separadas.

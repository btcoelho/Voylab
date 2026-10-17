# TRONCO-01 — revisão G2 e próximo bloco contínuo

**Data:** 17/10/2026  
**Estado:** plano para a próxima execução; nenhuma inferência G2.1 foi iniciada.  
**Ponto de paragem previsto:** falha de integridade/recurso, falha de um gate pré-registado ou análise completa dos 25 mundos de desenvolvimento.

## O que muda na interpretação

O G2 terminou corretamente no sentinela: `base_g2_schema` fez 4/5 relatórios explícitos, 0/5 decisões certas e 0/5 diagnósticos com evidência; a geração livre fez 0/5 ações válidas. Nos quatro relatórios aceites, `evidence_ids` ficou vazio e `location` não seguiu a forma anunciada. Assim, uma instrução textual mais detalhada não resolveu a tarefa nem produziu um teste limpo de descodificação livre contra restrita. A ponte G1 fez 5/5 relatórios e 2/5 decisões certas nesses mesmos casos.

O principal defeito técnico é a divergência entre contrato público, gramática, validador e pontuador. A gramática G2 aceitou qualquer objeto `location`; o validador verificou apenas que era um objeto; o pontuador exigiu valores e evidências precisos. Uma saída podia, portanto, ser operacionalmente aceite e cientificamente inepta. A verificação completa dos 300 IDs de consulta só foi feita numa auditoria pós-execução, embora todos tenham passado. O próximo pré-teste tem de fazer essa verificação **antes** da inferência.

Também há uma limitação na métrica de consulta. No G1, as 15 consultas do base em contradição, as 15 em insuficiência e as 15 em hipótese ausente foram marcadas com ganho de informação zero. Em contradição e hipótese ausente, o conjunto de modelos compatíveis já estava vazio; o ganho definido apenas como redução desse conjunto é zero independentemente de a consulta confirmar uma anomalia. A contagem de consultas redundantes continua útil para esse objetivo estreito, mas não mede sozinha o valor de replicação ou contraste. Os controlos aleatório/fixo apresentaram padrão parecido. O G2.1 deve relatar ambos os aspetos.

## Bloco G2.1 a realizar seguido

### 1. Fechar a validade do contrato e do pontuador, sem GPU

Congelar G1 e G2 como resultados históricos. Auditar, por categoria, o que `score_report` considera evidência suficiente e localização correta. Em particular, verificar se a contradição exige todos os registos com o mesmo input quando um par já demonstra o conflito, e se os demais critérios correspondem ao que o estado público pede ao agente. Documentar exemplos sintéticos genéricos positivos e negativos. Se o pontuador precisar de correção, criar uma versão nova antes do pré-registo; nunca recalcular G1/G2 como se tivessem usado esse critério.

Criar uma ação G2.1 curta e estruturada. Manter decisão `query`/`report`, veredicto, IDs de hipóteses e evidência, localização e confiança escolhidos pelo modelo. Retirar do caminho principal o campo livre `explanation`, que não é pontuado e consumiu parte do orçamento de geração no G2. O ambiente já admite explicação ausente. Definir `location` com apenas `feature` e `value`: `feature=input` exige o objeto completo de entrada observada; um campo como `phase` ou `partner` usa valor(es) observados; ausência de localização justificada usa `null`. Recusar chaves extra, IDs inventados, evidência duplicada e relatórios sem evidência mínima. Estas restrições estabelecem legalidade e proveniência; **não escolhem** o veredicto, os IDs corretos nem a localização correta pelo agente.

Usar uma instrução curta e uma descrição pública sem cadeias exemplificativas que pareçam valores a copiar. Fazer gramática e validador aceitar e rejeitar o mesmo conjunto de estruturas. Manter as falhas como falhas, sem completar campos, corrigir JSON, escolher consultas ou substituir relatórios no executor.

Definir antes do pré-registo uma medida computável de consulta que registe quando uma nova observação cria ou replica um contraste relevante, usando apenas o histórico observado naquele passo. Relatá-la ao lado do ganho de informação sobre hipóteses, sem alterar retroativamente a classificação G1/G2.

### 2. Preparar uma referência de capacidade e congelar o ensaio

Manter o checkpoint base 0,5B fixado. Selecionar **uma** referência de instruções com mais capacidade, pesos e licença verificáveis, que caiba na RTX 4070 de 12 GB no contexto escolhido. Fixar repositório, revisão, hashes, quantização, versão de bibliotecas, comprimento de contexto, limite de saída, geração determinística e uso de memória antes de expor qualquer mundo novo. Se nenhuma referência viável estiver disponível, parar antes da inferência e entregar o diagnóstico de recursos; repetir apenas o 0,5B acrescentaria pouca informação sobre capacidade.

Pré-registar 25 mundos de desenvolvimento novos e equilibrados, cinco por categoria. Excluir todos os mundos usados no piloto M17, G0g, G1 e **todos os 25 IDs agendados no G2**, incluindo os 20 que não chegaram a ser avaliados; esta exclusão conservadora simplifica a auditoria. Usar o mesmo estado público, orçamento de três consultas e limite de quatro ações para todas as condições.

Condições principais: base 0,5B + contrato G2.1 restrito; referência + mesmo contrato restrito; controlos estatístico, consulta aleatória, consulta fixa e simbólico ativo. Em cada modelo, testar também o **mesmo prompt sem gramática** nos cinco sentinelas; só prolongar esse braço livre se passar 5/5 relatórios válidos sem erros operacionais. As condições restritas e os controlos permanecem emparelhados nos mesmos mundos. O controlo simbólico é teto construído para resolubilidade, não comparação entre LLMs.

Em todos os braços, exigir que a saída seja exatamente um objeto JSON completo. Não extrair um objeto de texto adicional nem aceitar texto após o JSON; essa regra permite atribuir falhas de formato à condição que as produziu.

### 3. Pré-teste completo antes de carregar pesos

Em estados iniciais e após consultas simuladas, confirmar que **cada** ID de consulta legal é alcançável pela gramática e que o ramo de consulta desaparece ao esgotar o orçamento. Confirmar relatórios canónicos e rejeitar formas inválidas de `location`, campos extra, IDs inexistentes, evidência vazia/duplicada, ações incompletas e JSON truncado. Verificar ausência de categoria, alvo ou resposta oculta no prompt, reset entre episódios, ordem de persistência das saídas brutas e orçamento de contexto/saída. Guardar contagens e hashes. Qualquer discrepância pára o bloco antes da inferência.

### 4. Executar os gates automáticos nos mesmos mundos

**Sentinela operacional, 5 mundos (um por categoria, incluídos nos 25).** Correr todos os braços e controlos. Cada braço restrito passa apenas com 5/5 relatórios explícitos, zero falhas de geração/parser, zero truncagens e zero ações inválidas. Se nenhum passar, parar e analisar as saídas. Se pelo menos um passar, continuar **ambos** os braços restritos e controlos, mantendo todas as falhas no denominador. Um braço livre só continua se passar o seu próprio gate 5/5.

**Viabilidade científica, 10 mundos no total (dois por categoria).** Sem retocar prompt ou regras, avançar aos 25 apenas se pelo menos um braço restrito tiver: no máximo uma falha operacional em 10; pelo menos 5/10 decisões certas; pelo menos tantos diagnósticos com evidência quanto o melhor dos controlos aleatório e fixo nos mesmos 10 mundos; e reconhecimento de insuficiência em pelo menos 1/2 casos. Este gate é apenas um filtro de desenvolvimento para evitar gastar o lote completo numa condição ainda sem triagem elementar. Se falhar, parar na análise obrigatória dos 10.

**Extensão a 25.** Se o gate de 10 passar, correr os 15 restantes em todos os braços restritos e controlos, e nos braços livres aprovados no sentinela. Não alterar código, modelo, prompt, sementes ou critérios após a primeira inferência. Persistir cada ação bruta e resultado por episódio.

### 5. Análise obrigatória e decisão seguinte

No ponto de paragem, relatar por categoria e no conjunto: relatório explícito, falha operacional, decisão, insuficiência, sensibilidade, especificidade, diagnóstico e localização com evidência, decisão certa sem localização, IDs de evidência e hipóteses escolhidos, consultas e custo, ganho esperado/real no conjunto de hipóteses e valor de contraste/replicação, confiança e calibração apenas nos relatórios explícitos. Apresentar contagens e incerteza por **episódio**, nunca tratar passos da mesma execução como observações independentes.

Comparar base e referência sob o mesmo contrato; comparar geração livre e restrita apenas nos braços em que ambas produziram ações válidas suficientes. Inspecionar casos em que o formato melhora sem melhorar a decisão. Os 25 mundos são desenvolvimento: uma melhoria nesse lote orienta o próximo desenho, mas não aprova M17 nem abre automaticamente as reservas. Não há fine-tuning neste bloco.

## Estado atual

M17 continua não aprovado. O G2 está preservado no ponto de análise; os conjuntos diagnóstico e de confirmação não foram abertos. Este documento define o bloco seguinte e os seus pontos de paragem automáticos; não inicia G2.1.

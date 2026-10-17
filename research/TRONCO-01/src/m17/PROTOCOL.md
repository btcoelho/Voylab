# M17-A/B — protocolo congelado

**Versão:** 0.1.2  
**Data de congelamento:** 2026-10-17  
**Objetivo:** medir se um agente consegue distinguir um sistema coerente de uma contradição, informação insuficiente, mudança contextual de regra ou mecanismo fora das hipóteses apresentadas.

## Revisão técnica e avaliativa (0.1.2)

Uma auditoria do avaliador encontrou dois problemas antes do diagnóstico. Primeiro, atingir o limite de ações sem um relatório explícito criava automaticamente `undetermined`, o que podia contar como reconhecimento correto de insuficiência. A versão 0.1.2 marca estes episódios como terminação forçada, contabiliza a decisão e o diagnóstico como incorretos e exclui-os do numerador de reconhecimento de insuficiência. Segundo, o agente LLM é reutilizado entre episódios; o estado de feedback agora é limpo no início de cada episódio.

Relatórios passam a validar os tipos e referências de códigos de hipóteses, IDs de evidência, localização e explicação. Evidências ou hipóteses inexistentes são ações inválidas e recebem feedback operacional. A versão acrescenta contagem de ações, taxa de ações inválidas, taxa de relatórios explícitos e terminações forçadas. As métricas e os controlos da versão 0.1.1 que dependam destas regras não são comparáveis sem recálculo.

O piloto técnico usa 10 mundos de cada uma das cinco categorias, amostrados de forma determinística entre as três sementes de desenvolvimento (50 episódios por agente). A amostra é emparelhada entre agentes e aleatória para o agente; a proporção não aparece no prompt. Critérios provisórios de prontidão: taxa de ações inválidas ≤1%, relatório explícito em ≥98% dos episódios e zero truncagens silenciosas ou contaminação entre episódios. São critérios técnicos para decidir se vale a pena avançar, não gates de competência científica. O piloto não substitui a avaliação completa de desenvolvimento nem abre diagnóstico, confirmação ou treino. Após os resultados, a execução para na análise obrigatória.

## Revisão técnica antes do diagnóstico (0.1.1)

Antes de qualquer avaliação de modelo, uma auditoria de prompts no conjunto de desenvolvimento encontrou 1.200 tokens no maior estado medido, acima do limite de entrada de 1.024 usado na versão 0.1.0. A versão 0.1.1 define limite de contexto de 2.048 tokens para o modelo base e o M16, desativa truncagem silenciosa e termina a execução com erro explícito se um estado exceder esse limite. Quando `max_new_tokens` é explícito, a chamada de geração define `max_length=None` para evitar o aviso herdado de `GenerationConfig.max_length`, em vez de o suprimir.

Esta revisão corrige a integridade da entrada e a configuração de geração antes de abrir a partição diagnóstica. Não altera mundos, sementes, partições, observações, hipóteses, orçamento de consultas, pontuação, métricas, limiares ou regras de treino. A avaliação diagnóstica mede a versão 0.1.1; resultados de qualquer versão anterior não são comparáveis. A confirmação permanece fechada.

## Âmbito e salvaguardas

O gerador M17 é independente do código e dos dados M16. O estado público não contém a categoria, família, semente, índice do mundo ou regra oculta. O agente recebe exemplos, um modelo de trabalho, três hipóteses candidatas permutadas e 12 consultas possíveis. Cada consulta consome uma unidade de um orçamento de três. O agente pode consultar ou apresentar um relatório final.

Os cinco estados ocultos são NORMAL, CONTRADIÇÃO, INSUFICIÊNCIA, MUDANÇA e HIPÓTESE AUSENTE. Cada mundo tem oito registos, incluindo uma repetição; todos têm o mesmo formato, comprimento fixo e número de registos. A ordem dos registos, consultas, hipóteses e identificadores é aleatória. Os quatro mecanismos geradores são `dev_table`, `relational`, `multiphase` e `compositional`.

As respostas são avaliadas por correspondência com registos e previsões verificáveis. Palavras como “erro”, “contradição” e “incerteza” não pontuam sem a evidência necessária. A contradição exige localizar a entrada repetida com saídas incompatíveis; a mudança exige evidência de efeito de fase e identificação do modelo condicionado; hipótese ausente exige efeito do parceiro e evidência de que nenhuma hipótese listada explica os dados; insuficiência exige pelo menos duas hipóteses compatíveis e abstenção; normal exige uma conclusão apoiada no modelo de trabalho e registos consistentes. Um mundo normal pode permanecer ambíguo entre hipóteses.

O avaliador audita cada mundo antes da inferência. A identificação de NORMAL, MUDANÇA e HIPÓTESE AUSENTE tem de ser possível a partir das observações e consultas permitidas; INSUFICIÊNCIA tem de permanecer irresolúvel pelas consultas disponíveis. Os resultados publicados são agregados por semente, família e categoria. Não são exportados rótulos, IDs ou respostas individuais.

## Partições e ordem de execução

1. **Desenvolvimento:** sementes 53001, 53003 e 53009, família `dev_table`; 20 mundos por categoria e semente. Apenas este conjunto pode orientar depuração e a intervenção de treino.
2. **Diagnóstico pré-treino:** sementes 64001 (`relational`), 64003 (`multiphase`) e 64007 (`compositional`); 20 mundos por categoria e semente. Executar controlos, modelo base e adaptador M16 antes de qualquer novo fine-tuning. Estas sementes não podem orientar alterações ao avaliador nem treino.
3. **Confirmação cega:** sementes 75011 (`relational`), 75013 (`multiphase`) e 75017 (`compositional`); 20 mundos por categoria e semente. Permanecem fechadas até o protocolo estar congelado e existir uma decisão documentada sobre intervenção. Não ajustar modelo, prompts, pontuação ou limiares após abrir esta partição.

Cada partição tem três avaliações independentes por mecanismo e 100 mundos em cada semente. A avaliação de diagnóstico já conta como avaliação independente do M16 e do modelo base. A confirmação só é usada para comparar uma intervenção previamente definida, caso M16 falhe.

## Controlos e métricas

Controlos obrigatórios: modelo base Qwen 2.5 0.5B Instruct 4-bit, adaptador M16, detetor estatístico de resíduos/contradição, política de consulta aleatória, política de consulta fixa e controlo simbólico ativo. O controlo simbólico usa apenas observações, hipóteses e consultas públicas; conhece a forma das tabelas candidatas e funciona como verificação de integridade/limite superior, não como referência independente de aprendizagem. As políticas simples recebem o mesmo estado público e orçamento. Sementes, ordem e distribuição de categorias são comuns entre agentes.

Métricas primárias, reportadas por semente e categoria com intervalos Wilson de 95%:

- Sensibilidade: problemas reais (CONTRADIÇÃO, MUDANÇA, HIPÓTESE AUSENTE) reportados como rejeitados.
- Especificidade: NORMAL reportado como apoiado.
- Reconhecimento de insuficiência: INSUFICIÊNCIA reportada como indeterminada.
- Localização: problema localizado com os IDs e a característica exigidos pelo mecanismo.
- Diagnóstico de cinco vias: diagnóstico correto e sustentado por evidência identificadora.
- Calibração: Brier e erro de calibração esperado em dez intervalos.
- Investigação: consultas médias, consultas redundantes e redução média da incerteza entre hipóteses compatíveis. A redução é reportada por consulta; não prova que a consulta tenha sido útil para mecanismos fora da lista.
- Ações inválidas: consultas ou relatórios que não respeitam o esquema.

Uma consulta conta como redundante para a métrica de informação quando não reduz a incerteza entre as hipóteses listadas. Este indicador não é interpretado como medida completa de descoberta de mecanismos ausentes; a evidência do efeito de parceiro é avaliada separadamente.

## Metas provisórias de passagem

Em cada uma das três sementes independentes, o agente tem de atingir simultaneamente:

- Sensibilidade ≥ 85%.
- Especificidade ≥ 90%.
- Localização ≥ 70%.
- Reconhecimento de insuficiência ≥ 70%.
- Diagnóstico sustentado ≥ 70% em cada categoria individual.
- Ações inválidas ≤ 1% das ações.

Além disso, a média de diagnóstico sustentado nas três sementes tem de superar o melhor controlo simples por pelo menos 10 pontos percentuais. Uma média global não pode compensar uma categoria abaixo do limiar. Os valores são metas provisórias: com 20 casos por categoria e semente, os intervalos são largos; serão mostrados integralmente e não serão tratados como prova automática de capacidade científica.

“Passagem” descreve apenas este benchmark textual sintético. Não demonstra compreensão histórica, competência visual, criptanálise ou capacidade de decifrar o Voynich.

## Regra de treino

Não realizar novo fine-tuning antes dos resultados comparáveis de base, M16 e controlos no diagnóstico. Se M16 cumprir todos os limiares, preservar o adaptador e aumentar a dificuldade em trabalho posterior. Se falhar, identificar a categoria/capacidade ausente e definir uma única intervenção usando exclusivamente desenvolvimento. Treinar num adaptador novo; não modificar M16. Registar dados, configuração e objetivo antes de abrir confirmação. A confirmação testa o adaptador novo contra M16 e base, sem alterações posteriores.

## Limites e auditoria

O resultado depende dos mecanismos artificiais especificados e das três hipóteses que o ambiente apresenta. Os geradores partilham representação de entrada e famílias de regras, embora a família de confirmação não apareça em desenvolvimento. Não existe componente de visão nesta versão. O relatório tem de listar falhas por categoria e semente, incluindo quando nenhum agente satisfaz as metas.

Hash do protocolo e dos scripts, inventário de artefactos M16 e resultados agregados serão registados no pacote reproduzível. O M16 e as suas reservas originais permanecem intactos.

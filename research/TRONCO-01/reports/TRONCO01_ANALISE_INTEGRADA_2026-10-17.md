# TRONCO-01 — análise dos testes, revisão científica e plano proposto

Data de referência: 17 de outubro de 2026. Estado: parecer e desenho experimental; TRONCO ainda não aprovado cientificamente.

Esta revisão responde aos entregáveis A–H do documento TRONCO-01. Foi feita por leitura do pedido, dos scripts, dos relatórios e dos três JSON do piloto M17. Um script separado reconstruiu os agregados e registou hashes dos ficheiros consultados. Não houve novas inferências, treino, execução de testes ou alterações aos protocolos, reservas, adaptadores ou código M17. O piloto de desenvolvimento já estava concluído; o diagnóstico dos modelos e a confirmação continuam por executar. As afirmações sobre os 14 testes referem-se à execução anterior.

## A. O que os testes concluídos demonstram

| Evidência existente | Conclusão sustentada | Conclusão que continua em aberto |
|---|---|---|
| Auditoria M16 reporta 100% em L4/L5 nas três sementes, sem ações inválidas | O adaptador executou uma política aprendida no contrato sintético original | Descoberta de problemas não anunciados e transferência para mecanismos diferentes |
| 14 testes unitários passaram na execução anterior | Os casos estruturais e regressões implementados passam | Correção completa do avaliador, integração real com os LLMs e competência científica |
| Base: 50 episódios, 500/500 ações inválidas, zero consultas e relatórios explícitos | Falha operacional na interface M17 utilizada | Capacidade de formular hipóteses, investigar e reconhecer inadequação |
| M16: os mesmos 50 episódios e o mesmo padrão de falha | A transferência operacional para essa interface falhou | Se o treino M16 melhorou ou prejudicou raciocínio científico |
| Controlos estatístico, aleatório e fixo: 24/50, 22/50 e 23/50 diagnósticos sustentados | Há soluções parciais simples; sensibilidade isolada não caracteriza o objetivo | Superioridade de uma arquitetura aprendida |
| Controlo simbólico ativo: 50/50, dez por categoria, sem ações inválidas | Uma política construída com conhecimento das formas públicas de tabela resolve esta amostra | Aprendizagem, descoberta autónoma ou validação independente dos mecanismos |
| Auditorias estruturais anteriores de 300/300 mundos em desenvolvimento e diagnóstico | O auditor programado aceitou as propriedades verificadas nesses mundos | Validade de todos os critérios científicos ou desempenho de um agente |

Os dois modelos receberam os mesmos 50 mundos de desenvolvimento, dez por categoria. A repartição total pelas sementes foi 19, 13 e 18. São três sementes de uma família de desenvolvimento; as 500 tentativas de cada modelo não constituem 500 experiências independentes.

O resultado do controlo simbólico é útil como verificação de integridade. Foi construído e corrigido durante o desenvolvimento, conhece as representações das hipóteses e usa auxiliares do mesmo ecossistema de código. Não é um teste externo ou independente. Os seus 50 acertos não aprovam o TRONCO e não provam que uma arquitetura híbrida aprenderá mecanismos novos.

### Limitações adicionais encontradas nesta revisão

1. **A intervenção de prompt proposta não foi executada.** O wrapper ainda envia apenas uma mensagem de utilizador com o estado em JSON. Esse estado já inclui `task` e `response_schema`; não falta uma descrição de tarefa. Porém, não foi testada a mensagem de sistema direta anteriormente proposta. A execução anterior deveria ter distinguido essa omissão das correções do avaliador. O piloto não isolou o efeito da clareza das instruções.
2. **Não foram preservadas as causas das ações inválidas.** Os agregados não distinguem falha de parsing, ação desconhecida, campo inválido, ID inventado ou resposta incompleta. A leitura do código e das amostras antigas não substitui os registos das 1.000 tentativas deste piloto. Repetir centenas de gerações sem essa informação desperdiça diagnóstico.
3. **A calibração guardada é artificial.** Em todas as sementes dos dois modelos, os JSON contêm `brier=0` e `ece10=0`. O avaliador atribui confiança zero aos relatórios automáticos e considera-os incorretos; o cálculo recebe essas respostas fabricadas e produz zero. Como nenhum modelo emitiu relatório, a sua calibração não foi medida. Numa nova versão, a calibração de respostas explícitas deve ser indefinida quando não existirem respostas, acompanhada de cobertura e falhas. Os episódios falhados continuam no denominador do desempenho global.
4. **Há inconsistências documentais de versão e replicação.** O protocolo 0.1.2 mantém uma frase histórica a dizer que o diagnóstico mede 0.1.1 e outra que descreve três avaliações por mecanismo. O desenho listado tem uma semente por família no diagnóstico. Estas frases não sustentam três réplicas por mecanismo.
5. **O gate de superioridade precisa de uma classificação inequívoca dos controlos.** Se o novo controlo simbólico de 100% entrar no termo “melhor controlo simples”, exigir mais dez pontos percentuais torna a passagem impossível. O próximo protocolo deve distinguir uma referência que verifica a resolubilidade de um comparador cuja superioridade se pretende medir. Não se deve reinterpretar retroativamente o resultado atual para obter passagem.
6. **Apoio, ambiguidade e insuficiência não estão suficientemente separados.** O protocolo permite apoiar um NORMAL ainda ambíguo, mas pede abstenção em INSUFFICIENCY. A possibilidade de uma consulta discriminante diferencia os mundos gerados, mas a regra científica sobre a evidência já recolhida precisa de ser explícita.

Estes achados são de leitura dos ficheiros, não resultados de novos testes. São recomendações para uma futura versão ou um protótipo isolado; o M17 preservado não foi modificado.

## B. Parecer crítico à luz de TRONCO-01

A revisão é cientificamente defensável como hipótese de arquitetura. O seu melhor contributo é mudar a unidade de avaliação: uma sequência de previsões, observações, conflitos e decisões verificáveis. Um diagnóstico final correto pode resultar de uma regra fixa; uma explicação verbal convincente pode ser inventada depois do resultado. A previsão comprometida antes da medição permite testar o que o agente realmente antecipou.

A arquitetura não é, por si só, evidência de capacidade. Memória pode preservar erros, verificadores podem partilhar os pressupostos errados do gerador, e uma seleção excelente entre hipóteses falsas continua a poder conduzir a conclusões erradas. A necessidade de seis funções não implica seis modelos, seis serviços ou uma árvore multiagente.

A triagem também exige objetivos e custos explícitos: uma observação improvável pode ser irrelevante para a tarefa. Fornecer critérios de relevância e de custo não equivale a anunciar um problema. Sem essa informação, não há necessariamente uma única decisão A/B/C correta; o protocolo deve admitir dúvida justificada em vez de avaliar apenas a preferência do autor do mundo.

| Competência TRONCO-01 | Cobertura atual |
|---|---|
| 1. Observar dados desconhecidos | Existe um canal público estruturado; integração dos modelos falhou no piloto |
| 2. Identificar regularidades | Há regras programadas e imitação M16 no domínio original; transferência não medida |
| 3. Separar normalidade de anomalia | Controlos cobrem casos artificiais; não há evidência de desempenho dos LLMs no M17 |
| 4. Formular hipóteses | M17 fornece hipóteses; não testa formulação aberta |
| 5. Fazer previsões antecipadas | Não existe ação obrigatória de previsão antes da consulta |
| 6. Reconhecer uma hipótese falhada | Controlos verificam resíduos; falta evidência de deteção pelo modelo |
| 7. Reconhecer inadequação do conjunto de hipóteses | Existe uma categoria sintética e um controlo capaz de a resolver; capacidade aprendida não demonstrada |
| 8. Formular perguntas e escolher experiências | M17 oferece um menu; não testa perguntas livres nem os modelos chegaram a consultar |
| 9. Reconhecer insuficiência e incerteza | O controlo simbólico resolve a amostra; modelos não emitiram decisões válidas |
| 10. Rever conclusões | Não há avaliação de revisões versionadas que melhorem previsões futuras |
| 11. Registar/submeter/investigar | Não implementado; os três veredictos M17 não equivalem a estas três decisões |
| 12. Responder a contestações | Não medido |
| 13. Manter memória científica | Há artefactos reproduzíveis, mas não uma memória de agente com previsões e justificações temporais completas |
| 14. Parar, continuar e suspender | Há limites de orçamento; isso não demonstra uma política competente de paragem |

O resultado atual não justifica novo LoRA. Também não prova que o modelo de 0,5B seja incapaz da tarefa científica, porque a falha acontece antes de qualquer ação válida. Uma referência de maior capacidade será necessária se, depois de uma interface funcional, a limitação dominante continuar a ser a formulação de hipóteses ou a decisão.

## C. Arquitetura mínima recomendada

Começaria por **um único LLM proponente, um núcleo verificável e uma memória de eventos**. Os seis componentes funcionais da revisão podem ser funções desse mesmo processo.

| Função | Entrada | Saída verificável | Responsabilidade principal |
|---|---|---|---|
| Observação | Dados brutos e contexto de medição | Registo imutável, descritores e alertas provisórios | Código e estatística simples |
| Hipóteses | Observações e pressupostos | Hipóteses executáveis, versões e previsões | LLM propõe; núcleo valida e calcula |
| Diagnóstico | Previsões anteriores e novos resultados | Resíduos, incompatibilidades, ambiguidades e estado de adequação | Verificador externo |
| Decisão/investigação | Estado epistémico, relevância, orçamento e consultas possíveis | REGISTAR, SUBMETER ou INVESTIGAR; consulta ou paragem justificada | Política simples inicialmente; LLM ajuda a propor ações |
| Memória | Todos os eventos | Proveniência e dependências reconstituíveis | Armazenamento de eventos e projeções |

O ciclo mínimo é: observar → propor hipótese verificável → calcular e registar previsão → selecionar medição → obter resultado → comparar → rever hipótese ou pressupostos → decidir continuar, registar ou submeter.

No TRONCO, o canal de ações pode ser explícito sem anunciar a existência de um problema. Conhecer a sintaxe de uma consulta é uma condição de operação; receber a regra oculta ou um catálogo que contém a solução é informação científica adicional e deve ser tratado como condição distinta.

### O componente mínimo para reconhecer que todas as hipóteses falharam

É necessário ter hipóteses que produzam previsões testáveis, evidência nova e um critério de adequação aplicado a cada hipótese. Num mundo sem ruído, pode bastar verificar se cada hipótese contradiz alguma observação. Com ruído, são necessárias distribuições preditivas ou tolerâncias calibradas, pressupostos sobre a medição e controlo dos falsos alarmes.

Normalizar probabilidades entre candidatos não verifica adequação absoluta: pode haver um candidato relativamente melhor e todos serem maus. Acrescentar apenas uma etiqueta “outro” também não resolve o problema se essa etiqueta não tiver semântica e critérios de evidência.

O estado deve dizer “o conjunto atual é inadequado nos testes executados”, nunca “nenhuma explicação possível existe”. Um único desvio pode ser ruído, erro de medição, contexto omitido, hipótese errada ou mudança do mecanismo. Se os meios disponíveis não distinguirem essas causas, a decisão correta pode ser SUBMETER com incerteza preservada.

Para escapar à seleção entre hipóteses falsas, o planeador deve incluir experiências de crítica do modelo e propostas de expansão do conjunto, além de experiências que discriminam candidatos existentes. Hipóteses novas são avaliadas em observações posteriores e em previsões reservadas; ajustar a mesma evidência que motivou a expansão não basta.

### Decisão e paragem

Separar três eixos: estado operacional, estado epistémico e ação de triagem. Uma falha de geração pertence ao primeiro; insuficiência de evidência pertence ao segundo; SUBMETER pertence ao terceiro. Não são intercambiáveis.

- **REGISTAR:** preservar observações e a base para não investigar agora, com condições explícitas de reabertura.
- **SUBMETER:** a evidência, relevância, disponibilidade de experiências ou custo não permite uma decisão autónoma justificada. Nesta fase, gera um pedido auditável, sem criar especialistas ou revisor operacional.
- **INVESTIGAR:** existe uma questão relevante e uma ação viável cujo benefício esperado justifica o custo.

A função de escolha deve aproximar a redução esperada da perda de decisão, descontando custo de medição e computação. Informação entre hipóteses é um substituto possível, não a utilidade final. Atingir um limite rígido termina operacionalmente a execução; não significa que a investigação concluiu. Quando a utilidade esperada não puder ser estimada, o sistema deve registar essa limitação e usar uma regra de orçamento previamente definida.

## D. Memória científica mínima

Proponho um diário de eventos com observações imutáveis e projeções de estado versionadas, compatível em espírito com entidades, atividades e agentes do PROV. Não é necessário implementar todo o padrão W3C. [PROV Overview](https://www.w3.org/TR/prov-overview/).

| Registo | Campos essenciais |
|---|---|
| Observação | ID, fonte, instante, entrada, resultado bruto ou referência e hash, unidade e pressupostos de medição |
| Hipótese | ID e versão, descrição, expressão executável, pressupostos, dados usados no ajuste, teste que a poderia refutar |
| Previsão | Versão da hipótese, entrada futura, valor/distribuição/intervalo, dados de ajuste, ordem temporal anterior à medição |
| Experiência | Ação, previsões que motivaram a escolha, custo esperado/real, orçamento restante, resultado associado |
| Avaliação | Previsão confrontada, observação, resíduo ou estatística, regra de avaliação e pressupostos |
| Decisão | Estado epistémico, ação A/B/C, evidências citadas, fundamento, regra de paragem/reabertura |
| Revisão/contestação | Hipótese anterior e posterior, dependências afetadas, novo teste, previsões cuja qualidade deverá melhorar |
| Falha operacional | Entrada e saída de inferência ou referências, causa de validação, tokens, término da geração, custo e tentativas |

As observações e previsões antigas não são reescritas. Uma revisão cria uma nova versão e invalida apenas conclusões dependentes dos pressupostos alterados. O histórico de um regime anterior pode continuar correto para esse regime. A ordem de eventos e a relação causal entre previsão e medição devem ser verificadas pelo núcleo, não apenas descritas pelo modelo. Um hash local auxilia a integridade, mas não é por si só prova independente de anterioridade.

A memória persistente entre mundos só pode existir numa condição experimental explícita de aprendizagem contínua. Nas restantes comparações, cada episódio começa isolado.

## E. Protocolo experimental proposto

Este desenho é novo e não altera critérios M17. O protocolo detalhado está num ficheiro separado. Há primeiro um gate operacional e depois três experiências científicas.

### Gate operacional — localizar a causa da falha

Instrumentar uma cópia isolada: prompt e template efetivos, identificação do checkpoint/adaptador, saída bruta, tokens de entrada/saída, término por EOS/limite, resultado do parser e motivo de rejeição. Reservar espaço para a resposta dentro do contexto total.

Começar por uma tarefa mínima de emitir uma ação conhecida e por um pequeno caso nativo M16. Depois comparar o prompt atual com uma instrução de sistema direta nos mesmos poucos casos de desenvolvimento. Usar um limite de repetição previamente definido para falhas de sintaxe, evitando novo piloto de centenas de tentativas sem informação nova. Não acrescentar simultaneamente memória, tradução de ações e descodificação restrita: cada intervenção deve ter condição própria.

**Checkpoint:** identificar a classe dominante de erro e demonstrar comunicação válida num ensaio limitado. Se a geração mínima falhar, investigar carregamento/template/parser; se funcionar e a investigação falhar, só então medir a competência. Um piloto de engenharia pequeno não demonstra uma taxa de erro populacional de 1%.

### Experiência 1 — descobrir quando a explicação deixou de ser adequada

Hipótese: um ciclo com previsões comprometidas e verificação externa distingue inadequação de ambiguidade e ruído melhor do que um LLM simples, sem aumentar os falsos alarmes.

Ambiente: mundos sem problema, hipótese inicial correta/incorreta, hipóteses equivalentes, conjunto inadequado, mudança de regra, ruído elevado e falta de informação. O agente recebe variáveis observáveis, dados e ações operacionais, sem rótulo de categoria ou indicação de que existe um problema. Em parte dos casos formula as próprias hipóteses; a condição de catálogo fornecido é uma ablação identificada.

Métrica principal: deteção justificada de inadequação do conjunto atual, acompanhada da previsão anterior falhada e de evidência localizada. Medir falsos alarmes em mundos normais/ruidosos, reconhecimento de insuficiência e previsões futuras. Verbalizar dúvida ou acertar num rótulo não pontua sozinho.

Interpretação: se apenas o verificador reconhecer falhas, atribuir a melhoria ao sistema composto. Se o LLM não conseguir propor hipóteses executáveis, essa é a limitação específica a resolver.

### Experiência 2 — investigar para distinguir ou refutar hipóteses

Hipótese: seleção ativa com crítica e expansão do conjunto melhora previsões em intervenções reservadas por unidade de custo, incluindo quando as hipóteses iniciais estão todas erradas.

Comparações: consultas ativas, aleatórias, fixas e nenhuma consulta; conjunto fixo versus expansão; orçamento total comum. A experiência que aumenta a certeza entre candidatos errados não conta como sucesso se piorar a previsão reservada. Separar recuperação do mecanismo, quando identificável, de equivalência preditiva dentro do domínio observado.

Métricas: perda preditiva em ações nunca realizadas, melhoria sobre política aleatória, descoberta de efeitos omitidos, consultas desnecessárias, custo e falsos anúncios de descoberta. Fazer previsões antes das observações, não ajustar a pontuação à explicação final.

Interpretação: se a escolha ativa não superar os controlos a custo igual, preferir a política mais simples. Se a expansão só ajustar os dados já vistos, não há evidência de descoberta útil.

### Experiência 3 — rever, parar e reabrir com memória auditável

Hipótese: memória com dependências e previsões melhora revisão e paragem sem propagar crenças antigas para contextos incompatíveis.

Ambiente: sequências com mecanismos estáveis, mudanças reais, falsos alertas de ruído e dados posteriores a um encerramento. Introduzir contestações sintéticas com evidência verificável. Reservar famílias completas e testar a transferência com uma instância nova, comparando memória permitida e memória reiniciada.

Métricas: melhoria preditiva após revisão, tempo/custo até reconhecer mudança, reaberturas justificadas, abandono de hipóteses contraditas, integridade das citações e de previsões anteriores, decisões A/B/C e paragens oportunas. Reescrever uma explicação depois do resultado não constitui revisão demonstrada.

Interpretação: se a memória piorar a adaptação ou aumentar falsas descobertas, reduzir ou abandonar essa forma de memória. Se as vantagens não transferirem entre famílias, limitar a alegação ao domínio em que foram observadas.

### Comparações A–G

| Condição | Configuração | O que permite estimar |
|---|---|---|
| A | Base, interface mínima, sem memória externa nem verificadores | Referência de modelo |
| B | M16 no contrato e ferramentas originais, quando tecnicamente aplicável | Recuperação/competência nativa; tarefas diferentes não dão comparação direta com A |
| C | Base + memória | Efeito da memória, com o mesmo orçamento |
| D | Base + verificadores | Efeito da verificação externa |
| E | Base + memória + verificadores | Efeito conjunto e interação entre componentes |
| F | M16 + os mesmos mecanismos externos de E | Efeito do adaptador sob ferramentas e tarefas equivalentes |
| G | Estatístico/simbólico | Referência simples e controlo de resolubilidade, com papéis separados |

Se B não puder agir no ambiente novo sem tradução semântica, registar “não aplicável nesse contrato”, preservar a recuperação nativa separadamente e comparar o adaptador em F. Uma tradução que formule hipóteses ou escolha a conclusão acrescenta capacidade ao sistema e deve ser avaliada como tal. Uma referência de maior capacidade em inferência pode ser acrescentada para testar a limitação do modelo, mantendo ferramentas e orçamento equivalentes.

Os sete braços não precisam de ser todos lançados em escala no primeiro dia. Começar pelo desenho fatorial A/C/D/E e G, acrescentando M16 onde a interface for funcional. Reportar tokens, chamadas, consultas, chamadas do verificador, tempo e custo: igualar apenas o número de chamadas LLM não iguala o orçamento.

### Aprovação e generalização

As três avaliações independentes exigidas pela revisão devem ser operacionalizadas antes de executar: famílias/grupos de mecanismos reservados, cada qual com replicações e sementes próprias. Três sementes de uma única família não bastam para demonstrar transferência; uma semente por família não estima separadamente variação de semente e família.

O M17 diagnóstico e confirmação partilham as famílias listadas e diferem nas sementes; isto não é uma reserva de famílias inteiramente novas entre essas fases. Os testes estruturais também conhecem essas formas. O novo protocolo deve explicitar quem tem acesso às regras e que generalização se pretende provar.

Como propostas para TRONCO-01, a fixar antes dos novos resultados: limite superior de 95% para falsos alarmes ≤5%; limite inferior de 95% para deteção justificada de inadequação ≥80%; reconhecimento de insuficiência ≥70% como limite inferior; nenhuma violação de anterioridade ou evidência inventada; benefício de investigação positivo a custo igual em cada avaliação reservada. Dimensionar amostras para esses objetivos e corrigir a análise para dependência e multiplicidade. Estes valores são escolhas de desenho e risco, não conclusões da literatura nem gates aplicados a M17.

Calibração só sobre previsões/respostas realmente emitidas, com cobertura e falhas operacionais reportadas em separado. Não excluir episódios falhados do desempenho global. Falhas persistentes em problemas reais ou falsos alarmes bloqueiam progressão; uma média global não compensa uma família deficiente.

## F. Revisão científica e reutilização

### Fundamentos clássicos

As aplicações abaixo são hipóteses de engenharia. Os artigos não demonstram automaticamente um TRONCO competente.

| Referência verificada e acesso | Contributo operacional proposto | Limite |
|---|---|---|
| Tukey, *Exploratory Data Analysis* (1977), Addison-Wesley; [catálogo](https://search.worldcat.org/title/exploratory-data-analysis/oclc/3058187) consultado, livro integral não obtido | Exploração inicial e registo de regularidades sem impor um mecanismo | Explorar não confirma hipóteses; a verificação bibliográfica não equivale a uma leitura integral |
| [NIST/SEMATECH Handbook](https://www.nist.gov/programs-projects/nistsematech-engineering-statistics-handbook), incluindo [cartas de controlo](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3.htm) | Baselines de variabilidade, medição e sinais de alteração | Um sinal estatístico é condicionado pelos pressupostos e não identifica a causa |
| Reiter (1987), *A Theory of Diagnosis from First Principles*, AI 32:57–95; [texto](https://cse.sc.edu/~MGV/csce580f12/gradPres/reiter-diagnosis.pdf), DOI 10.1016/0004-3702(87)90062-2 | Representar conflitos entre observações, modelo e pressupostos; procurar diagnósticos alternativos | Parte de uma descrição do sistema. Descobrir uma descrição desconhecida requer mecanismos adicionais |
| Platt (1964), *Strong Inference*, Science 146:347–353; [texto](https://worthylab.org/wp-content/uploads/2019/05/platt1964.pdf) | Exigir alternativas e experiências que possam excluí-las | Método de investigação, sem garantia de que as alternativas propostas incluam um modelo adequado |
| Chaloner e Verdinelli (1995), *Bayesian Experimental Design: A Review*, Statistical Science 10:273–304; [resumo técnico dos autores](https://www.stat.cmu.edu/tr/tr599/tr599.html), DOI 10.1214/ss/1177009939 | Escolher medições por utilidade esperada, tratando parâmetros e previsões como incertos | O desenho depende do modelo, prior e utilidade; discriminação não substitui crítica de adequação |
| Alchourrón, Gärdenfors e Makinson (1985), *On the Logic of Theory Change: Partial Meet Contraction and Revision Functions*, JSL 50:510–530; [DOI](https://doi.org/10.2307/2274239), [bibliografia do autor](https://sites.google.com/site/davidcmakinson/) | Separar revisão, contração e dependências; preservar o que não depende do pressuposto rejeitado | Acesso integral não obtido nesta revisão. Não proponho uma implementação formal completa de AGM nem identifico consistência lógica com adequação estatística |
| Doyle (1979), *A Truth Maintenance System*, [MIT AIM-521](https://dspace.mit.edu/entities/publication/5377b306-4ecc-4687-b1f5-78cbb4a0543a) | Associar razões e pressupostos às conclusões e reavaliar dependências | Um gestor de razões preserva justificações, mas não assegura que sejam empiricamente verdadeiras |
| de Kleer (1986), *An Assumption-Based TMS*, AI 28:127–162; [texto do autor](https://dekleer.org/Publications/An%20Assumption-Based%20TMS.pdf) | Manter contextos alternativos e conclusões condicionadas a pressupostos | A gestão completa de contextos pode ser desnecessária e cara no protótipo; começar com dependências explícitas simples |
| Wald (1945), *Sequential Tests of Statistical Hypotheses*, AMS 16:117–186; [DOI](https://doi.org/10.1214/aoms/1177731118) | Inspirar decisões sequenciais e limites de evidência | O texto integral não ficou acessível. Não aplicar um SPRT clássico a ruído/dependência/consultas adaptativas sem justificar o modelo probabilístico e os limites de erro |
| Russell e Wefald (1991), *Do the Right Thing: Studies in Limited Rationality*; [editora](https://mitpress.mit.edu/9780262181440/do-the-right-thing/) | Comparar o benefício esperado de mais investigação com o custo de a executar | Acesso à descrição editorial; uma utilidade estimada é uma hipótese a validar, não um oráculo de paragem |
| W3C, [PROV Overview](https://www.w3.org/TR/prov-overview/) | Relacionar observações, agentes, atividades e artefactos derivados | Proveniência não verifica a verdade da conclusão; o esquema local proposto não implementa todo o padrão |
| Sandve et al. (2013), *Ten Simple Rules for Reproducible Computational Research*, PLoS CB 9:e1003285; [texto](https://www.chem.ucla.edu/dept/Faculty/merchant.html/pdf/ten_simple_rules.pdf) | Arquivar versões, parâmetros, sementes e resultados intermédios | Reprodutibilidade permite examinar uma falha; não transforma um avaliador errado numa validação |
| Yao et al., *ReAct* (ICLR 2023); [artigo](https://arxiv.org/abs/2210.03629) | Ciclo de raciocínio e ação com observações externas | Os resultados das tarefas estudadas não provam descoberta científica aberta |
| Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet* (ICLR 2024); [artigo](https://arxiv.org/abs/2310.01798) | Comparar autocrítica verbal com correção apoiada por evidência externa | Os resultados são dos modelos e tarefas avaliados; o título não é um teorema universal sobre todos os modelos atuais |

Reiter, Platt, AGM/TMS e valor da informação podem orientar mecanismos concretos. A integração mais simples é previsão executável + comparação + dependências + ação sob orçamento. Um motor lógico universal, ATMS completo ou inferência probabilística aninhada não são requisitos iniciais. O erro dominante precisa de justificar cada acréscimo.

### Trabalhos recentes solicitados: identificação, resultados, código e aplicação

**Model Discovery Agent — Kevin Murphy (2026).** Preprint [arXiv:2608.09696v5](https://arxiv.org/html/2608.09696v5), revisão de 27/09/2026. Combina propostas LLM, expansão do espaço de modelos, desenho por valor de informação e inferência Bayesiana aproximada. Relata maior eficiência amostral em ambientes mecanísticos; a v5 enfatiza química, glicose e neurónios. São resultados dos autores, não reproduzidos aqui. Os simuladores [NeuronBench](https://github.com/murphyk/neuronbench) e GlucoseBench estão ligados no artigo; confirmei MIT para NeuronBench, mas não um pacote completo licenciado de todo o agente. Aproveitamento: separar proposta de hipóteses e verificação. Teste: conjunto fixo versus expansão, mesmo LLM e orçamento, perda preditiva em intervenções reservadas. A inferência avançada e os simuladores podem ser mais complexos do que precisamos inicialmente.

**LLM-AutoSciLab — Kabra, Abhyankar, Desai, Iyer e Reddy (2026).** [Artigo](https://arxiv.org/pdf/2605.24043) e [implementação oficial](https://github.com/scientific-discovery/LLM-AutoSciLab). Autores anunciam aceitação NeurIPS 2026; consultei artigo e páginas oficiais, não proceedings. Hipóteses orientam experiências e refinamento. Reportam 67,6% de acerto simbólico em NewtonBench, 35,1% em química e 31,1% de recuperação exata de grafos; ganhos de 2–5 vezes referem-se a consultas, não ao custo computacional total. Código disponível; licença geral explícita não confirmada nesta revisão. Aproveitamento: interfaces e ciclos de aquisição. Teste: reprodução mínima seguida de ablação sem seleção por hipóteses. Os resultados permanecem limitados aos domínios e mecanismos avaliados.

**WorldZero.** [Repositório oficial](https://github.com/skishore23/worldzero), instrumento de investigação alpha 0.3.0, licença Apache-2.0. Não identifiquei uma publicação revista por pares. Usa leis ocultas, mundos nulos correspondentes e intervenções reversíveis. A evidência ilustrativa é de políticas programadas; o próprio projeto distingue-a de resultados de descoberta por modelos. Aproveitamento: fronteira público/oculto, replay, controlos negativos e contabilização. Teste: reproduzir controlos e depois substituir a política programada por um agente sem acesso à lei. É particularmente próximo da identificação não anunciada de mecanismos, mas maturidade e generalização continuam a exigir verificação.

**BoxingGym — Gandhi et al. (2025).** [Preprint](https://arxiv.org/abs/2501.01540) e [código MIT](https://github.com/kanishkg/boxing-gym). Avalia experiências e modelos em dez ambientes probabilísticos. Usa ganho esperado de informação e capacidade preditiva; relata dificuldades dos LLMs e ausência de melhoria consistente ao acrescentar um modelo estatístico explícito. Aproveitamento: API, ambientes e avaliação por consulta. Teste: reproduzir um domínio simples com políticas aleatória e ativa a orçamento comum, seguido de uma família reservada. Conhecimento prévio de famílias probabilísticas e adequação do modelo limitam a interpretação de descoberta aberta.

**NewtonBench — Zheng et al. (ICLR 2026).** [Artigo](https://arxiv.org/abs/2510.07172) e [código MIT](https://github.com/HKUST-KnowComp/NewtonBench). Contém 324 tarefas em doze domínios com leis contrafactuais. Os autores reportam fragilidade perante complexidade e ruído e que ferramentas podem prejudicar alguns modelos. Aproveitamento: avaliação externa de leis não convencionais e perturbações. Teste: comparar interface mínima e ferramentas a custo igual; separar acerto preditivo e lei recuperada. Não cobre por si só triagem A/B/C, e as instruções e famílias do benchmark não devem entrar no treino se forem usadas como reserva.

**ExplorationBench — Zhang et al. (2026).** [Preprint v2 de 08/10/2026](https://arxiv.org/abs/2609.30199) e [página oficial](https://explorationbench.com/). Dois ambientes executáveis, AlienCode e AlienLogic, separam exploração e aplicação em tarefas reservadas. Os autores observam aquisição de regras e trajetórias em que explorar mais estagna ou perde ganhos. A página oficial diz que as tarefas não são públicas; não confirmei código/tarefas disponíveis nem licença reutilizável. Aproveitamento imediato: desenho experimental e medição de transferência. Teste: reprodução quando houver acesso, ou desenho independente inspirado na separação entre exploração e teste. Não contar com integração imediata a partir de notícias que o descrevem como aberto; reportar médias e dispersão, não só a melhor trajetória.

**Prioridade para poupar trabalho:** estudar MDA como referência de arquitetura; avaliar BoxingGym para um primeiro ambiente reutilizável; avaliar WorldZero para controlos nulos e replay; reservar NewtonBench para transferência externa. LLM-AutoSciLab merece uma reprodução limitada após clarificar licença e dependências. ExplorationBench fornece agora uma metodologia, sem disponibilidade confirmada para integração local.

## G. Integração, desenvolvimento e checkpoints

| Ordem | Tarefa pequena proposta | Artefacto/critério de saída |
|---|---|---|
| 0 | Preservar M16/M17 e registar a evidência atual | Hashes e limitações, sem reclassificar o piloto como teste científico |
| 1 | Instrumentar uma cópia isolada e recuperar o contrato nativo | Classes de erro, saída efetiva e pequeno ensaio funcional; checkpoint obrigatório antes de escalar |
| 2 | Implementar diário de eventos, previsões e avaliador determinístico | Replay estrutural e validação de anterioridade; ainda sem alegação de aprendizagem |
| 3 | Ligar um LLM proponente e executar desenvolvimento da experiência 1 | Hipóteses verificáveis e falsos alarmes medidos; bloquear expansão se a triagem falhar |
| 4 | Fazer ablações A/C/D/E/G e decidir a referência de modelo | Atribuição explícita da melhoria ao modelo, memória ou ferramentas |
| 5 | Acrescentar investigação ativa, expansão e paragem | Experiências 2 e 3 com custos e previsões reservadas |
| 6 | Congelar protocolo e executar três avaliações independentes | Famílias reservadas, replicações e relatório completo de falhas |
| 7 | Considerar treino apenas para uma lacuna específica demonstrada | Dataset de desenvolvimento, controlo sem treino, regressão e transferência pré-definidos |

Para treino eventualmente justificado, preferir exemplos da competência em falta: gerar uma hipótese falsificável, antecipar uma consequência ou corrigir uma hipótese após uma previsão falhada. Avaliar a melhoria dessa competência contra a mesma arquitetura sem treino. Trocar de modelo se uma referência mais capaz, com as mesmas ferramentas, resolver de modo consistente a limitação que o modelo atual mantém. Não há evidência suficiente para definir épocas ou tamanho de dataset agora.

A RTX 4070 de 12 GB permite investigação local, mas VRAM, contexto, quantização e custos do verificador têm de ser medidos no piloto. O modelo de 0,5B não deve ser tratado como limite superior do raciocínio disponível. Memória e verificadores podem funcionar fora da GPU. Não proponho treino de especialistas, revisor ou sistema multiagente nesta fase.

Abandonaria ou reformularia a estratégia específica se: o benefício das ferramentas desaparecer quando custos e informação forem igualados; falsos alarmes persistirem em mecanismos novos; revisões só melhorarem o ajuste histórico; ou os ganhos se limitarem ao gerador conhecido. Isso reprovaria a configuração ou a alegação correspondente, não provaria a impossibilidade geral do objetivo.

## H. Recomendação e estado de progresso

Recomendo avançar para um protótipo híbrido mínimo e isolado, usando a falha operacional M17 como um problema a diagnosticar com poucas chamadas instrumentadas. O investimento seguinte deve produzir previsões anteriores às observações e decisões reconstituíveis. A evidência ainda não justifica novo LoRA nem a construção de níveis superiores.

Entregáveis de análise A–H: 8/8 documentados nesta etapa (100% desta tarefa documental), com limitações de acesso às fontes declaradas. Novo software de agente TRONCO-01 implementado nesta etapa: nenhum; apenas análise de ficheiros existentes e desenho/schema propostos. Competências TRONCO integralmente aprovadas por validação científica adequada: 0/14. Isto mede gates de demonstração, não a ausência de componentes aproveitáveis. A percentagem global de implementação do projeto não é estimável sem um plano de trabalho ponderado; os antigos 35% do M17 não se transferem para o novo âmbito.

O caminho mais curto para responder à pergunta central é exigir uma sequência auditável: hipótese que poderia falhar, previsão feita antes da medição, observação externa, revisão com ganho preditivo futuro e decisão de continuar ou parar sob custo. A capacidade fica demonstrada apenas quando essa sequência funciona também em casos normais, ruidosos, ambíguos e em famílias que não orientaram o desenvolvimento.

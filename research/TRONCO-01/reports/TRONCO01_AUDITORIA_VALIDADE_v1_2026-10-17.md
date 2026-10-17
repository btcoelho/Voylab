**TRONCO-01/M17/G2 — auditoria delimitada da validade, v1**

Data: 17/10/2026. Decisão: **a tarefa precisa de redefinição operacional; o instrumento atual permanece inapto para iniciar outro ensaio de modelo.**

A pergunta central não recebe um sim geral: o sistema verifica referências e algumas
relações observacionais, mas não separa de forma fiável sustentação científica,
legalidade, identificação e rótulo gerador. Há falsos negativos, falsos positivos e
dependência da ordem das linhas no pontuador. Um núcleo independente e limitado foi
construído para tornar esses problemas verificáveis; não foi integrado na produção.

**1. Base empírica e preservação**

Foram inventariados 44 artefactos selecionados: pedido original,
fontes, protocolos, pré-registos, agendas e registos G1 v0.2/G2, além de resultados
agregados de desenvolvimento M17. Os 11 hashes de fonte enumerados no pré-registo G2
coincidem com os ficheiros atuais; a agenda coincide com o hash declarado. Os ficheiros
históricos monitorizados permanecem inalterados.

Foram reconstruídas 235 execuções por condição em
30 mundos de desenvolvimento, não 235 amostras independentes.
As pontuações dos 178 relatórios explícitos foram reproduzidas
exatamente. As respostas de consultas registadas coincidiram com o replay. Isso confirma
consistência entre fontes preservadas, registos e agregação; não valida a regra científica.

Os 30 hashes de prompt de ações de modelo G2 e as contagens de entrada coincidiram com
reconstruções usando o tokenizer fixado. São reconstruções verificadas por hash, não
ficheiros originais de prompts/tokens. `raw` já foi descodificado com remoção de tokens
especiais. Não existem streams completos de tokens nem prova independente do momento
do freeze/da identidade binária dos pesos executados. O pré-registo não substitui essa
proveniência. Os resultados agregados M17 não permitem reconstruir saídas do modelo que
não foram guardadas. A ausência de summary.json G2 completo é coerente com a paragem
no sentinela; sentinel_summary.json e os registos estão preservados.

Não se leram datasets/gabaritos M17 de diagnóstico ou confirmação, não se instanciaram
geradores dessas partições e não se carregaram pesos. As chamadas de geração presentes
nos testes são doubles em memória, com tensores artificiais e texto fixo. Foram usados
apenas mundos de desenvolvimento já executados, fixtures manuais e interpretações
contrafactuais explicitamente identificadas. As três sementes por mecanismo referidas
no protocolo não correspondem ao desenho listado: há uma semente por família reservada;
esta observação usa apenas o texto do protocolo, sem abrir essas famílias.

**2. O alvo que falta definir**

`SPEC.md` distingue três perguntas: (a) W é compatível com o histórico? (b) W foi
identificado entre candidatos? (c) os candidatos sobreviventes concordam nas previsões
num domínio D explicitamente declarado? As três podem produzir respostas diferentes.
Compatibilidade não prova verdade universal; ambiguidade entre modelos não implica
ambiguidade preditiva no menu; refutar W não exige identificar uma alternativa única.

No próprio gerador, NORMAL começa ambíguo e admite uma consulta discriminante. CHANGE
também começa com W e o modelo de phase compatíveis. O pontuador espera supported para
NORMAL e rejected para CHANGE; o prompt G2 manda undetermined com vários candidatos.
A instrução e o critério não são a mesma pergunta.

Foi construído um gémeo contrafactual de um CHANGE G2 já executado, mantendo todos os
dados públicos e usando W como interpretação normal alternativa. Ambos passam as
verificações estruturais de identificabilidade do gerador. Três consultas com respostas
comuns esgotam o orçamento e deixam os estados públicos idênticos, mas o pontuador exige
veredictos diferentes. O par não é uma colisão observada entre duas sementes sorteadas;
é um contraexemplo explícito entre duas interpretações permitidas pelas tabelas e pelo
auditor. Inicialmente existiam consultas discriminantes. Portanto, não demonstra que
uma política ótima nunca poderia resolver os mundos. Demonstra que julgamento final
justificado e qualidade de aquisição de informação precisam de medidas separadas.

Sem especificar a afirmação, não existe um único avaliador correto para todos estes
sentidos de supported/undetermined. A referência devolve os sentidos separadamente e
o conjunto de veredictos defensáveis sob cada interpretação. Não usa categoria oculta.

**3. Defeitos e escolhas de especificação**

| ID | Classificação | Comportamento observado | Correção mínima proposta |
|---|---|---|---|
| F01 | defeito demonstrado | CONTRADICTION exige todos os IDs do primeiro grupo de conflito | procurar qualquer par contraditório efetivamente citado |
| F02 | defeito demonstrado | primeiro conflito/par de phase/partner encontrado condiciona a pontuação | avaliar existência de testemunho entre as evidências citadas, não exigir o primeiro testemunho interno |
| F03 | defeito demonstrado | CHANGE/HYPOTHESIS_ABSENT verificam feature mas ignoram location.value | validar o valor contra o testemunho citado e declarar que tipo de localização se avalia |
| F04 | defeito demonstrado | INSUFFICIENCY aceita candidatos extras se acertam apenas o subconjunto de linhas citado | conferir a declaração contra todo H e os candidatos que continuam compatíveis |
| F05 | divergência de contrato demonstrada | gramática e validador permitem qualquer objeto em location | schema canónico apenas para estrutura/proveniência e validação semântica separada; permitir respostas erradas para medir erros |
| F06 | comportamento demonstrado, impacto parcialmente observado | fallback extrai objeto de texto extra; json.loads conserva última ocorrência de uma chave repetida | decodificador que recuse duplicatas/números não finitos/texto exterior, preservando o original; regra nova versionada |
| F07 | defeito de verificação demonstrado | preflight testa apenas primeiro query_id e incrementa contador para todos com condição tautológica | exercer cada caminho e terminar no EOS; testar proibições e estados após consultas |
| F08 | lacuna processual demonstrada; alteração histórica não demonstrada | main G2 confere flags do pré-teste; preflight compara agenda, mas não valida todos os hashes de fontes/pesos antes de carregar | verificação de hashes na fronteira de execução e diário de proveniência; não inferir cronologia só de status textual |
| F09 | risco reproduzido por injeção de falha | evento bruto é anexado só depois de aplicar a ação; uma saída não tratada pode preceder a gravação | evento bruto independente antes de parsing/aplicação, depois eventos derivados com sequência |
| F10 | defeito demonstrado na agregação M17; G2 já tem mitigação | summarize M17 inclui terminações forçadas com confidence=0 e acerto falso no Brier | calibrar apenas previsões explícitas com evento-alvo declarado e reportar cobertura |
| S11 | especificação incompatível entre camadas | NORMAL aceita suporte ambíguo; prompt G2 exige undetermined se múltiplos candidatos; CHANGE é refutado pelo rótulo mesmo antes de evidência discriminante | declarar a afirmação julgada e separar compatibilidade de W, alternativas, previsões em D e qualidade das consultas |
| S12 | especificação discutível, não atribuição causal demonstrada | helper de phase permite partner/setting diferentes; phase não é eixo temporal; lista vazia não identifica uma causa única | nomear o que se demonstra, explicitar pressupostos e não avaliar causalidade que o desenho não identifica |

`results/findings.json` contém, para cada entrada, regra pretendida, comportamento,
contraexemplo, impacto histórico demonstrado ou desconhecido, proposta e âncora de fonte.
`results/counterexamples.json` guarda fixtures e resultados completos.

O impacto mais direto no material publicado é F02: **oito dos 25 relatórios do controlo
simbólico G1 e dois dos cinco do G2 mudam de pontuação quando se invertem/ordenam as
mesmas observações**. O relatório, IDs e valores não mudam. Não é incerteza amostral nem
uma nova execução do agente. Os 100% históricos desse controlo dependem de uma escolha
de testemunho pelo pontuador, em vez de uma regra invariante de validade da evidência.

Um exemplo M17 de terminação forçada produz Brier=0/ECE=0 sem uma previsão explícita.
Essa é uma falha de agregação M17; G2 já filtra calibração por relatórios explícitos.
Mesmo aí, confidence precisa de um evento-alvo definido para se interpretar calibração.

**4. Gramática, parsing e pré-teste**

Foram verificados 165 caminhos completos de consulta,
incluindo EOS, em 20 estados reconstruídos dos cinco mundos
G2 executados; os cinco estados sem orçamento recusaram o ramo query. Identificadores
inventados e campos exteriores extra foram recusados. Este é um resultado saudável.

Em contraste, a gramática e o validador aceitaram location vazio ou com campos
arbitrários, apesar da forma feature/value anunciada. O parser histórico também pode
recuperar um objeto de texto exterior. A injeção com um gerador simulado reproduz essa
aceitação; não foi encontrada ação aceite nos registos que dependesse de extração de
prosa. Há um caso real diferente: g2_insufficiency_1 repete a chave site dentro de
location. Foi marcado strict_json=true e aceite; a referência recusa essa interpretação
ambígua. Rejeição de chaves repetidas é uma política explícita de leitura inequívoca.

O pré-teste G2 verificou um ID de consulta por mundo e depois contou todos através de
uma condição que só confirma que um elemento da lista está na própria lista. O relatório
G2 já reconhecia a auditoria posterior dos 300 IDs. Essa correção posterior não torna a
verificação original pré-inferência. Um prefixo incompleto também pode ser alcançável
sem permitir EOS: a auditoria distingue agora essas duas propriedades.

Não se deve resolver isso obrigando o descodificador a produzir a conclusão correta.
O teste novo mantém respostas erradas/evidência vazia como ações potencialmente legais
e mede sustentação numa camada diferente. A localização proposta e a unicidade de IDs
são regras de representação/proveniência, sem seleção automática do diagnóstico.

**5. Referência e testes dos testes**

A referência importa apenas copy, itertools, json, jsonschema, math. Não reutiliza
preditores, conjuntos compatíveis, testemunhos ou pontuadores de produção. As três
formas públicas de tabela são interpretadas por um contrato literal explícito.
A enumeração compara os resultados com vetores de verdade indexados diretamente,
não com a mesma função sob outro nome.

- 10368 estados públicos finitos e 62208 verificações de afirmações, sem divergências.
- 27 testes de referência/integração passaram; incluem propriedades Hypothesis, sequências de consultas, reset, orçamento, terminação, ordem, renomeação de IDs, duplicatas, evidência e parsing.
- Quatro leis desejáveis falham por asserção no código histórico preservado, sem erro de infraestrutura; os seus logs vermelhos estão incluídos.
- Onze mutações não equivalentes foram detetadas por falhas de asserção. O controlo equivalente `len(rows)==0` versus `not rows` sobre listas sobreviveu. Nenhum sobrevivente relevante ficou por explicar neste painel.
- Reprodução numa diretoria temporária com fontes copiadas: passou os quatro comandos esperados. Essa reprodução elimina dependências dos caminhos das fontes vivas, mas continua na mesma máquina e com o mesmo operador.

O painel de mutações é direcionado e transparente, não uma campanha automática sobre
todo o projeto. As mutações foram feitas em cópias do núcleo de referência. O pontuador
histórico já falha quatro leis de base; não se atribui uma taxa de mutações válida a
uma bateria de aceitação cujo baseline está vermelho. A suíte unitária M17 original
foi lida e incluída como evidência; os seus testes geradores não foram reexecutados e
os antigos totais de testes PASS não são certificados por esta auditoria. Z3 não
acrescentava poder necessário aos contraexemplos e ao domínio
finito escolhido, pelo que não foi usado. A enumeração não cobre ruído, causalidade,
modelos abertos, linguagem natural ou todos os estados/bugs possíveis.

**6. Reanálise retrospectiva — não substitui os resultados históricos**

As colunas seguintes distinguem o rótulo histórico de dois alvos explícitos.
As comparações alternativas só usam relatórios realmente emitidos; as falhas continuam
identificadas no denominador total. A correspondência de um veredicto não exige, nesta
tabela, que o seu testemunho seja suficiente.

| Condição | Episódios | Relatórios explícitos | Acertos categóricos históricos | Veredicto compatível com ajuste observado | Veredicto compatível com identidade de W |
|---|---:|---:|---:|---:|---:|
| G1 base schema | 25 | 25 | 9 | 9 | 7 |
| G1 M16 schema | 25 | 24 | 4 | 12 | 1 |
| G2 base schema | 5 | 4 | 0 | 2 | 0 |
| G2 ponte G1 | 5 | 5 | 2 | 3 | 2 |
| G1 detetor estatístico | 25 | 25 | 15 | 25 | 10 |
| G1 simbólico | 25 | 25 | 25 | 20 | 25 |

Por exemplo, o detetor estatístico G1 acerta as 25 decisões de ajuste observacional,
mas só 15 rótulos históricos. O controlo simbólico acerta as 25 decisões de identidade,
mas dá undetermined em cinco estados onde W continua observacionalmente compatível.
Isto não elege um comparador vencedor: mostra que as métricas julgam afirmações diferentes.

Para o base G2, dois dos quatro veredictos explícitos coincidem com compatibilidade
observacional; **nenhum dos quatro tem sustentação por evidência citada**. As localizações
também violam a forma anunciada. A truncagem e a falha do braço livre continuam reais.
Esta auditoria não converte o G2 num sucesso nem demonstra incapacidade geral do modelo.
O gate histórico falhou e a paragem foi adequada.

Os novos contadores de localização tratam apenas contraste observacional direto.
Não são substitutos das pontuações históricas de localização por seleção de modelo.
Contagens, XMLs e perfis por episódio estão disponíveis; nenhuma reanálise é uma nova
confirmação, comparação causal entre prompts ou estimativa populacional.

**7. Decisão e ponto de análise obrigatório**

**A tarefa precisa de redefinição operacional.** O instrumento atual fica inapto para
nova inferência. A razão central é o alvo de conclusão não ser estável entre protocolo,
prompt e pontuador; reparar apenas location ou mudar de modelo não resolve esse problema.

A redefinição mínima é explicitar o objeto da conclusão: compatibilidade de W,
identificação entre hipóteses ou previsão em D. Diagnóstico deve conter testemunhos
verificáveis, sem confundir phase contextual com mudança causal. Qualidade de consultas
e sustentação do relatório final precisam de avaliação separada. As correções F01–F10
podem então ser derivadas dessa especificação e integradas numa versão nova, sem alterar
os resultados históricos. Não é necessária uma arquitetura maior para fazer isso.

O núcleo de referência é um instrumento de auditoria finito, não um agente aprovado.
Para autorizar um pequeno ensaio posterior, é preciso fechar a semântica pública,
integrar uma versão nova e reproduzir a aceitação/verificação de testemunhos, incluindo
os testes negativos. A presente execução termina aqui, antes de qualquer inferência.

O pacote permite a outra pessoa conferir exemplos, resultados e versões. Não houve
revisão por pessoa/equipa externa nem prova universal. Independência de implementação
não elimina pressupostos partilhados pelo autor. As conclusões sobre o benchmark
sintético não são conclusões sobre o manuscrito Voynich.

**Entregáveis e reprodução**

SPEC.md contém a especificação, reference_core.py a referência, results/inventory.json
o inventário/proveniência, results/findings.json os achados, results/counterexamples.json
os testemunhos e README.md os comandos de reprodução. SHA256SUMS.txt permite conferir o
conteúdo do pacote. Dependências diretas e runtime opcional estão fixados em ficheiros
separados. O relatório e a especificação também foram entregues separadamente em outputs.

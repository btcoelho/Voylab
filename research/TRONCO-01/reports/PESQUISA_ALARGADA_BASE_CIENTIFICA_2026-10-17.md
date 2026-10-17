# Alternativas para o núcleo científico do TRONCO-01/M17

Pesquisa concluída em **17 de outubro de 2026**. A recomendação é uma decisão de triagem, não uma aprovação científica dos candidatos.

## Conclusão

Há alternativas recentes que merecem prioridade sobre mais trabalho no AutoSciLab: **MechBench** para avaliação de mecanismos, **HypoSpace** para conclusões não únicas, **ALF** para seleção de experiências e **Autonomous Science Bench** para laboratório com orçamento e avaliação separada. POPPER e DoWhy acrescentam métodos estatísticos e causais especializados. A minha recomendação é começar pela validade da medição e pela insuficiência da evidência, antes de trocar o agente.

Nenhum candidato investigado demonstrou, por si, o contrato completo que queremos: distinguir suporte, refutação e insuficiência, justificar diagnóstico e localização, usando apenas a informação disponível ao agente. Isso limita a adoção integral; não elimina o valor dos componentes.

## Alcance e qualidade da pesquisa

Foram examinados **27 repositórios públicos e três trabalhos adicionais**, num total de 30 candidatos. Consultei artigos, documentação oficial, árvores de ficheiros e licenças. Em seis candidatos fiz inspeção dirigida de implementação: MechBench, HypoSpace, ALF, AS-Bench, POPPER e StatefulDiscovery. Foram guardados 30 ficheiros de código/configuração desses projetos; os hashes Git dos conteúdos foram comparados com as árvores recolhidas, sem discrepâncias.

O catálogo JSON anexo regista URLs, datas, requisitos, licenças observadas, limitações, nível de inspeção e referências dos snapshots. A pesquisa não é uma revisão sistemática exaustiva: a seleção favorece código aproveitável e o problema concreto de validade do M17. Não foram executados os frameworks, reproduzidas as tabelas dos artigos nem feitos novos ensaios de modelos. Não há, portanto, ganho experimental demonstrado nesta pesquisa.

Uma data de último push indica atividade observada, não uma nova versão científica. As datas abaixo distinguem artigo, revisão e release quando aplicável. A novidade foi verificada até à data desta pesquisa, incluindo trabalhos de setembro e outubro.

## O que saiu recentemente e muda a lista de prioridades

| Projeto | Novidade verificada | Interesse para nós |
|---|---|---|
| [AS-Bench](https://arxiv.org/abs/2610.18449) | Artigo de 13/10/2026 | Laboratório com orçamento e avaliação de previsões reservadas. |
| [MechBench](https://arxiv.org/abs/2609.35515) | Artigo de 28/09/2026 | Separa recuperar uma lei observável de recuperar o mecanismo. |
| [ALF](https://arxiv.org/abs/2609.31197) | Artigo de 25/09/2026 | Base modular para o ciclo de aquisição de dados. |
| [MechHypoBench](https://arxiv.org/abs/2610.05197) | Artigo de 04/10/2026 | Avalia consequências de hipóteses em condições não observadas. |
| [AgentDiscover](https://arxiv.org/abs/2610.05334) | Artigo de 04/10/2026 | Busca por programas com memória das tentativas. |
| [EurekaBench](https://arxiv.org/abs/2610.00492) | Artigo de 30/09/2026 | Tarefas longas de descoberta; requisitos locais elevados. |
| [EvoScientist](https://github.com/EvoScientist/EvoScientist/releases/tag/v0.3.7) | Release 0.3.7 de 17/10/2026 | Orquestração e memória atualizadas; não é um avaliador independente. |

## Os seis candidatos mais relevantes

### 1. MechBench — primeiro candidato para auditar o instrumento

O código MIT inclui avaliação simbólica e numérica e exportações distintas para o agente e o avaliador. A inspeção de `src/export_problems.py` e `src/evaluate.py` confirmou essa separação lógica e sondas de mecanismo depois de congelar a resposta. Isto poupa trabalho na avaliação executável e reduz a dependência de um juiz LLM. Não confirma ainda isolamento operacional: é preciso verificar os ficheiros e processos realmente acessíveis ao agente. [Código e documentação](https://github.com/tsinghua-fib-lab/MechBench).

A reserva decisiva para M17 é que o artigo filtra instâncias mecanisticamente ambíguas. Precisamos também de exemplos em que várias explicações são admissíveis. Portanto, seria uma base para testar mecanismos identificáveis, complementada por casos explícitos de insuficiência. Núcleo em Python >=3.12; não é necessário consultar um modelo para testar o avaliador. [Artigo](https://arxiv.org/abs/2609.35515).

### 2. HypoSpace — melhor correspondência com a questão da insuficiência

Em vez de impor uma única resposta escondida, representa conjuntos finitos de hipóteses compatíveis e avalia validade, unicidade e recuperação. Os domínios incluem grafos causais e interações booleanas. A versão v3 é de 29/05/2026, com original de 2025. Esta é a ideia mais diretamente aproveitável para estados publicamente indistinguíveis no M17. [Artigo](https://arxiv.org/abs/2510.15614v3).

A inspeção dos geradores encontrou enumeração de hipóteses compatíveis, incluindo enumeração posterior ao conjunto inicial no domínio booleano. Isso não substitui uma enumeração independente. Não identifiquei ficheiro de licença no snapshot público: recomendo aproveitar o método publicado, esclarecendo a licença antes de incorporar código. É um benchmark delimitado, não um laboratório científico completo. [Repositório](https://github.com/CTT-Pavilion/_HypoSpace).

### 3. ALF — alternativa direta para a função desempenhada pelo AutoRA

ALF organiza aquisição em componentes substituíveis: modelo aproximado, estratégia de aquisição, procura, oráculo e estado. Suporta experiências sobre dados existentes e interação com novas medições. Pode poupar o ciclo de seleção, atualização e registo das experiências. [Artigo de 25/09](https://arxiv.org/abs/2609.31197).

O núcleo `alf-core` 0.1.0 é inicial, usa Python >=3.12,<3.14.1 e não obriga a um framework de deep learning. O ficheiro LICENSE e o manifesto do core confirmam Apache-2.0, embora a API GitHub tenha devolvido NOASSERTION. A comparação útil será contra aleatório e uma regra simples, com o mesmo orçamento e sem acesso às respostas reservadas. ALF não fornece, só por si, um critério de verdade científica. [Código](https://github.com/instadeepai/alf).

### 4. Autonomous Science Bench — ambiente experimental com fronteiras explícitas

A versão 0.1 usa campanhas de experiências com orçamento, medições devolvidas por um serviço de laboratório e previsões avaliadas em condições reservadas. O artigo foi publicado a 13/10/2026. O objetivo predominante é descobrir bons desenhos e aprender a ordená-los; não cobre todas as categorias epistémicas do M17. [Artigo](https://arxiv.org/abs/2610.18449).

A arquitetura inspecionada separa laboratório, ledger e verificador. Há replay de medições publicadas e um gémeo digital; o contrato de backend ao vivo não demonstra integração laboratorial operacional. O artigo refere seis campanhas e o README atual sete; exemplos de limiares também divergem. É necessário congelar o manifesto exato. Código Apache-2.0, dados com licenças próprias; Python 3.13 e Deno, com execução local ou Harbor/Docker. [Repositório](https://github.com/Yibo-Wen/as-bench).

### 5. POPPER — método estatístico útil, com condições exigentes

POPPER propõe falsificação sequencial e agregação de evidência por e-values. É particularmente relevante para controlar decisões após vários testes adaptativos. As garantias dependem da validade condicional dos testes e da relação lógica entre a hipótese principal e as hipóteses testadas. Um teste estatístico válido sobre uma pergunta irrelevante não valida a alegação científica. [Artigo ICML 2025](https://proceedings.mlr.press/v267/huang25n.html).

O código inspecionado inclui conversões de p-values e acumulação de e-values; falta demonstrar que a utilização concreta satisfaz os pressupostos. Não identifiquei licença de código no snapshot. Recomendo uma pequena implementação independente do método estatístico e simulações sob a hipótese nula antes de qualquer integração com LLM. [Repositório](https://github.com/snap-stanford/POPPER).

### 6. StatefulDiscovery — aproveitar o registo de evidência

Mantém alegações, alternativas, experiências e estados como supported, refuted e inconclusive. O trabalho é de junho de 2026 e o código MIT pode poupar desenho de formatos e rastreabilidade. [Artigo](https://arxiv.org/abs/2606.11851).

A adjudicação da força da evidência continua a depender de um agente. Na inspeção, `CLAIMS_SCHEMA.json` exige `top_supported_claim_id` como string não vazia, enquanto uma skill admite vencedor nulo em cenário inconclusivo. Isto justifica testar o caso em que nenhuma alegação tem suporte; não demonstra que a execução já produza uma falsa conclusão. O README e o runner atual também divergem sobre dependências privadas. Execução documentada para Linux/macOS com Docker; Windows não verificado. [Código](https://github.com/SUSTech-GenAI/StatefulDiscovery).

## Outras possibilidades examinadas

As decisões seguintes são prioridades para este projeto, não classificações gerais de qualidade. “Adiar” significa que o candidato resolve outro problema ou exige recursos desproporcionados neste bloco. Os requisitos e licenças individuais estão no catálogo.

| Candidato e fonte primária | Possível aproveitamento / decisão |
|---|---|
| [DoWhy](https://github.com/py-why/dowhy) | Priorizar quando houver grafo e pressupostos causais explícitos; identificação e refutação causal. |
| [BayBE](https://github.com/emdgroup/baybe) | Alternativa estabelecida para planeamento bayesiano; adequada se o objetivo experimental já estiver definido. |
| [BoFire](https://github.com/experimental-design/bofire) | Útil para restrições e múltiplos objetivos na seleção de experiências. |
| [Ax da Meta](https://github.com/facebook/Ax) | Alternativa estabelecida de experimentação adaptativa; distinta de google/ax. |
| [AstaBench](https://github.com/allenai/asta-bench) | Reaproveitar harness, ferramentas e custos; algumas tarefas recorrem a juiz LLM. |
| [ScienceAgentBench Verified](https://github.com/OSU-NLP-Group/ScienceAgentBench) | Split corrigido de abril de 2026; boa referência para avaliação executável de análises científicas. |
| [NewtonBench original](https://github.com/HKUST-KnowComp/NewtonBench) | Auditar a versão original; o defeito do wrapper AutoSciLab não prova defeito neste benchmark. |
| [DiscoverPhysics](https://github.com/SampsonML/DiscoverPhysics) | Ambientes físicos e trajetórias reservadas; avaliação explicativa ainda inclui juiz LLM. |
| [Terminal-Bench-Science](https://github.com/harbor-framework/terminal-bench-science) | Verificadores executáveis e ambientes científicos; selecionar tarefas pequenas e adequadas. |
| [Google DeepMind Science Skills](https://github.com/google-deepmind/science-skills) | Poupa integração com ferramentas e fontes; rever licenças dos componentes e requisitos de API. |
| [EvoScientist](https://github.com/EvoScientist/EvoScientist) | Memória e execução; adiar substituição de agente até termos avaliador válido. |
| [Curie](https://github.com/Just-Curieous/Curie) | Orquestração de experiências computacionais; menos recente e não resolve o contrato epistémico. |
| [Robin](https://github.com/Future-House/robin) | Interessante em biomedicina; análise integrada depende de Edison e créditos/API. |
| [PiEvo](https://github.com/amair-lab/PiEvo) | Exploração de princípios e hipóteses; implicaria expansão de arquitetura antes de validar o núcleo. |
| [ShinkaEvolve](https://github.com/SakanaAI/ShinkaEvolve) | Bom candidato quando houver um avaliador numérico independente e resistente a exploração. |
| [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | Busca evolutiva de programas; depende da validade da função objetivo. |
| [AgentDiscover](https://github.com/mhdfb/AgentDiscover) | Memória de busca e coding agents; licença não identificada e infraestrutura adicional. |
| [AutoDS / AutoDiscovery](https://github.com/allenai/autodiscovery-neurips) | Surpresa bayesiana e exploração; surpresa não constitui critério de validade. |
| [SciAgentGym](https://github.com/CMarsRover/SciAgentGYM) | Ferramentas científicas e execução sequencial; ambiente amplo para a necessidade atual. |
| [EurekaBench](https://github.com/EurekaBench/EurekaBench) | README pede Linux, H100, Apptainer e APIs de agente/juiz; adiar piloto local. |
| [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2) | Experiências ML e manuscritos; licença atual personalizada, não MIT/Apache padrão. |

## Trabalhos a acompanhar, sem base executável pública confirmada nesta pesquisa

Não encontrar uma ligação confirmada nos materiais consultados não demonstra inexistência de código.

- **MechHypoBench, 04/10/2026:** interessa pela avaliação das consequências de hipóteses em condições reservadas. A interpretação da hipótese usa LLM antes da pontuação numérica; isso exige auditoria própria. Os mecanismos são instanciados sobre covariáveis empíricas, o que não prova causalidade no sistema real original. [Artigo](https://arxiv.org/abs/2610.05197).
- **SDABench, 13/07/2026:** a distinção entre capacidades descritiva, exploratória, inferencial, preditiva, causal e mecanística pode ajudar a delimitar o que cada teste do M17 mede. [Artigo](https://arxiv.org/abs/2607.11079).
- **SciDisco/SciThèque, 31/07/2026:** grafos reservados de evidência e passos verificáveis são uma pista metodológica; o treino/RL de modelos está fora do bloco autorizado de validade. [Artigo](https://arxiv.org/abs/2607.28990).

## O que esta pesquisa muda na decisão anterior

A escolha deixou de ser simplesmente continuar ou abandonar AutoRA/AutoSciLab. Há bases mais específicas para as dificuldades que encontrámos. A hipótese de trabalho mais promissora é **reaproveitar avaliadores, métodos de enumeração e ciclos experimentais pequenos**, demonstrando primeiro que cada um funciona no papel necessário.

Os resultados históricos de AutoRA e AutoSciLab não são alterados por esta triagem. Um resultado favorável publicado noutro benchmark não demonstra transferência para M17. Também não se deve transportar uma fuga de informação encontrada num wrapper para condenar automaticamente todos os projetos que esse wrapper usa.

As restrições de licença identificadas são práticas: não encontrei ficheiro de licença em POPPER, HypoSpace, AgentDiscover, AutoDS e EurekaBench nos snapshots recolhidos. Código publicamente visível não basta para assumir autorização de incorporação. ALF tem Apache-2.0 confirmado manualmente; AI Scientist v2 usa licença personalizada. Licenças de datasets e componentes terceiros precisam de verificação separada da licença do projeto.

## Próximo bloco recomendado, até uma nova decisão

Este é um plano de testes, ainda não executado. Os passos podem avançar sem novos modelos e terminar num único ponto de avaliação.

1. **Congelar versões e tarefa mínima.** Guardar commit, manifesto, dependências e visibilidade de cada artefacto. Definir formalmente o conjunto de conclusões admissíveis com a evidência pública, incluindo o caso de insuficiência. Preservar G1/G2 e reservas.
2. **MechBench: auditar o avaliador.** Comparar respostas corretas, equivalentes e deliberadamente erradas; testar ordem, renomeação e duplicação das observações. Verificar que respostas privadas e sondas reservadas não chegam ao processo do agente. Usar casos manuais e um avaliador pequeno independente. Qualquer acerto exige evidência admissível; um controlo que lê a resposta escondida serve apenas para testar o harness.
3. **HypoSpace: verificar conjuntos admissíveis.** Enumerar espaços causais/booleanos pequenos independentemente. Criar pares de mundos com observações idênticas e mecanismos distintos. A evidência pública igual deve induzir o mesmo conjunto admissível; só evidência discriminante deve permitir selecionar uma resposta única. Usar o método sem copiar código cuja licença esteja por esclarecer.
4. **ALF: procurar vantagem além da regra simples.** Fixar dados iniciais, sementes e orçamento. Comparar aleatório, regra simples e aquisição aprendida, com medidas e escolhas registadas. O modelo aproximado deve aprender apenas com medições permitidas. O ganho terá de existir sobre os dois controlos e ser relevante face ao custo; vencer apenas aleatório não basta, como mostrou o ensaio anterior.
5. **AS-Bench: testar as fronteiras do laboratório.** Executar controlos de referência e sem ação, consumo de orçamento, duplicação de consultas e falsificação de ledger. Confirmar que um registo produzido pelo agente não substitui o registo do laboratório. Verificar os limiares no manifesto congelado, resolvendo as divergências documentais antes de comparar resultados.
6. **POPPER e StatefulDiscovery: verificações pequenas adicionais.** Para POPPER, simular hipóteses nulas e alternativas, dependência entre testes e paragem adaptativa, verificando as condições estatísticas. Para StatefulDiscovery, testar episódios em que todas as alegações são inconclusivas e rastrear cada estado à evidência. A passagem destes testes não confere validade a juízos livres de um LLM.
7. **Análise obrigatória.** Emitir uma matriz por componente: regra, contraexemplo, resultado, falhas restantes e custo. Só propor um pequeno ensaio de modelo se o avaliador rejeitar os controlos errados, aceitar equivalências justificadas, representar ambiguidade e manter isolamento verificável. Uma falha deve produzir correção delimitada ou rejeição do componente, antes de nova inferência.

O trabalho adicional estritamente necessário parece menor em MechBench e na enumeração inspirada em HypoSpace. ALF é a comparação mais direta com AutoRA. AS-Bench merece uma prova técnica posterior por causa das dependências e da sua estreia muito recente. POPPER e DoWhy tornam-se prioritários se a tarefa mínima incluir inferência estatística ou causal explícita. **Ainda não recomendo integrar todos estes projetos numa arquitetura única.**

## Entregáveis e limites

O catálogo estruturado acompanha este relatório em `CATALOGO_ALTERNATIVAS_CIENTIFICAS_2026-10-17.json`. Identifica os 30 candidatos, fontes, requisitos, limitações e snapshots de implementação consultados. As cópias de trabalho permanecem no diretório de investigação; não foram incorporadas no núcleo do TRONCO-01.

Conclusão delimitada: **existem bases concretas que podem poupar trabalho e justificam um novo bloco de testes offline. Não há ainda demonstração de que qualquer uma substitua integralmente o instrumento científico do M17 ou produza ganho no nosso sistema.**

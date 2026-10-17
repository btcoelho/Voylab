# Relatório de estado — TRONCO-01, M17 e biblioteca Voynich

**Data de referência:** 17 de outubro de 2026  
**Repositório:** [btcoelho/Voylab](https://github.com/btcoelho/Voylab), branch `main`, commit `efb676de43d60f61f5e1ca967a6ed7f3650daa62`  
**Natureza:** síntese do estado e das fontes consultadas; não altera protocolos nem resultados históricos.

## O que queremos atingir

Queremos descobrir se um agente consegue investigar de forma cientificamente justificável usando a informação realmente disponibilizada a esse agente. A pergunta central é: **o sistema distingue uma conclusão apoiada pela evidência de uma conclusão errada, e reconhece quando os dados ainda não permitem decidir?** Não basta acertar num rótulo final. Temos de saber o que o agente conhecia, que hipótese propôs, o que previu antes da medição, que experiência escolheu, o que mudou depois do resultado, que evidência citou e por que decidiu continuar, parar ou pedir ajuda.

Há duas camadas. **TRONCO-01** é o objetivo amplo: um analista autónomo que observa, formula e testa explicações, reconhece anomalias e insuficiência, revê crenças com evidência, conserva proveniência e decide sob limites de custo. **M17/G1/G2 e os protótipos v2.x** são tarefas e instrumentos sintéticos mais estreitos, destinados a testar partes desse objetivo. A v2.7, por exemplo, avalia pequenas tabelas determinísticas sem consultas; não demonstra a capacidade do analista completo.

A biblioteca Voynich reúne experiências M12–M17 feitas em mundos e dados sintéticos. **Nenhuma experiência inventariada usou fólios históricos Voynich ou Egerton e nenhuma demonstra descodificação do manuscrito.** A biblioteca preserva trabalho experimental reutilizável; não justifica extrapolar resultados para o manuscrito.

## Como estamos a idealizar o sistema

A proposta atual é começar com **um agente proponente, um núcleo de verificação independente e uma memória de eventos**. Não há evidência que justifique seis agentes ou uma arquitetura multiagente. As responsabilidades podem ser funções simples:

| Função | Saída que tem de poder ser verificada |
|---|---|
| Observar | Fonte, conteúdo bruto, instante, unidades e hash |
| Formular hipótese | Explicação testável, pressupostos, versão e dados usados |
| Prever | Consequência registada antes da medição |
| Escolher experiência | Alternativas, motivo, orçamento e resultado do laboratório |
| Diagnosticar | Compatibilidade, resíduo, contradições e limites do teste |
| Rever e decidir | Eventos preservados, dependências e fundamento para registar, investigar ou submeter |

O ciclo é **observar → propor hipótese testável → registar previsão → medir → comparar → rever hipótese ou pressupostos → decidir continuar, registar ou submeter**. O agente não pode receber rótulos ocultos, pontuações do oráculo ou informação derivada da resposta privada durante a inferência. O avaliador usa essa referência só depois de a resposta estar congelada.

É necessário manter separados três estados: operacional (geração, parser e ação funcionaram), epistémico (evidência apoia, contradiz ou não decide) e triagem (REGISTAR, INVESTIGAR ou SUBMETER, considerando também relevância e custo). No contrato v2.7, `supported` significa compatível com o histórico público não vazio, não verdade universal; `rejected` significa incompatível com evidência citada; `undetermined` significa que não há observações suficientes. Consultas estão desativadas, portanto a v2.7 não testa aquisição ativa de informação.

O instrumento deve representar **várias conclusões defensáveis** quando os mesmos dados admitem mecanismos diferentes. Dois mundos indistinguíveis para o agente não podem ter respostas únicas esperadas diferentes sem informação adicional. A insuficiência é uma conclusão legítima. “Não encontrei explicação no conjunto atual” também não significa “não existe explicação possível”. Com ruído, toda a conclusão depende de pressupostos de medição e de limites de falso alarme.

## Estado atual

| Área | Evidência concluída | Estado e limite |
|---|---|---|
| Biblioteca M12–M17 | 141 ficheiros de dados, protocolos, código, resultados, relatórios e testes | Arquivada e sintética; não há promoção geral |
| G0–G2 | Protocolos, controlos e sentinela preservados | G2 parou após 5 mundos: 4/5 relatórios explícitos onde o gate exigia 5/5; os outros 20 não foram executados |
| Auditoria v1–v2.7 | Especificações, avaliador independente, enumeração, casos manuais, mutações e verificações de integração | Instrumento melhor auditado; foi identificado um defeito remanescente na gramática LMFE para listas vazias |
| Ensaio real v2.7 | 10 chamadas, sem retry nem consulta, Qwen2.5-0.5B-Instruct de 4 bits | **0/10 sucessos conjuntos**; resultado negativo de desenvolvimento |
| AutoRA + DiscoveryWorld | 3 políticas emparelhadas em 100 seeds não consecutivas | AutoRA e regra pública simples 100/100; aleatório 34/100. Ganho sobre aleatório, nenhum ganho próprio do AutoRA demonstrado |
| AutoSciLab | Auditoria em commit congelado e reprodução de fluxos determinísticos | Fuga de ground truth reproduzida em GRN e Newton/Chem; performance dos autores não reproduzida |
| Alternativas recentes | 27 repositórios + 3 artigos; inspeção dirigida de 6 implementações | Componentes promissores; nenhum sistema integral aprovado |
| M17 | Auditorias e resultados de desenvolvimento | **Não aprovado**; reservas de diagnóstico e confirmação continuam fechadas |

Não há uma percentagem global de progresso cientificamente defensável. O avanço real está na capacidade de reproduzir, separar classes de erro, testar o avaliador e encontrar contraexemplos. Não há evidência de melhoria da competência científica do checkpoint v2.7 ou de validade externa.

## O que mostram os ensaios

### M12–M17, G0–G2

O inventário Voynich regista: M12, políticas concorrentes sem promoção geral; M13, cobertura versus desacordo, com dois gates aprovados e dois reprovados; M14-R, reparações, quatro de seis critérios aprovados; M15, piloto de SFT em dados sintéticos M14; M16, currículo L4/L5 com gates aprovados em três sementes; M17, benchmark textual cuja avaliação base inicial foi interrompida após 709 avisos de geração, antes de guardar resultados válidos. Os dados preservados são históricos e não devem ser reclassificados como confirmação inédita.

O G2 posterior foi uma sentinela de cinco mundos, não o lote de 25. O gate exigia cinco relatórios explícitos sem falhas operacionais. Obteve quatro de cinco na condição com gramática; houve truncagem, falha de parser e ação inválida. Na condição, as respostas foram `supported` sem evidência citada e nenhuma acertou a decisão. A condição livre não produziu ações válidas. O gate falhou e os restantes vinte mundos não foram executados. O controlo simbólico acertou cinco, mas usou conhecimento da representação e não prova capacidade aprendida.

### Auditoria v1–v2.7 e ensaio do modelo

As auditorias posteriores criaram uma especificação mais explícita, um verificador sem as funções semânticas do scorer primário, enumeração finita, casos manuais, mutações e verificações de integração. Na v2.7, 37 testes e quatro mutações dirigidas passaram; a referência independente concordou em 1.587 estados enumerados e rejeitou 6.345 relatórios alterados no domínio explorado. A enumeração cobre tabelas binárias e históricos curtos; não cobre todas as ações de localização nem prova validade fora desse domínio. Estes resultados apoiam propriedades testadas do instrumento, não a competência do agente.

O ensaio real v2.7 executou dez episódios com dez JSON completos e EOS, três ações aceites e **zero sucessos conjuntos**. O modelo repetiu `supported / [A] / none_fit / no_observations` apesar de históricos diferentes. Sete respostas falharam na forma ou nas referências públicas; as três aceites também erraram cientificamente. Dois episódios vazios eram duplicados: há nove estados públicos distintos. A conferência independente recalculou os resultados e não encontrou rótulos privados nos prompts.

Foi reproduzido um defeito do adaptador de gramática LMFE: certas restrições de lista vazia (`maxItems: 0`, enumeração vazia e unicidade) não bloqueiam saídas que deviam bloquear. O validador final recusou ações inválidas, mas a promessa sobre o que a gramática restringia era maior do que o teste demonstrava. O defeito ajuda a explicar rejeições de forma, não explica a resposta científica errada repetida. Não houve nova inferência, fine-tuning, modelo maior ou acesso às reservas após a análise do lote.

### AutoRA + DiscoveryWorld

No cenário `Plant Nutrients Easy`, três braços receberam uma medição por seed. AutoRA por desacordo e a regra simples de escolher uma amostra com sinal público de crescimento identificaram a hipótese em 100/100; seleção aleatória, em 34/100. Como a heurística simples empatou com AutoRA, há ganho da seleção informada face ao acaso, mas **não há ganho incremental do framework AutoRA demonstrado**. O cenário é determinístico e fácil. O resultado não valida M17, descoberta causal geral, transferência para tarefas difíceis ou conclusão da missão DiscoveryWorld.

### AutoSciLab

Na versão inspecionada, o resumo do benchmark GRN envia ao prompt `edge_f1` calculado contra o grafo verdadeiro. Nos caminhos Newton/Chem, a avaliação intermédia da lei oculta influencia o prompt, a confiança e a seleção da resposta. A exposição foi reproduzida em GRN e confirmada no código de Newton/Chem. Resultados desses caminhos não demonstram descoberta só com dados públicos até a fronteira ser corrigida e reavaliada. Isto não prova que o NewtonBench original tenha o mesmo defeito. Os números publicados pelos autores não foram reproduzidos e o snapshot não continha licença explícita para incorporação direta.

## Componentes externos e o que podem poupar

O levantamento recente encontrou três tipos de ajuda, sem um substituto completo para o instrumento científico:

- **Avaliação e ambiguidade:** [MechBench](https://github.com/tsinghua-fib-lab/MechBench) fornece pontuação objetiva e separação de respostas privadas; precisa de casos de insuficiência. [HypoSpace](https://github.com/CTT-Pavilion/_HypoSpace) representa conjuntos de hipóteses admissíveis; melhor ideia metodológica para observações subdeterminantes, mas licença de código por esclarecer.
- **Desenho experimental e isolamento:** [ALF](https://github.com/instadeepai/alf) pode substituir o ciclo AutoRA; testar contra regra simples e aleatório a orçamento igual. [Autonomous Science Bench](https://github.com/Yibo-Wen/as-bench) separa laboratório, orçamento, ledger e verificador; congelar versão porque artigo e README divergem.
- **Métodos e registo:** [POPPER](https://github.com/snap-stanford/POPPER) e [DoWhy](https://github.com/py-why/dowhy) ajudam com falsificação sequencial e causalidade sob pressupostos explícitos. [StatefulDiscovery](https://github.com/SUSTech-GenAI/StatefulDiscovery) ajuda a registar alegações e estados inconclusivos, mas a avaliação continua dependente de agente. [REA](https://github.com/morluto/rea) e [Google AX](https://github.com/google/ax) oferecem ideias de ledger e orquestração, não garantias de validade científica.

O catálogo inclui ainda DoWhy, BayBE, BoFire, Ax da Meta, AstaBench, ScienceAgentBench Verified, NewtonBench original, DiscoverPhysics, Terminal-Bench-Science, Google DeepMind Science Skills, EvoScientist, Curie, Robin, PiEvo, ShinkaEvolve, OpenEvolve, AgentDiscover, AutoDS/AutoDiscovery, SciAgentGym, EurekaBench, AI Scientist v2, MechHypoBench, SDABench e SciDisco/SciThèque. A pesquisa foi triagem e inspeção dirigida; frameworks não foram executados e não se reproduziram os resultados dos artigos.

## Próximos passos encadeados

O ponto de análise após o lote v2.7 já foi atingido. O bloco seguinte deve ser offline e acabar numa única decisão:

1. Preservar G1, G2, v2.3 e v2.7 como resultados históricos; deixar os dez estados v2.7 apenas como regressão exposta.
2. Corrigir a representação de listas vazias no callback LMFE real. Acrescentar exemplos positivos e negativos que passem pelo tokenizer, callback e validador final.
3. Definir um diagnóstico pequeno e pré-registado que isole o veredicto das competências de localização e relatório. Se a localização for fixada como `none / []` ou omitida, isso tem de estar escrito antes de gerar respostas.
4. Implementar independentemente a enumeração de conjuntos de hipóteses inspirada no HypoSpace. Construir pares de mundos publicamente indistinguíveis e confirmar que recebem o mesmo conjunto de conclusões admissíveis.
5. Auditar MechBench com referências corretas e erradas e inspeção da fronteira pública/privada. Só após passar esta auditoria comparar ALF, regra simples e aleatório sob orçamento comum.
6. Testar o isolamento do laboratório e congelar a versão exata de AS-Bench. Usar POPPER/DoWhy apenas se a tarefa operacional exigir inferência estatística ou causal.
7. Fechar a análise obrigatória antes de qualquer nova inferência. Mesmo um resultado positivo autoriza apenas um pequeno ensaio de desenvolvimento; não aprova M17 ou o TRONCO completo.

## Registos e leitura recomendada

O arquivo do TRONCO está em [Voylab/research/TRONCO-01](https://github.com/btcoelho/Voylab/tree/main/research/TRONCO-01); a biblioteca sintética está em [Voylab/research/VOYNICH](https://github.com/btcoelho/Voylab/tree/main/research/VOYNICH). Leitura recomendada: `TRONCO01_ANALISE_INTEGRADA_2026-10-17.md` (objetivo e arquitetura); `TRONCO01_G2_SENTINELA_ANALISE_E_PONTO_DE_DECISAO_2026-10-17.md` (gate G2); `TRONCO01_REVISAO_RESULTADOS_V2_7_2026-10-17.md` (instrumento); `TRONCO01_RESULTADO_MODELO_V2_7_2026-10-17.md` (0/10); `AUTORA_DISCOVERYWORLD_GANHO_2026-10-17.md`; `AUTOSCILAB_AUDITORIA_INDEPENDENTE_2026-10-17.md`; `PESQUISA_ALARGADA_BASE_CIENTIFICA_2026-10-17.md` e `CATALOGO_ALTERNATIVAS_CIENTIFICAS_2026-10-17.json`. O [manifesto SHA-256](https://github.com/btcoelho/Voylab/blob/main/research/TRONCO-01/SHA256SUMS.txt) regista a integridade dos arquivos publicados.

## Bibliografia e registo integral de links

Esta lista recolhe os URLs únicos presentes nos relatórios e no catálogo arquivados no Voylab em 17/10/2026. Inclui artigos, repositórios, documentação e páginas bibliográficas; o relatório integrado explica a relação e os limites das fontes científicas. Os links de código REA/AX com `blob` apontam para os commits específicos inspecionados.

### Fundamentos, métodos e trabalhos usados na análise TRONCO

- Reiter, teoria de diagnóstico: [texto](https://cse.sc.edu/~MGV/csce580f12/gradPres/reiter-diagnosis.pdf).
- Platt, *Strong Inference*: [PDF](https://worthylab.org/wp-content/uploads/2019/05/platt1964.pdf).
- Chaloner & Verdinelli, desenho experimental bayesiano: [resumo dos autores](https://www.stat.cmu.edu/tr/tr599/tr599.html); [DOI](https://doi.org/10.1214/ss/1177009939).
- Alchourrón, Gärdenfors & Makinson, revisão de teorias: [DOI](https://doi.org/10.2307/2274239); [bibliografia de David Makinson](https://sites.google.com/site/davidcmakinson/).
- Doyle, *A Truth Maintenance System*: [MIT DSpace](https://dspace.mit.edu/entities/publication/5377b306-4ecc-4687-b1f5-78cbb4a0543a).
- de Kleer, *An Assumption-Based TMS*: [PDF](https://dekleer.org/Publications/An%20Assumption-Based%20TMS.pdf).
- Wald, testes sequenciais: [DOI](https://doi.org/10.1214/aoms/1177731118).
- Tukey, *Exploratory Data Analysis*: [WorldCat](https://search.worldcat.org/title/exploratory-data-analysis/oclc/3058187).
- NIST, [Engineering Statistics Handbook](https://www.nist.gov/programs-projects/nistsematech-engineering-statistics-handbook) e [cartas de controlo](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3.htm).
- Russell & Wefald, *Do the Right Thing*: [MIT Press](https://mitpress.mit.edu/9780262181440/do-the-right-thing/).
- W3C, [PROV Overview](https://www.w3.org/TR/prov-overview/); [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema).
- Sandve et al., regras para pesquisa computacional reprodutível: [artigo](https://www.chem.ucla.edu/dept/Faculty/merchant.html/pdf/ten_simple_rules.pdf).
- Yao et al., ReAct: [arXiv:2210.03629](https://arxiv.org/abs/2210.03629).
- Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet*: [arXiv:2310.01798](https://arxiv.org/abs/2310.01798).
- Yang et al., trabalhos sobre descoberta científica citados na análise: [arXiv:2501.01540](https://arxiv.org/abs/2501.01540), [arXiv:2510.07172](https://arxiv.org/abs/2510.07172), [arXiv:2609.30199](https://arxiv.org/abs/2609.30199), [arXiv HTML v5](https://arxiv.org/html/2608.09696v5).
- Kabra et al., AutoSciLab: [arXiv](https://arxiv.org/abs/2605.24043), [PDF](https://arxiv.org/pdf/2605.24043), [repositório oficial](https://github.com/scientific-discovery/LLM-AutoSciLab).
- WorldZero: [repositório](https://github.com/skishore23/worldzero); BoxingGym: [artigo](https://arxiv.org/abs/2501.01540), [código](https://github.com/kanishkg/boxing-gym); NewtonBench: [artigo](https://arxiv.org/abs/2510.07172), [código](https://github.com/HKUST-KnowComp/NewtonBench); NeuronBench: [código](https://github.com/murphyk/neuronbench); ExplorationBench: [página](https://explorationbench.com/).

### REA e Google AX, fontes inspecionadas por commit

- [REA, raiz no commit f85a932](https://github.com/morluto/rea/tree/f85a932d71279415dd95cc30083137d1161f83b8); [README](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/README.md); [licença](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/LICENSE); [avisos de terceiros](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/THIRD_PARTY_NOTICES.md); [package.json](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/package.json).
- REA: [ledger de obrigações](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/docs/reconstruction-obligation-ledgers.md); [workflow de evidência](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/.agents/skills/reverse-engineer-anything/references/evidence-workflows.md); [EvidenceLedger](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/application/investigation/EvidenceLedger.ts); [UnknownEvidence](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/application/investigation/UnknownEvidence.ts); [teste residual unknown](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/application/investigation/EvidenceLedger.residualUnknown.test.ts); [evidence.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/evidence.ts); [evidenceBundle.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/evidenceBundle.ts); [evidenceErrors.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/evidenceErrors.ts); [residualUnknown.ts](https://github.com/morluto/rea/blob/f85a932d71279415dd95cc30083137d1161f83b8/src/domain/residualUnknown.ts).
- [Google AX, raiz no commit 8d2ccf3](https://github.com/google/ax/tree/8d2ccf36f194f6f58c57b90753bd3986639b562f); [README](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/README.md); [licença](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/LICENSE); [DESIGN](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/DESIGN.md); [conceitos](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/concepts.md); [manifestos](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/manifests.md); [roadmap](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/roadmap.md); [runner](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/docs/runner.md); [go.mod](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/go.mod); [client do modelo](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/internal/model/client.go); [API proto](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/pkg/apis/v1alpha1/ax.proto); [types Go](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/pkg/apis/v1alpha1/types.go); [runner Go](https://github.com/google/ax/blob/8d2ccf36f194f6f58c57b90753bd3986639b562f/runner/runner.go).

### Alternativas e bibliografia recente (catálogo de 30 candidatos)

- MechBench: [artigo](https://arxiv.org/abs/2609.35515), [código](https://github.com/tsinghua-fib-lab/MechBench).
- HypoSpace: [artigo v3](https://arxiv.org/abs/2510.15614v3), [código](https://github.com/CTT-Pavilion/_HypoSpace).
- ALF: [artigo](https://arxiv.org/abs/2609.31197), [código](https://github.com/instadeepai/alf).
- Autonomous Science Bench: [artigo](https://arxiv.org/abs/2610.18449), [código](https://github.com/Yibo-Wen/as-bench).
- MechHypoBench: [artigo](https://arxiv.org/abs/2610.05197); AgentDiscover: [artigo](https://arxiv.org/abs/2610.05334); EurekaBench: [artigo](https://arxiv.org/abs/2610.00492).
- POPPER: [artigo ICML](https://proceedings.mlr.press/v267/huang25n.html), [código](https://github.com/snap-stanford/POPPER); StatefulDiscovery: [artigo](https://arxiv.org/abs/2606.11851), [código](https://github.com/SUSTech-GenAI/StatefulDiscovery).
- DoWhy: [código](https://github.com/py-why/dowhy); BayBE: [código](https://github.com/emdgroup/baybe); BoFire: [código](https://github.com/experimental-design/bofire); Ax da Meta: [código](https://github.com/facebook/Ax).
- AstaBench: [código](https://github.com/allenai/asta-bench); ScienceAgentBench Verified: [código](https://github.com/OSU-NLP-Group/ScienceAgentBench); NewtonBench original: [código](https://github.com/HKUST-KnowComp/NewtonBench); DiscoverPhysics: [artigo](https://arxiv.org/abs/2605.26087), [código](https://github.com/SampsonML/DiscoverPhysics).
- Terminal-Bench-Science: [código](https://github.com/harbor-framework/terminal-bench-science); Google DeepMind Science Skills: [código](https://github.com/google-deepmind/science-skills); EvoScientist: [código](https://github.com/EvoScientist/EvoScientist), [release 0.3.7](https://github.com/EvoScientist/EvoScientist/releases/tag/v0.3.7).
- Curie: [artigo](https://arxiv.org/abs/2502.16069), [código](https://github.com/Just-Curieous/Curie); Robin: [artigo Nature](https://www.nature.com/articles/s41586-026-10652-y), [código](https://github.com/Future-House/robin); PiEvo: [artigo](https://arxiv.org/abs/2602.06448), [código](https://github.com/amair-lab/PiEvo).
- ShinkaEvolve: [código](https://github.com/SakanaAI/ShinkaEvolve); OpenEvolve: [código](https://github.com/algorithmicsuperintelligence/openevolve); AutoDS/AutoDiscovery: [nota oficial](https://allenai.org/blog/autods), [código](https://github.com/allenai/autodiscovery-neurips).
- SciAgentGym: [artigo](https://arxiv.org/abs/2602.12984), [código](https://github.com/CMarsRover/SciAgentGYM); AI Scientist v2: [artigo](https://arxiv.org/abs/2504.08066), [código](https://github.com/SakanaAI/AI-Scientist-v2).
- SDABench: [artigo](https://arxiv.org/abs/2607.11079); SciDisco/SciThèque: [artigo](https://arxiv.org/abs/2607.28990).
- AgentDiscover: [código](https://github.com/mhdfb/AgentDiscover); EurekaBench: [código](https://github.com/EurekaBench/EurekaBench).

### Fontes adicionais citadas no levantamento integrado

- Curie: [arXiv:2502.16069](https://arxiv.org/abs/2502.16069). AI Scientist v2: [arXiv:2504.08066](https://arxiv.org/abs/2504.08066). PiEvo: [arXiv:2602.06448](https://arxiv.org/abs/2602.06448). SciAgentGym: [arXiv:2602.12984](https://arxiv.org/abs/2602.12984).
- DiscoverPhysics: [arXiv:2605.26087](https://arxiv.org/abs/2605.26087). MechBench: [arXiv:2609.35515](https://arxiv.org/abs/2609.35515). ALF: [arXiv:2609.31197](https://arxiv.org/abs/2609.31197).
- EurekaBench: [arXiv:2610.00492](https://arxiv.org/abs/2610.00492). MechHypoBench: [arXiv:2610.05197](https://arxiv.org/abs/2610.05197). AgentDiscover: [arXiv:2610.05334](https://arxiv.org/abs/2610.05334). AS-Bench: [arXiv:2610.18449](https://arxiv.org/abs/2610.18449).

O levantamento cobre os 100 URLs únicos encontrados nos ficheiros de referência arquivados: alguns são várias páginas do mesmo projeto, DOI, texto integral ou documentação. Para rastrear arquivos e versões publicados, consultar [Voylab/TRONCO-01](https://github.com/btcoelho/Voylab/tree/main/research/TRONCO-01), [Voylab/VOYNICH](https://github.com/btcoelho/Voylab/tree/main/research/VOYNICH) e o [catálogo detalhado das 30 alternativas](https://github.com/btcoelho/Voylab/blob/main/research/TRONCO-01/reports/CATALOGO_ALTERNATIVAS_CIENTIFICAS_2026-10-17.json).

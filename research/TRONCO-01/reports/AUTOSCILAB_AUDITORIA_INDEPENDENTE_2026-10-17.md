# Auditoria independente inicial — LLM-AutoSciLab

**Data:** 17-10-2026
**Checkout testado:** `scientific-discovery/LLM-AutoSciLab`, commit `351aae73e6c6c279e67943b77143b0f118d1e289`
**Decisão:** não aceitar os resultados de desempenho como demonstração independente de descoberta científica até corrigir a fronteira entre agente e avaliador. A ideia metodológica merece exploração; este snapshot não está pronto para adoção dos resultados nem para reutilização direta do código.

## O que foi executado

- Clonado o repositório oficial num checkout temporário em `work/AutoSciLab`.
- Compilação Python (`compileall`) de `autoscilab`, `scripts` e `newtonbench_vendor`: passou.
- Ajuda do launcher (`run_all_benchmarks.py --help`): passou.
- Execução determinística do oráculo GRN `g2_incoherent_feedforward`, difficulty `medium`, law `v1`, com leitura repetida dos mesmos parâmetros: resultado idêntico.
- Teste diferencial do caminho que constrói o prompt: um grafo errado e o grafo verdadeiro foram pontuados pelo oráculo com `edge_f1` 0,000 e 1,000; ambos os valores chegaram ao prompt de raciocínio.
- Leitura do caminho Newton: a pontuação da lei escondida é calculada antes do fim, usada para orientar o LLM, alterar confiança e selecionar a equação final.

Os resultados do teste estão em `AUTOSCILAB_AUDITORIA_SMOKE_2026-10-17.json`; o teste reproduzível está em `AUTOSCILAB_INDEPENDENT_AUDIT_SMOKE.py`.

## Defeitos que afetam a validade

### 1. GRN: métrica do grafo verdadeiro revelada durante a inferência

Em `autoscilab/grn_autoscilab/loop.py`, `_lineage_summary` chama `oracle.evaluate_graph()` para cada hipótese e acrescenta o `edge_f1` verdadeiro ao resumo. `_reason_hypotheses` passa esse resumo a `_build_reasoning_prompt`, que o inclui no prompt do LLM. Assim, durante o processo, o sistema revela ao agente quão semelhante cada hipótese está ao grafo oculto. O modelo pode escolher a hipótese pela nota do avaliador, em vez de a justificar exclusivamente pelas intervenções e observações disponíveis.

Contraexemplo reproduzido: duas hipóteses estruturalmente idênticas ao percurso do prompt, uma com grafo errado e outra com grafo verdadeiro, aparecem com `edge_f1=0.000` e `edge_f1=1.000`. O teste está no JSON e pode ser repetido pelo script independente.

### 2. Newton e tarefas de equações: lei de referência usada dentro do ciclo

`DiscoveryConfig.mid_run_gt_eval` é verdadeiro por omissão (`autoscilab/loop/discovery.py`). O runner oficial Newton também o ativa explicitamente (`scripts/run_paper_sweep.py`). Quando o ajuste interno ultrapassa R² 0,95, o ciclo chama `oracle.evaluate_law()` contra a lei escondida, passa o RMSLE/accuracy ao prompt de validação do LLM, limita a confiança com base na pontuação, mantém candidatos segundo o RMSLE verdadeiro e pode substituir a resposta final pela equação com melhor erro contra o oráculo. A pipeline Chem usa o mesmo `DiscoveryLoop` e herda o valor verdadeiro por omissão.

Isto transforma a resposta secreta num sinal de treino e num critério de seleção. Métricas finais obtidas nesse modo não medem descoberta com base apenas nas observações experimentais.

### 3. Reprodutibilidade e reutilização

- O checkout não contém ficheiros de testes rastreados pelo Git.
- O checkout não contém `LICENSE`, `LICENSE.txt` ou `COPYING`; não há licença de código explícita neste snapshot para autorizar incorporação direta no nosso repositório.
- O modo CLI `--use-internal-state` usa `action="store_true", default=True`, portanto não há forma de o desligar pela linha de comando. A interface de tarefa descreve o painel A/B/C/R como observável; ainda assim, o runner não permite testar a configuração só com o reporter.

## O que não foi reproduzido

Não executei o smoke test oficial com LLM nem as experiências do paper: nesta sessão não existem `OPENAI_API_KEY` nem `TOGETHER_API_KEY`. Não fiz chamadas externas, não incidi custo de inferência e não tratei os números reportados pelos autores como resultados reproduzidos.

O artigo apresenta 67,6% de exact accuracy em NewtonBench, 35,1% em ActiveSciBench-Chem e 31,1% de recuperação exata em ActiveSciBench-GRN, além de eficiência amostral 2–5× superior. Estes são resultados dos autores em [arXiv:2605.24043](https://arxiv.org/abs/2605.24043), não confirmados por esta auditoria. Os problemas acima mostram que, pelo menos nos percursos GRN e de equações identificados, a avaliação não é cega ao rótulo verdadeiro.

## Conclusão

**Apto como fonte de ideias e como código a auditar; inapto, neste estado, como evidência de que um agente descobre mecanismos a partir apenas da informação disponível ao agente.** A parte de seleção experimental por desacordo entre mecanismos é relevante para TRONCO-01. O resultado anunciado, contudo, precisa de ser reavaliado depois de remover o acesso do ciclo de inferência ao avaliador secreto.

## Próximo bloco recomendado

1. Criar uma interface pública de oráculo que devolva apenas intervenções e medidas designadas como observáveis; manter `evaluate_law`/`evaluate_graph` num avaliador externo, inacessível ao loop e ao prompt.
2. Remover do prompt GRN `edge_f1`, `motif_accuracy`, grafo verdadeiro, scores do avaliador e quaisquer aliases desses campos.
3. Desligar avaliação de ground truth no meio da execução; selecionar a hipótese final apenas por dados de validação independentes e pré-registados, sem consultar a lei oculta.
4. Adicionar um teste de não interferência: alterar os rótulos ocultos mantendo as observações públicas fixas não pode alterar prompts, ações, paragem ou resposta do agente.
5. Testar mutações de fuga de rótulo e verificar que os testes as detetam; congelar primeiro o protocolo e os critérios.
6. Reproduzir um caso de cada benchmark com orçamento baixo depois da reparação e comparar AutoSciLab, AutoRA, baselines simples e aleatório sob orçamento idêntico.
7. Resolver a licença do código antes de copiar módulos. Até lá, citar e implementar uma versão limpa da ideia, ou pedir aos autores uma licença explícita.

O próximo ponto de análise deve ocorrer depois da reparação e do teste de não interferência, antes de correr lotes de modelos ou tentar reproduzir as métricas publicadas.

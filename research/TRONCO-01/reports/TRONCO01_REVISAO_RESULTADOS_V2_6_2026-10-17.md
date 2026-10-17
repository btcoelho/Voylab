# TRONCO-01 v2.6 — verificação dos resultados e decisão

As alterações tiveram efeito técnico. Reproduzi os 32 testes e as três mutações dirigidas, conferi os hashes do arquivo e dos ficheiros locais e exercitei, nesta revisão, a função principal `trial_runner.run` com dependências simuladas. Não executei inferência aprendida nem carreguei pesos. A v2.6 original permanece intacta.

## Resultados observados

| Verificação | Resultado | Alcance |
|---|---|---|
| Suite existente | 32/32 passam | Componentes e harness; a suite original não chama `trial_runner.run` |
| Três mutações anteriores | 3 detectadas por asserção, com baselines aprovados | Duplicações, identidade da retoma e guard na entrada |
| Runner completo, dez relatórios de referência fixos | 10/10 sucessos conjuntos | Confirma ligação do runner ao scorer; loader e tokenizer substituídos por fakes |
| Runner completo, dez veredictos deliberadamente alterados | 0/10 sucessos conjuntos | Confirma rejeição semântica desses erros |
| Uma saída malformada e nove correctas | Lote completa dez episódios; 9 sucessos | Confirma classificação e continuação |
| Duas respostas correctas e uma falha técnica | Interrupção na terceira tentativa, um sentinel | Confirma política técnica de paragem |
| Retoma completa | Zero gerações adicionais | O loader simulado é chamado novamente; a identidade do diário só é conferida depois do loader |
| Dez casos semânticos manuais novos | 10/10 expectativas satisfeitas | Casos positivos e negativos de evidência, candidatos, diagnóstico, suficiência e localização |
| Integridade | 48 membros com hash no arquivo; cópia local v2.6 coincide | Confirma preservação e consistência do pacote |
| Manifesto candidato | 20 hashes internos e 3 externos coincidem | Continua em rascunho |

Os 10/10 do teste do runner são respostas fixas fornecidas pelo verificador, não resultados de um modelo. Neste teste, os rótulos esperados vêm do ficheiro histórico de referência; não foram calculados por `replay.labels`. O tokenizer real e LMFE foram exercitados no smoke anterior, que também usou um gerador simulado. As duas verificações têm alcances complementares; nenhuma testa a geração do checkpoint em GPU.

## Lacuna demonstrada nos testes científicos

Introduzi numa cópia temporária uma mutação que troca:

```python
elif v == 'rejected': cert = any(not prediction(working, r) for r in cited)
```

por `cert = True`. Assim, uma refutação sem citar qualquer evidência passa a poder receber sucesso conjunto. **Todos os 32 testes originais continuam a passar.**

O contraexemplo concreto usa `pilot_07`: mantém veredicto, candidatos, diagnóstico e suficiência correctos, mas envia `evidence_ids: []`. O scorer original recusa sucesso; o mutante aceita. Esta é uma lacuna demonstrada da suite, não uma aceitação errada demonstrada no scorer original.

Construí também um estado manual pequeno, sem derivar expectativas das funções semânticas do scorer: A prevê pelo glifo, B pelo contexto, e duas observações com o mesmo glifo têm saídas diferentes conforme o contexto. B explica ambas; A é refutado pela segunda. Dez verificações manuais passaram no scorer original. Duas delas detectam o mutante: refutação sem citação e refutação que cita apenas uma observação compatível com A.

Parte dos testes anteriores gera respostas usando `replay.labels` e `replay.prediction`, funções também usadas em `replay.score`. Essa parte verifica coerência interna. O replay histórico acrescenta âncoras de resultados guardados, e os novos casos manuais acrescentam expectativas externas; o número total de testes, por si, não estabelece validade científica.

## Congelamento ainda incompleto

O manifesto cobre pesos, `tokenizer.json` e `tokenizer_config.json`. A pasta do checkpoint também contém `config.json`, `generation_config.json`, `special_tokens_map.json`, `added_tokens.json`, `vocab.json` e `merges.txt`, sem cobertura no manifesto. É necessário incluir os ficheiros efectivamente usados no carregamento, começando pelas configurações do modelo e da geração, antes do congelamento. Esta observação não demonstra que esses ficheiros tenham mudado ou afectado uma avaliação anterior.

Inspeccionei o ambiente sem importar modelos: Python 3.12.3, Transformers 5.17.0, LMFE 0.11.3, Unsloth 2026.10.6, Torch 2.14.1+cu132 e bitsandbytes 0.50.2. Estes valores coincidem com os valores históricos citados. A pré-registração v2.6, porém, não contém a secção de ambiente que existia no candidato v2.5. O ambiente precisa de ser declarado e verificado como entrada do ensaio.

## Decisão e próximo bloco

**Ainda inapto para iniciar imediatamente inferência sob a alegação de validação encerrada.** A integração funcionou nos casos exercitados; falta incorporar a verificação semântica e completar o congelamento. Não surgiu evidência que imponha redefinir a tarefa neste bloco.

Podem ser feitos seguidos, sem checkpoints intermédios:

1. Integrar os casos manuais positivos e negativos e o teste de `trial_runner.run` no pacote seguinte; integrar a mutação do certificado e exigir que seja detectada.
2. Completar o manifesto com as configurações efectivamente carregadas e declarar o ambiente na pré-registração. Verificar identidade e estado da retoma antes de carregar o checkpoint.
3. Executar uma única verificação final do pacote resultante e fechar a análise pré-inferência com decisão fundamentada.
4. Se essa análise passar e houver autorização para o ensaio, congelar os documentos e executar uma vez os dez episódios de desenvolvimento, com o mesmo checkpoint e os limites registados. Analisar o lote completo por formato, legalidade e componentes científicos.

Os dez estados estão expostos: servem para regressão e diagnóstico. Um resultado positivo não validaria generalização, procura de informação, M17 ou o manuscrito. O resultado histórico v2.3 continua em 0/10; G1/G2 e reservas M17 não foram alterados.

O ponto obrigatório pedido pelo utilizador é uma análise antes de nova inferência. As correcções e verificações offline acima podem ser agrupadas; não requerem uma confirmação humana a cada passo.

## Reprodução

Na raiz do workspace:

```powershell
python -m unittest discover -s work/TRONCO01_TRIAL_v2_6/tests -v
python work/TRONCO01_V26_RESULT_REVIEW/verify_review.py
```

`verify_review.py` usa apenas biblioteca padrão, fakes e cópias temporárias; não modifica a v2.6. Guarda o resultado em `outputs/TRONCO01_V2_6_VERIFICACAO_INDEPENDENTE_2026-10-17.json`. `inspect_runtime.py` deve ser executado no Python WSL que contém as dependências e os caminhos Linux do manifesto; lê bytes e metadados de pacotes. O ZIP desta revisão inclui os scripts, resultados, este relatório e o pacote v2.6 original.

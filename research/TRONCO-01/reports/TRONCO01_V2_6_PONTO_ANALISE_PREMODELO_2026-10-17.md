# TRONCO-01 v2.6 — resultados até ao ponto obrigatório de análise

**Estado:** pacote técnico preparado para revisão humana. Pré-registo e manifesto continuam em rascunho. Não houve carregamento de pesos nem inferência.

## O que mudou

Foi criada uma cópia v2.6, deixando intactos os artefactos v2.5 e os resultados históricos. A cópia corrige e liga as peças que ainda faltavam:

- `model_backend.py` verifica internamente `__manifest_status__ == frozen_before_inference` antes de importar o loader. Um callback de teste permissivo já não consegue levar um manifesto draft até ao carregamento.
- `trial_runner.py` liga a agenda, o prompt Qwen, o harness e `replay.score`. Confere os hashes da pré-registração, agenda, prompt, pesos e tokenizer, além do limite de chamadas e da condição sem consultas.
- `mutation_check.py` só declara uma mutação detectada quando o teste sem mutação passa e a versão mutada falha por asserção, sem erros de execução.
- A agenda mantém os dez estados sintéticos anteriormente expostos. O protocolo é de desenvolvimento, com uma resposta e zero consultas por episódio; não permite estimar generalização nem isolar o efeito de cada alteração.

## Verificações reproduzidas

- **32 testes offline passaram.** Incluem relatórios correctos e incorrectos nos dez estados, scorer, localização do prompt no manifesto, saída EOS, retoma sem geração duplicada e sentinel numa falha técnica.
- **3 de 3 mutações dirigidas foram detectadas**, cada uma com baseline válido e falha de asserção. Isto substitui a alegação inválida do resultado v2.5: os seus três processos falharam ao importar `model_backend` e não testaram os mutantes.
- O caminho `Qwen25Generator.__call__` passou com o tokenizer Qwen e callback LMFE reais, mas usando um gerador simulado em CPU. Foram registados prompt de 517 tokens e saída de 50 tokens, incluindo EOS. **Não houve modelo aprendido nem pesos carregados.**
- O manifesto draft verificou **20 ficheiros internos e 3 externos**. Os hashes locais de pesos, `tokenizer.json` e `tokenizer_config.json` coincidem com a configuração candidata. O gate de produção recusa o estado draft.
- O replay dos registos v2.3 continua a dar **10 episódios, 19 chamadas, 4 saídas malformadas, 12 ações ilegais e 0/10 sucessos conjuntos**. São dados históricos; esta execução não os altera.

## O que estes resultados demonstram

As alterações surtiram efeito na integração e nos controlos técnicos: o runner agora pontua relatórios com o avaliador independente existente, os defeitos dirigidos são detectados e os estados draft são bloqueados antes de carregar o modelo. Os relatórios fixos mostram que o scorer aceita as respostas de referência nos dez estados e rejeita relatórios com veredicto alterado.

Isto **não demonstra melhoria do modelo** nem aptidão para M17. Não houve inferência aprendida, e os dez exemplos são repetidos e sintéticos. O piloto histórico permanece em 0/10. G1/G2, os dados do manuscrito e as reservas M17 continuam inalterados.

## Ponto obrigatório de análise

Antes de congelar o protocolo, a decisão humana deve incidir sobre: (1) utilidade de repetir os dez estados expostos como ensaio de desenvolvimento; (2) adequação de `replay.score` e dos critérios de sucesso conjunto; (3) política de falhas e limite de uma chamada; (4) aceitação de que qualquer diferença para v2.3 compara configurações completas e não identifica uma causa isolada.

Se a decisão for avançar, o próximo bloco é congelar pré-registo e manifesto, confirmar versões/runtime efectivos e executar uma única passagem fixa pelos dez episódios. Falhas de saída do modelo contam como falha e o lote continua; erro técnico/proveniência interrompe no sentinel. Depois analisa-se sucesso conjunto e cada componente. Um painel novo e não exposto será necessário antes de qualquer alegação de generalização; M17 exige validação separada.

## Artefactos

- Pacote reprodutível: `TRONCO01_TRIAL_v2_6/` dentro do ZIP entregue.
- `analysis_manifest_draft.json` permanece `draft_not_frozen`.
- `preregistration_draft.json` permanece `DRAFT_AWAITING_MANDATORY_ANALYSIS`.
- `protocol_status.json` regista zero chamadas, zero fine-tuning e zero carregamentos de pesos.

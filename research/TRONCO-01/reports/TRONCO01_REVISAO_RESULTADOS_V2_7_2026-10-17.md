# TRONCO-01 v2.7 — verificação, alcance e próximo bloco

**Decisão: instrumento apto para um pequeno ensaio de modelo em desenvolvimento, limitado ao contrato observacional atual.** Esta revisão cumpre o ponto obrigatório de análise anterior a nova inferência. Não encontrei, nos percursos exercitados, um defeito que obrigue a outra reescrita do núcleo antes desse ensaio. Não foi feita inferência aprendida nesta revisão; o pré-registo e o manifesto originais permanecem em rascunho.

## Resultados reproduzidos

| Verificação | Observado | Alcance |
|---|---|---|
| Suite v2.7 executada numa cópia temporária | 37 testes, zero falhas e zero erros | Inclui runner completo com saídas fixas e controlos de falha |
| Mutações dirigidas | 4/4 detetadas, com baselines válidos | Duplicação, identidade da retoma, gate de entrada e certificado de refutação |
| Integridade do pacote | CRC válido; 49 membros com hashes coincidem com os ficheiros locais | O membro adicional é o inventário de hashes |
| Manifesto e snapshot | 21 ficheiros internos e 11 artefactos externos conferidos | Conjunto de ficheiros, hashes e bloqueio draft confirmados |
| Runtime WSL | As seis versões declaradas coincidem | Identidade por versão; não equivale a uma imagem completa do sistema |
| Adaptador com tokenizer e LMFE reais | Smoke reproduzido numa cópia temporária, com modelo falso | JSON, callback de gramática e EOS; sem carregar pesos |
| Referência semântica separada | Concordância em 1.587 estados; 6.345 relatórios alterados recusados | Históricos de até duas observações distintas num domínio binário, três modelos de trabalho |
| Agenda candidata | 10 episódios, 9 estados públicos distintos | `pilot_01` e `pilot_02` são idênticos; todos os casos estão expostos |
| Replay histórico v2.3 | 19 chamadas, 4 saídas malformadas, 12 ações ilegais e 0/10 sucessos conjuntos | Leitura dos registos guardados; zero chamadas novas |

A referência separada interpreta literalmente as três tabelas públicas e calcula expectativas sem chamar `replay.labels`, `replay.prediction` ou `replay.score`. A enumeração inclui entradas iguais com saídas contraditórias. Verifica veredicto, conjunto de candidatos, ausência de certificado e invariância à ordem das observações. Não enumera todas as ações de localização, nem prova correção fora deste domínio. Os dez estados da agenda, incluindo os que têm três observações, foram também comparados com essa referência.

## As alterações surtiram efeito?

Sim, nos controlos técnicos e na capacidade dos testes para detetar regressões. Há uma precisão importante: **`replay.py` é idêntico entre v2.6 e v2.7**. A falha encontrada anteriormente era uma lacuna nos testes: o scorer original recusava corretamente uma refutação sem evidência, mas uma mutação que removia esse requisito passava na suite antiga. Agora essa mutação falha nos casos de refutação sem citação e de citação que não contradiz o modelo de trabalho. Não se deve descrever isto como uma correção de pontuações científicas que o scorer v2.6 calculava erradamente.

A v2.7 também move a verificação da identidade do diário para antes do carregador e incorpora testes do percurso `trial_runner.run`. As saídas fixas demonstram 10/10 sucessos para os relatórios de referência e 0/10 com veredictos alterados. Uma saída malformada conta como falha e permite continuar; uma falha técnica interrompe com sentinel. Os hashes dos restantes artefactos do checkpoint e as versões do runtime passaram a fazer parte dos controlos.

O erro de transcrição no hash candidato de `merges.txt` está resolvido: os bytes atuais coincidem com o hash do pré-registo draft e do manifesto. A verificação confirma consistência atual; um hash isolado não constitui prova de autoria ou autenticidade externa.

**Ainda não há uma medição de melhoria do modelo.** Os 10/10 referem-se a respostas fornecidas pelo teste; o smoke usa um modelo falso. O resultado aprendido histórico continua em 0/10. O próximo ensaio será a primeira medição do checkpoint através desta configuração corrigida.

## O que a tarefa permite concluir

O alvo é finito e bem delimitado: verificar compatibilidade do modelo de trabalho com observações públicas, listar os candidatos compatíveis e fornecer o certificado exigido. `supported` significa compatível com o histórico não vazio; não significa verdade universal. `undetermined` significa ausência de observações, segundo este contrato. A classificação da suficiência e o diagnóstico são propriedades adicionais desse mesmo histórico.

Esta definição distingue relatos verdadeiros e falsos para as tabelas declaradas, sem depender de uma categoria escondida. Não mede toda a noção de conclusão cientificamente justificada do pedido original. Assume observações completas, determinísticas e sem ruído. Diagnóstico e suficiência derivam do conjunto de candidatos e não são evidências independentes de capacidades distintas. Localização é facultativa: escolher `none` não demonstra capacidade de localizar uma discrepância. As consultas estão desativadas, pelo que o ensaio não mede aquisição de informação ou uso do orçamento.

Os dez episódios têm nove estados distintos e não formam uma amostra nova. A taxa agregada serve para diagnosticar esta configuração; não deve receber uma interpretação de generalização ou precisão populacional. A comparação com v2.3 será entre configurações completas, sem atribuir qualquer diferença a uma única alteração.

## Próximo bloco, executável seguido

1. Criar o registo do ensaio a partir do candidato v2.7 preservado, anexando esta decisão e declarando expressamente os nove estados distintos, a exposição anterior e o caráter de desenvolvimento. Manter uma chamada por episódio, zero consultas, o checkpoint atual e a ordem fixa.
2. Congelar pré-registo e manifesto antes de carregar o modelo. Calcular os hashes depois das alterações de estado e verificar os ficheiros, runtime e identidade do diretório de execução. A suite existente já passou; repeti-la apenas se houver alterações de código ou um problema concreto na preparação.
3. Executar uma única passagem pelos dez episódios. Não repetir saídas malformadas nem selecionar as melhores respostas. Erro de saída conta como falha e o lote continua; erro técnico ou de proveniência interrompe no sentinel e preserva os registos.
4. Conferir os registos por episódio e recalcular as pontuações. Apresentar formato, legalidade, EOS/truncação, veredicto, candidatos, diagnóstico, suficiência e certificado, além do sucesso conjunto. Reportar os episódios vazios duplicados explicitamente. Se o lote parar, apresentar os casos em falta e evitar usar a taxa dos concluídos como resultado do lote completo.
5. Comparar descritivamente com v2.3, sem inferência causal sobre cada alteração. Fechar um relatório de erros e decidir o único próximo alvo com base nas falhas observadas.

**Novo ponto obrigatório de análise: depois deste lote e da sua reavaliação independente, antes de modificar prompt, orçamento, gramática, modelo ou dados para tentar melhorar a taxa.** Se o lote funcionar, um painel novo e não exposto será necessário antes de falar em generalização. Se falhar, a análise por componente deve indicar a correção mínima. Não há motivo demonstrado para expandir a arquitetura neste bloco.

G1/G2, os resultados históricos e as reservas M17 permanecem preservados. Este parecer sustenta apenas o ensaio de desenvolvimento acima; não aprova M17, o manuscrito, fine-tuning ou modelos maiores.

## Reprodução e evidência

Na raiz do workspace:

```powershell
python work/TRONCO01_V27_RESULT_REVIEW/verify_review.py
```

No Python WSL que contém as dependências e o snapshot declarados:

```bash
python /mnt/c/Users/Bruno/Documents/Codex/2026-10-17/files-pasted-by-the-user-projeto/work/TRONCO01_V27_RESULT_REVIEW/inspect_runtime.py
```

Os scripts preservam o pacote v2.7. Suites, mutações e smoke que escrevem resultados correm em cópias temporárias. Os resultados desta revisão são `TRONCO01_V2_7_VERIFICACAO_INDEPENDENTE_2026-10-17.json` e `TRONCO01_V2_7_RUNTIME_VERIFICADO_2026-10-17.json`. O ZIP desta revisão contém scripts, relatório, resultados e o pacote v2.7 original.

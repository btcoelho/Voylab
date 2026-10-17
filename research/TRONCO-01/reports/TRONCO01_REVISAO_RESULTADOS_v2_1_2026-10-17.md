# Verificação dos resultados TRONCO-01 v2.1

**Decisão: as correções do núcleo tiveram efeito e os resultados guardados são reproduzíveis. O instrumento completo permanece inapto para iniciar um ensaio de modelo até se corrigirem dois defeitos de execução demonstrados e se verificar o adaptador do tokenizer.**

## Evidência desta revisão

Verificaram-se os 57 ficheiros do manifesto congelado: 13 do instrumento/controlo e 44 de evidência histórica. O preflight foi repetido numa cópia temporária com dados incluídos no pacote. Passaram os 22 testes e o processo devolveu PASS_FOR_PREMODEL_REVIEW. Os resultados da enumeração, mutações, gramática e reanálise histórica ficaram exatamente iguais aos guardados. Os ficheiros congelados originais ficaram inalterados.

As cinco sondas do painel de mutações também foram executadas sobre o código sem mutações e passaram. Isso confirma a condição de base desse painel: a morte de uma mutação não depende de uma lei que já falhasse no original. Não houve chamada a modelo; os exemplos de geração foram funções stub.

## As alterações surtiram efeito?

Sim, para os casos verificados:

- Uma referência de evidência inventada bloqueia a aprovação conjunta, mesmo junto de um contraexemplo verdadeiro.
- Uma cópia redundante com ID novo deixa o certificado invariável quando o conteúdo é o mesmo. Os IDs efetivamente citados continuam sujeitos a legalidade e unicidade.
- A refutação de W usa a informação observada, e o conjunto compatível considera todo o histórico.
- O ajuste de W, a ambiguidade entre candidatos e a suficiência para identificação têm saídas distintas.
- Localização inventada e associação confundida não obtêm crédito como contraste direto.
- O bruto é gravado antes de descodificação/aplicação. Alterar um ficheiro congelado faz o guard falhar.

A gramática em lm-format-enforcer passou os sete exemplos válidos e recusou os exemplos malformados testados. Esta verificação foi ao nível de caracteres. O adaptador Transformers/Qwen e EOS nos tokens reais continuam por verificar para o schema v2.1. Os testes da antiga gramática não certificam automaticamente a nova.

## Dois defeitos adicionais demonstrados

### A. Resultado PASS antigo permanece depois de uma falha nova

Numa cópia temporária, executou-se o preflight com sucesso; em seguida acrescentou-se um comentário a instrument.py e repetiu-se o preflight. O processo devolveu exit code 1 e identificou a divergência de hash, mas o ficheiro results/preflight_gate_v2_1.json conservou PASS_FOR_PREMODEL_REVIEW da execução anterior.

O guard falha corretamente. O defeito é de publicação do estado do gate: um consumidor que leia apenas o JSON pode confundir um PASS antigo com a avaliação atual. Correção mínima: produzir um resultado novo com identificador de execução e estado RUNNING/PASS/FAIL, gravado atomicamente, incluindo falhas iniciais de hash. A autorização de execução deve exigir um resultado correspondente aos hashes atuais, além de êxito do processo.

Impacto observado: esta revisão não encontrou uma execução de modelo autorizada por esse resultado antigo. O contraexemplo foi feito só numa cópia.

### B. Geração é chamada depois de o episódio terminar

Terminou-se um episódio legalmente e chamou-se FrozenExecutor.step com uma função de geração stub. A função foi chamada uma vez; só depois Episode.apply recusou a ação com “episode already terminated”.

A máquina de estados protege o estado, mas o wrapper verifica a terminação demasiado tarde. Num ensaio real isto pode consumir uma inferência desnecessária ou contaminar os denominadores de ações. Correção mínima: verificar episódio terminal antes de invocar a função de geração e testar que a contagem de chamadas fica em zero.

Impacto observado: uma chamada stub, nenhuma chamada a modelo. O teste existente cobre a terminação da máquina de estados, não esta fronteira do executor.

## O que os números permitem concluir

A enumeração de 10 368 estados confere conjuntos compatíveis e o veredicto de W num domínio de quatro pontos com variação de glyph/phase; setting e partner ficam fixos. Não enumera todo o instrumento, todos os certificados, transições, contrastes ou classes de estados inválidos. O painel de cinco mutações é direcionado. Esses limites não anulam os resultados; delimitam o seu alcance.

A reanálise continua a conter 235 execuções por condição em 30 mundos de desenvolvimento e 178 relatórios explícitos. São as mesmas respostas históricas. No braço base schema G2 há dois veredictos coincidentes com o alvo v2.1 em quatro relatórios, zero conjuntos exatos de candidatos e zero certificados suficientes; o quinto episódio não tem relatório explícito. Nenhum desses relatórios foi produzido sob o novo schema.

Logo, não há evidência nova de melhoria do modelo. A melhoria demonstrada é do contrato e da forma de medir. O alvo atual continua a ser um subproblema determinístico do TRONCO-01, com candidatos públicos e sem ruído. Não valida investigação autónoma geral ou inferência sobre manuscritos.

## Próximo bloco delimitado

1. Corrigir os dois defeitos de execução numa versão nova, preservando v2.1. Exigir resultado atual e atómico do gate e zero chamadas de geração após término.
2. Ligar a gramática do contrato corrigido ao tokenizer local efetivamente escolhido. Verificar caminhos completos e EOS para consultas e relatórios, incluindo diagnóstico/suficiência, ausência e presença de localização, casos malformados e respostas falsas mas legais. Nenhum carregamento de pesos é necessário.
3. Repetir apenas os testes afetados, a bateria necessária do pacote e a reprodução portátil; congelar código, dependências, prompt, tokenizer e configuração/schedule do eventual ensaio. A identidade dos pesos existentes tem de ficar documentada antes da inferência.
4. Emitir uma decisão de aptidão para esse runtime e contrato. Se passar, preparar um pequeno ensaio pré-registado com o modelo já disponível, com denominadores e critérios de paragem definidos antes dos resultados. O primeiro passo continua a ser corrigir e verificar o instrumento sem inferência.

Os critérios de fecho deste bloco são concretos: uma falha não pode deixar um PASS atual utilizável; um episódio terminado não pode chamar a geração; o tokenizer deve permitir terminar todos os exemplos válidos ensaiados; e a cadeia deve conservar os contraexemplos/certificados corretos. Não é necessária expansão arquitetural para cumprir estes critérios.

As sondas, resultados de reprodução e hashes estão em TRONCO01_VERIFICACAO_RESULTADOS_v2_1_2026-10-17.json. A repetição foi na mesma máquina e pelo mesmo operador; revisão externa continua ausente.

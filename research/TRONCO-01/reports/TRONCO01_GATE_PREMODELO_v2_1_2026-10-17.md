# TRONCO-01 — gate pré-modelo v2.1

**Resultado do gate local: PASS_FOR_PREMODEL_REVIEW.** A cadeia operacional corrigida passou os controlos pré-modelo que foram executados. Isto chega ao ponto de análise humana obrigatório; não autoriza nem inicia uma nova inferência.

Não houve geração por modelo, fine-tuning, carregamento de pesos ou acesso a reservas M17. A única função de geração usada nos testes era um stub determinístico para verificar a ordem do gate e do diário.

## O que foi integrado

A v2.1 fixa como afirmação primária se W prevê todas as observações públicas do episódio. Em campos separados, o agente apresenta os candidatos compatíveis, o diagnóstico none_fit/identified/ambiguous e a suficiência para identificação. A categoria escondida do gerador não altera as respostas esperadas.

A cadeia nova contém schema Draft 2020-12, descodificador de objeto JSON único, verificação estrutural, verificação de IDs e orçamento, avaliação de sustentação, localização opcional por contraste direto, máquina de estados e diário JSONL. O diário sincroniza a saída bruta em disco antes de a descodificar ou aplicar. Um guard verifica hashes do protocolo, código, testes e agenda no limite imediatamente anterior à função de geração; uma divergência bloqueia a chamada.

A política de certificado evita a instabilidade v2: observações idênticas por conteúdo contam uma vez para sustentar W. A citação ainda exige IDs existentes e únicos; uma refutação precisa de citar um contraexemplo real. Uma resposta errada mas legal continua a ser representável e pontuada como erro.

## Verificações

| Verificação | Resultado |
|---|---:|
| Testes pytest, incluindo sequências Hypothesis, orçamento, ordem, parser, diário e bloqueio por hash | 22 passaram |
| Enumeração por vetores de verdade independentes | 10 368 estados; 10 368 verificações de candidatos e 10 368 de ajuste de W |
| Mutações direcionadas no núcleo | 5/5 detetadas: IDs inventados, certificado parcial, dependência da ordem, duplicatas por ID e localização fabricada |
| Gramática JSON no lm-format-enforcer, nível de caracteres | 7/7 ações válidas chegam a EOS; relatório errado mas bem formado continua possível; campos extra, tipo errado, relatório incompleto e prefixo sem fecho não terminam |
| Diário em falha injetada | texto bruto permanece gravado antes da falha de aplicação |
| Hashes congelados | 13 ficheiros e agenda verificados no início e no fim do preflight |
| Reanálise G1/G2 | 235 episódios, 178 relatórios explícitos, 0 divergências na reprodução das respostas de consulta |

A execução está no ficheiro results/preflight_gate_v2_1.json do pacote. A bateria de mutações é deliberadamente direcionada, não uma campanha completa.

## Reanálise histórica

Os relatórios G1/G2 precedem o contrato v2.1. Nenhum passa o schema v2.1 completo porque não contém diagnosis e sufficiency e alguns ainda usam campos antigos. Isso mede incompatibilidade de formato, não incapacidade demonstrada do modelo sob o contrato novo.

| Condição histórica | Relatórios explícitos | Veredicto v2.1 coincidente | Conjunto exato de candidatos | Certificado suficiente |
|---|---:|---:|---:|---:|
| G1 base schema | 25 | 9 | 3 | 14 |
| G1 controlo simbólico | 25 | 20 | 25 | 20 |
| G2 base schema | 4 | 2 | 0 | 0 |
| G2 controlo simbólico | 5 | 4 | 5 | 4 |

Estas são componentes retrospectivas, não uma taxa conjunta v2.1 e não substituem resultados históricos. No G2 base schema, nenhum dos quatro relatórios explícitos satisfaz evidência e candidatos sob a nova regra. O quinto episódio terminou sem relatório. Os controlos não são desempenho de modelo. A mudança de v1 para v2.1 também mudou a pergunta operacional.

## Alcance e reserva

O resultado confirma que a cadeia de referência aplica de forma consistente o contrato determinístico delimitado. Não valida o alvo científico mais amplo para hipóteses omitidas, ruído, causalidade, manuscritos ou generalização.

A gramática foi verificada no parser de caracteres do lm-format-enforcer; o adaptador de tokenizer Transformers/Qwen não foi executado neste gate. O guard e a geração foram testados com ficheiros e função stub. A execução foi feita na mesma máquina e não houve revisão externa. A lista de hashes deteta alterações posteriores ao freeze, mas o manifesto local não tem assinatura externa.

## Ponto de análise obrigatório

O gate atingiu **pronto para revisão pré-modelo**, com **22 testes aprovados**. A decisão sobre adequação do contrato v2.1, sobre os limites científicos e sobre eventual ensaio pequeno deve ser tomada agora, antes de qualquer chamada de modelo. Se a decisão for avançar depois dessa análise, o trabalho seguinte é um pré-registo pequeno, limitado ao modelo já disponível, com critérios v2.1 congelados. Fine-tuning, modelos maiores e reservas M17 continuam fora deste bloco.

Reprodução: no pacote, instalar requirements.txt, executar freeze_sources.py uma vez após revisão e depois executar preflight.py. O pacote inclui os registos selecionados necessários à reanálise e exclui dados privados, pesos e reservas M17.

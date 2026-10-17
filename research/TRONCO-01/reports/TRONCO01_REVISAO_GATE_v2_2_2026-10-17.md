# TRONCO-01 v2.2 — resultado do gate pré-modelo

**Estado:** PASS para revisão pré-modelo. Não foi feita inferência nem carregamento de pesos.

## O que mudou e efeito observado

- O gate inicia com o estado `RUNNING` e publica o resultado atual atomicamente. Numa cópia descartável, injetei uma alteração num ficheiro congelado: a execução terminou com código 1 e o JSON atual passou a `FAIL`, sem conservar o PASS anterior.
- O executor verifica se o episódio terminou antes de consultar o guard ou chamar o gerador. A regressão confirma zero chamadas posteriores; a suíte completa passou com 23 testes.
- A gramática foi exercitada pelo callback de tokens do LM Format Enforcer com o tokenizer Qwen2.5 local (vocabulário 151 665), sem pesos. Duas ações válidas, incluindo um relatório errado mas estruturalmente válido, chegaram a EOS. Três ações malformadas foram bloqueadas.
- A enumeração verificou 10 368 estados; as cinco mutações direcionadas foram detetadas. A reanálise cobriu 235 episódios e 178 relatórios, sem erros de replay de consultas.
- Os 57 ficheiros congelados passaram a verificação de hash.

## Decisão

O efeito das alterações foi demonstrado e reproduzível. O instrumento está pronto para **revisão pré-modelo** de um ensaio pequeno e delimitado. A decisão não equivale a autorização para iniciar inferência: o ponto de análise obrigatório do protocolo vem agora, antes de qualquer nova avaliação. Não demonstra validade externa, nem resolve os limites do espaço enumerado, a cobertura parcial das mutações ou a ausência de validação do ciclo completo de geração do modelo. G1/G2 continuam resultados históricos; a reanálise v2.2 é retrospectiva.

## Próximos passos

1. Rever a especificação v2.2, o congelamento do protocolo, a identidade do modelo/pesos pretendidos, prompts, agenda e critérios do ensaio pequeno.
2. Se a análise aprovar esse desenho, registar previamente essas escolhas e só então executar o ensaio delimitado.
3. Comparar os resultados por episódio com a avaliação independente e decidir se a tarefa está apta para uma fase posterior.

O pacote executável preserva fontes e registos originais e inclui o código, testes, resultados e instruções de reprodução.

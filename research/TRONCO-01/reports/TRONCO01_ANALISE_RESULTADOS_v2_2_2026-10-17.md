# Verificação dos resultados v2.2

## Resultados confirmados

O arquivo ZIP está íntegro. Numa extração independente, os 57 ficheiros congelados coincidem com o manifesto e o preflight voltou a terminar com PASS_FOR_PREMODEL_REVIEW. A suíte repetida passou com 23 testes. Os restantes estágios passaram: enumeração de 10 368 estados, cinco mutações direcionadas, cinco trajetos de tokenizer e reanálise de 235 episódios/178 relatórios. A extração usou o ambiente Python já existente; não foi uma instalação limpa de dependências.

A verificação do tokenizer inclui dois trajetos válidos até EOS e três trajetos malformados bloqueados. Isto confirma esses exemplos no callback real do tokenizer, sem carregar pesos; não certifica toda a linguagem JSON nem a execução completa de um modelo.

## Efeito das alterações

O bloqueio de geração após terminação está implementado antes da chamada ao guard e ao gerador, com uma regressão que exige zero chamadas. A publicação do resultado do gate passou a substituir um PASS anterior por FAIL quando a falha ocorre dentro do bloco protegido, incluindo a divergência de hash testada anteriormente.

A conclusão anterior sobre a eliminação de PASS antigo precisa de ser restringida. O import de FrozenRunGuard ocorre antes de main() e antes de publicar RUNNING. Na cópia descartável substituí instrument.py por uma exceção na importação: o processo terminou com código 1, mas o JSON conservou PASS_FOR_PREMODEL_REVIEW e o run_id antigo. Não há demonstração de execução de um modelo apesar do erro; o problema comprovado é o estado persistido enganador se for consultado isoladamente.

Há ainda uma lacuna de reprodução: grammar_preflight.py importa transformers e torch, mas requirements.txt não os declara. O tokenizer usa um snapshot local configurável; o pacote não distribui os ficheiros desse tokenizer. O sucesso no ambiente atual não demonstra instalação autónoma noutro computador.

## Alcance científico

Estes resultados demonstram melhorias no instrumento de avaliação e execução. Não houve nova inferência, nem evidência de melhoria da capacidade do modelo. G1/G2 permanecem históricos. O alvo operacional continua a ser ajuste a observações públicas de tabelas determinísticas; supported não implica verdade geral, causalidade nem transferência para manuscritos.

## Decisão e próximo bloco

O núcleo passou os controlos descritos para esta tarefa delimitada. A execução automatizada ainda deve fechar os dois pontos concretos acima antes do pequeno ensaio. Não é necessária uma expansão de arquitetura.

O próximo bloco pode ser feito seguido:

1. Colocar a importação do instrumento dentro do tratamento que publica RUNNING/FAIL e acrescentar a regressão da falha de inicialização. Um consumidor do resultado deve exigir sucesso do processo e identidade da execução atual.
2. Declarar as dependências efetivamente usadas e documentar a identidade/configuração do tokenizer. Verificar reprodução com essas dependências declaradas.
3. Repetir uma vez o gate corrigido e congelar um protocolo concreto do pequeno ensaio: modelo existente e pesos identificados, prompt, agenda de desenvolvimento, orçamento, limites de geração, tratamento de erros e medidas por episódio.
4. Entregar a decisão de aptidão e esse protocolo no ponto de análise obrigatório antes da inferência, conforme o pedido original. Se aprovado, executar o ensaio como exploração de desenvolvimento, com critérios fixos e preservação dos registos brutos.

Evidência executável da revisão: TRONCO01_REVISAO_INDEPENDENTE_v2_2_2026-10-17.json. O código congelado e o pacote v2.2 originais não foram alterados nesta revisão.

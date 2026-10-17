# Revisão dos resultados v2.3 e próximo bloco

## Resultado da conferência

O ZIP final está íntegro e contém 67 entradas. Confirmei os 57 hashes congelados tanto na pasta de trabalho como na extração. Os 24 testes passaram novamente a partir do ZIP, incluindo as regressões de falha de importação e bloqueio de geração após terminação. A verificação de dependências do ambiente isolado terminou sem conflitos; esse ambiente não contém PyTorch. Os cinco ficheiros de resultados derivados conferidos coincidem entre a pasta de trabalho e o arquivo.

Os resultados guardados confirmam o gate PASS, enumeração de 10 368 estados, cinco mutações selecionadas detetadas, dois trajetos válidos do tokenizer até EOS e três malformados bloqueados, além da reanálise de 235 episódios e 178 relatórios sem erros de replay. Nesta revisão repeti a suíte e a integridade; não repeti todos os estágios do gate, que já tinham sido reproduzidos em ambiente novo e na extração final. Não alterei o instrumento nem executei inferência.

## Efeito e alcance

As correções tiveram efeito nos defeitos reproduzidos. A falha de importação já publica FAIL com run_id atual; episódios terminados já impedem novas chamadas; a verificação do tokenizer pode ser instalada e executada sem a dependência pesada de PyTorch. O efeito observado pertence ao instrumento. Ainda não existem novas medidas da capacidade do modelo.

O núcleo tem suporte suficiente para um pequeno ensaio de desenvolvimento dentro do contrato determinístico escrito. A análise obrigatória do núcleo pode ser encerrada com este alcance. A execução do ensaio depende agora de estímulos, prompt, configuração e integração congelados. Cobertura finita, painel de mutações e testes locais não demonstram validade geral, revisão por outra pessoa ou transferência para o Voynich.

## Ajuste necessário ao desenho proposto

Dez sementes arbitrárias não garantem testar insuficiência ou os três diagnósticos. A seleção deve ser feita antes da inferência, pelos critérios públicos que o avaliador usa. Uma agenda pequena útil é:

| Tipo de estado público | Veredicto esperado | Diagnóstico esperado | Episódios |
|---|---|---|---:|
| Histórico vazio | undetermined | ambiguous na classe com três candidatos | 2 |
| W ajusta H; mais de um candidato ajusta H | supported | ambiguous | 2 |
| W ajusta H; apenas W ajusta H | supported | identified | 2 |
| W falha; apenas outro candidato ajusta H | rejected | identified | 2 |
| Nenhum candidato ajusta H, incluindo W | rejected | none_fit | 2 |

Isto constitui amostragem intencional de desenvolvimento. O histórico vazio tem sufficiency=no_observations; a suficiência de identidade tem de ser pontuada separadamente do ajuste de W. Não se deve interpretar supported como confirmação geral de uma hipótese. Os exemplos devem respeitar o domínio declarado e ter chaves/oráculos separados dos prompts. As reservas M17 continuam fechadas.

## Próximo bloco contínuo recomendado

1. Construir e auditar os dez episódios segundo a matriz, fixar o prompt integral e o backend do checkpoint local proposto. Congelar estímulos, código, parâmetros, tokenizer, pesos e agenda antes da primeira chamada. A agenda de preflight atual é só uma fixture; não serve como agenda do ensaio.
2. Integrar o ciclo de chamada, diário bruto e avaliador auditado, verificando a interação com respostas simuladas e o gate. Usar o contrato existente; alterações semânticas exigem nova análise.
3. Executar o primeiro episódio como sentinela técnica, contando-o entre os dez. Prosseguir automaticamente com os nove restantes se a execução respeitar o protocolo. Uma resposta científica errada não é motivo para interromper ou repetir. Uma falha que invalide o registo ou a avaliação exige parar e preservar o ocorrido.
4. Fechar o lote: máximo de quatro chamadas por episódio, dez episódios, sem treino ou ajustes depois de observar respostas. Relatar todos os episódios, componentes da pontuação, truncações, ações ilegais e número de consultas. Uma resposta truncada não é um relatório completo; se gerar ação extra, o limite de chamadas continua a aplicar-se.
5. Fazer a análise obrigatória dos resultados do lote antes de ampliar a amostra, mudar o prompt ou treinar. G1/G2 mantêm o estatuto histórico; os números do novo lote são exploração de desenvolvimento.

Esta revisão antecede a proposta de nova inferência. Nenhuma chamada ao modelo foi feita nesta conferência.

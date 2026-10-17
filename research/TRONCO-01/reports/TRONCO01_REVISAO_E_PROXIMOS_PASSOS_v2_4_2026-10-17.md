# Revisão dos resultados v2.4 e próximo bloco

Data: 2026-10-17. Esta revisão reproduziu os testes existentes, confrontou o resumo com o diário e acrescentou contraexemplos offline. Não carregou pesos, não fez inferência e não alterou o pacote v2.4, G1/G2, o lote v2.3 ou as reservas M17.

## Conclusão

As alterações melhoraram comportamentos concretos da infraestrutura. Ainda não há resultados de modelo com a v2.4 e, portanto, não há evidência de melhoria do raciocínio científico. A formulação anterior «preparação offline aprovada» deve ser entendida como aprovação dos casos então testados: esta revisão encontrou duas lacunas adicionais. O instrumento continua inapto para iniciar o próximo ensaio na configuração atual.

## Evidência conferida

- Os 16 testes existentes voltaram a passar, em 0,111 segundos. O número de testes é um registo de execução, não uma demonstração de validade.
- Os 21 hashes do manifesto do ZIP coincidem com os membros arquivados e com os ficheiros atuais no disco; o teste de integridade ZIP passou.
- O replay independente voltou a produzir exatamente o resumo guardado: 10 episódios, 19 chamadas, quatro saídas malformadas no limite de 256 tokens sem EOS, 12 ações ilegais, três relatórios legais, zero consultas e zero sucessos conjuntos.
- As 12 ações ilegais guardadas citam observações inexistentes. Mesmo removendo o campo de explicação antigo, o validador v2.4 recusa as 12 ações. Isto demonstra o efeito da restrição estrutural nos registos antigos; não prevê o que o modelo produziria sob a nova gramática.
- A pré-verificação guardada do tokenizer contém quatro caminhos completos com EOS e sete caminhos inválidos bloqueados. A revisão conferiu esse ficheiro e o código correspondente; não repetiu a pré-verificação completa do tokenizer. O relatório de 70 tokens é um exemplo com listas extensas, não uma prova de que qualquer geração termine dentro de 256 tokens.

## O que surtiu efeito e qual é o seu alcance

| Alteração | Evidência | Alcance |
|---|---|---|
| Resumo reconstruído do diário | Replay e testes de contagem, taxa e sentinela | Corrige agregação e classificação retrospectiva; não muda respostas antigas. |
| Bloqueio de IDs inexistentes | As 12 ações ilegais antigas são recusadas pelo validador novo | Fecha a aceitação desses IDs; a ligação ao gerador real continua por testar. |
| Feedback após rejeição | Teste simulado muda o segundo prompt e permite terminar | Aplica-se a rejeições de `apply`; erros de JSON ou de esquema terminam o episódio sem esse feedback. |
| Retoma de episódio parcial | Testes recusam interrupções e duplicados | Protege esses casos; a identificação completa do protocolo na retoma tem a lacuna abaixo. |
| Resposta curta e sem explicação | Prompt novo e caminhos guardados no tokenizer | Mostra que há respostas curtas admissíveis; não demonstra redução real de truncações. |
| Gramática sem seleção da resposta científica | Um relatório errado continua estruturalmente admissível | É um controlo útil contra fornecer a resposta; um exemplo não prova ausência de qualquer fuga possível. |

## Dois problemas adicionais reproduzidos

### D1 — Divergência entre gramática e validador para duplicações

Regra pretendida: `uniqueItems: true` nas listas de candidatos, evidências e valores de localização.

Comportamento observado: o parser de caracteres do LM Format Enforcer aceita uma ação completa com `["A","A"]`, `["o1","o1"]` ou valores de localização `["g0","g0"]`, respeitando os restantes limites de comprimento. O validador Python rejeita os três casos.

Classificação: defeito demonstrado na conformidade entre os dois mecanismos. O ensaio foi ao nível de caracteres; não executou geração nem um percurso de tokens destes exemplos.

Impacto: a validação final impede que essas ações sejam pontuadas como relatórios válidos, mas a restrição usada durante a geração não garante a mesma linguagem. Hoje isso pode terminar como `model_output_failure`, sem oportunidade de correção. Não foi demonstrado que este defeito tenha ocorrido no lote v2.3.

Correção mínima proposta: fazer a gramática de produção respeitar a unicidade ou documentar explicitamente a restrição como pós-validação e congelar a política correspondente. Para manter a promessa atual de impedir essas saídas, recomenda-se a primeira opção, sem normalização silenciosa das listas. Acrescentar os três contraexemplos ao teste do parser e ao percurso real de tokens, e demonstrar que uma mutação que reintroduza duplicados é detetada.

### D2 — Retoma concluída não verifica a identidade dos inputs

Regra pretendida: um diário e os seus resultados pertencem à agenda e ao protocolo congelados.

Contraexemplo mínimo: executar um episódio simulado; alterar o ficheiro congelado da agenda, mantendo o ID do episódio; voltar a chamar `execute_trial`. O `FrozenManifestGuard.verify()` deteta a alteração quando chamado diretamente, mas a retoma devolve o resumo antigo e faz zero verificações do guard, porque já não há episódios por gerar. Também não compara os estados públicos recebidos com os guardados no diário.

Classificação: defeito demonstrado de verificação da proveniência na retoma. Não demonstra que um ficheiro alterado passe pelo guard antes de uma nova geração; esse guard funciona no teste existente. Não altera a correção das pontuações antigas.

Impacto: um chamador pode receber resultados antigos ao fornecer uma agenda diferente com os mesmos IDs, sem indicação da incompatibilidade. Não há evidência de que isso tenha contaminado v2.3; o replay deste lote voltou a conferir os estados usados nos prompts.

Correção mínima proposta: verificar o manifesto ao entrar no ensaio, incluindo retomas sem chamadas; guardar no início uma identidade canónica do protocolo, agenda, prompt, esquema e configuração; comparar essa identidade e os estados dos episódios antes de aceitar qualquer retoma. Não permitir que um manifesto novo faça passar o diário antigo por uma execução da nova configuração. Acrescentar regressões para agenda alterada com IDs iguais, manifesto substituído e retoma integralmente concluída.

## Próximos passos que podem ser executados num único bloco

1. Corrigir D1 e D2 numa revisão nova, preservando o pacote v2.4 como o objeto desta análise. Definir claramente quais as rejeições que admitem feedback e quais terminam o episódio.
2. Executar os contraexemplos desta revisão como regressões e introduzir mutações que reabram os dois defeitos. Verificar aceitação de ações válidas e preservação de respostas cientificamente erradas mas estruturalmente válidas.
3. Integrar o adaptador de geração com o harness e a gramática, usando primeiro um backend simulado. Conferir estado público, esquema enviado, saída bruta, contagem de tokens, EOS, interrupção, sentinela e retoma através do mesmo caminho de código a usar no ensaio. A conformidade entre o schema e o backend não pode ficar demonstrada apenas por callbacks artificiais.
4. Preparar uma pré-registração própria para um pequeno ensaio de resposta científica direta, mantendo o checkpoint anterior como primeira escolha e congelando hashes, parâmetros, limite de tokens, agenda de desenvolvimento, denominadores e critérios de paragem. Uma agenda deve ter hash fixo e nenhuma seleção posterior com base nos resultados. Registar uma referência independente para os estados escolhidos.
5. Encerrar esse bloco com um único ponto de análise antes da primeira inferência. Só depois de resolvidas as divergências, de passar a integração e de o protocolo estar congelado, iniciar o ensaio real previsto nesse protocolo.

O objetivo inicial recomendado é resposta científica direta, porque os dez estados antigos admitem um relatório correto imediato: zero consultas não prova uma incapacidade de investigar. Uma avaliação da política de consulta exige outro critério explícito de aquisição de informação e não deve ser confundida com este diagnóstico da interface. Não se justifica expandir a arquitetura, fazer fine-tuning ou introduzir um modelo maior neste bloco.

## Reprodução desta revisão

O ficheiro `TRONCO01_VERIFICADOR_REVISAO_v2_4.py` usa o pacote e o arquivo originais nas suas localizações do workspace. Usa ficheiros temporários para o contraexemplo de retoma. Sem `--grammar` só requer a biblioteca padrão; a opção `--grammar` usa o ambiente de dependências registado na v2.4 e importa o parser, sem carregar tokenizer ou pesos. O JSON desta revisão contém os três contraexemplos de duplicação, a retoma alterada, a conferência de hashes e as 12 ações históricas verificadas.

O replay é uma implementação de referência separada e não importa as funções semânticas do avaliador original. Foi produzido neste projeto; isso não equivale a reprodução por um investigador externo.

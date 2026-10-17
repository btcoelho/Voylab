# Verificação dos resultados v2 e decisão sobre continuidade

**Decisão: houve progresso na definição e na verificação de um subproblema, mas o instrumento completo permanece inapto para novo ensaio de modelo.** Os resultados retrospectivos são reproduzíveis. Há duas questões adicionais a resolver: a composição da legalidade com a pontuação e o efeito da política de citação sobre duplicatas redundantes.

## O que foi conferido

Os nove testes v2 passaram novamente. A reanálise foi executada numa diretoria temporária usando as fontes/registos preservados. O resumo e todos os perfis por episódio ficaram exatamente iguais aos ficheiros guardados: 235 execuções por condição, 178 relatórios explícitos, zero divergências no replay das respostas de consulta. Não são 235 mundos independentes: o corpus corresponde a 30 mundos de desenvolvimento, com múltiplas condições por mundo.

Os hashes do núcleo, especificação, script de reanálise e resultados v2 ficaram iguais antes e depois desta verificação. As sondas adicionais e os resultados completos estão em `TRONCO01_VERIFICACAO_V2_2026-10-17.json`. Não houve nova inferência de modelos.

## Efeito das alterações

| Alteração | Efeito verificado | Alcance |
|---|---|---|
| Separar ajuste de W de identificação entre candidatos | W pode receber `supported` enquanto o diagnóstico é `ambiguous` | Resolve a ambiguidade de significado neste subproblema |
| Conferir candidatos contra todo o histórico | Um candidato refutado por uma linha disponível não pertence ao conjunto compatível | Correção demonstrada no núcleo independente |
| Usar contraexemplo citado para refutação | Uma observação que contradiz W basta para a refutação | Não exige identificar uma alternativa única |
| Conferir localização por contraste direto e valores observados | A localização inventada e o par com outros campos confundidos são recusados | Função isolada; não é um avaliador de localização integrado ao sucesso conjunto |
| Ignorar a categoria geradora na conclusão | Trocar NORMAL por CHANGE mantendo o estado público não altera a avaliação | Impede esse canal oculto no núcleo v2 |
| Exigir citação integral para suporte | Um relatório que cite apenas parte do histórico perde o certificado | Regra de rastreabilidade nova; não é uma melhoria de capacidade do modelo |

O núcleo antigo e os executores G1/G2 não foram corrigidos por esta implementação. Foi criada uma referência alternativa. Parsing, gramática, aplicação de ações, logging e gate de execução continuam por integrar numa versão nova e verificável.

## Duas reservas encontradas nesta revisão

### 1. Pontuação sem bloqueio da legalidade

Contraexemplo mínimo: duas observações tornam apenas C compatível e refutam W=A. O relatório declara `rejected`, candidatos `[C]` e cita `[b, invented]`, sendo b um contraexemplo verdadeiro. `assess` devolve simultaneamente `science_supported=true` e `unobserved_evidence_ids=[invented]`.

O núcleo pressupõe uma camada anterior de validação. Portanto, isto demonstra uma lacuna de composição: o indicador não é seguro como decisão final sem um bloqueio explícito da legalidade. A interpretação da refutação sobre b continua correta; o relatório completo contém uma referência ilegal. A futura decisão final precisa de exigir descodificação válida, estrutura válida, legalidade e sustentação, mantendo os indicadores separados para diagnóstico.

Impacto histórico verificado: **0 dos 178 relatórios explícitos possuem IDs de evidência não observados nesta reanálise**. Este contraexemplo não altera os números guardados; demonstra que os nove testes não bastam para aprovar o instrumento completo.

### 2. Duplicata redundante altera o certificado

Com H=[a], um relatório compatível que cite a recebe sucesso conjunto. Acrescentando uma cópia idêntica de a com outro ID, o veredicto e os candidatos compatíveis não mudam, mas o mesmo relatório perde o certificado por não citar o novo ID.

Isto segue a regra v2 de citar todas as linhas. É uma escolha de especificação discutível, em conflito com a pretendida invariância da sustentação à duplicação de um registo. O teste existente de duplicatas verifica apenas o conjunto compatível e não a pontuação completa. A versão seguinte deve definir a distinção entre cópia redundante e nova medição e verificar o certificado sobre essa definição. Nas tabelas determinísticas, uma opção mínima é exigir cobertura das observações distintas por conteúdo, conservando a validação de todos os IDs citados.

## Como interpretar os números

No braço G2 base schema, dois dos quatro veredictos coincidem com o alvo de ajuste observacional. Nenhum dos quatro tem certificado suficiente ou conjunto exato de candidatos sob v2. Logo, 0/4 relatórios explícitos satisfazem o critério conjunto, correspondendo também a 0/5 episódios planeados nesse braço quando se inclui a falha operacional. O braço livre continua sem relatórios explícitos.

O controlo simbólico G2 passa de 5/5 decisões históricas para 4/5 sob o alvo v2. Isto é mudança do significado da pergunta e dos requisitos do relatório; o controlo não foi reexecutado nem adaptado ao novo contrato. Não demonstra deterioração ou melhoria do agente. Pelo mesmo motivo, comparar diretamente taxas v1 e v2 não estima o efeito causal das correções.

Há ainda um limite científico: em v2, com qualquer observação presente, o alvo principal só permite ajuste ou refutação; `undetermined` fica reservado ao histórico vazio. Assim, a competência de reconhecer insuficiência com dados presentes precisa de permanecer uma saída explícita sobre identificação/previsão. Verificar tabelas determinísticas é um subproblema útil do TRONCO-01, mas não valida a capacidade científica geral originalmente pretendida.

## Próximo bloco, executável em conjunto

1. **Fechar o contrato v2.1.** Manter explícitos ajuste de W, identificação/insuficiência entre candidatos e o significado do certificado. Resolver a política de duplicatas e citação. Qualquer previsão exige um domínio declarado. Não voltar a usar rótulos geradores como resposta esperada.
2. **Integrar uma cadeia nova completa.** Um schema canónico deve alimentar gramática e validação; o parser deve preservar o bruto e recusar interpretações ambíguas. Gravar o bruto antes de aplicar a ação. O resultado final deve exigir legalidade e sustentação, conservando ambas as métricas. Conferir fontes congeladas e agenda na fronteira de execução.
3. **Reproduzir e eliminar os defeitos demonstrados.** Exercitar pares contraditórios mínimos, testemunhos alternativos, ordem, IDs, duplicatas, referências inventadas, localizações e sequências de consulta. Verificar orçamento, término e EOS da gramática. Fazer mutações sobre o núcleo efetivamente integrado v2.1; a campanha v1 não certifica automaticamente esta versão.
4. **Verificar o comportamento completo sem LLM.** Usar respostas fixas corretas, erradas mas legais, malformadas e truncadas. Um controlo determinístico conforme ao novo contrato deve passar casos manuais com respostas escritas independentemente. A bateria deve recusar os erros relevantes e preservar os testemunhos válidos. Reanalisar G1/G2 apenas para medir impacto retrospectivo.
5. **Produzir novo parecer de aptidão.** Entregar código, especificação congelada, contraexemplos, diferenças de reanálise e um comando de reprodução portátil. Parar nesse ponto para análise. Uma execução por outra pessoa acrescentaria verificação externa; a atual repetição na mesma máquina não equivale a isso.

Este bloco pode decorrer seguido, sem novas chamadas de modelo. A decisão sobre um pequeno ensaio deve ocorrer depois de se verificar a cadeia integrada. O efeito positivo já demonstrado é a clarificação do alvo e a reprodução verificável dos resultados; melhoria do desempenho de um modelo ainda não foi medida.

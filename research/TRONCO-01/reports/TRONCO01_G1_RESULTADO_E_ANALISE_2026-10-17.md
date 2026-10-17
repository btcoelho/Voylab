# TRONCO-01 — resultado e análise do G1

**Data:** 17/10/2026  
**Estado:** G1 v0.2 concluído em desenvolvimento; ponto de análise obrigatória atingido.  
**Decisão:** não abrir as reservas, não fazer fine-tuning e não aprovar M17.

## Execução e integridade

O primeiro ensaio do sentinela, v0.1, foi invalidado como avaliação científica. A gramática aceitava campos de relatório dentro de ações `query` e permitia relatórios incompletos. O validador G1 rejeitou essas saídas, mas o pré-teste inicial não verificava essas combinações. Mantive o registo bruto em `run_20261017`; não o contei como resultado dos modelos.

Corrigi a interface para usar dois ramos de gramática estritos, um para consulta e outro para relatório. O novo pré-teste foi concluído sem carregar pesos: 100 estados, 825 IDs de consulta legais alcançáveis, 200 referências inválidas rejeitadas e 275 caminhos de schema inválidos bloqueados. Também confirmou o limite de contexto, o orçamento de consultas e a ausência de rótulos ocultos no estado público.

O G1 v0.2 foi pré-registado e executado em 25 mundos de desenvolvimento equilibrados, cinco por categoria. Os mundos não se sobrepõem ao piloto M17 anterior, às fixtures G0g nem à tentativa v0.1. Os hashes do checkpoint base e do adaptador M16 coincidem com os do G0g. As reservas diagnóstica e de confirmação permaneceram fechadas.

Ambas as condições com schema passaram o sentinela operacional: 5/5 relatórios explícitos, sem falhas de geração, parser, truncamento ou ação inválida. A regra congelada avançou então para os outros 20 mundos. O lote terminou completo.

## Resultados nos 25 mundos

| Condição | Relatório explícito | Decisão correta | Diagnóstico com evidência | Sensibilidade a problemas¹ | Especificidade | Insuficiência reconhecida | Ações inválidas | Consultas médias |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Base, wrapper M17 atual | 0/25 | 0/25 | 0/25 | 0/15 | 0/5 | 0/5 | 25 | 0,00 |
| M16, wrapper M17 atual | 0/25 | 0/25 | 0/25 | 0/15 | 0/5 | 0/5 | 25 | 0,00 |
| Base + instrução G1 + schema | 25/25 | 9/25 | 2/25 | 6/15 | 2/5 | 1/5 | 0 | 2,92 |
| M16 + instrução G1 + schema | 24/25 | 4/25 | 2/25 | 0/15 | 4/5 | 0/5 | 1 | 1,48 |
| Detetor estatístico | 25/25 | 15/25 | 11/25 | 10/15 | 5/5 | 0/5 | 0 | 0,00 |
| Consulta aleatória | 25/25 | 19/25 | 10/25 | 14/15 | 5/5 | 0/5 | 0 | 3,00 |
| Consulta fixa | 25/25 | 19/25 | 10/25 | 14/15 | 5/5 | 0/5 | 0 | 3,00 |
| Controlo simbólico ativo | 25/25 | 25/25 | 25/25 | 15/15 | 5/5 | 5/5 | 0 | 0,40 |

¹ Problemas identificáveis: contradição, mudança e hipótese ausente, n=15. Especificidade usa os cinco mundos normais; insuficiência usa os cinco casos próprios. “Diagnóstico com evidência” exige o critério mais estrito de identificação/localização do avaliador. Todos os denominadores são episódios; as consultas dentro de um episódio não são réplicas.

### Onde erraram os modelos

O base com schema emitiu dez relatórios `supported`, dez `rejected` e cinco `undetermined`. Acertou 2/5 casos normais, 3/5 contradições, 1/5 insuficiências, 1/5 mudanças e 2/5 casos sem hipótese adequada. Só dois episódios passaram o diagnóstico com evidência. A confiança média foi 0,90, apesar de 9/25 decisões corretas; o Brier calculado apenas nos 25 relatórios emitidos foi 0,522.

O M16 com schema emitiu `supported` em 24 dos 25 episódios. Acertou 4/5 casos normais e nenhum dos 15 problemas identificáveis nem dos cinco casos de insuficiência. Passou o diagnóstico com evidência em 2/25. A confiança média nos 24 relatórios foi 0,9125, contra 4/24 decisões corretas; o Brier nesses relatórios foi 0,722. A única falha operacional ocorreu num episódio de desenvolvimento.

Os wrappers M17 sem a instrução G1 também falharam operacionalmente em todos os episódios: o modelo base respondeu com texto de recusa ou pedido de contexto, e o M16 emitiu `review`, uma ação incompatível com o ambiente M17. A condição G1 combina instrução explícita e descodificação restrita; este ensaio não separa o efeito de cada componente.

O base fez 73 consultas em 25 episódios. O ganho médio de informação sobre o conjunto de hipóteses foi 0,110 por consulta, perto dos controlos aleatório e fixo (0,107). O M16 fez 37 consultas, com ganho médio 0,108. Não há evidência neste lote de que as consultas escolhidas pelos modelos superem as consultas aleatórias/fixas. O controlo simbólico ativo resolveu os 25 mundos com média de 0,4 consultas; serve como controlo de resolubilidade no ambiente, não como resultado de um LLM.

O contraste entre 14/15 de sensibilidade dos controlos aleatório/fixo e 0/5 de reconhecimento de insuficiência mostra que detetar anomalias ou rejeitar hipóteses não basta para demonstrar triagem científica. As estimativas são exploratórias e os intervalos são largos com n=5 por categoria.

## Leitura científica

O G1 v0.2 demonstra que a gramática torna a interação executável. Não demonstra que o agente escolha consultas informativas, reconheça insuficiência, calibre confiança ou localize a evidência que justifica a conclusão. A falha principal passou da interface para a decisão e para o diagnóstico: o base consulta quase todo o orçamento sem vantagem mensurável sobre consultas aleatórias, e o M16 tende a sustentar o modelo mesmo nos casos problemáticos.

Logo, **M17 continua não aprovado**. O ensaio é apenas desenvolvimento; não sustenta transferência nem taxas populacionais de erro. O campo de calibração do resumo automático original inclui episódios sem relatório explícito; os valores Brier acima foram recalculados apenas sobre relatórios emitidos.

## Próximo bloco recomendado

1. Preservar o G1 v0.2 como resultado de desenvolvimento negativo e não alterar os critérios retroativamente.
2. Fazer uma análise de erro por relatório: suficiência das evidências citadas, hipóteses compatíveis, localização e decisão de parar/consultar. Usar os 25 mundos já expostos apenas para explicar falhas, sem os tratar como nova confirmação.
3. Escolher uma intervenção única para desenvolvimento — por exemplo, testar um modelo de referência mais capaz sob o mesmo protocolo ou testar uma instrução explícita para justificar `query`/`report` e `undetermined`. Qualquer roteador externo que decida a ação passa a ser condição híbrida separada.
4. Pré-registar a intervenção e os respetivos critérios em mundos novos de desenvolvimento. Só depois de uma nova análise independente discutir se faz sentido abrir uma avaliação reservada. Não treinar até existir uma lacuna específica e uma comparação que consiga atribuir o ganho.

## Artefactos

- [Pacote reproduzível G1](</C:/Users/Bruno/Documents/Codex/2026-10-17/files-pasted-by-the-user-projeto/outputs/TRONCO01_G1_REPRODUCIBLE_2026-10-17.zip>)
- [Relatório G0g e revisão do plano](</C:/Users/Bruno/Documents/Codex/2026-10-17/files-pasted-by-the-user-projeto/outputs/TRONCO01_REVISAO_G0G_E_PROXIMO_BLOCO_2026-10-17.md>)



# Especificação mínima de auditoria — versão 1

Esta é uma especificação de referência explícita, criada para auditar o instrumento.
Não substitui retroativamente M17/G1/G2 nem foi integrada nos seus executores.

## Universo e pressupostos

Um estado público contém o histórico H de entradas completas e saídas observadas,
um modelo de trabalho W, candidatos C, um menu de consultas Q e um orçamento B.
Uma entrada tem glyph, setting, partner e phase. Cada uma das três formas públicas
de tabela é interpretada literalmente e deterministicamente. Sem essas hipóteses,
um conflito pode ser ruído, erro de medição ou variáveis omitidas: não atribuímos causa.

`reference_core` só reconhece as três declarações públicas exatas, por contrato.
Não interpreta linguagem livre, não descobre novas hipóteses, não testa causalidade.
Dados com IDs duplicados ou tabelas incompletas exigem validação do estado antes de uso;
os estados do corpus histórico têm representação válida e o teste finito mantém essa pré-condição.

Seja F(H) o conjunto de candidatos que acertam TODAS as observações de H.
Igualdade de IDs de candidato não implica equivalência de previsões. Modelos distintos
podem prever o mesmo em Q e divergir num domínio externo D. D deve ser declarado.

## Três afirmações diferentes

1. **Compatibilidade observacional do modelo de trabalho (`observed_fit`).**
   `supported`: W pertence a F(H), com H não vazio. Significa apenas ausência de
   contraexemplo no histórico. `rejected`: há uma observação que W não prevê.
   Histórico vazio: `undetermined`. Não significa verdade universal ou identificação única.
2. **Identificação do modelo (`model_identity`).**
   `supported`: W é o único candidato compatível. `rejected`: W é incompatível.
   `undetermined`: W continua compatível com pelo menos uma alternativa, ou H é vazio.
   Se W é refutado mas várias alternativas permanecem, a refutação de W é decidida;
   a identidade da alternativa continua incerta. São afirmações distintas.
3. **Previsão num domínio D (`target_prediction`).**
   Se W é incompatível: `rejected`. Se W é compatível e todos os candidatos
   sobreviventes concordam em D: `supported` condicionalmente à classe de modelos.
   Se discordam em D: `undetermined`. Sem D explícito, não há esta avaliação.

Um estado pode, portanto, permitir `supported` para a primeira afirmação e
`undetermined` para a segunda. `profile` devolve esse conjunto de interpretações,
sem impor uma categoria oculta. Isso é análise de sensibilidade semântica, não um
novo critério que aceite qualquer resposta. Um futuro ensaio deve declarar a afirmação.

Insuficiência pode ser: identidade ambígua, previsões ambíguas em D, falta de um
modelo adequado, ou impossibilidade de medir onde as hipóteses divergem. Não são sinónimos.
Há consultas úteis para discriminar candidatos quando estes preveem saídas diferentes
num ponto ainda legal. A inexistência dessas consultas não prova irrelevância para
diagnóstico fora da classe candidata nem garante informação suficiente fora de Q.

## Diagnóstico, evidência e localização

- **Contraexemplo de W:** uma observação citada que contradiz a sua previsão.
- **Conflito de determinismo observacional:** qualquer par de registos com a mesma
  entrada completa e saídas diferentes. Um par basta; duplicatas redundantes não
  passam a ser requisitos obrigatórios. Qualquer testemunho válido é aceite,
  independentemente da ordem das linhas ou da existência de outros conflitos.
- **Inadequação da lista:** F(H) vazio. Uma evidência de exclusão precisa de refutar
  todos os candidatos; não prova ausência de uma hipótese externa explicativa.
- **Ambiguidade entre candidatos:** candidatos declarados correspondem a F(H), não
  incluem um candidato eliminado por uma observação que o relatório omite.
- **Contraste direto de um campo:** duas entradas diferem nesse campo, têm os outros
  três campos iguais, e saídas diferentes. Localização declara valores realmente
  observados nesse testemunho. Isto é evidência de dependência sob os pressupostos
  declarados; não constitui intervenção causal independente.
- Uma seleção de modelo baseado em tabelas pode apoiar dependência de phase sem
  existir um contraste direto. Tem de ser identificada como inferência dependente
  da classe de hipóteses; não se deve chamar-lhe contraste controlado observado.
- phase é um rótulo contextual. Não há eixo temporal ou desenho causal que autorize,
  por si só, concluir mudança real de mecanismo ou separá-la de ruído.

`evidence_supports` verifica a afirmação sobre W sob `observed_fit` ou `model_identity`;
não constitui um avaliador completo de diagnóstico de cinco vias. `location_support`
verifica exclusivamente testemunhos observacionais diretos. `None` significa
localização não afirmada; `False` significa forma ou testemunho não verificado.
Não se deve interpretar `False` como prova de que nenhuma inferência de localização
baseada num modelo poderia ser feita. O perfil expõe candidatos e todos os testemunhos.

## Quatro camadas de avaliação

1. **Descodificação:** exatamente um objeto, com chaves únicas e números finitos;
   sem extração de fragmentos nem texto exterior. Rejeição de chaves repetidas é
   uma regra explícita de interpretação inequívoca; a biblioteca JSON histórica
   pode aceitar essas chaves e conservar só a última.
2. **Estrutura:** query/report, campos, tipos, localização feature/value, ausência
   de campos extra. Uma explicação textual é opcional. Listas de IDs têm elementos únicos.
3. **Legalidade:** consulta disponível e orçamento positivo; referências apenas a
   observações já vistas e hipóteses públicas. Evidência vazia e conclusões falsas
   continuam estruturalmente possíveis: a interface não escolhe verdade pelo agente.
4. **Sustentação:** coerência da conclusão com a afirmação declarada, todo o histórico
   e o testemunho citado. Um relatório legal pode ser cientificamente errado.

IDs e ordem não têm significado epistémico. Duplicar um registo existente não traz
informação nova; repetir uma medição independente é outra operação e exige um modelo
de observação. Uma falha operacional não é uma abstenção escolhida.

## Sequências e orçamento

Uma consulta aceite acrescenta exatamente uma observação, retira o ID do menu e
consome uma unidade. Uma consulta recusada não altera o estado. Orçamento nunca é
negativo. Relatórios legais terminam a interação mesmo quando errados. Ações depois
do término são erros explícitos. Novos episódios têm estado independente.

Uma política pode gastar o orçamento sem discriminar dois mundos. O relatório final
deve ser avaliado à luz da evidência realmente recolhida. A qualidade dessa aquisição
e a possibilidade de ter investigado melhor devem ter avaliação separada.

## Independência e limites de validação

O núcleo de referência não importa funções do gerador, pontuador, controlos ou parser
históricos. A enumeração usa vetores de verdade indexados diretamente para conferir
as tabelas. A implementação e esta especificação foram escritas pelo mesmo agente:
independência de implementação não equivale a revisão humana externa.

O domínio exaustivo tem duas glyphs, duas phases, saídas binárias, três tipos de tabela
e todos os históricos parciais consistentes de quatro pontos. Conflitos e transições
são exercitados separadamente. Não há prova universal sobre ruído, linguagem natural,
causalidade, desempenho de LLMs ou manuscritos históricos.

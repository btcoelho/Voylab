# Contrato operacional v2 — alvo observacional delimitado

Estado: versão de decisão para auditoria e ensaio pequeno; não integrada nos executores históricos.

## Pergunta principal

**O modelo de trabalho W é compatível com todas as observações públicas H recolhidas neste episódio?**

Para cada observação completa `(glyph, setting, partner, phase) -> output`, cada candidato é interpretado literalmente segundo a sua tabela pública. `supported` significa que H não está vazio e W prevê todas as saídas observadas. `rejected` significa que pelo menos uma observação pública contradiz W. `undetermined` significa que ainda não há observações. Não se usa categoria oculta, intenção do gerador ou identidade da causa.

Este resultado é ajuste observacional finito. Não afirma verdade universal, causalidade, mudança de mecanismo ou que a lista de candidatos seja completa.

## Diagnóstico em campo separado

O conjunto `F(H)` contém exatamente os candidatos declarados que acertam **todas** as linhas de H. O diagnóstico é `none_fit` se `F(H)` é vazio, `identified` se tem um elemento, e `ambiguous` se contém mais de um. `ambiguous` não significa automaticamente que as previsões sejam diferentes no domínio de interesse; qualquer afirmação preditiva exige que esse domínio seja declarado e comparado separadamente.

Insuficiência é registada como propriedade do estado: não há observações, não há candidato compatível, há múltiplos candidatos, ou os sobreviventes divergem numa consulta/domínio declarado. Não substitui o veredicto sobre W. A aquisição de informação (consultas disponíveis, discriminantes e orçamento gasto) também é avaliada separadamente do acerto do relatório.

## Certificados de evidência

- `supported`: citar todas as observações públicas do episódio. A alegação refere-se ao histórico completo, pelo que uma amostra parcial não certifica a ausência de contraexemplos.
- `rejected`: citar pelo menos uma observação efetivamente contradita por W. Mais linhas podem ser citadas, mas não são necessárias para refutar W.
- `undetermined`: permitido apenas quando H está vazio; não existe certificado factual.
- O conjunto de candidatos declarado tem de ser exatamente `F(H)`, em todas as três situações. É uma saída diagnóstica separada; nunca determina o veredicto principal.
- A estrutura e a legalidade da ação são medidas antes da sustentação. Uma resposta falsa mas legal continua a ser um erro científico observável, não é corrigida pelo parser.

## Localização

Por omissão, a localização não é pontuada. Se for declarada como testemunho observacional direto, tem de corresponder a um contraste citado em que apenas o campo nomeado varia e a saída muda, ou a um par com a mesma entrada completa e saídas incompatíveis. O valor tem de ser observado no testemunho. Associação baseada em ajuste de modelo recebe outro rótulo e não pode ser chamada efeito controlado ou causal.

## Estados indistinguíveis

Se dois estados têm exatamente a mesma informação pública e a pergunta julgada, recebem a mesma resposta esperada, mesmo que os seus rótulos geradores difiram. Se um protocolo continuar a exigir alvos diferentes, o exemplo é não identificável e não pode pontuar uma resposta do agente.

## Portas de uso

1. Este contrato e o schema são congelados antes de qualquer chamada de modelo.
2. A bateria manual e as leis de invariância/ordem/certificado têm de passar; as mutações relevantes têm de ser mortas.
3. Reanálises de G1/G2 são retrospectivas e mantêm os resultados históricos intactos.
4. A aprovação deste núcleo autoriza apenas um ensaio pequeno com o modelo já disponível, nos termos de um pré-registo próprio. Não autoriza fine-tuning, modelos maiores, dados de confirmação ou alegações sobre manuscritos históricos.

## Limites

O contrato assume tabelas determinísticas, observações sem ruído, entradas completamente observadas e candidatos codificados corretamente. A validade científica para ruído, confusão, hipóteses omitidas, medidas reais, manuscritos ou causalidade exige uma tarefa diferente e um modelo de observação explícito.

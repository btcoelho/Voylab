# Auditoria M17 — o veredicto esperado é identificável?

**Data:** 17 de outubro de 2026. Só partição de desenvolvimento (sementes 53001, 53003, 53009; 300 mundos). Diagnóstico e confirmação não foram gerados. Sem chamadas de modelo. A saída só contém agregados, sem IDs de mundos.

O M17 atribui o veredicto esperado pela **categoria oculta** do mundo. A auditoria compara-o com o que o agente consegue ver:

1. **Estado inicial.** O veredicto do contrato v2, calculado só com as linhas públicas e o modelo de trabalho (`supported` se encaixa em todas, `rejected` se não, `undetermined` só sem linhas), coincide com o esperado pelo M17?
2. **Evidência alcançável.** Existe algum conjunto de até 3 consultas do menu que leve a um estado cujo veredicto do contrato v2 coincide com o esperado?

## Resultado (60 mundos por categoria)

| Categoria | Esperado M17 | Veredicto v2 no estado inicial | Coincide inicialmente | Alcançável com ≤3 consultas |
|---|---|---|---|---|
| NORMAL | supported | supported | 60/60 | 60/60 |
| CONTRADICTION | rejected | rejected | 60/60 | 60/60 |
| HYPOTHESIS_ABSENT | rejected | rejected | 60/60 | 60/60 |
| CHANGE | rejected | supported | 0/60 | 60/60 |
| INSUFFICIENCY | undetermined | supported | 0/60 | **0/60** |

## O que isto significa

1. **INSUFFICIENCY não é compatível com o contrato v2.** O modelo de trabalho encaixa em todas as linhas e nenhuma consulta o contradiz, por isso o contrato dá sempre `supported`. O M17 espera `undetermined`, que no v2 só existe com histórico vazio. As duas definições não podem valer ao mesmo tempo. O M17 trata como insuficiente o caso em que nenhuma consulta do menu separa os candidatos que encaixam; isto é legível no estado público (assinatura distinta das outras categorias), mas é outra definição de `undetermined`.
2. **CHANGE e NORMAL são idênticos no estado inicial.** Têm a mesma assinatura pública (60 e 60) e veredictos esperados diferentes, `rejected` e `supported`. A diferença só aparece ao consultar. É um desenho legítimo, porque a aquisição de informação faz parte da tarefa, mas um agente que não consulta não os consegue distinguir. Em CHANGE, 257 das 720 consultas do menu (36%) contradizem o modelo de trabalho; uma consulta ao acaso acerta cerca de 1 em 3.
3. **CONTRADICTION e HYPOTHESIS_ABSENT são identificáveis só com o estado inicial**, sem consultas.

A assinatura pública usada é: o modelo de trabalho encaixa em todas as linhas; número de cartas que encaixam (0, 1, 2 ou mais); conflito na mesma entrada; alguma consulta do menu separa as cartas que encaixam.

## Limites

A auditoria é ao nível das cartas declaradas e do menu, não ao nível do espaço completo de funções (o domínio M17 tem 64 entradas e 4 saídas, impossível de enumerar). Usa a leitura literal do contrato v2, que o M17 não adotou. Não diz que o M17 está errado: diz que, medido pelo contrato v2, INSUFFICIENCY não pode ser pontuada, e que o M17 precisa de uma definição própria de insuficiência, escrita e pré-registada, se continuar a ser usado.

## Reproduzir

```bash
python -m unittest discover -s tests -v
python audit_m17.py --output ../../results/AUDITORIA_M17_IDENTIFICABILIDADE_DEV_2026-10-17.json
```

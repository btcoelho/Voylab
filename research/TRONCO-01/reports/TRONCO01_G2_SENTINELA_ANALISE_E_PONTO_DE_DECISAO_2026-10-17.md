# TRONCO-01 — G2 sentinela e análise obrigatória

**Data:** 17/10/2026  
**Protocolo:** `TRONCO-01 G2 contract and decoding ablation v0.1`  
**Estado:** sentinela concluído; ponto de análise obrigatória atingido.  
**Decisão:** parar G2 após os cinco sentinelas. A extensão não foi autorizada pelo gate pré-registado. Reservas fechadas; sem fine-tuning.

## Integridade e execução

O pré-registo foi congelado antes da inferência. O pré-teste sem pesos passou: 25 mundos equilibrados; 300 IDs de consulta; 100 localizações canónicas aceites pelo validador; 50 caminhos de gramática e 50 verificações de contexto. Os hashes dos scripts, fontes M17 e checkpoint base coincidiram com o pré-registo. Foram excluídos 107 IDs de mundos anteriores.

Na revisão pós-execução detetei que o pré-teste inicial contou todos os IDs listados, mas só testou a alcançabilidade de um ID por mundo. Fiz então uma auditoria pós-execução separada, sem pesos, que testou individualmente os 300 IDs contra a gramática G2; todos passaram. A gramática não impediu a execução, mas esta verificação completa ocorreu depois da inferência, pelo que fica registada como limitação processual.

O lote executou os cinco mundos sentinela em três condições de modelo e quatro controlos. O gate exigia 5/5 relatórios explícitos sem falhas operacionais na condição `base_g2_schema`. O resultado foi 4/5 relatórios explícitos, com uma truncagem a 192 tokens, falha de parser e ação inválida. O gate falhou e, conforme a regra congelada, os outros 20 mundos não foram executados.

## Resultados dos sentinelas

| Condição | Relatórios explícitos | Decisões certas | Diagnósticos com evidência | Consultas / redundantes | Falhas operacionais |
|---|---:|---:|---:|---:|---:|
| Base, ponte G1 | 5/5 | 2/5 | 1/5 | 15 / 13 | 0 |
| Base, contrato G2 + gramática | 4/5 | 0/5 | 0/5 | 0 / 0 | 1 |
| Base, contrato G2 livre | 0/5 | 0/5 | 0/5 | 0 / 0 | 5 |
| Detetor estatístico | 5/5 | 3/5 | 2/5 | 0 / 0 | 0 |
| Consulta aleatória | 5/5 | 4/5 | 2/5 | 15 / 14 | 0 |
| Consulta fixa | 5/5 | 4/5 | 2/5 | 15 / 13 | 0 |
| Controlo simbólico ativo | 5/5 | 5/5 | 5/5 | 2 / 0 | 0 |

Os cinco casos são um sentinela por categoria; os resultados são diagnósticos e exploratórios, com grande incerteza. A ponte G1 confirma que, nesses mundos, o base conseguiu emitir relatórios, mas consultou até ao limite e acertou duas decisões. Os controlos dão contexto para a dificuldade dos casos, não substituem uma comparação confirmatória.

## Análise das falhas G2

Na condição restrita, os quatro relatórios explícitos foram todos `supported`; nenhum citou evidência (`evidence_ids` vazio), nenhum escolheu uma consulta e nenhum acertou a decisão. As quatro localizações também falharam a forma pretendida: o modelo escreveu `feature` e espalhou campos/valores observados como chaves adicionais, sem o objeto `value` esperado. Isto explica o diagnóstico 0/5 mesmo nos casos em que a gramática aceitou a ação.

O contrato G2 foi clarificado no texto, mas a gramática e o validador mantiveram `location` como qualquer objeto. O pré-teste demonstrou que formas canónicas passavam, mas não verificou a rejeição de formas semanticamente inválidas. Portanto, o gate operacional atual só verifica JSON, tipos básicos e IDs; não garante que o relatório obedeça à semântica de localização ou evidência.

Na condição livre, nenhuma saída se tornou uma ação válida. As respostas incluíram JSON truncado, texto extra após o objeto e campos com tipos/formas incompatíveis. Três das cinco ações atingiram o limite de 192 tokens. Este braço mostra que, com este prompt e limite, a geração livre não é operacionalmente utilizável; não permite estimar o efeito científico da descodificação em condições comparáveis, porque não produziu relatórios válidos.

O G2 não sustenta a conclusão de que a clarificação textual melhore localização, decisão ou consulta. Também não isola bem a descodificação livre face à restrita: as duas condições falharam por mecanismos diferentes e a condição livre não chegou a fornecer ações válidas para comparação científica.

## Próximos passos recomendados

1. Preservar G2 como resultado negativo do sentinela e manter os 20 mundos de extensão sem execução. Os cinco mundos sentinela passam a constar como expostos e ficam excluídos de qualquer nova avaliação.
2. Corrigir o contrato antes de outra chamada ao modelo: exigir `location` com apenas `feature` e `value`; definir quando `value` é objeto de entrada completa, valor(es) de campo ou `null`; rejeitar chaves extra e combinações inválidas. Definir também requisitos mínimos de evidência coerentes com `score_report`, sem incluir a resposta correta.
3. Reduzir a instrução G2 a regras curtas e fazer o formato público e a gramática expressarem a mesma estrutura. Aumentar `max_new_tokens` apenas se houver justificação pré-registada e orçamento de contexto confirmado. Não interpretar a truncagem isolada como causa das falhas científicas.
4. Criar G2.1 com pré-registo novo, novos mundos não expostos, testes positivos e negativos do contrato e um sentinela operacional. A comparação livre/restrita só deve avançar para 25 casos se a condição restrita passar o gate; manter ações inválidas e relatórios semanticamente inválidos separados.

**Ponto de análise atingido.** A decisão seguinte é reformular o contrato e o protocolo G2.1 antes de pedir ao modelo outra avaliação. M17 continua não aprovado; G2 não abriu qualquer reserva.

## Artefactos

- Pré-registo e fontes: `work/TRONCO01_G2/`
- Execução: `work/TRONCO01_G2/run_20261017_v01/`
- Relatório G1 anterior: `outputs/TRONCO01_G1_RESULTADO_E_ANALISE_2026-10-17.md`

# TRONCO-01 — análise de erros G1 e bloco contínuo G2

**Data:** 17/10/2026  
**Estado:** plano; não foram iniciadas inferências G2.  
**Decisão atual:** M17 permanece não aprovado; as reservas diagnóstica e de confirmação continuam fechadas.

## O que os episódios G1 mostram

Os números seguintes vêm dos 25 episódios de desenvolvimento G1 v0.2 por condição. São observações sobre este lote, não estimativas confirmatórias.

| Condição | Decisões certas | Diagnósticos com evidência | Decisão certa sem localização | Consultas redundantes / total |
|---|---:|---:|---:|---:|
| Base + instrução G1 + schema | 9/25 | 2/25 | 7/25 | 65/73 |
| M16 + instrução G1 + schema | 4/25 | 2/25 | 2/25 | 33/37 |
| Consulta aleatória | 19/25 | 10/25 | 9/25 | 67/75 |
| Consulta fixa | 19/25 | 10/25 | 9/25 | 67/75 |
| Controlo simbólico ativo | 25/25 | 25/25 | 0/25 | 0/10 |

O base gastou as três consultas disponíveis em 24/25 episódios. Dessas 73 consultas, 65 tinham ganho esperado de informação nulo pelo critério atual do ambiente. O M16 fez 37 consultas, 33 redundantes. A proximidade dos controlos aleatório e fixo confirma que o G1 ainda não demonstrou seleção ativa útil. Este ganho mede redução do conjunto de hipóteses listadas; pode não capturar outros usos de uma medição, pelo que não deve ser a única métrica de consulta.

Há uma falha de contrato de saída que merece correção antes de interpretar os 2/25 diagnósticos como incapacidade pura de raciocínio. O `response_schema` público apresenta `location.feature` como a cadeia exemplificativa `input field or null`. O base repetiu **literalmente essa cadeia nos 25 relatórios**. Nos sete casos em que acertou uma decisão fora da categoria normal, falhou a localização. O pontuador exige, por exemplo, `feature: "input"` e o vetor completo de entrada para uma contradição do mesmo input, `feature: "phase"` para mudança e `feature: "partner"` para efeito do par. A gramática G1 restringe `location` apenas a ser um objeto, por isso deixa passar a cópia do texto exemplificativo. O M16 também apresentou valores não canónicos em vários casos. O resultado G1 mantém-se válido **sob o contrato usado**, mas atribuir toda a diferença de diagnóstico à capacidade do modelo seria excessivo.

Além disso, a condição G1 mudou simultaneamente a instrução de sistema e a descodificação por schema. O contraste com o wrapper nativo mede o pacote inteiro; não identifica isoladamente o efeito da gramática. As decisões, consultas, evidência e confiança continuam fracas mesmo onde o JSON foi válido. A clarificação do contrato não deve ser presumida como solução científica.

## Bloco G2 a executar seguido

### 1. Auditoria e congelamento, sem GPU

Preservar os artefactos e as pontuações G1. Fazer uma tabela de correspondência entre cada campo do estado público, o validador e `score_report`; explicitar especialmente a semântica de `location`, `candidate_model_codes`, `evidence_ids` e `undetermined`. Corrigir a documentação pública de `location` numa **versão G2**, com formas canónicas e exemplos genéricos que não contenham a resposta de nenhum mundo. Manter o pontuador G1 como referência; se uma alteração ao pontuador se revelar necessária, versioná-la, justificá-la e não usar G1 como confirmação retroativa.

Criar testes locais para verificar que as formas canónicas são aceites, que os exemplos genéricos não contêm rótulos ocultos, que a gramática continua a permitir consultas e relatórios legais e que falhas de parser ou ações inválidas ficam registadas. Congelar código, prompts, gramática, pontuador, hashes, sementes, modelos, limites e a lista de mundos num pré-registo antes de qualquer inferência G2.

### 2. Comparação emparelhada em mundos novos de desenvolvimento

Selecionar 25 mundos novos, cinco por categoria, sem sobreposição com G0g, piloto M17, G1 v0.1 ou G1 v0.2. Usar os mesmos mundos, observações iniciais, orçamento de três consultas e limite de quatro ações em todas as condições:

1. **Ponte G1:** base com o contrato público G1 e a instrução + gramática G1, sem alterações.
2. **Contrato G2:** mesmo checkpoint base e mesma gramática de estrutura/IDs, com a descrição pública de localização corrigida. Fixar previamente qualquer alteração de redação da instrução de sistema e registá-la como parte da intervenção.
3. **Ablation G2 livre:** exatamente o prompt da condição 2, com geração livre e o mesmo parser/validador pós-geração. Isto separa o efeito da descodificação restrita do efeito da instrução G2.
4. **Controlos:** estatístico, consulta aleatória, consulta fixa e simbólico ativo, identificados como políticas distintas. O simbólico serve apenas de teto de resolubilidade construído.

Incluir cinco mundos sentinela, um por categoria, nos 25. A condição 2 avança automaticamente aos outros 20 só se produzir 5/5 relatórios explícitos, sem falha de geração, parser, truncamento ou ação inválida. Se passar, executar os outros 20 em **todas** as condições e controlos, conservando falhas no denominador. Se falhar, parar após os sentinelas e analisar as saídas brutas. Não afinar prompts nem repetir gerações dentro do lote.

### 3. Métricas e análise obrigatória

No fim do sentinela falhado ou dos 25 mundos, apresentar, por condição e categoria: decisão correta; diagnóstico e localização com evidência; decisões corretas sem localização; reconhecimento de informação insuficiente; sensibilidade e especificidade; relatórios explícitos; tipos de ação inválida; consultas redundantes, ganho esperado e real de informação; custo de consultas; confiança e calibração apenas sobre relatórios explícitos. Incluir contagens e incerteza por episódio, sem tratar consultas como réplicas independentes.

Comparar primeiro **G1 vs G2 restrito** para estimar o efeito da clarificação do contrato nos mesmos mundos, depois **G2 restrito vs G2 livre** para isolar a descodificação. Inspecionar os relatórios brutos que mudarem de resultado. A análise deve verificar se aumentou a localização **e** se melhoraram as decisões, a insuficiência e a escolha de consultas. Uma melhoria só de formato não constitui avanço científico suficiente.

**Ponto de paragem obrigatório:** após esta análise, decidir se há motivo para testar um modelo de referência mais capaz sob o contrato G2, reformular a tarefa/medidas ou preparar uma avaliação reservada. Não abrir reservas, não fazer fine-tuning e não declarar aprovação M17 automaticamente neste bloco. Os 25 mundos continuam a ser desenvolvimento; qualquer passagem a reservas requer nova decisão explícita baseada nos resultados completos.

## Fonte dos números

`work/TRONCO01_G1/run_20261017_v02/episodes.jsonl`, `work/TRONCO01_G1/run_20261017_v02/preregistration.json`, `work/TRONCO01_G1/preflight_g1.py`, `work/M17_DESCOBERTA_DIAGNOSTICO/environment.py`. O relatório G1 e o pacote reproduzível permanecem em `outputs`.

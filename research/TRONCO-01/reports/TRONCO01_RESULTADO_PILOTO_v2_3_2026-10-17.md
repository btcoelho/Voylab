# Resultado do piloto sintético TRONCO-01 v2.3

## Decisão

O instrumento **não está apto para um pequeno ensaio de modelo** com esta interface e configuração. O piloto de desenvolvimento não confirmou a capacidade-alvo: houve 0/10 sucessos conjuntos, nenhuma consulta aceite e apenas 3 relatórios legais. Isto é evidência de falha da configuração testada, não uma estimativa geral da capacidade do modelo nem uma validação sobre o manuscrito Voynich.

## Resultados

- Episódios: 10; chamadas geradas: 19.
- Classificação retrospectiva: {'model_output_failure': 4, 'call_limit_no_report': 3, 'reported': 3}.
- Ações de relatório: 15; relatórios legais: 3; relatórios rejeitados: 12.
- Consultas legais: 0; sucessos conjuntos: 0/10.
- Nos três relatórios legais, `verdict=undetermined`, `candidate_model_codes=[A]`, `diagnosis=none_fit` e `sufficiency=no_candidate_fits`. Em dois episódios a referência era `supported / [A] / identified / identity_resolved`; no terceiro era `rejected / [] / none_fit / no_candidate_fits`. Nenhum relatório acertou o veredicto ou o certificado de evidência.

## Problemas verificados

1. **Saída truncada/malformada:** quatro episódios terminaram em `JSONDecodeError` após geração. `pilot_01` ficou guardado como falha técnica, embora o diário contenha geração e erro de descodificação; reclassifico-o apenas nesta análise como falha de saída do modelo. Não houve retry.
2. **Ação de consulta não usada:** nos três episódios sem relatório terminal, o modelo repetiu quatro relatórios que citavam IDs de evidência não observados. O ambiente rejeitou-os; não houve consulta aceite.
3. **Decisão inconsistente nos relatórios legais:** os três relatórios legais deram a mesma combinação de resposta apesar de estados que exigiam suporte, rejeição e conjuntos de candidatos diferentes.
4. **Resumo de retoma enganador:** o resumo final marca `sentinel_technical_failure=false`, apesar do evento `sentinel_stop` anterior. O primeiro episódio foi tecnicamente reclassificado pelo runner na retoma, mas o estado de sentinela não foi recuperado. O diário preserva a sequência completa.
5. **Verificação independente:** recalculou os rótulos dos dez estados iniciais e a legalidade das ações, sem importar o avaliador em auditoria. Divergências com rótulos do calendário = nenhuma; divergências de legalidade = nenhuma; divergências com o score guardado = nenhuma.

## Efeito das alterações e limites

O harness conseguiu retomar sem repetir episódios concluídos, preservar saídas brutas e acabar os dez casos após a emenda. A emenda classificou corretamente as falhas de descodificação a partir de `pilot_02`, mas `pilot_01` permaneceu com o rótulo antigo; a retoma também tornou incorreto o indicador de falha da sentinela. Assim, o registo bruto é utilizável, mas os campos agregados do runner exigem reconciliação pós-execução.
A restrição de 256 tokens foi insuficiente para alguns relatórios em JSON com texto explicativo longo. A gramática permitiu sequências estruturalmente admissíveis, mas não evitou referências a IDs inexistentes nem decisões semanticamente erradas. Não alterei prompt, modelo, gramática ou limite durante o lote.

## Próximos passos

1. Congelar este resultado como histórico; manter G1/G2 e reservas intactos.
2. Corrigir o harness antes de qualquer novo modelo: estado de sentinela persistente em retoma, classificação de erro pelo tipo real, resumo sempre reconstruído a partir do diário e distinção entre relatório tentado, ação ilegal e relatório terminal válido.
3. Reduzir a resposta estruturada a campos curtos, eliminar explicação livre, limitar IDs às opções do estado atual e testar a terminação JSON sob o orçamento fixo; congelar nova versão e repetir primeiro testes sem modelo e testes de mutação.
4. Fazer nova avaliação apenas após um novo ponto de análise, com protocolo e orçamento preregistados. Não fazer fine-tuning com este painel.

## Reprodutibilidade

O JSON anexo contém score independente, estados por episódio e SHA-256 dos registos. O verificador independente está incluído no pacote. O pacote exclui a chave privada do oráculo; as mensagens e ações completas continuam no diário bruto.

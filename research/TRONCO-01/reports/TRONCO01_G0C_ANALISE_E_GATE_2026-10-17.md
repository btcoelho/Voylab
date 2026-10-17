# TRONCO-01 — diagnóstico de inferência e gate de transporte G0c/G0d

> **Correção metodológica (17/10/2026):** a descodificação restrita excluía as ações exatas pedidas nos três casos `report` de cada execução e fixava o tipo de ação a partir de `requested_action`. O gate de correspondência exata neste modo era impossível de passar e a decisão sobre competência dos modelos abaixo fica sem efeito. Os dados brutos permanecem válidos como observações operacionais. A interpretação corrigida e o próximo protocolo estão em `TRONCO01_REVISAO_G0C_G0D_E_BLOCO_SEGUINTE_2026-10-17.md`.

**Data:** 17/10/2026  
**Estado:** diagnóstico e validação de reparo concluídos; gate de avanço falhou para ambos os modelos.  
**Decisão:** parar no ponto de análise obrigatório. Não iniciar piloto M17, avaliação reservada ou fine-tuning.

## Perguntas e desenho

G0c comparou, nas quatro fixtures de transporte G0b, (1) geração livre com instrução equilibrada entre `query` e `report` e (2) geração restringida a objetos JSON que satisfazem o esquema e usam referências públicas válidas. O base e o adaptador M16 receberam os mesmos estados e prompts. Foram feitas 16 gerações. Dois controlos canónicos adicionais compararam `AutoModelForCausalLM` do Transformers com o carregador Unsloth.

Como a intervenção de descodificação restrita melhorou a validade estrutural mas não a correspondência pedida, G0d fez a única validação prevista do reparo em quatro fixtures novas, com IDs e valores inéditos. Foram oito gerações restritas, quatro por modelo. O orçamento foi cumprido, sem retentativas.

## Resultados

| Bloco | JSON estrito | Ação válida | Correspondência exata |
|---|---:|---:|---:|
| G0c base, geração livre, fixtures anteriores | 4/4 | 1/4 | 1/4 |
| G0c base, descodificação restrita | 4/4 | 4/4 | 1/4 |
| G0c M16, geração livre | 4/4 | 0/4 | 0/4 |
| G0c M16, descodificação restrita | 4/4 | 4/4 | 0/4 |
| G0d base, descodificação restrita, fixtures novas | 4/4 | 4/4 | 1/4 |
| G0d M16, descodificação restrita, fixtures novas | 4/4 | 4/4 | 0/4 |

O base acertou a consulta pedida nas duas validações, mas escolheu `supported` nos três relatórios de G0c e nos relatórios G0d, incluindo casos cujo pedido era `rejected` ou `undetermined`. O M16 escolheu uma consulta diferente no G0c e falhou as quatro correspondências exatas em G0d. Com descodificação restrita, ambos emitiram respostas pertencentes ao conjunto pré-construído de ações válidas; por isso, os 4/4 de validade nesse modo verificam o funcionamento da restrição, não uma capacidade aprendida pelo modelo. A correspondência ao pedido continua a ser a medida independente relevante.

## Diagnóstico do carregamento

O checkpoint carregou sem exceção tanto por `AutoModelForCausalLM` como por Unsloth. Os dois controlos produziram texto de recusa, sem JSON estrito; as formulações diferiram. Portanto, não há evidência de falha de carregamento ou de descodificação que explique os resultados G0b. O controlo usado pedia um objeto exato dentro de um campo `task` de um estado JSON, pelo que não é um teste puro de capacidade de JSON: ele mistura seguir instruções aninhadas com transporte. Os resultados G0c/G0d sobre fixtures M17 continuam a mostrar a falha de ação, mas os controlos canónicos não permitem concluir que o modelo ou o loader sejam incapazes de produzir JSON em qualquer contexto.

## Integridade e limites

- 18/18 gerações G0c e 8/8 G0d concluídas; sem limite de tokens atingido nas respostas registadas.
- Prompts, estados, alvos e hashes foram gravados antes das chamadas em cada execução.
- G0d usa estados e IDs diferentes dos usados no desenvolvimento G0b/G0c.
- Os cinco ficheiros-fonte M17 monitorizados mantêm os hashes de G0b.
- Nenhuma reserva científica foi aberta. Não houve treino nem alteração do adaptador M16.
- As fixtures medem cumprimento de uma ação explícita, não escolha científica, qualidade de evidência ou calibração.
- O conjunto de saídas restritas foi gerado por uma trie finita de objetos válidos. Este método é apropriado para o ensaio de transporte com alvos conhecidos; não é ainda o descodificador de produção nem valida um esquema geral arbitrário.

## Próximos passos recomendados

1. **Manter o gate fechado.** Nenhum modelo atingiu 4/4 correspondências exatas em fixtures novas; não executar piloto de mundos M17 nem usar resultados como evidência científica.
2. **Separar a camada de protocolo do comportamento científico.** Para garantir apenas serialização, a camada determinística da aplicação pode validar e serializar uma ação já escolhida. Avaliar separadamente se o modelo escolhe entre consulta e relatório e se fundamenta `supported`, `rejected` ou `undetermined` nos dados.
3. **Definir um benchmark de decisão, não de eco.** Congelar estados novos onde a ação correta decorra de evidência pública e de uma regra de parada explícita; pontuar ação, referências, veredicto, abstenção e orçamento de consultas. Incluir baselines determinísticos e pelo menos um modelo de referência sem adaptador.
4. **Só depois escolher uma intervenção.** Comparar prompt, restrição de esquema e, se houver justificativa, adaptação supervisionada. Qualquer treino precisa de divisão por mundos, alvos de validação separados e avaliação reservada ainda fechada.
5. **Novo ponto de análise antes de abrir reservas.** Exigir protocolo congelado, reprodução do benchmark, controles negativos/positivos e critérios de avanço definidos antes das chamadas.

## Artefactos

O pacote reproduzível contém os executores, pré-registos, agendas, gerações brutas e resumos de G0c e G0d, além do pré-registo G0b usado para recuperar as fixtures de desenvolvimento.

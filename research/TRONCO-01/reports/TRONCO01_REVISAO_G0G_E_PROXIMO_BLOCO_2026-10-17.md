# TRONCO-01 — revisão do G0g e bloco seguinte

**Data:** 17/10/2026  
**Estado:** plano para a próxima execução; nenhuma inferência nova foi iniciada nesta revisão.

## O que o G0g permite concluir

O G0g foi a primeira avaliação de transporte corrigida e completa: 32/32 gerações, alvos e opções validados previamente no ambiente. O gate pré-registado de 8/8 cópias exatas falhou: base restrito 7/8; M16 restrito 6/8. A geração livre obteve 0/8 alvos exatos em ambos os modelos. Não há aprovação para piloto M17.

As três diferenças restritas têm causas distintas:

| Caso | Diferença observada | Leitura |
|---|---|---|
| Base, `transport_supported_2` | Relatório `supported`, modelo, evidência, localização e confiança iguais ao alvo; só `explanation` mudou de «G0f transport target.» para «short statement». | Falha legítima da igualdade literal pré-registada, mas não falha dos campos discretos de decisão. |
| M16, `transport_query_1` | Relatório `undetermined` válido em vez de consulta `qP2`. | Falha de seleção do tipo de ação. |
| M16, `transport_query_2` | Relatório `undetermined` válido em vez de consulta `qV0`. | Repete a preferência por relatório perante um pedido explícito de consulta. |

O prompt continha `requested_action` e a descodificação restrita oferecia o alvo exato entre opções completas. Mesmo 8/8 nesse ensaio demonstraria apenas transporte de uma ação fornecida, não escolha autónoma. Reclassificar agora o resultado do base como passagem, com um critério de campos discretos, alteraria retroativamente o gate. O G0g permanece **falhado** e os seus dados ficam preservados.

## Próximo bloco contínuo — novo protocolo G1 em desenvolvimento

### 1. Congelar o objeto experimental e a interface

Criar uma versão G1 separada. O agente recebe apenas o estado público real de `Episode.state()`: sem `requested_action`, categoria, alvo, rótulo oculto ou lista de respostas completas. Registar o prompt efetivo e verificar esses campos antes da inferência. Excluir do novo conjunto os oito mundos usados em G0g e quaisquer fixtures anteriores de transporte.

A interface pode construir o JSON e restringir **formato, tipos e referências a IDs públicos**; a seleção `query`/`report`, o ID da consulta, o veredicto e as afirmações do relatório continuam a vir do agente. A gramática não recebe a resposta correta nem uma lista de relatórios prontos. Uma entrada inválida produz falha registada, sem substituição semântica, consulta escolhida pelo executor ou relatório forçado contado como abstenção voluntária. Preservar os wrappers originais como condições de comparação; a interface nova é uma condição experimental distinta.

Fazer testes locais, sem GPU, para: ambas as ações alcançáveis quando legais; todos os IDs de consulta legais alcançáveis; campos e referências inválidos rejeitados; JSON truncado e saída vazia registados; fim de orçamento; ausência de fuga de categoria; reset entre episódios; saída bruta persistida antes de qualquer exceção. Congelar código, hashes, parâmetros de geração, lista de mundos, limites e pontuador num manifesto antes da primeira chamada ao modelo.

### 2. Executar um sentinela operacional de cinco mundos

Usar um mundo de desenvolvimento por categoria, nunca visto no transporte, no máximo quatro ações por episódio e primeira ação inválida como falha operacional. Testar separadamente base e M16 com a nova interface; correr os controlos determinísticos nos mesmos mundos e com o mesmo orçamento de consultas. Sem retentativas ou mudanças de prompt durante o lote.

Para uma condição avançar ao lote de 25, exigir **5/5 relatórios explícitos**, zero erros de parser/geração, zero truncamentos e zero ações inválidas. Não exigir acerto científico em cinco casos; a amostra serve apenas para provar que episódios completos são executáveis. Se nenhuma condição passar, parar no ponto de análise com os textos brutos. Se uma passar, avançar automaticamente apenas com essa condição.

### 3. Executar 25 mundos de desenvolvimento

Cinco mundos por categoria, excluindo os oito do G0g. Emparelhar os mesmos mundos e dados iniciais entre condições aprovadas e controlos; limitar a quatro ações por episódio e ao mesmo orçamento de consultas. Persistir cada ação, resposta do ambiente, custo e eventual falha. Não tratar ações sucessivas como observações independentes.

Relatar, por categoria e no conjunto: sensibilidade a problemas identificáveis, especificidade, reconhecimento de insuficiência por relatório `undetermined` escolhido, exatidão do diagnóstico com evidência, localização, taxa de relatório explícito, consultas redundantes, ganho de informação e custo. Manter falhas operacionais no denominador de desempenho e distinguir ausência de relatório de abstenção. Apresentar contagens e incerteza; 25 mundos são exploração, não validação de transferência nem prova de limites de erro baixos.

### 4. Análise obrigatória e decisão seguinte

Parar após falha do sentinela ou conclusão dos 25 mundos. Comparar os resultados brutos com controlos e verificar integridade de partições e recursos. Decidir então entre: corrigir interface operacional, testar um modelo de referência mais capaz sob o mesmo protocolo, ou formular uma intervenção científica específica para consulta/insuficiência. Qualquer política externa que escolha `query`/`report` é um agente híbrido com condição e atribuição próprias, nunca melhoria atribuída silenciosamente ao modelo.

**Fora deste bloco:** reservas diagnóstica e de confirmação, fine-tuning, afirmação de aprovação M17. A única paragem antecipada é uma falha de integridade antes da inferência ou o sentinela sem condições aprovadas.

## Porquê este bloco

Repetir a cópia de JSON com outro prompt acrescentaria pouca evidência sobre a falha central: reconhecer quando consultar, quando a informação é insuficiente e quando relatar uma contradição. O G1 mede decisões a partir de evidência pública e deixa a formatação sob controlo mecânico auditável. Mantém o G0g como resultado negativo sem o reinterpretar.

# TRONCO-01 — execução G0f/G0g e ponto de análise

**Data:** 17/10/2026  
**Estado:** G0g válido concluiu 32/32 chamadas; gate operacional não passou.  
**Decisão:** parar antes do piloto M17. Não abrir reservas nem fazer fine-tuning.

## Integridade do ciclo

G0f foi interrompido após uma geração porque o executor encontrou `NameError` antes de gravar a saída. O resultado não persistiu e não foi repetido sob o mesmo protocolo. G0f está marcado como incompleto e não entra na análise.

Foi congelado G0g v0.1 com oito fixtures baseadas em mundos de desenvolvimento M17 gerados a partir da seed `53003`. Antes de qualquer peso de modelo ser carregado, o pré-teste verificou os alvos e todas as opções permitidas com `Episode.apply`, conferiu IDs públicos, testou referências inválidas, ações alternativas legais, JSON incompleto e campos obrigatórios ausentes. Todos os oito casos passaram.

G0g comparou geração livre e descodificação restrita para o modelo base e o adaptador M16, com 32 chamadas no total e sem retentativas. Cada saída foi gravada imediatamente. Os 32 hashes de prompt coincidem com a agenda congelada. Os cinco ficheiros-fonte M17 monitorizados mantêm os hashes registados antes da execução.

## Resultados

| Modelo e condição | JSON estrito | Ação válida no ambiente | Alvo exato válido | EOS | Limite atingido |
|---|---:|---:|---:|---:|---:|
| Base, livre | 6/8 | 1/8 | 0/8 | 6/8 | 2/8 |
| Base, restrita | 8/8 | 8/8 | 7/8 | 8/8 | 0/8 |
| M16, livre | 7/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| M16, restrita | 8/8 | 8/8 | 6/8 | 8/8 | 0/8 |

A condição restrita do base falhou apenas em `transport_supported_2`; a do M16 falhou nas duas consultas, respondendo `report` em vez de `query`. O gate foi pré-registado como 8/8 alvos exatos válidos, sem falha ou truncamento. Nenhuma condição passou. A validade sintática e no ambiente de 8/8 sob restrição demonstra o funcionamento da interface; a seleção de alvos continua abaixo do gate.

## Interpretação

O resultado mais informativo para a engenharia é a separação entre condições. A geração livre continua pouco fiável para o contrato M17 neste modelo e adaptador. A restrição produz JSON e ações aceites pelo ambiente, mas não resolve toda a seleção: o base errou um relatório de suporte e o M16 manteve preferência por relatório nos pedidos de consulta.

As oito fixtures são um ensaio operacional pequeno de copiar ações explícitas. Não medem escolha de consulta útil, reconhecimento científico de inadequação, insuficiência, ruído ou mudança. Não sustentam conclusões populacionais nem aprovação do agente.

## Próximos passos

1. **Não repetir G0g nem afrouxar o gate retroativamente.** Preservar os resultados como a primeira execução corrigida e válida.
2. **Rever apenas as três discrepâncias restritas** (um relatório do base e duas consultas do M16), incluindo os textos brutos. Classificar se são erro de escolha, enviesamento do adaptador ou incompatibilidade do prompt.
3. **Escolher uma única intervenção para um novo gate pré-registado.** A opção mais direta é testar um modelo de referência mais capaz no mesmo conjunto de transporte, com os mesmos controlos e a mesma validação. Outra opção é uma política explícita de seleção `query/report`, mas isso passa a ser um agente híbrido e exige uma condição experimental própria.
4. **Só avançar ao piloto se a condição escolhida passar 8/8.** Então executar cinco mundos de desenvolvimento e avançar automaticamente para 25 apenas se todos terminarem com relatório explícito e sem falha operacional.
5. **Ponto de análise antes de ciência reservada.** Rever o piloto e os controlos, congelar novo manifesto e manter confirmação e diagnóstico reservados fechados até decisão explícita.

Nenhum piloto de mundos, avaliação reservada ou treino foi executado neste ciclo.

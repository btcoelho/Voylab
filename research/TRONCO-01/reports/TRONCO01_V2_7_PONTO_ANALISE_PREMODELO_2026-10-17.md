# TRONCO-01 v2.7 — ponto obrigatório de análise pré-modelo

**Estado:** auditoria offline concluída; aguardando análise obrigatória. Pré-registo e manifesto continuam em rascunho. Não foram carregados pesos nem feitas inferências aprendidas.

## Resultado das verificações

- A suite offline terminou com **37/37 testes aprovados**.
- O runner completo foi exercitado com saídas fixas: relatórios de referência pontuam 10/10; veredictos alterados pontuam 0/10; saída malformada conta como falha e o calendário prossegue; erro técnico grava sentinel e interrompe; identidade de retoma divergente bloqueia antes do carregador.
- **4 mutações dirigidas foram mortas**, cada uma com baseline válido e falha por asserção: duplicação de campos, identidade da retoma, gate de entrada e certificado de evidência para refutação.
- O smoke do adaptador fez uma chamada a um modelo falso em CPU, com tokenizer Qwen e callback LMFE reais. Confirmou JSON, EOS e o caminho de geração. Não carregou pesos; não é inferência do modelo.
- O manifesto rascunho verificou **21 ficheiros internos e 11 artefactos do snapshot**, cobrindo o conjunto exato e os hashes. O gate de produção bloqueou corretamente o estado draft.
- O runtime WSL coincide com as versões candidatas: Python 3.12.3, Transformers 5.17.0, LMFE 0.11.3, Unsloth 2026.10.6, Torch 2.14.1+cu132 e bitsandbytes 0.50.2.
- A conferência encontrou um erro de transcrição de um carácter no hash esperado de `merges.txt`. Corrigi o hash no pré-registo draft após verificar o ficheiro local; o artefacto do checkpoint não foi alterado. A preparação seguinte confirmou todos os 11 hashes.
- O replay histórico v2.3 reproduziu 10 episódios, 19 chamadas, 4 saídas malformadas, 12 ações ilegais e 0/10 sucessos conjuntos. Os registos históricos ficaram intactos.

## O que as alterações demonstram

A v2.7 corrige a lacuna semântica descoberta na v2.6: agora os testes rejeitam refutação sem evidência e citações que não refutam o modelo. O scorer aceita os dez relatórios de referência e rejeita casos de controlo alterados. Os checks de runtime, snapshot e identidade da retoma protegem a execução contra configuração divergente.

Isto valida o comportamento do instrumento em casos manuais e sintéticos controlados. Não demonstra competência do modelo, melhoria face a G1/G2, validade para M17, capacidade de consulta ou generalização. O conjunto tem dez estados já expostos, ordem fixa, uma resposta e zero consultas; uma taxa de sucesso nele serviria apenas como regressão de desenvolvimento.

## Decisão e ponto de análise

**Decisão técnica:** a implementação está pronta para revisão científica pré-modelo, mas o ensaio não deve ser tratado como avaliação confirmatória nem como prova de aptidão para M17. A validade científica da tarefa e do scorer continua limitada pelos dez estados repetidos e pela ausência de política de consulta.

O ponto obrigatório de análise foi alcançado. Antes de qualquer carregamento de checkpoint ou inferência, rever:

1. se uma única resposta sem consultas mede a pergunta científica pretendida;
2. se os critérios conjuntos de veredicto, candidatos, diagnóstico, suficiência, certificado e localização são justificáveis;
3. se os dez casos públicos servem apenas para regressão ou se é necessário construir um painel novo e reservado;
4. se o protocolo pode ser congelado sem alterar a definição do resultado.

G1/G2, v2.3, v2.5 e v2.6 permanecem históricos e inalterados. Não houve fine-tuning, modelo maior, avaliação M17 ou inferência aprendida. O próximo passo dependente de análise é decidir a validade da tarefa e do conjunto; só depois se deve congelar um protocolo e considerar uma execução de modelo.

## Artefactos de reprodução

O ZIP desta entrega contém o pacote v2.7, resultados offline, o replay histórico e o pacote v2.6 preservado para comparação. O checkpoint não está incluído.

# TRONCO-01 — conteúdo do pacote de análise

Esta entrega contém análise e propostas; não contém um novo agente cientificamente validado.

- `TRONCO01_ANALISE_INTEGRADA_2026-10-17.md`: entregáveis A–H, auditoria dos testes concluídos, arquitetura, bibliografia e recomendação.
- `TRONCO01_PROTOCOLO_PROPOSTO_v0_1.md`: gate operacional, três experiências, comparações e requisitos de congelamento. Estado: proposta.
- `TRONCO01_MEMORIA_SCHEMA_v0_1.json`: esquema de eventos proposto. Não implementa verificação de anterioridade, execução de hipóteses ou invariantes entre eventos.
- `TRONCO01_AUDITORIA_EVIDENCIA_2026-10-17.json`: agregados reconstruídos dos ficheiros existentes, limitações da calibração e hashes dos inputs M17.

O arquivo ZIP preserva uma cópia dos inputs analisados em `work/M17_DESCOBERTA_DIAGNOSTICO/`, o script de leitura em `work/tronco01_review/collect_evidence.py`, esta documentação em `outputs/` e a revisão recebida em `inputs/`. A cópia dentro do ZIP é um snapshot para análise; não modifica a experiência existente.

Para recalcular os agregados depois de extrair o ZIP, usar Python 3.10 ou posterior e executar, a partir da pasta extraída:

    python work/tronco01_review/collect_evidence.py

O script usa apenas a biblioteca padrão e lê resultados já existentes; não carrega modelos, não chama o gerador, não inicia benchmarks nem treino. A nova execução reescreve o manifesto de análise na pasta extraída e apresenta os agregados. Os caminhos absolutos no manifesto original documentam o ambiente desta revisão e podem diferir no novo ambiente.

Os 14 testes referidos passaram na etapa anterior. Nesta revisão não foram repetidos. Os ficheiros M17 consultados mantiveram os mesmos hashes. A documentação distingue resultados executados de hipóteses de engenharia e experiências propostas.

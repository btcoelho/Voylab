# TRONCO-01 v2.7 — ponto obrigatório de análise pré-modelo

Estado: pacote técnico preparado para a análise obrigatória. Pré-registo e manifesto permanecem em rascunho.

## Alterações verificadas

- Os casos semânticos manuais de evidência, conjunto de candidatos, diagnóstico, suficiência e localização estão integrados em `tests/test_runner.py`.
- A mesma suite percorre `trial_runner.run` com o guard real e saídas fixas. Cobre dez relatórios de referência, veredictos alterados, uma resposta malformada e uma falha técnica.
- O diário, agenda, limite de chamadas e hash do pré-registo são verificados antes de instanciar o carregador. Uma retoma com identidade divergente bloqueia com zero chamadas ao carregador.
- O pré-registo enumera todos os ficheiros presentes no snapshot local. O carregador compara o conjunto exacto, confere cada hash e exige cobertura no manifesto.
- `runtime_environment.py` compara Python, Transformers, LMFE, Unsloth, Torch e bitsandbytes com as versões registadas, antes do carregamento.
- O verificador de mutações inclui a remoção do certificado de evidência para refutação.

## Resultados offline

- 37 testes passam.
- Quatro mutações são detectadas por asserções após baselines válidos: duplicação, identidade da retoma, gate na entrada e certificado de refutação.
- A mutação semântica que escapava aos testes v2.6 agora falha em dois casos negativos: refutação sem evidência e citação que não refuta o modelo.
- O manifesto candidato verifica 21 ficheiros internos e 11 artefactos externos do snapshot. As versões instaladas no WSL coincidem com as seis versões registadas.
- O adaptador/tokenizer smoke anterior usou o tokenizer e LMFE reais com geração simulada. O runner de lote desta versão continua a usar loader e gerador simulados nos testes.
- Não houve carregamento de pesos nem inferência aprendida. A suite prova a ligação técnica e critérios em casos controlados, não o desempenho do modelo nem generalização.

## Âmbito e limite

O ensaio proposto ainda usa dez estados sintéticos já expostos, com uma resposta directa e zero consultas. É regressão de desenvolvimento; não valida política de consulta, generalização, manuscrito ou M17. G1/G2 e os resultados históricos permanecem inalterados.

O checkpoint de análise termina aqui. Rever se a tarefa directa e o scorer respondem à pergunta pretendida, se os dez casos repetidos valem como ensaio de desenvolvimento e se o critério de sucesso conjunto está adequado. Depois dessa análise, o próximo bloco pode congelar os documentos, executar uma verificação final e, se a decisão for avançar, correr uma única vez os dez episódios.

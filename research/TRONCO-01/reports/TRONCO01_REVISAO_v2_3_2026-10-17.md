# TRONCO-01 v2.3 — resultado e ponto de análise

**Gate:** PASS_FOR_PREMODEL_REVIEW. Execução `8b956fad-8bfe-4f59-ac67-4ddc7a394352`. Nenhuma inferência ou carregamento de pesos ocorreu.

As alterações produziram o efeito esperado. O gate publica RUNNING antes de importar o instrumento e regista FAIL com run_id novo se a importação falhar. A regressão reproduziu o cenário que deixava um PASS antigo em v2.2. O executor continua a impedir chamadas depois da terminação.

Instalei as dependências fixadas num ambiente virtual novo, sem PyTorch, e repeti o gate completo. Passaram 24 testes, enumeração de 10 368 estados, cinco mutações selecionadas, cinco trajetos do tokenizer e reanálise de 235 episódios/178 relatórios sem erros de replay. Os 57 hashes congelados foram confirmados. O TokenEnforcer usou o tokenizer local identificado por seis hashes; dois trajetos válidos chegaram a EOS e três malformados foram bloqueados.

O efeito demonstrado é sobre o instrumento, não sobre a capacidade de um modelo. O teste de tokenizer usa o TokenEnforcer diretamente; não testa o ciclo de geração de um modelo. A amostra sintética e o painel de mutações são limitados. G1/G2 continuam resultados históricos e a reanálise v2.3 é retrospectiva.

Deixei uma proposta concreta para um ensaio exploratório: Qwen2.5-0.5B-Instruct bnb 4-bit local, dez mundos novos com sementes 81001–81010, até três consultas e quatro chamadas por episódio, ação JSON limitada por gramática, e pontuação conjunta de legalidade e sustentação. A identidade local do ficheiro de pesos está registada no protocolo. A agenda, o prompt completo e o backend ainda precisam de congelamento e revisão; por isso a proposta não é uma pré-registração final.

**Decisão:** o núcleo está apto para a revisão pré-modelo de um ensaio pequeno de desenvolvimento. O ponto de análise obrigatório é agora. Fechem a identidade/configuração do modelo, o prompt e a agenda de mundos, avaliem o uso de dez casos de desenvolvimento e aceitem as limitações antes de qualquer inferência. A proposta não sustenta uma afirmação de desempenho geral nem transfere resultados para o manuscrito Voynich.

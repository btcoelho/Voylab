# TRONCO-01 v2.3 — material para o ponto de análise pré-modelo

**Estado:** proposta preparada para revisão. Nenhuma inferência foi executada.

## Resultado do gate

A versão v2.3 corrige o caso de falha durante a importação: publica primeiro RUNNING, depois importa o instrumento dentro da região que regista falhas. Foi acrescentado um teste que começa com um PASS antigo, injeta erro de importação e exige um FAIL com novo run_id. A suíte passou com 24 testes. O gate completo passou numa instalação limpa de dependências.

As dependências diretas agora incluem versões fixas de pytest, Hypothesis, jsonschema, LM Format Enforcer e Transformers. Instalei-as num ambiente virtual novo, sem PyTorch, e repeti o gate. O teste exercita o TokenEnforcer diretamente. O tokenizer continua a ser um recurso local; cada execução regista hashes dos ficheiros usados.

## Protocolo proposto para discussão

- **Objetivo:** medir se o modelo relata apoio, refutação ou insuficiência segundo as observações e se identifica corretamente o conjunto de modelos candidatos compatíveis com todo o histórico público.
- **Checkpoint candidato:** snapshot local `unsloth/Qwen2.5-0.5B-Instruct-bnb-4bit`, revisão `216d96b52c97a3c8294776df8477592f6828981c`; SHA-256 do ficheiro local `model.safetensors`: `fa6ed98084afb0497d9075a82ab17fdfc0b5d99fb6b37d8f761463e67c100f45`. A identidade do ficheiro e o backend de carregamento têm de ser confirmados na execução pré-registada.
- **Amostra:** 10 mundos sintéticos novos, gerados e congelados antes da primeira chamada. Usar sementes fixas `81001`–`81010`. A seleção serve para depuração/desenvolvimento; não é amostra confirmatória e não permite alegação estatística de desempenho geral. Reservas G2 ficam excluídas.
- **Interação:** até três consultas por episódio e um relatório final. Uma chamada por ação; máximo de quatro chamadas por episódio. Sem repetição automática de chamadas falhadas. Gravar prompt, texto bruto, tokens/terminação disponíveis, ação descodificada, observação, resultado e hashes da configuração.
- **Geração:** temperatura 0, top-p 1, máximo 256 tokens por ação, EOS permitido apenas após JSON completo. Gramática v2.3 aplicada a cada chamada. O valor de semente do gerador deve ser registado; se a implementação não for determinística, o resultado é apenas exploratório.
- **Pontuação primária:** aprovação conjunta da legalidade e da resposta sustentada pela evidência. Relatar separadamente veredicto, conjunto exato de candidatos, diagnóstico, suficiência, certificado de evidência e localização. Denominador inclui todos os 10 episódios; falhas técnicas contam como falha operacional e não são repetidas.
- **Relato:** tabela por episódio, contagens e proporções com denominador explícito, chamadas e consultas usadas, falhas de parsing/execução e auditoria independente das saídas. Sem comparações de significância com G1/G2 nem alegação de generalização.

## Decisões a rever antes de qualquer chamada

1. Confirmar se este checkpoint é o modelo pretendido e se o hash corresponde aos pesos que se pretende carregar.
2. Confirmar se 10 mundos novos e as sementes propostas são adequados. A agenda final e os estados públicos devem ser gerados, auditados, hashados e anexados antes do ensaio; a chave/oráculo fica separada dos prompts.
3. Fixar a conversa de sistema/utilizador completa, o formato do prompt, backend, parâmetros, timeout, limite de contexto e política de falhas. Temperatura e top-p, por si só, não garantem determinismo.
4. Rever a métrica conjunta e aceitar explicitamente que este é um ensaio de desenvolvimento pequeno, sem força para sustentar uma conclusão geral.

**Ponto de análise obrigatório:** depois de fechar estes itens e obter gate PASS v2.3 numa instalação reproduzível, antes da primeira inferência. O pacote científico continua limitado a mundos sintéticos determinísticos; não avalia leitura do manuscrito Voynich, causalidade ou hipóteses fora da classe fornecida.

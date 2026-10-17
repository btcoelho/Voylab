# Piloto local do v3 (sem treino) — artefactos mínimos, passos e previsões

**17 de outubro de 2026.** Decisão de Bruno: piloto **local**. Só sementes de desenvolvimento (91xxx). Nenhuma reserva.
Objetivo: ver se um modelo lê o estado, produz ações válidas e **onde** falha (procura, inferência, evidência ignorada, revisão). Não mede competência.

## 1. O que já está escrito e testado aqui (sem modelo)
`research/TRONCO-01/v3/pilot/`: `pilot_harness.py` (prompt determinista, esquemas de ação por fase, episódio completo, agregação com IC de Wilson),
`select_worlds.py` (48 mundos de dev, 16 por veredicto, hash fixo), `run_pilot.py` (uma tentativa real por pasta, hashes do código),
`fake_backends.py` (testes), `check_local_env.py` (inventário só de leitura), `hf_backend.py` (modelo real; **escrito mas não executado**: aqui não há torch).
O prompt tem cerca de 2,3 mil caracteres (~900 tokens), cabe em 4096.

## 2. O que sei e o que NÃO sei do teu ambiente
**Sei** (dos manifestos congelados do ensaio v2.7, não do estado atual): Python 3.12.3, transformers 5.17.0, lm-format-enforcer 0.11.3, unsloth 2026.10.6,
torch 2.14.1+cu132, bitsandbytes 0.50.2; execução num utilizador Linux `bcoelho` (WSL) com GPU NVIDIA; checkpoint
`unsloth/Qwen2.5-0.5B-Instruct-bnb-4bit` na cache do Hugging Face (snapshot 216d96b5…); o adaptador M16 existe como ZIP em
`Codex/2026-10-17/…/outputs/M16_UNSLOTH_ADAPTER_2026-10-17.zip` (18,5 MB).
**Não sei**: se esse ambiente ainda existe e funciona; versões atuais; VRAM livre. A minha ligação ao teu computador só vê as pastas ligadas
(Codex e VOIYNICH): não vê o WSL, a cache do Hugging Face nem a GPU. Por isso o inventário tem de ser corrido por ti, no sítio onde o modelo corre.

## 3. Artefactos mínimos necessários
| # | Artefacto | Verificação |
|---|---|---|
| 1 | Clone deste repositório (`main`) no sítio onde o modelo corre | `git rev-parse HEAD` |
| 2 | Python ≥ 3.12 com `torch`, `transformers`, `lm-format-enforcer` nas versões do manifesto (ou outras, registadas) | `check_local_env.py` |
| 3 | Snapshot local do modelo (pesos `model.safetensors`, `tokenizer.json`, `config.json`) | `check_local_env.py` (hash dos JSON) |
| 4 | GPU com memória livre para o modelo + ~1 GB de contexto | `nvidia-smi` |
| 5 | Pasta de saída gravável e **vazia** | — |
Opcionais, **fora do piloto**: o adaptador M16 (só se quiseres comparar base e adaptado), `llguidance` com a correção `const: []` (a validar noutra etapa; o piloto usa `lm-format-enforcer`, como o v2.7).

## 4. Passos (comandos a correr por ti, na máquina do modelo)
```bash
git clone https://github.com/btcoelho/Voylab && cd Voylab/research/TRONCO-01/v3
python pilot/check_local_env.py > ../../../env_local.json                       # só leitura
python -m unittest discover -s tests                                             # tem de passar (41 testes)
python pilot/run_pilot.py --backend fake_random --out ../../../pilot_dry         # ensaio sem modelo
python pilot/run_pilot.py --backend hf --snapshot <pasta do snapshot> --out ../../../pilot_real_1
```
`run_pilot.py --backend hf` recusa correr duas vezes na mesma pasta. Põe a pasta de saída numa pasta ligada (por exemplo dentro de Codex) para eu a ler.

## 5. Previsões ex-ante (escritas antes de qualquer corrida com modelo; todas refutáveis)
Modelo esperado: Qwen2.5-0.5B-Instruct 4 bits, ação por turno, decodificação gananciosa, sem retries, 48 mundos.
- **M1.** Saídas JSON válidas: 100% (gramática). **Ações aceites pelo ambiente < 98%** (erros semânticos: `query_id` fora do menu ou cartas inexistentes). Se for ≥ 98%, refuta-se.
- **M2.** Alcance ≤ alcance da aleatória em dev + 0,10 (aleatória ≈ 0,56 no equilibrado; a comparar com a referência calculada nos mesmos 48 mundos).
- **M3.** Erro de inferência entre episódios completos > 25% (veredicto que não é o do próprio histórico).
- **M4.** Revisão: tipo I ≥ 80% nos mundos de mudança (não reconhece a contradição).
- **M5.** Consultas: média < 1 (compromete-se cedo) — paragem prematura > 50%.

## 6. Regras de decisão (fixadas agora)
- Condição de elegibilidade para avançar na escada: ações aceites ≥ 98%, episódios completos ≥ 98%.
- Se a elegibilidade falhar por **prompt, esquema ou gramática**, é permitido corrigir só essas peças e repetir o piloto (máximo 3 rondas, cada uma registada com falhas, correções e critérios; a tarefa, as métricas e os mundos não mudam).
- Se falhar por **capacidade** do modelo, não se mexe no prompt para o salvar: regista-se e sobe-se na escada (modelo maior).
- Nada do piloto serve de evidência de competência, e nenhum mundo do piloto entra em validação ou cega.

## 7. Registo de execução
**17/10/2026, ambiente** (`Codex/pilot_v3/env_local.json`): WSL2, Python 3.12.3, RTX 4070 12 GB. Pacotes só no venv `~/voynich-lab/.venv`, com as versões do manifesto v2.7. Snapshot `216d96b5…` presente (o `model.safetensors` não tem hash). Pacote do piloto = `git archive` de 31d906e (sha256 `b2acdfea…`).

**17/10/2026, testes e ensaio:** 41/41 testes no venv; `fake_random` com 12 mundos correu até ao fim.

**17/10/2026, arranque real abortado (`real_1`), 0 chamadas ao modelo.** O `lm-format-enforcer` 0.11.3 importa `PreTrainedTokenizerBase` de `transformers.tokenization_utils`, que o transformers 5.17 já não expõe. O manifesto fixa duas versões que, juntas, não funcionam. A falha ocorreu ao construir o backend, antes de qualquer mundo ser apresentado, por isso não há saídas nem transcrições. O `attempt_once.lock` de `real_1` fica onde está, como registo; não se apaga.

Decisão: não é uma ronda do piloto, porque nenhum mundo foi apresentado. Não se instalam nem atualizam pacotes, para não sair do manifesto. A correção é só de importação: `hf_backend._transformers_compat()` reexporta a classe com o nome antigo, e o resultado fica registado (`compat`). Antes do piloto corre um teste de fumo (`pilot/smoke_hf.py`) sobre texto escrito à mão, sem mundos do piloto. A tentativa válida usa uma pasta nova, `real_2`. Os prompts, o esquema, os mundos, as métricas e as previsões M1–M5 não mudam. O `code_sha256` do `summary.json` passa a incluir o novo hash do `hf_backend.py`.

**17/10/2026, teste de fumo 1** (pacote 0f65beb): 44/44 testes; a importação passou e o modelo carregou; a geração falhou porque `apply_chat_template(..., return_tensors="pt")` devolve um `BatchEncoding` no transformers 5, não um tensor. Correção: pedir `return_dict=True`, passar `input_ids` e `attention_mask`. Nenhum mundo do piloto foi apresentado.

**17/10/2026, teste de fumo 2** (6aee974): passou nos dois esquemas. O modelo carregou em 5 s em `cuda:0`; cada geração levou 2 a 4 s. Na fase de exploração, o modelo respondeu `"query_id": "qN"`, copiando o marcador do modelo de ação. Foi o primeiro sinal do problema da ronda 1.

### Ronda 1 do piloto (`real_2`, 22:06–22:13, código 6aee974, esquema por fase)
Hashes do código e dos 48 mundos verificados contra o repositório (`worlds_sha256` `cdf24285…`). Saídas em `research/TRONCO-01/v3/results/piloto_R1/`.

| Medida | Resultado |
|---|---|
| JSON válido | 145/145 |
| Ações aceites | **1/145 (0,7%)** |
| Episódios completos | **0/48**; 48 terminados à força (3 inválidas seguidas) |
| Saídas | 132× `query_id: "qN"`, 12× `"qNe"`, 1× `"q1"` (a única aceite) |

- **M1 confirmada**: JSON 100%, ações aceites < 98%. O erro é semântico, como previsto: `query_id` fora do menu.
- **M2–M5 não avaliáveis**: não há episódios completos.
- **Elegibilidade falhou** (aceites 0,7% < 98%; completos 0% < 98%).

**Diagnóstico.** A falha está no esquema, e não (ainda) na capacidade de investigar. O esquema da ronda 1 aceita qualquer texto em `query_id`, e o modelo de ação do prompt mostra um marcador literal (`qN`) que o modelo copia. A gramática garante a forma, mas não os ids que o ambiente aceita. Os ids válidos já estão no prompt; o esquema só não os usava. A regra §6 permite corrigir prompt, esquema ou gramática, até 3 rondas, sem mexer na tarefa, nas métricas ou nos mundos.

**Correção da ronda 2 (uma só peça: esquema).** `action_schema(fase, estado)` restringe `query_id` ao menu atual (e retira a opção `query` quando o orçamento chega a 0), as cartas aos ids existentes e as previsões às posições 1–4. O prompt, os mundos, as métricas e o ambiente não mudam. O backend continua a receber só o texto e o esquema. Testes: o esquema admite exatamente os ids que o ambiente aceita, ao longo de todo o orçamento. O esquema da ronda 1 fica disponível com `--schema phase`.

**Custo conhecido desta correção.** Depois dela, "ações aceites" deixa de medir se o modelo segue o formato, porque a gramática o garante. Essa capacidade ficou medida na ronda 1 (0,7%) e é reportada como tal. A partir da ronda 2, as métricas que contam são as de investigação: alcance, erro de inferência, paragem prematura e revisão.

**Previsões ex-ante da ronda 2** (escritas antes de a correr):
- **R2-a.** Ações aceites ≥ 98% e episódios completos ≥ 98%. A única falha possível são cartas repetidas. Se falhar, o defeito está na gramática ou no ambiente, não no modelo.
- **R2-b.** M2: alcance ≤ alcance da aleatória nos mesmos 48 mundos + 0,10. Referência calculada antes (`results/PILOTO_REFERENCIAS.json`): aleatória 35/48 = 0,73, logo o limite é 0,83. Primeiro do menu dá 32/48; sem consultas, 16/48.
- **R2-c.** M3: erro de inferência > 25% entre os completos.
- **R2-d.** M4: tipo I na revisão ≥ 80% nos mundos de mudança.
- **R2-e.** M5: média de consultas < 1 ou paragem prematura > 50%. Espera-se também uma preferência pela primeira posição do menu e pela primeira carta.

**Regra para depois da ronda 2.** Se a elegibilidade passar, o piloto fecha, e os valores de M2–M5 caracterizam o modelo de 0,5B (não servem de evidência de competência). Se a investigação estiver ao nível de "sem consultas" ou "primeiro do menu", isso é capacidade, e sobe-se na escada de modelos sem mexer no prompt. Se a elegibilidade voltar a falhar por esquema ou gramática, há uma ronda 3, a última.

### Ronda 2 do piloto (`real_3`, 22:22–22:38, código 98eba84, esquema por estado)
Hashes do código e dos mundos verificados. Os números foram recalculados de forma independente a partir das transcrições, repetindo cada saída num `Episode` novo e confirmando o hash de cada prompt (`pilot/analyse_pilot.py`): coincidem com o `summary.json`. Saídas em `results/piloto_R2/`.

| Medida | Resultado | Previsão |
|---|---|---|
| JSON válido | 215/215 | — |
| Ações aceites | 146/215 (67,9%) | R2-a ≥ 98%: **refutada** |
| Episódios completos | 25/48 (52%); 23 terminados à força | R2-a ≥ 98%: **refutada** |
| Causa das 69 inválidas | **69/69 por cartas repetidas** (`["Qu","Qu","Qu","Qu"]`) | era o único modo de falha previsto em R2-a |

Os 25 completos são uma subamostra selecionada (os episódios em que a carta não saiu repetida), por isso os valores abaixo são descritivos:
- **Comportamento constante.** 100% dos commits (94, válidos e inválidos) com `supported`; 2,0 consultas em todos os completos (orçamento esgotado); a primeira consulta foi `q1` em 36 de 48 episódios (75%; das 145 consultas aceites, 47 foram à posição 1); `keep` em 25/25 revisões; 0 suspensões.
- **M2 / R2-b**: alcance 7/25 = 0,28 [0,14; 0,48] ≤ 0,83, **confirmada**. Fica ao nível de responder sempre `supported`: 16/48 = 0,33 nos 48 mundos, porque os alvos estão equilibrados.
- **M3 / R2-c**: erro de inferência 22/25 = 88% [70%; 96%] > 25%, **confirmada**.
- **M4 / R2-d**: tipo I 14/14 = 100% [78%; 100%] nos mundos de mudança, **confirmada**. Tipo II 0/11.
- **M5 / R2-e**: média de consultas 2,0 (não < 1) e paragem prematura 0%, **refutada**. O modelo não pára cedo: consulta sempre até ao fim do orçamento e escolhe a primeira posição. A preferência pela primeira posição, essa, confirma-se.

**Diagnóstico.** A elegibilidade voltou a falhar por **gramática**. O lm-format-enforcer não impede ids repetidos num array, e com descodificação gananciosa a mesma saída inválida repete-se três vezes, o que termina o episódio. O comportamento de investigação já é claro: uma política constante (consulta, consulta, `supported`, `keep`), que não depende da evidência. Isto é **capacidade**, e o prompt não se mexe para o salvar.

**Porque fazer a ronda 3, a última, mesmo assim.** A escada de modelos usa este mesmo arnês. Ele tem de passar a elegibilidade de forma independente do modelo; caso contrário, um modelo maior pode falhar por gramática e não por raciocínio.

**Correção da ronda 3 (esquema e o texto do modelo de ação que o descreve).** As cartas passam a ser um objeto com um `true`/`false` obrigatório por carta (`{"Qu":true,"Ne":false,"Ka":false}`). Assim, repetir uma carta deixa de ser expressável. O arnês converte o objeto na lista que o ambiente sempre recebeu, pela ordem em que as cartas são mostradas, e regista a ação convertida (`env_action`). O ambiente, os mundos, as métricas e o resto do prompt não mudam. As rondas 1 e 2 continuam reproduzíveis (`--schema phase` / `state`): os hashes dos prompts de R1 e R2 foram confirmados com o código novo.

**Previsões ex-ante da ronda 3:**
- **R3-a.** Ações aceites ≥ 98% e completos ≥ 98%, ou seja, elegibilidade cumprida. Se falhar, o piloto **suspende-se**: as 3 rondas esgotaram-se, e reformula-se a interface de ação antes de qualquer modelo.
- **R3-b.** Mantém-se a política constante: `supported` em ≥ 90% dos commits, média de consultas ≥ 1,8, `q1` como primeira consulta em ≥ 60% dos episódios, `keep` em ≥ 90% das revisões.
- **R3-c.** Alcance entre 0,20 e 0,45, perto de 1/3, que é o nível de responder sempre o mesmo. Erro de inferência > 50%. Tipo I ≥ 80%.

**Decisão já fixada para depois da ronda 3.** Se R3-a passar, o arnês fica elegível e o piloto fecha. O modelo de 0,5B fica classificado como **sem capacidade mensurável** nesta tarefa (política constante), e o passo seguinte é o degrau seguinte da escada (modelo maior), com o mesmo arnês e as mesmas previsões M1–M5. Nada disto é evidência de competência, e nenhum destes mundos entra em validação ou cega.

### Defeito encontrado durante a análise (não afeta resultados)
O `world_id` **não é único**: os 48 mundos do piloto têm 20 ids, porque o id omite o alvo, o tipo e o k0. Os mundos em si são todos distintos (48 estados públicos diferentes). Verifiquei onde o id é usado: a análise do piloto (corrigida para emparelhar por ordem), a semente das políticas aleatórias (mundos com o mesmo id partilham a sequência aleatória, o que reduz a independência sem enviesar) e as chaves de ordenação, que continuam determinísticas por estabilidade. Nenhum resultado anterior usa o id como chave de dicionário. Correção no congelamento do protocolo: um id único (incluir alvo, tipo, k0, orçamento) e as sementes das políticas a partir dele. Não se corrige agora, porque isso mudaria a seleção dos mundos do piloto a meio.

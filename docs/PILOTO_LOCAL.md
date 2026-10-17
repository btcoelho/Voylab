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

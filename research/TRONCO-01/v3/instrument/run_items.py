"""Fase 3: pontua cada item por escolha forçada num modelo local (sem gerar, sem gramática, sem treino).

Para cada item: contexto = chat template(system, user) + prefix; para cada candidata, soma das log-probabilidades
dos seus tokens dado o contexto. Guarda o contexto exato (texto e ids), as pontuações e o número de tokens.
Retoma: itens já pontuados no ficheiro de saída são saltados. Uma pasta por modelo; nada é reescrito.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "pilot")]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Scorer:
    def __init__(self, snapshot: str):
        import torch
        from hf_backend import _transformers_compat
        self.compat = _transformers_compat()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, device_map="auto")
        self.model.eval()

    def score(self, item: dict) -> dict:
        torch, tok = self.torch, self.tok
        msgs = [{"role": "system", "content": item["system"]}, {"role": "user", "content": item["user"]}]
        ctx = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False) + item["prefix"]
        ctx_ids = tok(ctx, add_special_tokens=False)["input_ids"]
        seqs, starts, boundary_ok = [], [], []
        for c in item["candidates"]:
            full = tok(ctx + c, add_special_tokens=False)["input_ids"]
            if full[: len(ctx_ids)] == ctx_ids:
                seqs.append(full); boundary_ok.append(True)
            else:                                   # the boundary merged tokens: score the candidate tokens appended
                seqs.append(ctx_ids + tok(c, add_special_tokens=False)["input_ids"]); boundary_ok.append(False)
            starts.append(len(ctx_ids))
        L = max(len(s) for s in seqs)
        pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
        ids = torch.full((len(seqs), L), pad, dtype=torch.long)
        mask = torch.zeros((len(seqs), L), dtype=torch.long)
        for k, s in enumerate(seqs):
            ids[k, : len(s)] = torch.tensor(s); mask[k, : len(s)] = 1
        dev = self.model.device
        # Only the last K positions are needed (K covers every candidate plus the position before it). Asking the model
        # for K logits instead of L avoids a [batch, L, vocab] float tensor (~2 GB at L~1000, vocab 151k), which
        # filled the 12 GB GPU on the 3B run (18/10, 08:20) and pushed Windows into shared-memory fallback.
        K = max(len(s) - st for s, st in zip(seqs, starts)) + 1 + (L - min(len(s) for s in seqs))
        with torch.no_grad():
            logits = self.model(input_ids=ids.to(dev), attention_mask=mask.to(dev), logits_to_keep=K).logits.float()
        logp = torch.log_softmax(logits, dim=-1)              # position j of logp = sequence position L - K + j
        off = L - K
        scores, ntok, toklp, first_ids = [], [], [], []
        for k, s in enumerate(seqs):
            tgt = torch.tensor(s[starts[k]:], device=dev)
            pos = torch.arange(starts[k] - 1, len(s) - 1, device=dev) - off
            assert int(pos.min()) >= 0
            tl = logp[k, pos, tgt]
            scores.append(float(tl.sum())); ntok.append(len(s) - starts[k]); toklp.append([float(x) for x in tl])
            first_ids.append(s[starts[k]])
        # round 2 (18/10): per-token log-probs and first token ids, so choices can be read off the first token
        # (what greedy decoding decides) instead of a length-biased sum
        return {"item_id": item["item_id"], "scores": scores, "ntokens": ntok, "token_logprobs": toklp,
                "first_token_ids": first_ids, "boundary_ok": boundary_ok,
                "context_sha256": sha(ctx.encode()), "context_ids_sha256": sha(json.dumps(ctx_ids).encode()),
                "context_tokens": len(ctx_ids), "context": ctx, "context_ids": ctx_ids}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--items", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    raw = a.items.read_bytes()
    items = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l][: a.limit]
    scores_path = a.out / "scores.jsonl"
    texts_path = a.out / "contexts.jsonl.gz"
    done = set()
    if scores_path.exists():
        done = {json.loads(l)["item_id"] for l in scores_path.read_text(encoding="utf-8").splitlines() if l}
    t0 = time.time()
    s = Scorer(a.snapshot)
    load = time.time() - t0
    with scores_path.open("a", encoding="utf-8") as fs, gzip.open(texts_path, "at", encoding="utf-8") as ft:
        for it in items:
            if it["item_id"] in done:
                continue
            r = s.score(it)
            ft.write(json.dumps({k: r[k] for k in ("item_id", "context", "context_ids")}, ensure_ascii=False) + "\n")
            fs.write(json.dumps({k: v for k, v in r.items() if k not in ("context", "context_ids")}) + "\n")
            fs.flush()
    import torch, transformers
    manifest = {"snapshot": a.snapshot, "items_sha256": sha(raw), "items": len(items), "load_seconds": round(load, 1),
                "total_seconds": round(time.time() - t0, 1), "compat": s.compat, "python": platform.python_version(),
                "torch": torch.__version__, "transformers": transformers.__version__,
                "code_sha256": {n: sha((HERE / n).read_bytes()) for n in ("run_items.py", "items.py")}}
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()

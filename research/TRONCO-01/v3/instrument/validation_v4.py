"""Partição de validação V4 (§22). Gerada só depois do congelamento, a partir de uma ronda futura do beacon drand anunciada
no congelamento (docs/V3_ESPECIFICACAO.md §9). Nunca reutiliza sementes de desenvolvimento nem reservadas."""
from __future__ import annotations

import collections
import hashlib
import json
import random
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument")]
import generator_v3 as g  # noqa: E402
import variants as VA  # noqa: E402

DRAND = "https://api.drand.sh"
PER_TARGET = 75


def derive_seeds(randomness: str, k: int = 3) -> list[int]:
    out, i = [], 0
    while len(out) < k:
        s = 100000 + int(hashlib.sha256(f"tronco01-v4-validacao|{randomness}|{i}".encode()).hexdigest(), 16) % 800000
        i += 1
        if 91000 <= s < 92000 or s in out:
            continue
        try:
            g.guard_seed(s)
        except g.ReservedSeedError:
            continue
        out.append(s)
    return out


def build(randomness: str):
    seeds = derive_seeds(randomness)
    ws, infeasible = VA.build("V4", seeds=seeds)
    rng = random.Random(f"tronco01-v4-validacao-amostra|{randomness}")
    keep = []
    for t in ("rejected", "supported", "undetermined"):
        pool = sorted([w for w in ws if w["reference"]["target_verdict"] == t], key=lambda w: w["uid"])
        keep += rng.sample(pool, PER_TARGET) if len(pool) > PER_TARGET else pool
    return keep, {"seeds": seeds, "built": len(ws), "kept": len(keep),
                  "per_target": dict(collections.Counter(w["reference"]["target_verdict"] for w in keep)),
                  "infeasible_cells": len(infeasible)}


def fetch_round(chain: str, rnd: int, session=None):
    import requests
    s = session or requests
    r = s.get(f"{DRAND}/{chain}/public/{rnd}", timeout=30, verify="/root/.ccr/ca-bundle.crt")
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    ws, info = build(sys.argv[1])
    print(json.dumps(info))

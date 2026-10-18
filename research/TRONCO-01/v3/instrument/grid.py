"""Grelha ITT (fase 2 do instrumento): uma categoria por episódio, N = episódios previstos.

Precedência (escrita em docs/PILOTO_LOCAL.md §9):
  incompleto
  -> v != p : "sorte" se v == alvo, senão "inferencia"
  -> v == p e ainda há consulta decisiva : "prematuro_certo" se v == alvo, senão "prematura"
  -> v == alvo : "fundamentado" ; senão "pesquisa"
v = veredicto comprometido (suspend conta como undetermined), p = veredicto do próprio histórico (leitura 70),
alvo = target_verdict do gerador. Revisão: "revisao_final_correta" = veredicto final == veredicto pós-evidência.
"""
from __future__ import annotations

import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3)]
import generator_v3 as g  # noqa: E402
import scoring as sc  # noqa: E402

CATEGORIES = ("fundamentado", "sorte", "prematuro_certo", "inferencia", "pesquisa", "prematura", "incompleto")


def classify(world: dict, ep) -> dict:
    """ep: an env_v3.Episode after the episode was played (or replayed)."""
    if ep.committed is None or ep.final is None:
        return {"category": "incompleto", "target": world["reference"]["target_verdict"], "revision_final_correct": False,
                "committed": None, "final": None}
    hid = world["hidden"]
    W, T, menu = hid["w"], hid["T"], hid["menu"]
    A = g.admissible_idx(sc.history_rows(world, ep.queried))
    p = g.verdict(A, W, T)
    v = ep.committed["verdict"]
    a = world["reference"]["target_verdict"]
    free = [q for q in menu if q not in ep.queried]
    decisive = p == "undetermined" and ep.left > 0 and sc.can_still_determine(A, W, T, free, ep.left)
    if v != p:
        cat = "sorte" if v == a else "inferencia"
    elif decisive:
        cat = "prematuro_certo" if v == a else "prematura"
    else:
        cat = "fundamentado" if v == a else "pesquisa"
    post = g.revision_reference(world, ep.queried)["post_verdict"]
    return {"category": cat, "own": p, "target": a, "committed": v, "final": ep.final["verdict"], "post": post,
            "revision_final_correct": ep.final["verdict"] == post}


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    out = {c: sum(r["category"] == c for r in rows) for c in CATEGORIES}
    rec = {}
    for t in ("supported", "rejected", "undetermined"):
        pool = [r for r in rows if r["target"] == t]
        rec[t] = (sum(r["category"] == "fundamentado" for r in pool), len(pool))
    out["recall"] = {t: f"{k}/{m}" for t, (k, m) in rec.items()}
    out["macro"] = sum(k / m for k, m in rec.values() if m) / 3
    out["revision_final_correct"] = sum(r["revision_final_correct"] for r in rows)
    out["N"] = n
    return out

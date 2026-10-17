"""Evaluate the reference policies on development (and substitute) worlds. No model calls."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import policies as P  # noqa: E402

REPS_RANDOM = 5
SUBSTITUTE_SEEDS = (92001, 92003, 92009)


def paired_ci(x, y):
    d = [p - q for p, q in zip(x, y)]
    m = sum(d) / len(d)
    var = sum((u - m) ** 2 for u in d) / (len(d) - 1) if len(d) > 1 else 0.0
    se = math.sqrt(var / len(d))
    return {"diff": m, "ci95": [m - 1.96 * se, m + 1.96 * se], "n": len(d)}


def evaluate(worlds):
    per = {}        # policy -> list of per-world metric dicts (averaged over reps for random)
    for cls in P.POLICIES:
        pol = cls()
        reps = REPS_RANDOM if pol.name == "aleatoria" else 1
        rows = []
        for w in worlds:
            eps = [P.run_episode(pol, w, r) for r in range(reps)]
            rows.append({k: sum(float(e[k]) for e in eps) / reps for k in eps[0]})
        per[pol.name] = rows
    meta = [{"target": w["reference"]["target_verdict"], "family": w["meta"]["family"],
             "difficulty": w["meta"]["difficulty"], "kind": w["reference"]["kind"],
             "need": w["reference"]["queries_needed"]} for w in worlds]
    return per, meta


def summarise(per, meta):
    names = list(per)
    reach = {n: [r["reach"] for r in per[n]] for n in names}
    out = {"n": len(meta), "policies": {}}
    for n in names:
        rows = per[n]
        m = lambda k: sum(r[k] for r in rows) / len(rows)  # noqa: E731
        out["policies"][n] = {"reach": m("reach"), "queries_mean": m("queries"), "invalid_rate": m("invalid"),
                              "revision_type_I_rate": m("revision_type_I"), "revision_type_II_rate": m("revision_type_II")}
    cmp_pairs = [("bayes_ig", "aleatoria"), ("bayes_ig", "sem_consultas"), ("bayes_ig", "simples"),
                 ("simples", "aleatoria"), ("oraculo", "bayes_ig"), ("aleatoria", "sem_consultas"), ("greedy_a", "simples"), ("bayes_ig", "greedy_a")]
    out["paired_reach"] = {f"{x} - {y}": paired_ci(reach[x], reach[y]) for x, y in cmp_pairs}

    def block(filt):
        idx = [i for i, m_ in enumerate(meta) if filt(m_)]
        if len(idx) < 2:
            return None
        return {"n": len(idx), "reach": {n: sum(reach[n][i] for i in idx) / len(idx) for n in names},
                "bayes_ig_minus_simples": paired_ci([reach["bayes_ig"][i] for i in idx], [reach["simples"][i] for i in idx]),
                "bayes_ig_minus_aleatoria": paired_ci([reach["bayes_ig"][i] for i in idx], [reach["aleatoria"][i] for i in idx])}
    out["by_family"] = {f: block(lambda m_, f=f: m_["family"] == f) for f in g.FAMILIES}
    out["by_target"] = {t: block(lambda m_, t=t: m_["target"] == t) for t in g.VERDICTS}
    out["by_need"] = {str(k): block(lambda m_, k=k: m_["need"] == k) for k in (1, 2, None)}
    # revision: pegajosa vs rest
    by_kind = {}
    for kind in g.KINDS:
        idx = [i for i, m_ in enumerate(meta) if m_["kind"] == kind]
        if idx:
            by_kind[kind] = {n: {"typeI": sum(per[n][i]["revision_type_I"] for i in idx) / len(idx),
                                 "typeII": sum(per[n][i]["revision_type_II"] for i in idx) / len(idx),
                                 "should_revise": sum(per[n][i]["should_revise"] for i in idx) / len(idx)}
                             for n in ("bayes_ig", "pegajosa", "sem_consultas")}
    out["revision_by_kind"] = by_kind
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    res = {"model_calls": 0, "sets": {}}
    for name, seeds in (("dev", a.DEV_SEEDS), ("substitute", SUBSTITUTE_SEEDS)):
        worlds = a.dev_set(seeds=seeds)
        per, meta = evaluate(worlds)
        res["sets"][name] = summarise(per, meta)
        res["sets"][name]["seeds"] = list(seeds)
    text = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()

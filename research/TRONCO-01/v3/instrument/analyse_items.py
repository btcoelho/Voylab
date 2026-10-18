"""Fase 3: análise das pontuações de escolha forçada. Fixada antes de ver resultados.

Escolha do modelo = candidata com maior log-probabilidade (soma). Probabilidade do modelo = softmax das somas.
IC 95%: bootstrap agrupado por structure_group (2 000 reamostragens, semente fixa).
"""
from __future__ import annotations

import collections
import json
import math
import random
import sys
from pathlib import Path


def load(items_path: Path, scores_path: Path):
    items = {json.loads(l)["item_id"]: json.loads(l) for l in items_path.read_text(encoding="utf-8").splitlines() if l}
    scores = {}
    for l in scores_path.read_text(encoding="utf-8").splitlines():
        if l:
            r = json.loads(l)
            scores[r["item_id"]] = r
    return items, scores


def probs(s):
    m = max(s)
    e = [math.exp(x - m) for x in s]
    z = sum(e)
    return [x / z for x in e]


def choice(item, sc):
    s = sc["scores"]
    return item["candidates"][s.index(max(s))]


def cluster_boot(units, stat, n=2000, seed=11):
    """units: list of (cluster, value-or-tuple); stat: function(list of values) -> float."""
    by = collections.defaultdict(list)
    for c, v in units:
        by[c].append(v)
    keys = sorted(by)
    rng = random.Random(seed)
    est = stat([v for c in keys for v in by[c]])
    boots = []
    for _ in range(n):
        sample = [v for c in (rng.choice(keys) for _ in keys) for v in by[c]]
        boots.append(stat(sample))
    boots.sort()
    return {"est": round(est, 3), "ci95": [round(boots[int(0.025 * n)], 3), round(boots[int(0.975 * n) - 1], 3)],
            "n_items": len(units), "n_clusters": len(keys)}


def acc(vals):
    return sum(vals) / len(vals) if vals else float("nan")


def balanced_acc(vals):
    """vals: (answer, correct)."""
    by = collections.defaultdict(list)
    for a, ok in vals:
        by[a].append(ok)
    return sum(acc(v) for v in by.values()) / len(by)


def analyse(items, scores):
    out = {}
    fam = collections.defaultdict(list)
    for iid, it in items.items():
        if iid in scores:
            fam[it["family"]].append(it)
    out["coverage"] = {f: len(v) for f, v in fam.items()}
    out["boundary_merges"] = sum(not all(s["boundary_ok"]) for s in scores.values())
    # probes
    for f in ("sonda_celula", "sonda_compat", "sonda_separa", "sonda_contradicao", "sonda_veredicto"):
        units = [(it["cluster"], (it["answer"], choice(it, scores[it["item_id"]]) == it["answer"])) for it in fam[f]]
        out[f] = {"accuracy": cluster_boot(units, lambda v: acc([x[1] for x in v])),
                  "balanced_accuracy": cluster_boot(units, balanced_acc),
                  "chance": round(1 / len(fam[f][0]["candidates"]), 3) if fam[f] else None,
                  "choices": dict(collections.Counter(choice(it, scores[it["item_id"]]) for it in fam[f]))}
    # minimal pairs
    pairs = collections.defaultdict(dict)
    for it in fam["par_minimo"]:
        pairs[it["meta"]["pair"]][it["meta"]["side"]] = it
    pu = []
    for pid, d in pairs.items():
        if set(d) != {"A", "B"}:
            continue
        A, B = d["A"], d["B"]
        cA, cB = choice(A, scores[A["item_id"]]), choice(B, scores[B["item_id"]])
        pA, pB = probs(scores[A["item_id"]]["scores"]), probs(scores[B["item_id"]]["scores"])
        ri = A["candidates"].index('rejected"')
        rej_side, oth = (pA, pB) if A["answer"] == 'rejected"' else (pB, pA)
        pu.append((A["cluster"], (cA != cB, cA == A["answer"] and cB == B["answer"], rej_side[ri] > oth[ri],
                                  rej_side[ri] - oth[ri])))
    out["pares_minimos"] = {"pairs": len(pu),
                            "sensitivity": cluster_boot(pu, lambda v: acc([x[0] for x in v])),
                            "both_correct": cluster_boot(pu, lambda v: acc([x[1] for x in v])),
                            "p_rejected_moves_right_way": cluster_boot(pu, lambda v: acc([x[2] for x in v])),
                            "mean_shift_p_rejected": cluster_boot(pu, lambda v: sum(x[3] for x in v) / len(v))}
    # metamorphoses (verdict)
    base = collections.defaultdict(dict)
    for it in fam["meta_verdict"]:
        base[it["meta"]["base"]][it["meta"]["transform"]] = it
    mv = {}
    for tr in ("cards", "enum", "attr"):
        units = []
        for b, d in base.items():
            if "orig" in d and tr in d:
                units.append((d["orig"]["cluster"], choice(d["orig"], scores[d["orig"]["item_id"]]) ==
                              choice(d[tr], scores[d[tr]["item_id"]])))
        mv[tr] = cluster_boot(units, acc)
    orig = [d["orig"] for d in base.values() if "orig" in d]
    mv["orig_accuracy"] = cluster_boot([(it["cluster"], choice(it, scores[it["item_id"]]) == it["answer"]) for it in orig], acc)
    mv["orig_choice_distribution"] = dict(collections.Counter(choice(it, scores[it["item_id"]]) for it in orig))
    mv["orig_recall"] = {a: f"{sum(choice(it, scores[it['item_id']]) == a for it in orig if it['answer'] == a)}/"
                            f"{sum(it['answer'] == a for it in orig)}" for a in ('rejected"', 'supported"', 'undetermined"')}
    out["metamorfoses_veredicto"] = mv
    # query choice
    qb = collections.defaultdict(dict)
    for it in fam["query_choice"]:
        qb[it["meta"]["base"]][it["meta"]["transform"]] = it
    qu_inv, qu_info, qu_pos1, qu_pos1_rev, qu_val = [], [], [], [], []
    for b, d in qb.items():
        if set(d) != {"orig", "menu_reversed"}:
            continue
        o, r = d["orig"], d["menu_reversed"]
        co, cr = choice(o, scores[o["item_id"]]), choice(r, scores[r["item_id"]])
        qu_inv.append((o["cluster"], o["meta"]["input_of"][co] == r["meta"]["input_of"][cr]))
        po = probs(scores[o["item_id"]]["scores"])
        mass_info = sum(p for c, p in zip(o["candidates"], po) if o["meta"]["informative"][c])
        share_info = sum(o["meta"]["informative"].values()) / len(o["candidates"])
        qu_info.append((o["cluster"], (mass_info, share_info)))
        qu_pos1.append((o["cluster"], o["meta"]["position"][co] == 1))
        v2 = o["meta"]["value2"]
        best, mean_u = max(v2.values()), sum(v2.values()) / len(v2)
        exp_model = sum(p * v2[c] for c, p in zip(o["candidates"], po))
        qu_val.append((o["cluster"], (exp_model, mean_u, best, v2[co])))
        qu_pos1_rev.append((r["cluster"], r["meta"]["position"][cr] == 1))
    out["escolha_de_consulta"] = {
        "invariance_to_menu_reversal": cluster_boot(qu_inv, acc),
        "chooses_position_1_orig": cluster_boot(qu_pos1, acc),
        "chooses_position_1_reversed": cluster_boot(qu_pos1_rev, acc),
        "prob_mass_on_informative": cluster_boot(qu_info, lambda v: sum(x[0] for x in v) / len(v)),
        "informative_share_uniform_baseline": cluster_boot(qu_info, lambda v: sum(x[1] for x in v) / len(v)),
        "value2_expected_under_model": cluster_boot(qu_val, lambda v: sum(x[0] for x in v) / len(v)),
        "value2_of_chosen": cluster_boot(qu_val, lambda v: sum(x[3] for x in v) / len(v)),
        "value2_uniform": cluster_boot(qu_val, lambda v: sum(x[1] for x in v) / len(v)),
        "value2_best": cluster_boot(qu_val, lambda v: sum(x[2] for x in v) / len(v))}
    return out


if __name__ == "__main__":
    items, scores = load(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps(analyse(items, scores), ensure_ascii=False, indent=1))

"""Round-0 audit of the v3 generator on development seeds only (no reserve, no model)."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src" / "m17_audit"))
import generator_v3 as g  # noqa: E402
import stats as S  # noqa: E402

DEV_SEEDS = (91001, 91003, 91009)
PER_CELL = 3
ALPHA = 0.05
STRATIFY_K0 = True
INFEASIBLE_CELLS: list = []
INFEASIBLE = {("undetermined", "stable_informative")}


def dev_set(seeds=DEV_SEEDS, per_cell=PER_CELL, with_indirect=False, balanced=False):
    worlds = []
    for seed in seeds:
        for diff, fam, target in product(g.DIFFICULTIES, g.FAMILIES, g.VERDICTS):
            kinds = (g.KINDS_V2 if with_indirect else g.KINDS) if diff == "medio" else g.KINDS[:2]
            for kind in kinds:
                if (target, kind) in INFEASIBLE:
                    continue
                for i in range(1, per_cell + 1):
                    k0 = (2 + (i - 1) % 3) if STRATIFY_K0 else None
                    try:
                        worlds.append(g.make_world(seed, diff, fam, i, target, kind, k0=k0, max_tries=1500))
                    except RuntimeError:
                        INFEASIBLE_CELLS.append([diff, fam, target, kind, k0])
    if balanced:
        worlds = balance_trim(worlds)
    return worlds


def balance_trim(worlds):
    """Equalise targets inside every (difficulty, family, initial-row-count) group so that structural
    properties of the public state cannot differ between targets. Deterministic (by world_id)."""
    groups = defaultdict(lambda: defaultdict(list))
    for w in worlds:
        groups[(w["meta"]["difficulty"], w["meta"]["family"], len(w["hidden"]["obs"]))][w["reference"]["target_verdict"]].append(w)
    keep = []
    for g_, by_t in groups.items():
        m = min(len(by_t[t]) for t in g.VERDICTS) if all(by_t[t] for t in g.VERDICTS) else 0
        for t in g.VERDICTS:
            keep += sorted(by_t[t], key=lambda w: w["world_id"] + w["reference"]["kind"])[:m]
    return keep


def public_state(p):
    """Only public fields; recomputes the verdict by an independent route."""
    cards = {c["id"]: hs_card(c) for c in p["candidate_models"]}
    return cards


def hs_card(card):
    return g.hs.card_hypothesis(g.D, card)


def public_verdict(p, extra_rows=()):
    rows = [(g.INPUTS.index(g.D.as_tuple(o["input"])), o["output"]) for o in p["observations"]] + list(extra_rows)
    w = hs_card(next(c for c in p["candidate_models"] if c["id"] == p["working_model_id"]))
    T = [g.INPUTS.index(g.D.as_tuple(x)) for x in p["held_out_inputs"]]
    return g.verdict(g.admissible_idx(rows), w, T)


def features(p):
    obs = p["observations"]
    ids = [int(o["id"][1:]) for o in obs]
    cid = [c["id"] for c in p["candidate_models"]]
    A0 = g.admissible_idx([(g.INPUTS.index(g.D.as_tuple(o["input"])), o["output"]) for o in obs])
    outs = [o["output"] for o in obs]
    return {"S": {"n_obs": len(obs), "obs_id_first": ids[0] // 100, "obs_id_sorted": ids == sorted(ids),
                  "work_pos": cid.index(p["working_model_id"]), "cards_sorted": cid == sorted(cid),
                  "json_len": len(json.dumps(p, sort_keys=True)) // 40,
                  "menu_len": len(p["query_menu"]), "first_menu_glyph": p["query_menu"][0]["input"]["glyph"]},
            "D": {"ones": sum(o == "1" for o in outs), "distinct_in": len({json.dumps(o["input"], sort_keys=True) for o in obs}),
                  "cards_support": "".join(str(len(g.SUPPORT[hs_card(c)])) for c in p["candidate_models"])},
            "E": {"A0": min(len(A0), 12), "cards_fit": sum(all(hs_card(c)[g.INPUTS.index(g.D.as_tuple(o["input"]))] == o["output"] for o in obs) for c in p["candidate_models"])}}


def col(rows, grp, name):
    vals = [r[grp][name] for r in rows]
    if all(isinstance(v, int) and not isinstance(v, bool) for v in vals) and len(set(vals)) > 6:
        b = S.quantile_bins(vals)
        vals = [b(v) for v in vals]
    return vals


def audit(worlds):
    labels = [w["reference"]["target_verdict"] for w in worlds]
    rows = [features(w["public"]) for w in worlds]
    out = {"worlds": len(worlds), "model_calls": 0, "seeds": list(DEV_SEEDS),
           "set_sha256": hashlib.sha256("\n".join(json.dumps(w["public"], sort_keys=True) for w in worlds).encode()).hexdigest()}
    out["infeasible_cells_skipped"] = sorted({tuple(c) for c in INFEASIBLE_CELLS})
    out["balance"] = {"target_verdict": dict(Counter(labels)),
                      "max_share": max(Counter(labels).values()) / len(labels),
                      "kind": dict(Counter(w["reference"]["kind"] for w in worlds)),
                      "queries_needed": dict(Counter(str(w["reference"]["queries_needed"]) for w in worlds)),
                      "initial_verdict": dict(Counter(w["reference"]["initial_verdict"] for w in worlds)),
                      "should_revise_by_kind": {k: sum(w["reference"]["should_revise"] for w in worlds if w["reference"]["kind"] == k)
                                                for k in g.KINDS}}
    # identifiability: verdict recomputed from public information only, on the oracle history
    mism = 0
    for w in worlds:
        extra = [(q, w["hidden"]["h"][q]) for q in w["reference"]["oracle_queries"]]
        mism += public_verdict(w["public"], extra) != w["reference"]["target_verdict"]
        mism += public_verdict(w["public"]) != w["reference"]["initial_verdict"]
    out["identifiability"] = {"public_recomputation_mismatches": mism}
    # duplicates (canonical public state)
    canon = Counter(json.dumps([sorted((json.dumps(o["input"], sort_keys=True), o["output"]) for o in w["public"]["observations"]),
                                sorted(json.dumps(c["table"], sort_keys=True) for c in w["public"]["candidate_models"]),
                                w["public"]["working_model_id"] and 0, sorted(json.dumps(x, sort_keys=True) for x in w["public"]["held_out_inputs"])])
                    for w in worlds)
    out["duplicate_public_states"] = sum(c - 1 for c in canon.values() if c > 1)
    # R1: state-only rule from public evidence features (A0 size, fitting cards, n_obs)
    key = [(r["E"]["A0"], r["E"]["cards_fit"], r["S"]["n_obs"]) for r in rows]
    tab = defaultdict(Counter)
    for k, y in zip(key, labels):
        tab[k][y] += 1
    # leave-one-out to avoid optimism
    ok = 0
    for i, (k, y) in enumerate(zip(key, labels)):
        c = Counter(tab[k]); c[y] -= 1
        pred = c.most_common(1)[0][0] if sum(c.values()) > 0 else "supported"
        ok += pred == y
    lo, hi = S.wilson(ok, len(labels))
    maj = max(Counter(labels).values()) / len(labels)
    out["R1_state_only_rule"] = {"accuracy_loo": ok / len(labels), "ci95": [lo, hi], "majority_baseline": maj,
                                 "chance_uniform": 1 / len(set(labels))}
    # R4 leakage: surface+distribution vs target verdict
    cols = {}
    for grp in ("S", "D"):
        for name in rows[0][grp]:
            cols[f"{grp}.{name}"] = col(rows, grp, name)
    pv = {k: S.association(v, labels)["p"] for k, v in cols.items()}
    adj = S.holm(pv, ALPHA)
    out["R4_leakage"] = {"tests": len(pv), "rejected_after_holm": sorted(k for k, (_, r) in adj.items() if r),
                         "smallest": sorted(({"feature": k, "p": pv[k]} for k in pv), key=lambda d: d["p"])[:4]}
    sd = [{f"{grp}.{n}": col(rows, grp, n)[i] for grp in ("S", "D") for n in rows[0][grp]} for i in range(len(rows))]
    nb = S.naive_bayes_cv(sd, labels)
    out["R4_leakage"]["naive_bayes_SD"] = {"accuracy": nb["accuracy"], "ci95": nb["ci95"], "majority_baseline": maj}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--no-stratify", action="store_true")
    a = ap.parse_args()
    global STRATIFY_K0
    STRATIFY_K0 = not a.no_stratify
    r = audit(dev_set())
    text = json.dumps(r, ensure_ascii=False, indent=2) + "\n"
    if a.output:
        a.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()

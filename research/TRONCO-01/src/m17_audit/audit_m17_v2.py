"""M17 audit v2 (alternative (a)): generator audit on dev and substitute families.

Never generates a reserved world (see guard.py). Output is aggregate-only plus set hashes;
world IDs are not written. Run:  python audit_m17_v2.py --output results/RONDA_N.json
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import guard
import features as F
import identifiability as I
import stats as S

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "m17"))
from agents import SymbolicActiveControl  # noqa: E402
from environment import Episode  # noqa: E402

CATS = guard.CATEGORIES
ALPHA = 0.05
PERMS_NULL = 100


def canonical_public(public: dict) -> str:
    """Public state without record/query IDs and ordering: used to detect duplicates across sets."""
    p = copy.deepcopy(public)
    obs = sorted((json.dumps(o["input"], sort_keys=True), o["output"]) for o in p["observations"])
    menu = sorted(json.dumps(q["input"], sort_keys=True) for q in p["query_menu"])
    cards = sorted(json.dumps({k: c[k] for k in ("statement", "table")}, sort_keys=True)
                   for c in p["candidate_models"])
    work = json.dumps({k: p["working_model"][k] for k in ("statement", "table")}, sort_keys=True)
    return json.dumps([obs, menu, cards, work])


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def set_hashes(worlds):
    return {"worlds": len(worlds),
            "public_states_sha256": sha("\n".join(json.dumps(w["public"], sort_keys=True) for w in worlds)),
            "world_ids_sha256": sha("\n".join(w["world_id"] for w in worlds)),
            "canonical_public_sha256": sha("\n".join(sorted(canonical_public(w["public"]) for w in worlds)))}


def binned_columns(rows, group):
    """Per-feature categorical columns for a feature group, with pooled (category-blind) bins."""
    cols = {}
    for name in rows[0][group]:
        vals = [r[group][name] for r in rows]
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
            b = S.quantile_bins(vals)
            vals = [b(v) for v in vals]
        cols[name] = vals
    return cols


def leak_tests(rows, labels, groups=("S", "D")):
    cols = {}
    for g in groups:
        cols.update({f"{g}.{k}": v for k, v in binned_columns(rows, g).items()})
    cats = sorted(set(labels))
    results, pvals = {}, {}
    contrasts = [("ALL", None)] + [(f"{a}|{b}", (a, b)) for a, b in combinations(cats, 2)]
    for name, col in cols.items():
        for cname, pair in contrasts:
            idx = range(len(labels)) if pair is None else [i for i, y in enumerate(labels) if y in pair]
            idx = list(idx)
            r = S.association([col[i] for i in idx], [labels[i] for i in idx])
            key = f"{name}@{cname}"
            results[key] = r
            pvals[key] = r["p"]
    adj = S.holm(pvals, ALPHA)
    rejected = sorted(k for k, (_, rej) in adj.items() if rej)
    top = sorted(pvals, key=pvals.get)[:5]
    return {"tests": len(pvals), "rejected_after_holm": rejected,
            "smallest": [{"test": k, "p": pvals[k], "p_holm": adj[k][0],
                          "cramers_v": results[k]["cramers_v"], "n": results[k]["n"]} for k in top]}, cols


def null_calibration(rows, labels, perms=PERMS_NULL, seed=7):
    """Permute category labels: the share of permutations with any Holm rejection must be about alpha."""
    rng = random.Random(seed)
    any_rej = 0
    base_cols = {}
    for g in ("S", "D"):
        base_cols.update({f"{g}.{k}": v for k, v in binned_columns(rows, g).items()})
    cats = sorted(set(labels))
    for _ in range(perms):
        perm = labels[:]
        rng.shuffle(perm)
        pvals = {}
        for name, col in base_cols.items():
            pvals[name] = S.association(col, perm)["p"]          # 5-way family only (fast)
        any_rej += any(rej for _, rej in S.holm(pvals, ALPHA).values())
    return {"permutations": perms, "family": "5-way tests, S+D features", "share_with_any_rejection": any_rej / perms}


def nb_rows(rows, groups):
    out = []
    for i in range(len(rows)):
        d = {}
        for g in groups:
            for k, v in binned_columns(rows, g).items():
                d[f"{g}.{k}"] = v[i]
        out.append(d)
    return out


def classifier_block(rows, labels):
    sd = nb_rows(rows, ("S", "D"))
    e = nb_rows(rows, ("E",))
    return {"surface_and_distribution": {**S.naive_bayes_cv(sd, labels),
                                         "pairwise": {k: {"accuracy": v["accuracy"], "ci95": v["ci95"]}
                                                      for k, v in S.pairwise_nb(sd, labels).items()}},
            "evidence_positive_control": S.naive_bayes_cv(e, labels)}


def transfer(train_rows, train_labels, test_rows, test_labels, groups):
    """Naive Bayes fitted on one set, scored on another (family transfer)."""
    cols_tr, cols_te = {}, {}
    for g in groups:
        for name in train_rows[0][g]:
            vals_tr = [r[g][name] for r in train_rows]
            vals_te = [r[g][name] for r in test_rows]
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals_tr):
                b = S.quantile_bins(vals_tr)
                vals_tr, vals_te = [b(v) for v in vals_tr], [b(v) for v in vals_te]
            cols_tr[f"{g}.{name}"], cols_te[f"{g}.{name}"] = vals_tr, vals_te
    names = sorted(cols_tr)
    classes = sorted(set(train_labels))
    prior = Counter(train_labels)
    counts = {(y, k): Counter() for y in classes for k in names}
    levels = {k: set() for k in names}
    for i, y in enumerate(train_labels):
        for k in names:
            counts[(y, k)][cols_tr[k][i]] += 1
            levels[k].add(cols_tr[k][i])
    import math
    correct = 0
    for i, y_true in enumerate(test_labels):
        best, best_s = None, -1e300
        for y in classes:
            s = math.log(prior[y] / len(train_labels))
            for k in names:
                s += math.log((counts[(y, k)][cols_te[k][i]] + 1) / (prior[y] + len(levels[k]) + 1))
            if s > best_s:
                best, best_s = y, s
        correct += best == y_true
    lo, hi = S.wilson(correct, len(test_labels))
    return {"accuracy": correct / len(test_labels), "ci95": [lo, hi], "n": len(test_labels),
            "chance": 1 / len(classes)}


def planted_end_to_end(worlds, strength, seed=11):
    """Plant a leak into real public states (first observation ID encodes the category) and run
    the same pipeline. Positive control for the extractor and the tests together."""
    rng = random.Random(seed)
    rows, labels = [], []
    for w in worlds:
        pub = copy.deepcopy(w["public"])
        if rng.random() < strength:
            code = F.OBS_ID_POOL[CATS.index(w["category"])]
            pub["observations"][0]["id"] = "r" + code
        rows.append(F.extract(pub))
        labels.append(w["category"])
    res, _ = leak_tests(rows, labels)
    hit = [k for k in res["rejected_after_holm"] if k.startswith("S.obs_id_first_rank")]
    return {"strength": strength, "detected": bool(hit), "rejected_tests": len(res["rejected_after_holm"])}


def state_only_rule(K_by_world, labels, fit_on=None):
    """Best fixed answer per support set, fitted on `fit_on` (default: the same worlds)."""
    fit = fit_on if fit_on is not None else list(range(len(labels)))
    table = defaultdict(Counter)
    for i in fit:
        table[K_by_world[i]][labels[i]] += 1
    rule = {k: v.most_common(1)[0][0] for k, v in table.items()}
    return rule


def state_only_accuracy(K_by_world, labels, rule, idx):
    exp = I.EXPECTED
    cat_ok = sum(rule.get(K_by_world[i]) == labels[i] for i in idx)
    ver_ok = sum(exp.get(rule.get(K_by_world[i]), None) == exp[labels[i]] for i in idx)
    lo, hi = S.wilson(cat_ok, len(idx))
    vlo, vhi = S.wilson(ver_ok, len(idx))
    return {"n": len(idx), "category_accuracy": cat_ok / len(idx), "category_ci95": [lo, hi],
            "verdict_accuracy": ver_ok / len(idx), "verdict_ci95": [vlo, vhi]}


def symbolic_probe(worlds):
    per = defaultdict(Counter)
    for w in worlds:
        r = Episode(w).run(SymbolicActiveControl())
        c = per[w["category"]]
        c["n"] += 1
        c["decision_correct"] += r["decision_correct"]
        c["diagnosis_correct"] += r["diagnosis_correct"]
        c["localized_correct"] += r["localized_correct"]
        c["queries_" + str(r["query_count"])] += 1
        c["invalid_actions"] += r["invalid_actions"]
        c["forced_termination"] += r["forced_termination"]
    out = {}
    for cat in CATS:
        c = per[cat]
        out[cat] = {**dict(c), "decision_ci95": S.wilson(c["decision_correct"], c["n"]),
                    "localized_ci95": S.wilson(c["localized_correct"], c["n"])}
    return out


MENU_KEYS = ("menu_first_informative_pos", "menu_informative_count")


def reclassify(rows):
    """Round 2 correction: menu informativeness is computed from the evidence, so it is E, not S."""
    for r in rows:
        for k in MENU_KEYS:
            r["E"][k] = r["S"].pop(k)
    return rows


def ambiguous_subset(rows, labels, ident):
    """Round 2: the evidence cannot settle NORMAL vs CHANGE at the start; test whether surface or
    distribution features could. This is the only place where an accidental clue would be a shortcut."""
    idx = [i for i, r in enumerate(ident) if r["ambiguous_at_start"]]
    sub_rows = [rows[i] for i in idx]
    sub_labels = [labels[i] for i in idx]
    res, _ = leak_tests(sub_rows, sub_labels)
    sd = nb_rows(sub_rows, ("S", "D"))
    return {"n": len(idx), "by_category": dict(Counter(sub_labels)), "association": res,
            "naive_bayes_surface_and_distribution": S.naive_bayes_cv(sd, sub_labels),
            "majority_baseline": max(Counter(sub_labels).values()) / len(idx)}


def audit(perms=PERMS_NULL, round_no=2) -> dict:
    t0 = time.time()
    sets = {"dev": guard.build_set(guard.DEV), "substitute": guard.build_set(guard.SUBSTITUTE)}
    requested = list(guard.REQUESTED)
    guard_ok = all(not (guard.reachable_seeds(s) & guard.RESERVED_SEEDS) for s, _, _, _ in requested)
    out = {"round": round_no, "audit": "M17 v2, alternative (a): dev + substitute families, reserved seeds never generated",
           "model_calls": 0, "reserved_seeds_never_requested": guard_ok,
           "seeds_requested": sorted({s for s, _, _, _ in requested}),
           "sets": {}, "limits": [
               "Substitute families are fresh seeds of the same generator, not the reserved seeds; "
               "findings about generator logic transfer, distributional claims about the reserved sets do not.",
               "Identifiability is evaluated at listed-account level, using the generator's own support "
               "conditions; mechanisms outside the three listed accounts are covered only for HYPOTHESIS_ABSENT.",
               "Association tests have power only for leaks of about 20% prevalence or more at these sample sizes "
               "(see power); weaker leaks are not excluded.",
               "Query analysis is non-adaptive; an adaptive policy can only need fewer queries."]}
    all_public = {}
    for name, worlds in sets.items():
        pub_ok = all(F.public_has_no_hidden_fields(w["public"]) for w in worlds)
        rows = [F.extract(w["public"]) for w in worlds]
        if round_no >= 2:
            rows = reclassify(rows)
        labels = [w["category"] for w in worlds]
        families = [w["family"] for w in worlds]
        ident = [I.analyse(w) for w in worlds]
        Ks = [tuple(r["support_categories"]) for r in ident]
        block = {"hashes": set_hashes(worlds), "public_has_no_hidden_fields": pub_ok,
                 "worlds_by_category": dict(Counter(labels)), "families": sorted(set(families))}
        # identifiability
        by_cat = {}
        for cat in CATS:
            sub = [r for r, y in zip(ident, labels) if y == cat]
            by_cat[cat] = {"n": len(sub), "self_consistent": sum(r["self_consistent"] for r in sub),
                           "ambiguous_at_start": sum(r["ambiguous_at_start"] for r in sub),
                           "verdict_ambiguous_at_start": sum(r["verdict_ambiguous_at_start"] for r in sub),
                           "non_identifiable": sum(r["non_identifiable"] for r in sub),
                           "budget_identifiable": sum(bool(r["budget_identifiable"]) for r in sub),
                           "min_queries": dict(Counter(str(r["min_queries"]) for r in sub)),
                           "support_sets": dict(Counter("+".join(r["support_categories"]) for r in sub))}
        block["identifiability"] = by_cat
        # state-only shortcut
        rule = state_only_rule(Ks, labels)
        block["state_only_rule"] = {"rule": {"+".join(k): v for k, v in rule.items()},
                                    "accuracy_same_set": state_only_accuracy(Ks, labels, rule, list(range(len(labels))))}
        block["_Ks"], block["_rule"] = Ks, rule
        # leak tests
        res, _ = leak_tests(rows, labels)
        block["leakage_association"] = res
        block["leakage_null_calibration"] = null_calibration(rows, labels, perms=perms)
        block["classifiers"] = classifier_block(rows, labels)
        if round_no >= 2:
            block["evidence_ambiguous_subset"] = ambiguous_subset(rows, labels, ident)
        all_public[name] = (rows, labels, families)
        out["sets"][name] = block
    # family structure inside the substitute set
    rows, labels, fam = all_public["substitute"]
    cols = {}
    for g in ("S", "D"):
        cols.update({f"{g}.{k}": v for k, v in binned_columns(rows, g).items()})
    fam_p = {k: S.association(v, fam)["p"] for k, v in cols.items()}
    adj = S.holm(fam_p, ALPHA)
    out["family_effect_on_surface_and_distribution"] = {
        "tests": len(fam_p), "rejected_after_holm": sorted(k for k, (_, r) in adj.items() if r),
        "smallest": sorted(({"feature": k, "p": fam_p[k]} for k in fam_p), key=lambda d: d["p"])[:5]}
    # per-family leak association within each family (category vs surface/distribution)
    per_family = {}
    for f in sorted(set(fam)):
        idx = [i for i, x in enumerate(fam) if x == f]
        r, _ = leak_tests([rows[i] for i in idx], [labels[i] for i in idx])
        per_family[f] = {"n": len(idx), "tests": r["tests"], "rejected_after_holm": r["rejected_after_holm"]}
    out["leakage_by_family"] = per_family
    # transfer dev -> each substitute family
    dev_rows, dev_labels, _ = all_public["dev"]
    tr = {}
    for f in sorted(set(fam)):
        idx = [i for i, x in enumerate(fam) if x == f]
        tr[f] = {"surface_and_distribution": transfer(dev_rows, dev_labels, [rows[i] for i in idx],
                                                      [labels[i] for i in idx], ("S", "D")),
                 "evidence_positive_control": transfer(dev_rows, dev_labels, [rows[i] for i in idx],
                                                       [labels[i] for i in idx], ("E",))}
    out["transfer_dev_to_substitute_family"] = tr
    # state-only rule fitted on dev, applied to substitute
    Kd, rule_d = out["sets"]["dev"]["_Ks"], out["sets"]["dev"]["_rule"]
    Ks_sub = out["sets"]["substitute"]["_Ks"]
    out["state_only_rule_dev_to_substitute"] = {
        f: state_only_accuracy(Ks_sub, labels, rule_d, [i for i, x in enumerate(fam) if x == f])
        for f in sorted(set(fam))}
    for b in out["sets"].values():
        b.pop("_Ks"), b.pop("_rule")
    # cross-set duplicates
    canon = {n: Counter(canonical_public(w["public"]) for w in ws) for n, ws in sets.items()}
    out["duplicate_public_states"] = {
        "within_dev": sum(c - 1 for c in canon["dev"].values() if c > 1),
        "within_substitute": sum(c - 1 for c in canon["substitute"].values() if c > 1),
        "across_dev_and_substitute": len(set(canon["dev"]) & set(canon["substitute"]))}
    # power
    n_tests = out["sets"]["dev"]["leakage_association"]["tests"]
    out["power"] = {
        "synthetic": {str(s): S.detection_rate(60, 5, s, n_tests, sims=100) for s in (0.1, 0.2, 0.3, 0.4)},
        "end_to_end_on_dev": [planted_end_to_end(sets["dev"], s) for s in (0.0, 0.1, 0.2, 0.3, 0.5)],
        "note": "synthetic: share of simulated planted leaks rejected by Holm over all tests (60 worlds per category)"}
    # label consistency: public-only symbolic reference
    out["symbolic_reference_probe"] = {n: symbolic_probe(ws) for n, ws in sets.items()}
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--perms", type=int, default=PERMS_NULL)
    ap.add_argument("--round", type=int, default=2, dest="round_no")
    args = ap.parse_args()
    result = audit(perms=args.perms, round_no=args.round_no)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()

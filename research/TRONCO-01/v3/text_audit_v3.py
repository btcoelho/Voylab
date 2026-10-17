"""Audit of the text presentation of v3 states (prediction Q11). Dev/confirmation seeds only, no model."""
from __future__ import annotations

import argparse
import json
from itertools import combinations
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src" / "m17_audit"))
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import stats as S  # noqa: E402

CONFIRM_SEEDS = (93001, 93003, 93009)
BALANCED = True


def render_prompt(p: dict) -> str:
    """Deterministic text shown to a language-model agent. Same order as the JSON state, no extra hints."""
    L = ["OBSERVAÇÕES"]
    L += [f"- {o['id']}: " + ", ".join(f"{k}={v}" for k, v in o["input"].items()) + f" -> {o['output']}"
          for o in p["observations"]]
    L.append("CARTAS")
    for c in p["candidate_models"]:
        L.append(f"- {c['id']} ({c['statement']})")
        L += [f"    {k} -> {v}" for k, v in c["table"].items()]
    L.append(f"CARTA DE TRABALHO: {p['working_model_id']}")
    L.append("ENTRADAS RETIDAS (prever depois)")
    L += ["- " + ", ".join(f"{k}={v}" for k, v in x.items()) for x in p["held_out_inputs"]]
    L.append(f"CONSULTAS DISPONÍVEIS (orçamento {p['remaining_query_budget']})")
    L += [f"- {q['id']}: " + ", ".join(f"{k}={v}" for k, v in q["input"].items()) for q in p["query_menu"]]
    return "\n".join(L)


def text_features(w):
    p = w["public"]
    t = render_prompt(p)
    lines = t.split("\n")
    work_line = next(i for i, ln in enumerate(lines) if ln.startswith("- " + p["working_model_id"] + " ("))
    ids = [c["id"] for c in p["candidate_models"]]
    menu_inputs = [g.INPUTS.index(g.D.as_tuple(q["input"])) for q in p["query_menu"]]
    return {"chars": len(t) // 80, "lines": len(lines), "work_card_line": work_line // 3,
            "work_card_position": ids.index(p["working_model_id"]), "card_ids_sorted": ids == sorted(ids),
            "menu_len": len(menu_inputs)}, useful_positions(w, menu_inputs), len(menu_inputs)


def useful_positions(w, menu_inputs):
    """Menu positions of every query that belongs to at least one minimal determining set (all of them, not the first found)."""
    need = w["reference"]["queries_needed"]
    if not need:
        return None
    hid = w["hidden"]
    base = [(i, hid["h"][i]) for i in hid["obs"]]
    found = set()
    for combo in combinations(hid["menu"], need):
        if g.verdict(g.admissible_idx(base + [(i, hid["h"][i]) for i in combo]), hid["w"], hid["T"]) != "undetermined":
            found |= set(combo)
    return sorted(menu_inputs.index(q) for q in found)


def audit(worlds):
    labels = [w["reference"]["target_verdict"] for w in worlds]
    feats, useful, lens = zip(*[text_features(w) for w in worlds])
    pv = {}
    for name in feats[0]:
        vals = [f[name] for f in feats]
        if all(isinstance(v, int) and not isinstance(v, bool) for v in vals) and len(set(vals)) > 6:
            b = S.quantile_bins(vals)
            vals = [b(v) for v in vals]
        pv[name] = S.association(vals, labels)["p"]
    # position of useful queries: association with target only among determined targets
    det = [i for i, u in enumerate(useful) if u is not None]
    rel = [round(sum(useful[i]) / len(useful[i]) / (lens[i] - 1) * 4) for i in det]       # mean relative position, 5 levels
    pv["useful_mean_relative_position(det. targets)"] = S.association(rel, [labels[i] for i in det])["p"]
    adj = S.holm(pv, 0.05)
    # is menu position 0 useful more often than chance?  chance per world = |useful| / menu_len
    first = sum(0 in useful[i] for i in det)
    expected = sum(len(useful[i]) / lens[i] for i in det)
    lo, hi = S.wilson(first, len(det))
    first_by_position = Counter(p for i in det for p in useful[i])
    return {"worlds": len(worlds), "model_calls": 0, "target_counts": dict(Counter(labels)),
            "text_features_tests": len(pv), "rejected_after_holm": sorted(k for k, (_, r) in adj.items() if r),
            "smallest": sorted(({"feature": k, "p": pv[k]} for k in pv), key=lambda d: d["p"])[:4],
            "menu_position_0_is_useful": {"observed_share": first / len(det), "ci95": [lo, hi],
                                          "expected_share_if_uniform": expected / len(det), "worlds": len(det)},
            "useful_query_count_by_menu_position": dict(sorted(first_by_position.items()))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--unbalanced", action="store_true")
    args = ap.parse_args()
    global BALANCED
    BALANCED = not args.unbalanced
    worlds = a.dev_set(seeds=CONFIRM_SEEDS, with_indirect=True, balanced=BALANCED)
    r = audit(worlds)
    r["seeds"] = list(CONFIRM_SEEDS)
    text = json.dumps(r, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()

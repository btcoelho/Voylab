"""Audit of the M17 generator: is the expected verdict fixed by what the agent may see?

Development split only (diagnostic and confirmation seeds are never generated).
Output is aggregate-only: no world IDs and no per-world labels are written.

Two questions, both answered from public state plus, on the evaluator side, the
hidden answers to the (at most three) menu queries an agent is allowed to make:

1. Initial rows. Does the v2 contract verdict (supported / rejected / undetermined,
   computed from public rows and the working model only) equal the M17 expected
   verdict, which is looked up from the hidden category?
2. Reachable evidence. For how many worlds does some set of at most three queries
   lead to a public state whose v2 contract verdict equals the M17 expected one?
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "m17"))
sys.path.insert(0, str(HERE.parent.parent / "hypothesis_sets"))

import hypothesis_sets as hs  # noqa: E402
from evaluate_m17 import CATEGORIES, DEV, PER_CATEGORY  # noqa: E402
from generator import QUERY_BUDGET, _hidden_predict, _predict, make_world  # noqa: E402

EXPECTED = {"NORMAL": "supported", "CONTRADICTION": "rejected", "INSUFFICIENCY": "undetermined",
            "CHANGE": "rejected", "HYPOTHESIS_ABSENT": "rejected"}
FIELDS = ("glyph", "setting", "partner", "phase")


def domain_for(public: dict) -> hs.Domain:
    """Domain read off the public state only: levels per field and the output alphabet."""
    levels = {f: [] for f in FIELDS}
    outputs = []
    inputs = [o["input"] for o in public["observations"]] + [q["input"] for q in public["query_menu"]]
    for inp in inputs:
        for f in FIELDS:
            if inp[f] not in levels[f]:
                levels[f].append(inp[f])
    for card in public["candidate_models"]:
        stated = hs._STATEMENT_FEATURES[card["statement"].strip().lower()]
        for key, value in card["table"].items():
            if value not in outputs:
                outputs.append(value)
            for feature, token in zip(stated, key.split("|")):
                if token not in levels[feature]:
                    levels[feature].append(token)
    for o in public["observations"]:
        if o["output"] not in outputs:
            outputs.append(o["output"])
    return hs.Domain(FIELDS, tuple(tuple(sorted(levels[f])) for f in FIELDS), tuple(sorted(outputs)))


def contract_verdict(domain, public, observations) -> str:
    """v2 contract: undetermined only with no rows; else W fits every row or it does not."""
    if not observations:
        return "undetermined"
    ev = hs.Evidence.from_observations(domain, observations)
    return "supported" if hs.card_fits(domain, public["working_model"], ev) else "rejected"


def signature(domain, public) -> tuple:
    """Everything an agent can read off the initial public state, reduced to categorical facts."""
    obs = public["observations"]
    ev = hs.Evidence.from_observations(domain, obs)
    fit = [c for c in public["candidate_models"] if hs.card_fits(domain, c, ev)]
    working_fits = hs.card_fits(domain, public["working_model"], ev)
    informative = False
    for q in public["query_menu"]:
        x = domain.as_tuple(q["input"])
        preds = set()
        for c in fit:
            idx = [domain.features.index(f) for f in hs.card_features(domain, c)]
            preds.add(str(c["table"]["|".join(x[i] for i in idx)]))
        informative |= len(preds) > 1
    return (working_fits, min(len(fit), 2), bool(ev.conflicts), informative)


def audit_world(world: dict) -> dict:
    public = world["public"]
    domain = domain_for(public)
    obs = public["observations"]
    initial = contract_verdict(domain, public, obs)
    target = EXPECTED[world["category"]]
    reachable = initial == target
    menu = public["query_menu"]
    if not reachable:
        for r in range(1, QUERY_BUDGET + 1):
            for subset in combinations(menu, r):
                extra = [{"id": f"x{n}", "input": q["input"],
                          "output": _hidden_predict(world["hidden"], q["input"])}
                         for n, q in enumerate(subset)]
                if contract_verdict(domain, public, obs + extra) == target:
                    reachable = True
                    break
            if reachable:
                break
    working_card = next(c for c in world["cards"] if c["id"] == public["working_model"]["id"])
    separating = sum(_hidden_predict(world["hidden"], q["input"]) != _predict(working_card, q["input"])
                     for q in menu)
    return {"category": world["category"], "initial": initial, "expected": target,
            "reachable": reachable, "signature": signature(domain, public),
            "queries_that_contradict_working_model": separating, "menu_size": len(menu)}


def audit() -> dict:
    per = defaultdict(lambda: Counter())
    sig_to_expected = defaultdict(Counter)
    total = 0
    for seed, family in DEV:
        for ci, category in enumerate(CATEGORIES):
            for i in range(PER_CATEGORY):
                world = make_world(category, family, seed, ci * PER_CATEGORY + i)
                r = audit_world(world)
                total += 1
                c = per[category]
                c["worlds"] += 1
                c["initial_verdict_" + r["initial"]] += 1
                c["initial_matches_expected"] += r["initial"] == r["expected"]
                c["reachable_within_budget"] += r["reachable"]
                c["menu_queries_contradicting_working_model"] += r["queries_that_contradict_working_model"]
                c["menu_queries_total"] += r["menu_size"]
                sig_to_expected[r["signature"]][r["expected"]] += 1
    mixed = {str(sig): dict(v) for sig, v in sig_to_expected.items() if len(v) > 1}
    return {
        "audit": "M17 expected verdict vs what the agent can see (dev split only, aggregate-only)",
        "split": "dev", "seeds": [s for s, _ in DEV], "worlds": total, "model_calls": 0,
        "query_budget": QUERY_BUDGET,
        "signature_fields": ["working_model_fits_all_rows", "fitting_cards(0,1,2+)",
                             "same_input_conflict", "some_menu_query_separates_fitting_cards"],
        "by_category": {c: dict(per[c]) for c in CATEGORIES},
        "public_signatures": {str(k): dict(v) for k, v in sig_to_expected.items()},
        "signatures_with_conflicting_expected_verdicts": mixed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()

"""Counterfactual identifiability of the M17 category, computed from the public state.

For a generated world, list every alternative (category', hidden listed account c') that
the generator *could* have produced from the same public state, using the generator's own
support conditions (the same predicates as `generator.audit_world`, applied to the
alternative instead of the true hidden mechanism). Then ask which menu queries would
separate the true world from each alternative.

Definitions
  support set K(P)    categories having at least one alternative.
  ambiguous at start  |K(P)| > 1: the initial state alone does not fix the category.
  verdict-ambiguous   K(P) holds alternatives with different expected verdicts.
  separating queries  menu queries on which the true hidden answer differs from the
                      alternative's answer.
  non-identifiable    some alternative with a different expected verdict has no separating
                      query anywhere in the menu: no policy can tell the two apart.
  budget-identifiable a set of at most QUERY_BUDGET menu queries separates the world from
                      every alternative with a different expected verdict.
The analysis is non-adaptive (a fixed set of queries), so it is an upper bound on the number
of queries an adaptive policy needs. Hidden answers come from the evaluator side only.
"""
from __future__ import annotations

from itertools import combinations

import guard  # noqa: F401
from features import FIELDS, _cards, _has_conflict, _pair_effect
from generator import QUERY_BUDGET, _hidden_predict, _predict

EXPECTED = {"NORMAL": "supported", "CONTRADICTION": "rejected", "INSUFFICIENCY": "undetermined",
            "CHANGE": "rejected", "HYPOTHESIS_ABSENT": "rejected"}


def _fits(cards, rows):
    return [c for c in cards if all(_predict(c, r["input"]) == r["output"] for r in rows)]


def _fits_after_dropping_one_copy(card, rows):
    """Card consistent with the rows if, for each conflicted input, at least one output is predicted."""
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r["input"][f] for f in FIELDS), []).append(r)
    for group in groups.values():
        pred = _predict(card, group[0]["input"])
        if pred not in {r["output"] for r in group}:
            return False
    return True


def _isolating(fit, target, menu):
    for q in menu:
        v = _predict(target, q["input"])
        if sum(_predict(c, q["input"]) == v for c in fit) == 1:
            return True
    return False


def alternatives(public: dict) -> list[dict]:
    rows = public["observations"]
    menu = public["query_menu"]
    cards = _cards(public)
    by_id = {c["id"]: c for c in cards}
    work = by_id[public["working_model"]["id"]]
    conflict = _has_conflict(rows)
    out = []
    if conflict:
        for c in cards:
            if _fits_after_dropping_one_copy(c, rows):
                out.append({"category": "CONTRADICTION", "hidden": c["id"]})
        return out
    fit = _fits(cards, rows)
    fit_ids = {c["id"] for c in fit}
    if not fit:
        if _pair_effect(rows):
            out.append({"category": "HYPOTHESIS_ABSENT", "hidden": None})
        return out
    zero_port = len(fit) >= 2 and all(
        len({_predict(c, q["input"]) for c in fit}) == 1 for q in menu)
    if len(fit) >= 2 and work["id"] in fit_ids and _isolating(fit, work, menu):
        out.append({"category": "NORMAL", "hidden": work["id"]})
    if zero_port and work["kind"] == "glyph":
        for c in fit:
            if c["kind"] in ("glyph", "glyph_phase"):
                out.append({"category": "INSUFFICIENCY", "hidden": c["id"]})
    if len(fit) >= 2 and work["kind"] == "glyph" and work["id"] in fit_ids:
        for c in fit:
            if c["kind"] == "glyph_phase" and _isolating(fit, c, menu):
                out.append({"category": "CHANGE", "hidden": c["id"]})
    return out


def analyse(world: dict) -> dict:
    """Evaluator-side analysis of one generated world (uses its hidden mechanism)."""
    public = world["public"]
    menu = public["query_menu"]
    cards = {c["id"]: c for c in _cards(public)}
    alts = alternatives(public)
    categories = sorted({a["category"] for a in alts})
    verdicts = sorted({EXPECTED[a["category"]] for a in alts})
    true_answers = [_hidden_predict(world["hidden"], q["input"]) for q in menu]
    own = world["category"]
    sets_to_hit = []
    non_identifiable = 0
    for a in alts:
        if EXPECTED[a["category"]] == EXPECTED[own]:
            continue
        if a["hidden"] is None:
            continue                       # no listed account fits: category fixed by the state itself
        card = cards[a["hidden"]]
        sep = frozenset(i for i, q in enumerate(menu) if _predict(card, q["input"]) != true_answers[i])
        if not sep:
            non_identifiable += 1
        else:
            sets_to_hit.append(sep)
    budget_ok, min_queries = None, None
    if non_identifiable == 0:
        if not sets_to_hit:
            budget_ok, min_queries = True, 0
        else:
            budget_ok, min_queries = False, None
            for r in range(1, QUERY_BUDGET + 1):
                if any(all(set(sub) & s for s in sets_to_hit) for sub in combinations(range(len(menu)), r)):
                    budget_ok, min_queries = True, r
                    break
    return {"category": own, "support_categories": categories, "support_verdicts": verdicts,
            "self_consistent": own in categories,
            "ambiguous_at_start": len(categories) > 1,
            "verdict_ambiguous_at_start": len(verdicts) > 1,
            "alternatives_with_other_verdict": len(sets_to_hit) + non_identifiable,
            "non_identifiable": non_identifiable > 0,
            "budget_identifiable": budget_ok, "min_queries": min_queries}

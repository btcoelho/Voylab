"""Answer-level scoring for v3 (spec section 5 + decomposition of section 11).

An answer is {"stop": "commit"|"suspend", "verdict": str, "admissible_cards": [hypotheses],
              "predictions": {input_index: output}}.
All references are computed from the history the agent actually has, never from a category label.
"""
from __future__ import annotations

import generator_v3 as g


def history_rows(world: dict, queried: list[int]):
    hid = world["hidden"]
    return [(i, hid["h"][i]) for i in list(hid["obs"]) + list(queried)]


def can_still_determine(A, w, T, menu_free) -> bool:
    """Is there an unused query one of whose possible answers would make the verdict determined?"""
    for q in menu_free:
        for y in {h[q] for h in A}:
            if g.verdict(frozenset(h for h in A if h[q] == y), w, T) != "undetermined":
                return True
    return False


def score(world: dict, queried: list[int], answer: dict, left: int) -> dict:
    hid, ref = world["hidden"], world["reference"]
    w, T, menu = hid["w"], hid["T"], hid["menu"]
    rows = history_rows(world, queried)
    A = g.admissible_idx(rows)
    v_ref = g.verdict(A, w, T)
    target = ref["target_verdict"]
    inference_error = answer["verdict"] != v_ref
    search_error = v_ref != target
    evidence_ignored = inference_error and v_ref in ("rejected", "supported")
    free = [q for q in menu if q not in queried]
    determinable = can_still_determine(A, w, T, free) if left > 0 else False
    premature = answer["stop"] == "commit" and left > 0 and v_ref == "undetermined" and determinable
    suspend_correct = (answer["stop"] == "suspend" and v_ref == "undetermined" and not determinable)
    # queries asked when the verdict was already determined
    wasted, seen = 0, list(hid["obs"])
    for q in queried:
        if g.verdict(g.admissible_idx([(i, hid["h"][i]) for i in seen]), w, T) != "undetermined":
            wasted += 1
        seen.append(q)
    preds = answer.get("predictions", {})
    valid = [preds[t] in {h[t] for h in A} for t in T if t in preds]
    exact = [preds[t] == hid["h"][t] for t in T if t in preds]
    ref_cards = [c for c in hid["cards"] if c in A]
    given = list(answer.get("admissible_cards", []))
    sc = g.hs.score_set_answer(frozenset(ref_cards), given) if given or ref_cards else {"exact": True}
    return {"inference_error": inference_error, "search_error": search_error and not inference_error,
            "evidence_ignored": evidence_ignored, "premature_stop": premature, "queries_after_determined": wasted,
            "prediction_valid": (sum(valid) / len(valid)) if valid else None,
            "prediction_exact": (sum(exact) / len(exact)) if exact else None,
            "cards_exact": bool(sc.get("exact")), "reference_verdict": v_ref,
            "suspend_used": answer["stop"] == "suspend", "suspend_correct": suspend_correct,
            "reach": answer["verdict"] == target}

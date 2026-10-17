"""Independent M17 symbolic-system generator; imports no M16 code."""
from __future__ import annotations

import hashlib
import itertools
import random
from copy import deepcopy

QUERY_BUDGET = 3
N_INITIAL_UNIQUE = 7
N_OBSERVATIONS = 8  # fixed across all five hidden categories


def _world_rng(seed, index, family, category):
    raw = f"m17:{seed}:{index}:{family}:{category}".encode()
    return random.Random(int(hashlib.sha256(raw).hexdigest()[:16], 16))


def _id(seed, index, family):
    return hashlib.sha256(f"m17-world:{seed}:{index}:{family}".encode()).hexdigest()[:16]


def _input_key(inp):
    return tuple(inp[k] for k in ("glyph", "setting", "partner", "phase"))


def _predict(card, inp):
    kind = card["kind"]
    table = card["table"]
    if kind == "glyph":
        return table[inp["glyph"]]
    if kind == "setting":
        return table[inp["setting"]]
    if kind == "glyph_phase":
        return table[f"{inp['glyph']}|{inp['phase']}"]
    raise ValueError(kind)


def _hidden_predict(hidden, inp):
    kind = hidden["kind"]
    if kind == "card":
        return _predict(hidden["card"], inp)
    if kind == "pair":
        g = hidden["glyph_index"][inp["glyph"]]
        p = hidden["partner_index"][inp["partner"]]
        s = hidden["setting_index"][inp["setting"]]
        if hidden["family"] == "dev_table":
            v = (g + 2 * p + s) % len(hidden["outputs"])
        elif hidden["family"] == "relational":
            v = (3 * g + p + s) % len(hidden["outputs"])
        elif hidden["family"] == "multiphase":
            v = (g * p + 2 * s + (g ^ p)) % len(hidden["outputs"])
        elif hidden["family"] == "compositional":
            v = (g + p + s + (g * p) % 3) % len(hidden["outputs"])
        else:
            raise ValueError(hidden["family"])
        return hidden["outputs"][v]
    raise ValueError(kind)


def _make_labels(rng):
    glyphs = [f"glyph_{x}" for x in rng.sample(("k2", "m7", "q4", "v9", "b3", "t8"), 4)]
    settings = [f"site_{x}" for x in rng.sample(("r5", "c1", "n8", "d3"), 2)]
    partners = [f"mark_{x}" for x in rng.sample(("h2", "p6", "w4", "a9", "z1", "f7"), 4)]
    phases = [f"state_{x}" for x in rng.sample(("u3", "e8", "j1", "s5"), 2)]
    outputs = [f"out_{x}" for x in rng.sample(("L4", "N2", "R8", "C5", "W1", "G7"), 4)]
    return glyphs, settings, partners, phases, outputs


def _make_menu(rng, glyphs, settings, partners, phases):
    full = [{"glyph": g, "setting": s, "partner": p, "phase": t}
            for g in glyphs for s in settings for p in partners for t in phases]
    while True:
        menu = rng.sample(full, 12)
        glyph_phase = {(x["glyph"], x["phase"]) for x in menu}
        if 5 <= len(glyph_phase) <= 7:
            return menu


def _new_cards(rng, glyphs, settings, phases, outputs):
    codes = rng.sample(("K4", "P7", "V2", "D9", "H3", "M8"), 3)
    cards = [
        {"id": codes[0], "kind": "glyph", "statement": "Output depends only on glyph.",
         "table": {g: rng.choice(outputs) for g in glyphs}},
        {"id": codes[1], "kind": "setting", "statement": "Output depends only on setting.",
         "table": {s: rng.choice(outputs) for s in settings}},
        {"id": codes[2], "kind": "glyph_phase", "statement": "Output depends on glyph and phase.",
         "table": {f"{g}|{t}": rng.choice(outputs) for g in glyphs for t in phases}},
    ]
    return cards


def _public_card(card):
    return {"id": card["id"], "statement": card["statement"], "table": dict(card["table"])}


def _compatible(cards, rows):
    return [c["id"] for c in cards if all(_predict(c, r["input"]) == r["output"] for r in rows)]


def _select_rows(menu, target, cards, rng, mode):
    """Select seven unique rows; categories A/D/E are identifiable from the initial set."""
    candidates = []
    for indexes in itertools.combinations(range(len(menu)), N_INITIAL_UNIQUE):
        inputs = [menu[i] for i in indexes]
        rows = [{"input": x, "output": _hidden_predict(target, x)} for x in inputs]
        fits = _compatible(cards, rows)
        if mode == "unique_target" and fits == [target["card"]["id"]]:
            candidates.append(rows)
        elif mode == "ambiguous_target" and target["card"]["id"] in fits and len(fits) >= 2:
            required = set(target.get("required_fit_ids", ()))
            if not required.issubset(set(fits)):
                continue
            isolating = False
            for q in menu:
                target_value = _predict(target["card"], q)
                if sum(_predict(c, q) == target_value for c in cards if c["id"] in fits) == 1:
                    isolating = True
                    break
            if isolating:
                candidates.append(rows)
        elif mode == "no_candidate" and not fits:
            # Require evidence that changing partner while holding glyph/setting/phase fixed
            # changes output; this makes the missing interaction observable.
            evidence = False
            for a, b in itertools.combinations(rows, 2):
                ia, ib = a["input"], b["input"]
                if ((ia["glyph"], ia["setting"], ia["phase"])
                        == (ib["glyph"], ib["setting"], ib["phase"])
                        and ia["partner"] != ib["partner"] and a["output"] != b["output"]):
                    evidence = True
                    break
            if evidence:
                candidates.append(rows)
        elif mode == "ambiguous" and len(fits) >= 2:
            viable = [c for c in cards if c["id"] in fits]
            indistinguishable_on_port = all(
                _predict(c, q) == _predict(viable[0], q) for c in viable for q in menu
            )
            if indistinguishable_on_port:
                candidates.append(rows)
    if not candidates:
        return None
    return rng.choice(candidates)


def make_world(category: str, family: str, seed: int, index: int):
    """Create one world. `category`, `family`, and all truth live outside public state."""
    if category not in {"NORMAL", "CONTRADICTION", "INSUFFICIENCY", "CHANGE", "HYPOTHESIS_ABSENT"}:
        raise ValueError(category)
    if family not in {"dev_table", "relational", "multiphase", "compositional"}:
        raise ValueError(family)
    rng = _world_rng(seed, index, family, category)
    glyphs, settings, partners, phases, outputs = _make_labels(rng)
    menu = _make_menu(rng, glyphs, settings, partners, phases)
    cards = _new_cards(rng, glyphs, settings, phases, outputs)
    card_by_id = {c["id"]: c for c in cards}
    menu_by_key = {_input_key(x): x for x in menu}

    if category in {"NORMAL", "CONTRADICTION"}:
        true_card = rng.choice(cards)
        target = {"kind": "card", "card": true_card, "required_fit_ids": [true_card["id"]]}
        mode = "unique_target" if category == "CONTRADICTION" else "ambiguous_target"
        rows = _select_rows(menu, target, cards, rng, mode)
        if rows is None:
            # Search fresh, independently randomized cards/menus instead of silently
            # accepting a world the evaluator cannot identify.
            return make_world(category, family, seed + 7919, index)
        working = true_card
    elif category == "INSUFFICIENCY":
        stable = next(c for c in cards if c["kind"] == "glyph")
        phase_card = next(c for c in cards if c["kind"] == "glyph_phase")
        visible_pairs = {(x["glyph"], x["phase"]) for x in menu}
        all_pairs = {(g, t) for g in glyphs for t in phases}
        missing_pairs = all_pairs - visible_pairs
        if not missing_pairs:
            return make_world(category, family, seed + 7919, index)
        for g, t in visible_pairs:
            phase_card["table"][f"{g}|{t}"] = stable["table"][g]
        missing = rng.choice(sorted(missing_pairs))
        changed = stable["table"][missing[0]]
        phase_card["table"][f"{missing[0]}|{missing[1]}"] = rng.choice([o for o in outputs if o != changed])
        target_card = rng.choice((stable, phase_card))
        target = {"kind": "card", "card": target_card}
        rows = _select_rows(menu, target, cards, rng, "ambiguous")
        if rows is None:
            return make_world(category, family, seed + 7919, index)
        working = stable
    elif category == "CHANGE":
        phase_card = next(c for c in cards if c["kind"] == "glyph_phase")
        stable = next(c for c in cards if c["kind"] == "glyph")
        # Ensure the proposed stable account is contradicted by the phase-dependent rule.
        for g in glyphs:
            first = phases[0]
            phase_card["table"][f"{g}|{first}"] = stable["table"][g]
            phase_card["table"][f"{g}|{phases[1]}"] = rng.choice(
                [o for o in outputs if o != stable["table"][g]])
        target = {"kind": "card", "card": phase_card}
        target["required_fit_ids"] = [phase_card["id"], stable["id"]]
        rows = _select_rows(menu, target, cards, rng, "ambiguous_target")
        if rows is None:
            return make_world(category, family, seed + 7919, index)
        working = stable
    else:
        stable = next(c for c in cards if c["kind"] == "glyph")
        target = {"kind": "pair", "glyph_index": {g: i for i, g in enumerate(glyphs)},
                  "partner_index": {p: i for i, p in enumerate(partners)},
                  "setting_index": {s: i for i, s in enumerate(settings)},
                  "outputs": outputs, "family": family}
        rows = _select_rows(menu, target, cards, rng, "no_candidate")
        if rows is None:
            return make_world(category, family, seed + 7919, index)
        working = stable

    # Every category has the same number of rows and a repeated input. Only one
    # category corrupts one copy; order and record IDs are randomized independently.
    duplicate_source = rng.choice(rows)
    observations = [dict(input=dict(r["input"]), output=r["output"]) for r in rows]
    observations.append({"input": dict(duplicate_source["input"]), "output": duplicate_source["output"]})
    if category == "CONTRADICTION":
        duplicate = observations[-1]
        duplicate["output"] = rng.choice([o for o in outputs if o != duplicate["output"]])
    order = list(range(len(observations)))
    rng.shuffle(order)
    record_ids = rng.sample([f"r{x}" for x in ("A2", "C7", "D4", "F9", "H1", "J6", "L3", "N8", "Q5", "S0", "U4", "W7")],
                            len(observations))
    obs = []
    for new_idx, old_idx in enumerate(order):
        row = observations[old_idx]
        obs.append({"id": record_ids[new_idx], "input": dict(row["input"]), "output": row["output"]})

    query_ids = rng.sample([f"q{x}" for x in ("B5", "E1", "G8", "K3", "M6", "P2", "R9", "T4", "V0", "X7", "Y2", "Z6")],
                           len(menu))
    query_menu = [{"id": query_ids[i], "input": dict(inp)} for i, inp in enumerate(menu)]
    rng.shuffle(query_menu)
    public_cards = [_public_card(c) for c in cards]
    rng.shuffle(public_cards)
    return {
        "world_id": _id(seed, index, family),
        "category": category,
        "family": family,
        "seed": seed,
        "index": index,
        "hidden": target,
        "working_model_id": working["id"],
        "cards": cards,
        "public": {
            "task": "Review a device record, a provisional account, and candidate accounts. Decide what the evidence supports. You may request up to three allowed measurements before reporting.",
            "device": "unknown_system",
            "working_model": _public_card(working),
            "candidate_models": public_cards,
            "observations": obs,
            "query_menu": query_menu,
            "remaining_query_budget": QUERY_BUDGET,
            "response_schema": {
                "query": {"action": "query", "query_id": "one ID from query_menu"},
                "report": {"action": "report", "verdict": "supported | rejected | undetermined",
                           "candidate_model_codes": [], "evidence_ids": [],
                           "location": {"feature": "input field or null", "value": "value or null"},
                           "confidence": "number from 0 to 1", "explanation": "short statement"},
            },
        },
    }


def public_world(world):
    return deepcopy(world["public"])


def audit_world(world):
    """Hidden-side proof checks. The returned data are for evaluator files only."""
    from collections import defaultdict

    rows = world["public"]["observations"]
    cards = world["cards"]
    compatible = _compatible(cards, rows)
    conflicts = defaultdict(set)
    for row in rows:
        conflicts[_input_key(row["input"])].add(row["output"])
    has_conflict = any(len(v) > 1 for v in conflicts.values())
    if world["category"] == "NORMAL":
        target = world["hidden"]["card"]["id"]
        target_card = next(c for c in cards if c["id"] == target)
        isolating_query = any(
            sum(_predict(c, q["input"]) == _predict(target_card, q["input"])
                for c in cards if c["id"] in compatible) == 1
            for q in world["public"]["query_menu"]
        )
        identified = target in compatible and len(compatible) >= 2 and isolating_query and not has_conflict
        return {"identified": identified, "compatible_count": len(compatible), "direct_conflict": has_conflict}
    if world["category"] == "CONTRADICTION":
        identified = has_conflict and world["hidden"]["kind"] == "card"
        return {"identified": identified, "compatible_count": len(compatible), "direct_conflict": has_conflict}
    if world["category"] == "INSUFFICIENCY":
        menu = world["public"]["query_menu"]
        fitting = [c for c in cards if c["id"] in compatible]
        same_port = len(fitting) >= 2 and all(
            _predict(c, q["input"]) == _predict(fitting[0], q["input"])
            for c in fitting for q in menu
        )
        identified = same_port and not has_conflict
        return {"identified": identified, "compatible_count": len(compatible),
                "direct_conflict": has_conflict, "zero_port_information": same_port}
    if world["category"] == "CHANGE":
        target = world["hidden"]["card"]["id"]
        target_card = next(c for c in cards if c["id"] == target)
        working = world["working_model_id"]
        isolating_query = any(
            sum(_predict(c, q["input"]) == _predict(target_card, q["input"])
                for c in cards if c["id"] in compatible) == 1
            for q in world["public"]["query_menu"]
        )
        identified = (target in compatible and working in compatible and target != working
                      and len(compatible) >= 2 and isolating_query and not has_conflict)
        return {"identified": identified, "compatible_count": len(compatible), "direct_conflict": has_conflict}
    # An absent mechanism must yield consistent records, no candidate fit, and
    # a directly observable partner interaction in the evidence.
    pair = False
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            ia, ib = a["input"], b["input"]
            if ((ia["glyph"], ia["setting"], ia["phase"])
                    == (ib["glyph"], ib["setting"], ib["phase"])
                    and ia["partner"] != ib["partner"] and a["output"] != b["output"]):
                pair = True
    identified = not compatible and not has_conflict and pair
    return {"identified": identified, "compatible_count": len(compatible),
            "direct_conflict": has_conflict, "pair_effect": pair}


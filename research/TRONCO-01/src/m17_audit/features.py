"""Features of the public state, in three groups.

S  surface: order, IDs, length, key layout. Carry no scientific content, so any
   association with the hidden category would be a leak.
D  distribution: which labels appear, output statistics. Also carry no scientific
   content for the category question, so an association would be a leak.
E  evidence: facts the agent is *supposed* to use (conflicts, which listed accounts fit,
   whether a menu query separates them). Associations here are legitimate; they serve
   as the positive control showing the pipeline can see category information.

Only `world["public"]` is read. Hidden fields are never touched.
"""
from __future__ import annotations

import json
import math
from collections import Counter

import guard  # noqa: F401  (puts ../m17 on sys.path)
from generator import _predict

OBS_ID_POOL = ["A2", "C7", "D4", "F9", "H1", "J6", "L3", "N8", "Q5", "S0", "U4", "W7"]
QUERY_ID_POOL = ["B5", "E1", "G8", "K3", "M6", "P2", "R9", "T4", "V0", "X7", "Y2", "Z6"]
LABEL_POOLS = {
    "glyph": [f"glyph_{x}" for x in ("k2", "m7", "q4", "v9", "b3", "t8")],
    "setting": [f"site_{x}" for x in ("r5", "c1", "n8", "d3")],
    "partner": [f"mark_{x}" for x in ("h2", "p6", "w4", "a9", "z1", "f7")],
    "phase": [f"state_{x}" for x in ("u3", "e8", "j1", "s5")],
    "output": [f"out_{x}" for x in ("L4", "N2", "R8", "C5", "W1", "G7")],
}
FIELDS = ("glyph", "setting", "partner", "phase")


def _kind(statement: str) -> str:
    s = statement.lower()
    return "glyph" if "only on glyph" in s else "setting" if "only on setting" in s else "glyph_phase"


def _cards(public):
    return [{**c, "kind": _kind(c["statement"])} for c in public["candidate_models"]]


def _entropy(values):
    n = len(values)
    return -sum(c / n * math.log2(c / n) for c in Counter(values).values()) if n else 0.0


def _rank(pool, ident, prefix):
    return pool.index(ident[len(prefix):])


def _is_sorted(seq):
    return list(seq) == sorted(seq)


def _dup_positions(obs):
    seen = {}
    for pos, o in enumerate(obs):
        key = tuple(o["input"][f] for f in FIELDS)
        if key in seen:
            return seen[key], pos
        seen[key] = pos
    return None, None


def _fits(cards, rows):
    return [c for c in cards if all(_predict(c, r["input"]) == r["output"] for r in rows)]


def _has_conflict(rows):
    outs = {}
    for r in rows:
        outs.setdefault(tuple(r["input"][f] for f in FIELDS), set()).add(r["output"])
    return any(len(v) > 1 for v in outs.values())


def _phase_effect(rows):
    return any(a["input"]["glyph"] == b["input"]["glyph"] and a["input"]["phase"] != b["input"]["phase"]
               and a["output"] != b["output"] for i, a in enumerate(rows) for b in rows[i + 1:])


def _pair_effect(rows):
    return any(tuple(a["input"][f] for f in ("glyph", "setting", "phase"))
               == tuple(b["input"][f] for f in ("glyph", "setting", "phase"))
               and a["input"]["partner"] != b["input"]["partner"] and a["output"] != b["output"]
               for i, a in enumerate(rows) for b in rows[i + 1:])


def informative_positions(public):
    """Positions in the menu of queries on which the fitting cards disagree."""
    cards = _cards(public)
    fit = _fits(cards, public["observations"])
    out = []
    for pos, q in enumerate(public["query_menu"]):
        if len({_predict(c, q["input"]) for c in fit}) > 1:
            out.append(pos)
    return out


def extract(public: dict) -> dict:
    obs = public["observations"]
    menu = public["query_menu"]
    cards = _cards(public)
    p1, p2 = _dup_positions(obs)
    oid = [_rank(OBS_ID_POOL, o["id"], "r") for o in obs]
    qid = [_rank(QUERY_ID_POOL, q["id"], "q") for q in menu]
    card_ids = [c["id"] for c in public["candidate_models"]]
    work_pos = card_ids.index(public["working_model"]["id"])
    inf = informative_positions(public)
    rows_out = [o["output"] for o in obs]
    card_out = [v for c in cards for v in c["table"].values()]
    fit = _fits(cards, obs)
    S = {
        "dup_first_pos": p1, "dup_second_pos": p2, "dup_gap": p2 - p1,
        "obs_id_first_rank": oid[0], "obs_id_last_rank": oid[-1], "obs_id_sorted": _is_sorted(oid),
        "obs_id_mean_rank": sum(oid) / len(oid),
        "query_id_first_rank": qid[0], "query_id_sorted": _is_sorted(qid),
        "card_working_position": work_pos, "card_ids_sorted": _is_sorted(card_ids),
        "working_card_code_rank": sorted(card_ids).index(public["working_model"]["id"]),
        "json_length": len(json.dumps(public, sort_keys=True, ensure_ascii=False)),
        "key_order": "|".join(public.keys()) + "#" + "|".join(obs[0].keys()) + "#" + "|".join(obs[0]["input"].keys()),
        "menu_first_informative_pos": inf[0] if inf else -1,
        "menu_informative_count": len(inf),
    }
    D = {
        "rows_distinct_outputs": len(set(rows_out)),
        "rows_top_output_frac": Counter(rows_out).most_common(1)[0][1] / len(rows_out),
        "rows_output_entropy": _entropy(rows_out),
        "cards_output_entropy": _entropy(card_out),
        "menu_glyph_phase_pairs": len({(q["input"]["glyph"], q["input"]["phase"]) for q in menu}),
        "top_output_label": Counter(rows_out).most_common(1)[0][0],
    }
    present = {f: set() for f in FIELDS}
    for src in [o["input"] for o in obs] + [q["input"] for q in menu]:
        for f in FIELDS:
            present[f].add(src[f])
    for field, pool in LABEL_POOLS.items():
        for label in pool:
            if field == "output":
                D[f"has_{label}"] = label in set(rows_out) | set(card_out)
            else:
                D[f"has_{label}"] = label in present[field]
    E = {
        "has_conflict": _has_conflict(obs), "n_fit_cards": len(fit),
        "working_fits": any(c["id"] == public["working_model"]["id"] for c in fit),
        "informative_query": bool(inf), "phase_effect_in_rows": _phase_effect(obs),
        "pair_effect_in_rows": _pair_effect(obs),
        "rows_distinct_glyphs": len({o["input"]["glyph"] for o in obs}),
        "rows_distinct_partners": len({o["input"]["partner"] for o in obs}),
        "rows_distinct_phases": len({o["input"]["phase"] for o in obs}),
        "rows_distinct_settings": len({o["input"]["setting"] for o in obs}),
    }
    return {"S": S, "D": D, "E": E}


HIDDEN_KEYS = {"category", "family", "hidden", "seed", "index", "world_id", "cards", "working_model_id"}


def public_has_no_hidden_fields(public: dict) -> bool:
    """Top-level and nested key check; values are data and are not inspected."""
    def keys(x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield k
                yield from keys(v)
        elif isinstance(x, list):
            for v in x:
                yield from keys(v)
    return not (HIDDEN_KEYS & set(keys(public)))

"""TRONCO-01 task v3: deterministic world generator (see docs/V3_ESPECIFICACAO.md).

World = hidden hypothesis h, three declared cards, working card W, initial rows, held-out
intervention inputs T (not queryable), and a phase-2 evidence block. Verdicts are defined
only from the admissible set A(H); the category is never an input to the reference.

Seeds are drawn by the caller; `guard_seed` refuses reserved seeds (shared with M17 audit).
"""
from __future__ import annotations

import random
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "hypothesis_sets"))
import hypothesis_sets as hs  # noqa: E402

D = hs.TRONCO_V27
INPUTS = D.inputs
N = len(INPUTS)
SPACE = sorted(hs.enumerate_hypotheses(D, 2))
SUPPORT = {h: hs.essential_support(D, h) for h in SPACE}
CARD_POOL = [h for h in SPACE if 1 <= len(SUPPORT[h]) <= 2]

DIFFICULTIES = ("facil", "medio")          # "dificil" (latent confounder) is NOT implemented yet
FAMILIES = ("single", "pair", "mixed")
VERDICTS = ("rejected", "supported", "undetermined")
KINDS = ("stable_uninformative", "stable_informative", "change")
KINDS_V2 = KINDS + ("change_indirect",)   # change_indirect: no block input repeats an earlier input
BUDGET = 2
N_HELD_OUT = 4
RESERVED = frozenset({64001, 64003, 64007, 75011, 75013, 75017})
DRAW_STRIDE = 7919


class ReservedSeedError(RuntimeError):
    pass


def guard_seed(seed: int) -> None:
    for k in range(0, 60):
        if seed + k * DRAW_STRIDE in RESERVED or seed - k * DRAW_STRIDE in RESERVED:
            raise ReservedSeedError(f"seed {seed} reaches a reserved seed")


def verdict(A, w, T) -> str:
    """Reference verdict from A(H) alone. `w` is the working hypothesis, T indices of held-out inputs."""
    if not A:
        return "inconsistent"
    if w not in A:
        return "rejected"
    return "supported" if all(h[i] == w[i] for h in A for i in T for _ in (0,)) else "undetermined"


def admissible_idx(rows) -> frozenset:
    """rows: iterable of (input_index, output)."""
    rows = list(rows)
    return frozenset(h for h in SPACE if all(h[i] == y for i, y in rows))


def determination(h, obs, T, w, menu, budget):
    """Oracle: smallest query set (from menu, size <= budget) whose true answers give a determined verdict."""
    base = [(i, h[i]) for i in obs]
    for size in range(0, budget + 1):
        for q in combinations(menu, size):
            v = verdict(admissible_idx(base + [(i, h[i]) for i in q]), w, T)
            if v != "undetermined":
                return v, size, q
    return "undetermined", None, ()


def revision_reference(world: dict, queried: list[int]) -> dict:
    """Reference for the revision phase, computed from the history the agent actually has."""
    hid = world["hidden"]
    h, h2, w, T = hid["h"], hid["h2"], hid["w"], hid["T"]
    pre = [(i, h[i]) for i in list(hid["obs"]) + list(queried)]
    post = pre + [(i, h2[i]) for i in hid["block"]]
    pv, qv = verdict(admissible_idx(pre), w, T), verdict(admissible_idx(post), w, T)
    return {"pre_verdict": pv, "post_verdict": qv, "should_revise": pv != qv}


def card_public(h, cid):
    feats = [f for f in D.features if f in SUPPORT[h]]
    idx = [D.features.index(f) for f in feats]
    table = {}
    for x, y in zip(INPUTS, h):
        table["|".join(x[i] for i in idx)] = y
    stmt = "Output depends on " + " and ".join(feats) + "."
    return {"id": cid, "statement": stmt, "table": table}


def _rows(h, idxs, rng, prefix):
    ids = rng.sample(range(100, 999), len(idxs))
    return [{"id": f"{prefix}{k}", "input": dict(zip(D.features, INPUTS[i])), "output": h[i]}
            for i, k in zip(idxs, ids)]


def make_world(seed: int, difficulty: str, family: str, index: int, target: str, kind: str,
               budget: int = BUDGET, max_tries: int = 3000, k0: int | None = None) -> dict:
    guard_seed(seed)
    if difficulty not in DIFFICULTIES or family not in FAMILIES:
        raise ValueError("unsupported difficulty or family")
    if kind in ("change", "change_indirect") and difficulty == "facil":
        raise ValueError("change needs difficulty medio")
    if kind not in KINDS_V2:
        raise ValueError("unknown kind")
    rng = random.Random(f"v3|{seed}|{difficulty}|{family}|{index}|{target}|{kind}|{budget}|{k0}")
    pool = {"single": [h for h in CARD_POOL if len(SUPPORT[h]) == 1],
            "pair": [h for h in CARD_POOL if len(SUPPORT[h]) == 2], "mixed": CARD_POOL}[family]
    for attempt in range(max_tries):
        h = rng.choice(pool)
        others = rng.sample([c for c in CARD_POOL if c != h], 3)
        cards = rng.sample([h] + others[:2], 3) if rng.random() < 0.6 else others
        k0_ = k0 if k0 is not None else rng.randint(2, 4)
        order = list(range(N))
        rng.shuffle(order)
        obs = order[:k0_]
        T = order[k0_:k0_ + N_HELD_OUT]
        fitting = [c for c in cards if all(c[i] == h[i] for i in obs)]
        if not fitting:
            continue
        w = rng.choice(fitting)           # the working card always fits the initial rows (decoy possible)
        menu = [i for i in range(N) if i not in obs and i not in T]
        v0 = verdict(admissible_idx([(i, h[i]) for i in obs]), w, T)
        if v0 != "undetermined":
            continue
        tv, need, q = determination(h, obs, T, w, menu, budget)
        if tv != target:
            continue
        h2, block = h, []
        if kind == "change":
            xs = obs[0]
            cand = [c for c in SPACE if c[xs] != h[xs]]
            h2 = rng.choice(cand)
            extra = rng.sample([i for i in range(N) if i not in T and i != xs], 2)
            block = [xs] + extra
        elif kind == "change_indirect":
            free = [i for i in range(N) if i not in T and i not in obs and i not in q]
            if len(free) < 3:
                continue
            block = rng.sample(free, 3)
            h2 = rng.choice([c for c in SPACE if c != h])
            for hist in (list(obs), list(obs) + list(q)):
                rows_ = [(i, h[i]) for i in hist] + [(i, h2[i]) for i in block]
                if admissible_idx(rows_):
                    block = []
                    break
            if not block:
                continue
        else:
            if kind == "stable_informative":
                final = admissible_idx([(i, h[i]) for i in obs])
                free = [i for i in range(N) if i not in T and i not in obs]
                informative = [i for i in free if len({c[i] for c in final}) > 1]
                if not informative:
                    continue
                block = rng.sample(informative, min(2, len(informative)))
            else:
                final = admissible_idx([(i, h[i]) for i in list(obs) + list(q)])
                free = [i for i in range(N) if i not in T and i not in obs and i not in q]
                quiet = [i for i in free if len({c[i] for c in final}) == 1]
                if len(quiet) < 2:
                    continue
                block = rng.sample(quiet, 2)
        pre = [(i, h[i]) for i in list(obs) + ([] if kind == "stable_informative" else list(q))]
        # the revision reference is recomputed on the agent's own history at scoring time
        post_v = verdict(admissible_idx(pre + [(i, h2[i]) for i in block]), w, T)
        pre_v = verdict(admissible_idx(pre), w, T)
        should_revise = post_v != pre_v
        if kind == "stable_uninformative" and should_revise:
            continue
        if kind == "stable_informative" and not should_revise:
            continue
        if kind in ("change", "change_indirect") and post_v != "inconsistent":
            continue
        order_cards = list(cards)
        codes = rng.sample(["Ka", "Lo", "Mi", "Ne", "Os", "Pa", "Qu", "Ru"], 3)
        public = {
            "observations": _rows(h, obs, rng, "r"),
            "candidate_models": [card_public(c, cid) for c, cid in zip(order_cards, codes)],
            "working_model_id": codes[order_cards.index(w)],
            "held_out_inputs": [dict(zip(D.features, INPUTS[i])) for i in T],
            "query_menu": [{"id": f"q{n}", "input": dict(zip(D.features, INPUTS[i]))}
                           for n, i in enumerate(menu, 1)],
            "remaining_query_budget": budget,
        }
        return {"world_id": f"v3-{seed}-{difficulty}-{family}-{index}",
                "public": public,
                "hidden": {"h": h, "h2": h2, "w": w, "obs": obs, "T": T, "menu": menu, "block": block,
                           "cards": cards},
                "reference": {"initial_verdict": v0, "target_verdict": tv, "queries_needed": need,
                              "oracle_queries": list(q), "kind": kind, "should_revise": should_revise,
                              "post_verdict": post_v, "pre_verdict": pre_v},
                "meta": {"seed": seed, "difficulty": difficulty, "family": family, "attempts": attempt + 1}}
    raise RuntimeError("no world satisfied the constraints; the cell may be infeasible")

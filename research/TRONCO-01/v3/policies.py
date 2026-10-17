"""Reference policies for task v3 (see docs/V3_PREVISOES_EXANTE.md). Only `oracle` reads hidden fields."""
from __future__ import annotations

import random
from functools import lru_cache

import generator_v3 as g
import scoring


def view(world: dict) -> dict:
    """What a policy may see: public state decoded to indices and hypotheses."""
    p = world["public"]
    rows = tuple((g.INPUTS.index(g.D.as_tuple(o["input"])), o["output"]) for o in p["observations"])
    cards = {c["id"]: g.hs.card_hypothesis(g.D, c) for c in p["candidate_models"]}
    return {"rows": rows, "cards": list(cards.values()), "w": cards[p["working_model_id"]],
            "T": tuple(g.INPUTS.index(g.D.as_tuple(x)) for x in p["held_out_inputs"]),
            "menu": tuple(g.INPUTS.index(g.D.as_tuple(q["input"])) for q in p["query_menu"]),
            "budget": p["remaining_query_budget"]}


@lru_cache(maxsize=None)
def _value(A: frozenset, w, T: tuple, menu: tuple, b: int):
    """Minimal expected P(undetermined) with b adaptive queries; prior uniform on A."""
    v0 = 1.0 if g.verdict(A, w, T) == "undetermined" else 0.0
    if b == 0 or v0 == 0.0:
        return v0, None
    best, arg = v0, None
    for q in menu:
        groups = {}
        for h in A:
            groups.setdefault(h[q], []).append(h)
        if len(groups) < 2:
            continue
        val = sum(len(m) / len(A) * _value(frozenset(m), w, T, menu, b - 1)[0] for m in groups.values())
        if val < best - 1e-12:
            best, arg = val, q
    return best, arg


class Policy:
    name = "base"
    revises = True

    def answer(self, v, rows, left):
        """Exact answer from A(H) of the policy's own history (the same for every reference policy)."""
        A = g.admissible_idx(rows)
        preds = {}
        for t in v["T"]:
            vals = sorted({h[t] for h in A}, key=lambda y: (-sum(h[t] == y for h in A), y))
            preds[t] = vals[0] if vals else g.D.outputs[0]
        return {"stop": "commit", "verdict": g.verdict(A, v["w"], v["T"]),
                "admissible_cards": [c for c in v["cards"] if c in A], "predictions": preds}

    def choose(self, v, rows, left, rng, hidden=None):
        return None


class SemConsultas(Policy):
    name = "sem_consultas"


class Aleatoria(Policy):
    name = "aleatoria"

    def choose(self, v, rows, left, rng, hidden=None):
        used = {i for i, _ in rows}
        free = [q for q in v["menu"] if q not in used]
        return rng.choice(free) if free else None


class Simples(Policy):
    name = "simples"

    def choose(self, v, rows, left, rng, hidden=None):
        used = {i for i, _ in rows}
        free = [q for q in v["menu"] if q not in used]
        if not free:
            return None
        others = [c for c in v["cards"] if c != v["w"]]
        score = {q: sum(c[q] != v["w"][q] for c in others) for q in free}
        return max(free, key=lambda q: (score[q], -free.index(q)))


class BayesIG(Policy):
    name = "bayes_ig"

    def choose(self, v, rows, left, rng, hidden=None):
        A = g.admissible_idx(rows)
        used = {i for i, _ in rows}
        menu = tuple(q for q in v["menu"] if q not in used)
        return _value(A, v["w"], v["T"], menu, left)[1]


class GreedyA(Policy):
    """ADDED AFTER P5 WAS REFUTED (post hoc, flagged): one-step greedy, minimise expected |A| after the query."""
    name = "greedy_a"

    def choose(self, v, rows, left, rng, hidden=None):
        A = g.admissible_idx(rows)
        used = {i for i, _ in rows}
        best, arg = None, None
        for q in v["menu"]:
            if q in used:
                continue
            c = [sum(h[q] == y for h in A) for y in g.D.outputs]
            exp = sum(n * n for n in c) / len(A)
            if best is None or exp < best - 1e-12:
                best, arg = exp, q
        return arg


class Rival(Policy):
    """Cheap heuristic fixed in docs/V3_PREVISOES_EXANTE_2.md: query where W and a fitting rival card differ."""
    name = "rival"

    def choose(self, v, rows, left, rng, hidden=None):
        used = {i for i, _ in rows}
        free = [q for q in v["menu"] if q not in used]
        if not free:
            return None
        rivals = [c for c in v["cards"] if c != v["w"] and all(c[i] == y for i, y in rows)]
        for r in rivals:
            for q in free:
                if r[q] != v["w"][q]:
                    return q
        seen = [g.INPUTS[i] for i in used]
        dist = lambda q: min(sum(a != b for a, b in zip(g.INPUTS[q], s)) for s in seen)  # noqa: E731
        return max(free, key=lambda q: (dist(q), -free.index(q)))


class PrimeiroDoMenu(Policy):
    name = "primeiro_do_menu"

    def choose(self, v, rows, left, rng, hidden=None):
        used = {i for i, _ in rows}
        free = [q for q in v["menu"] if q not in used]
        return free[0] if free else None


class CegaPegajosa(Policy):
    name = "cega_pegajosa"
    revises = False


class IgnoraEvidencia(BayesIG):
    name = "ignora_evidencia"
    revises = False

    def answer(self, v, rows, left):
        a = super().answer(v, rows, left)
        a["verdict"] = "undetermined"
        return a


class Pegajosa(BayesIG):
    name = "pegajosa"
    revises = False


class Oraculo(Policy):
    name = "oraculo"

    def choose(self, v, rows, left, rng, hidden=None):
        _, _, q = g.determination(hidden["h"], hidden["obs"], list(v["T"]), hidden["w"],
                                  [m for m in v["menu"]], v["budget"])
        asked = {i for i, _ in rows} - set(hidden["obs"])
        todo = [x for x in q if x not in asked]
        return todo[0] if todo else None


POLICIES = [SemConsultas, Aleatoria, Simples, BayesIG, Oraculo, Pegajosa, GreedyA]
POLICIES_V2 = POLICIES + [Rival, PrimeiroDoMenu, CegaPegajosa, IgnoraEvidencia]


def run_episode(policy: Policy, world: dict, seed: int) -> dict:
    rng = random.Random(f"{policy.name}|{world['world_id']}|{seed}")
    v = view(world)
    hid = world["hidden"]
    rows = list(v["rows"])
    queried, invalid = [], 0
    for left in range(v["budget"], 0, -1):
        q = policy.choose(v, tuple(rows), left, rng, hid)
        if q is None:
            break
        if q not in v["menu"] or q in {i for i, _ in rows}:
            invalid += 1
            break
        rows.append((q, hid["h"][q]))
        queried.append(q)
    ans = policy.answer(v, tuple(rows), v["budget"] - len(queried))
    committed = ans["verdict"]
    detail = scoring.score(world, queried, ans, v["budget"] - len(queried))
    post_rows = rows + [(i, hid["h2"][i]) for i in hid["block"]]
    final = g.verdict(g.admissible_idx(post_rows), v["w"], v["T"]) if policy.revises else committed
    ref = g.revision_reference(world, queried)
    revised = final != committed
    return {**{k: x for k, x in detail.items() if k != "reference_verdict" and x is not None},
            "reach": committed == world["reference"]["target_verdict"], "queries": len(queried),
            "invalid": invalid, "should_revise": ref["should_revise"],
            "revision_type_I": ref["should_revise"] and not revised,
            "revision_type_II": revised and not ref["should_revise"]}

"""Fase 2: políticas com defeitos plantados, jogadas pelo ambiente real. O rótulo esperado vem da construção de cada
política (regras escritas aqui, sem usar a precedência da grelha), e cada precondição usada é verificada e contada."""
from __future__ import annotations

import collections
import random
import sys
from itertools import combinations
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "pilot"), str(V3 / "instrument")]
import env_v3 as E  # noqa: E402
import generator_v3 as g  # noqa: E402
import policies as P  # noqa: E402

VERDICTS = ("rejected", "supported", "undetermined")


def own(world, queried):
    hid = world["hidden"]
    rows = [(i, hid["h"][i]) for i in list(hid["obs"]) + list(queried)]
    return g.verdict(g.admissible_idx(rows), hid["w"], hid["T"])


def oracle_queries(world):
    """Target determined: the oracle's minimal true-answer queries. Target undetermined: no subset within the budget
    determines it (definition of the target), so spending the whole budget on any queries leaves it undetermined and
    leaves no decisive query (budget 0)."""
    ref, hid = world["reference"], world["hidden"]
    if ref["target_verdict"] != "undetermined":
        return list(ref["oracle_queries"])
    return list(hid["menu"][: world["public"]["remaining_query_budget"]])


def bayes_queries(world):
    v = P.view(world)
    rows, out = list(v["rows"]), []
    pol, rng = P.BayesIG(), random.Random(0)
    for left in range(v["budget"], 0, -1):
        q = pol.choose(v, tuple(rows), left, rng, world["hidden"])
        if q is None:
            break
        out.append(q)
        rows.append((q, world["hidden"]["h"][q]))
    return out


def least_informative_pair(world):
    """Spend the whole budget on the pair whose true answers leave the own verdict furthest from the target."""
    hid, budget = world["hidden"], world["public"]["remaining_query_budget"]
    best = None
    for Q in combinations(hid["menu"], budget):
        bad = own(world, Q) != world["reference"]["target_verdict"]
        if best is None or (bad and not best[0]):
            best = (bad, list(Q))
    return best[1]


def play(world, queries, commit_verdict, revise_rule, invalid=False, invalid_revision=False):
    ep = E.Episode(world)
    qid = {i: k for k, i in ep._menu_ids.items()}
    if invalid:
        for _ in range(3):
            ep.step({"action": "query", "query_id": "nao-existe"})
        return ep
    for q in queries:
        assert ep.step({"action": "query", "query_id": qid[q]})["ok"]
    assert ep.step({"action": "commit", "verdict": commit_verdict, "admissible_cards": [], "predictions": {}})["ok"]
    if invalid_revision:                                 # committed, then three invalid revision actions
        for _ in range(3):
            ep.step({"action": "query", "query_id": "q1"})
        return ep
    post = g.revision_reference(world, ep.queried)["post_verdict"]
    final = revise_rule(commit_verdict, post)
    if final == commit_verdict:
        assert ep.step({"action": "keep"})["ok"]
    else:
        assert ep.step({"action": "revise", "verdict": final, "admissible_cards": []})["ok"]
    return ep


def correct_revision(committed, post):
    return post


def build(world):
    """Returns {policy: (episode, expected_category, expected_revision_correct)} plus precondition counters."""
    a = world["reference"]["target_verdict"]
    p0 = own(world, [])
    assert p0 == "undetermined"                         # generator invariant: every world starts undetermined
    bq = oracle_queries(world)
    pb = own(world, bq)
    assert pb == a                                      # the oracle queries reach the target (checked, not assumed)
    out = {}
    out["fundamentado"] = (play(world, bq, pb, correct_revision), "fundamentado", True)
    wrong = next(v for v in VERDICTS if v not in (pb, a))
    out["inferencia"] = (play(world, bq, wrong, correct_revision), "inferencia", True)
    out["sorte"] = (play(world, [], a, correct_revision), "sorte" if a != p0 else "prematuro_certo", True)
    out["prematura"] = (play(world, [], p0, correct_revision), "prematura" if a != p0 else "prematuro_certo", True)
    lq = least_informative_pair(world)
    pl = own(world, lq)
    out["pesquisa"] = (play(world, lq, pl, correct_revision), "pesquisa" if pl != a else "fundamentado", True)
    out["incompleto"] = (play(world, [], None, None, invalid=True), "incompleto", False)
    nr = "supported" if pb == "rejected" else pb
    out["nunca_rejected"] = (play(world, bq, nr, correct_revision), "inferencia" if pb == "rejected" else "fundamentado", True)
    out["sem_revisao"] = (play(world, bq, pb, None, invalid_revision=True), "incompleto", False)
    ep_keep = play(world, bq, pb, lambda c, post: c)
    post = g.revision_reference(world, bq)["post_verdict"]
    out["nunca_rever"] = (ep_keep, "fundamentado", post == pb)
    out["sempre_inconsistent"] = (play(world, bq, pb, lambda c, post: "inconsistent"), "fundamentado", post == "inconsistent")
    return out


def run(worlds):
    import grid
    conf = collections.Counter()
    rev = collections.Counter()
    rows_by_policy = collections.defaultdict(list)
    for w in worlds:
        for name, (ep, exp_cat, exp_rev) in build(w).items():
            r = grid.classify(w, ep)
            conf[(name, exp_cat, r["category"])] += 1
            rev[(name, exp_rev == r["revision_final_correct"])] += 1
            rows_by_policy[name].append(r)
    return conf, rev, rows_by_policy

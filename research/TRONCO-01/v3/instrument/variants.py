"""Variantes do gerador para a tarefa de consultas (docs/V3_CONSULTAS.md §5). O gerador por omissão não muda.

Todas: mundos de desenvolvimento (sementes 91xxx), mesma grelha de células que audit_v3.dev_set, conjunto equilibrado,
ordem do menu baralhada por mundo (semente derivada do uid).
"""
from __future__ import annotations

import random
import sys
from itertools import product
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument")]
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import query_leverage as QL  # noqa: E402


def shuffle_menu(w):
    rng = random.Random("menu|" + w["uid"])
    hid, pub = w["hidden"], w["public"]
    order = list(range(len(hid["menu"])))
    rng.shuffle(order)
    hid["menu"] = [hid["menu"][k] for k in order]
    pub["query_menu"] = [{"id": f"q{n}", "input": dict(zip(g.D.features, g.INPUTS[i]))} for n, i in enumerate(hid["menu"], 1)]
    return w


def rederive_reference(w):
    """After changing the menu, the target (which depends on the menu) is recomputed by the same oracle."""
    hid = w["hidden"]
    tv, need, q = g.determination(hid["h"], hid["obs"], hid["T"], hid["w"], hid["menu"], w["public"]["remaining_query_budget"])
    w["reference"].update({"target_verdict": tv, "queries_needed": need, "oracle_queries": list(q)})
    return w


def cells(budget, k0_of, infeasible, seeds=None):
    worlds = []
    for seed in (seeds or a.DEV_SEEDS):
        for diff, fam, target in product(g.DIFFICULTIES, g.FAMILIES, g.VERDICTS):
            kinds = g.KINDS_V2 if diff == "medio" else g.KINDS[:2]
            for kind in kinds:
                if (target, kind) in a.INFEASIBLE:
                    continue
                for i in range(1, a.PER_CELL + 1):
                    k0 = k0_of(i)
                    try:
                        worlds.append(g.make_world(seed, diff, fam, i, target, kind, budget=budget, k0=k0, max_tries=1500))
                    except RuntimeError:
                        infeasible.append([seed, diff, fam, target, kind, k0])
    return worlds


def build(name, seeds=None):
    """seeds=None: development seeds (91xxx). Other seeds only for a pre-registered partition (§22)."""
    infeasible = []
    if name == "V1":
        ws = cells(2, lambda i: 5 + (i - 1) % 3, infeasible)
    elif name == "V2":
        ws = cells(1, lambda i: 2 + (i - 1) % 3, infeasible)
    elif name == "V3":
        ws = cells(2, lambda i: 2 + (i - 1) % 3, infeasible)
        out = []
        for w in ws:
            v = QL.values(w)
            ranked = sorted(w["hidden"]["menu"], key=lambda q: (-v[q], q))
            top = [ranked[0]] + ([ranked[1]] if v[ranked[1]] >= v[ranked[0]] - 0.05 else [])
            low = sorted((q for q in ranked if q not in top), key=lambda q: (v[q], q))[: 6 - len(top)]
            w["hidden"]["menu"] = sorted(top + low)
            out.append(rederive_reference(w))
        ws = out
    elif name in ("V4", "V5"):                  # ronda 2: full 16-input menu; V4 budget 1, V5 budget 2 (adaptive)
        budget = 1 if name == "V4" else 2
        ws = cells(budget, lambda i: 2 + (i - 1) % 3, infeasible, seeds)
        for w in ws:
            w["hidden"]["menu"] = list(range(g.N))
            rederive_reference(w)
    elif name == "V6":                          # ronda 2: budget 1, 6 menu queries drawn at random (no values used)
        ws = cells(1, lambda i: 2 + (i - 1) % 3, infeasible)
        for w in ws:
            rng = random.Random("v6|" + w["uid"])
            w["hidden"]["menu"] = sorted(rng.sample(w["hidden"]["menu"], min(6, len(w["hidden"]["menu"]))))
            rederive_reference(w)
    else:
        raise ValueError(name)
    ws = [shuffle_menu(w) for w in ws]
    return a.balance_trim(ws), infeasible

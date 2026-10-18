"""Piloto humano V4 (docs/V3_CONSULTAS.md §11): seleção determinística dos 20 episódios e exportação para a página."""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument"), str(V3 / "pilot")]
import generator_v3 as g  # noqa: E402
import pilot_harness as H  # noqa: E402
import query_leverage as QL  # noqa: E402
import variants as VA  # noqa: E402

QUOTA = {"supported": 7, "rejected": 7, "undetermined": 6}


def select():
    ws, _ = VA.build("V4")
    rng = random.Random("tronco01-v4-piloto-humano")
    rng.shuffle(ws)
    rows = []
    for w in ws:
        v = QL.values(w)
        rev = g.revision_reference(w, [])
        rows.append((w, max(v.values()) >= 0.80, v))
    chosen, count, hi = [], {k: 0 for k in QUOTA}, 0
    # pass 1: fill target quotas, alternating quality strata so that 10/10 is reached
    for want_hi in [True, False] * 20:
        for w, q_hi, v in rows:
            t = w["reference"]["target_verdict"]
            if w in [c[0] for c in chosen] or count[t] >= QUOTA[t] or q_hi != want_hi:
                continue
            if (q_hi and hi >= 10) or (not q_hi and len(chosen) - hi >= 10):
                continue
            chosen.append((w, q_hi, v)); count[t] += 1; hi += q_hi
            break
        if len(chosen) == 20:
            break
    return chosen


def split(chosen):
    """Two sets of 10, as balanced as possible by target and by quality stratum (exhaustive over the 184 756 splits;
    the first minimum in lexicographic order is taken, so the split is deterministic)."""
    from itertools import combinations
    n = len(chosen)
    tg = [w["reference"]["target_verdict"] for w, _, _ in chosen]
    qh = [q for _, q, _ in chosen]
    best, best_cost = None, None
    for X in combinations(range(n), n // 2):
        xs = set(X)
        cost = abs(sum(qh[k] for k in xs) - sum(qh[k] for k in range(n) if k not in xs))
        for t in set(tg):
            cost += abs(sum(tg[k] == t for k in xs) - sum(tg[k] == t for k in range(n) if k not in xs))
        if best_cost is None or cost < best_cost:
            best, best_cost = X, cost
    X = sorted(best)
    return X, [k for k in range(n) if k not in best]


def helper_state(w, rows):
    """Condition B help, computed by the reference code from what the participant has seen."""
    hid = w["hidden"]
    A = g.admissible_idx(rows)
    cards = {c["id"]: g.hs.card_hypothesis(g.D, c) for c in w["public"]["candidate_models"]}
    pats = {}
    for h in A:
        k = "".join(h[t] for t in hid["T"])
        pats[k] = pats.get(k, 0) + 1
    return {"n_admissible": len(A), "w_admissible": hid["w"] in A,
            "cards_admissible": [cid for cid, hc in cards.items() if hc in A],
            "patterns": dict(sorted(pats.items())), "w_pattern": "".join(hid["w"][t] for t in hid["T"])}


def helpers(w):
    hid = w["hidden"]
    base = [(i, hid["h"][i]) for i in hid["obs"]]
    out = {"inicio": helper_state(w, base), "consulta": {}, "evidencia": {}}
    for q in w["public"]["query_menu"]:
        i = g.INPUTS.index(g.D.as_tuple(q["input"]))
        rows = base + [(i, hid["h"][i])]
        out["consulta"][q["id"]] = helper_state(w, rows)
        out["evidencia"][q["id"]] = helper_state(w, rows + [(j, hid["h2"][j]) for j in hid["block"]])
    return out


def interleave(data, X, Y):
    """Fixed order X, Y, X, Y, ... so that condition alternates within every participant (A,B,A,B or B,A,B,A)."""
    xs = [d for d in data if (d["n"] - 1) in X]
    ys = [d for d in data if (d["n"] - 1) in Y]
    for d in xs:
        d["set"] = "X"
    for d in ys:
        d["set"] = "Y"
    out = [d for pair in zip(xs, ys) for d in pair]
    for k, d in enumerate(out, 1):
        d["n"] = k
    return out


def reference_answers(w):
    """Per query: verdict after the query (commit reference) and after the new evidence (revision reference)."""
    hid = w["hidden"]
    base = [(i, hid["h"][i]) for i in hid["obs"]]
    out = {}
    for q in w["public"]["query_menu"]:
        i = g.INPUTS.index(g.D.as_tuple(q["input"]))
        rows = base + [(i, hid["h"][i])]
        post = rows + [(j, hid["h2"][j]) for j in hid["block"]]
        out[q["id"]] = {"commit": g.verdict(g.admissible_idx(rows), hid["w"], hid["T"]),
                        "revision": g.verdict(g.admissible_idx(post), hid["w"], hid["T"])}
    return out


def practice(chosen, k=2):
    """Two practice episodes from the same V4 development build, never among the 20; not analysed."""
    ws, _ = VA.build("V4")
    used = {w["uid"] for w, _, _ in chosen}
    rng = random.Random("tronco01-v4-piloto-humano-treino")
    pool = [w for w in ws if w["uid"] not in used]
    rng.shuffle(pool)
    picked, seen = [], set()
    for w in pool:                       # one 'supported' and one 'rejected' target, for clear feedback
        t = w["reference"]["target_verdict"]
        if t in ("supported", "rejected") and t not in seen:
            picked.append((w, max(QL.values(w).values()) >= 0.80, QL.values(w))); seen.add(t)
        if len(picked) == k:
            break
    out = export(picked)
    for d, (w, _, _) in zip(out, picked):
        d["set"] = "T"; d["n"] = "T" + str(d["n"]); d["feedback"] = reference_answers(w)
    return out


def page_episode(d):
    st = d["user_text"].split("\nCONSULTAS DISPONÍVEIS")[0]
    ev = [", ".join(f"{k}={v}" for k, v in e["input"].items()) + " -> " + e["output"] for e in d["new_evidence"]]
    out = {"n": d["n"], "uid": d["uid"], "set": d["set"], "state": st,
           "menu": [{"id": q["id"], "input": q["input"], "answer": q["answer"]} for q in d["menu"]],
           "evidence": ev, "cards": d["cards"], "help": d["help"]}
    if "feedback" in d:
        out["feedback"] = d["feedback"]
    return out


def build_page(episodes, training, template: Path, rules: Path) -> str:
    data = {"rules": rules.read_text(encoding="utf-8"), "training": [page_episode(d) for d in training],
            "episodes": [page_episode(d) for d in episodes]}
    return template.read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, ensure_ascii=False))


def export(chosen):
    out = []
    for n, (w, q_hi, v) in enumerate(chosen, 1):
        hid = w["hidden"]
        st = {"observations": list(w["public"]["observations"]), "candidate_models": w["public"]["candidate_models"],
              "working_model_id": w["public"]["working_model_id"], "held_out_inputs": w["public"]["held_out_inputs"],
              "phase": "explore", "remaining_query_budget": 1, "query_menu": w["public"]["query_menu"]}
        out.append({"n": n, "uid": w["uid"], "target": w["reference"]["target_verdict"], "quality_hi": q_hi,
                    "user_text": H.render_state(st, cards_object=True),
                    "menu": [{"id": q["id"], "input": q["input"], "answer": hid["h"][g.INPUTS.index(g.D.as_tuple(q["input"]))],
                              "value2": round(v[g.INPUTS.index(g.D.as_tuple(q["input"]))], 4)} for q in w["public"]["query_menu"]],
                    "new_evidence": [{"input": dict(zip(g.D.features, g.INPUTS[i])), "output": hid["h2"][i]} for i in hid["block"]],
                    "cards": [c["id"] for c in w["public"]["candidate_models"]], "help": helpers(w)})
    return out


if __name__ == "__main__":
    ch = select()
    data = export(ch)
    X, Y = split(ch)
    data = interleave(data, X, Y)
    txt = json.dumps(data, ensure_ascii=False, indent=1)
    Path(sys.argv[1]).write_text(txt + "\n", encoding="utf-8")
    import collections
    print(len(data), dict(collections.Counter(d["target"] for d in data)), "qualidade alta", sum(d["quality_hi"] for d in data),
          "sha", hashlib.sha256(txt.encode()).hexdigest()[:16], "ordem", "".join(d["set"] for d in data))
    tr = practice(ch)
    Path(sys.argv[1]).with_name("PILOTO_HUMANO_TREINO.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if len(sys.argv) > 2:
        here = Path(__file__).resolve().parent
        Path(sys.argv[2]).write_text(build_page(data, tr, here / "piloto_humano_template.html", here / "piloto_humano_regras.txt"),
                                     encoding="utf-8")

"""Fase 3: itens de escolha forçada, só a partir de mundos de desenvolvimento (sementes 91xxx).

Cada item: {item_id, family, cluster, system, user, prefix, candidates, answer, meta}. O modelo é pontuado pela
log-probabilidade de cada candidata depois de (system, user, prefix). As respostas certas são calculadas por código.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "pilot")]
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import pilot_harness as H  # noqa: E402
import scoring as sc  # noqa: E402

VERDICT_PREFIX = '{\n  "action": "commit",\n  "verdict": "'
QUERY_PREFIX = '{\n  "action": "query",\n  "query_id": "'
VERDICTS = ("rejected", "supported", "undetermined")
PROBE_SYSTEM = H.SYSTEM_PROMPT_V31.split("Podes consultar")[0] + "Responde apenas com a resposta pedida, sem mais texto."
N_PER_FAMILY = 200
N_META_BASE = 160


# ----------------------------------------------------------------------------------------------- states
def state(world, Q, ys, budget_left=0, new_block=False):
    pub, hid = world["public"], world["hidden"]
    used = set(Q)
    obs = list(pub["observations"]) + [{"id": f"n{k}", "input": dict(zip(g.D.features, g.INPUTS[i])), "output": y}
                                       for k, (i, y) in enumerate(zip(Q, ys), 1)]
    menu_idx = {q["id"]: g.INPUTS.index(g.D.as_tuple(q["input"])) for q in pub["query_menu"]}
    st = {"observations": obs, "candidate_models": [dict(c) for c in pub["candidate_models"]],
          "working_model_id": pub["working_model_id"], "held_out_inputs": list(pub["held_out_inputs"]),
          "phase": "revision" if new_block else "explore", "remaining_query_budget": budget_left,
          "query_menu": [q for q in pub["query_menu"] if menu_idx[q["id"]] not in used]}
    if new_block:
        st["new_evidence"] = [{"id": f"b{k}", "input": dict(zip(g.D.features, g.INPUTS[i])), "output": hid["h2"][i]}
                              for k, i in enumerate(hid["block"], 1)]
    return st


def rows_of(world, Q, ys):
    hid = world["hidden"]
    return [(i, hid["h"][i]) for i in hid["obs"]] + list(zip(Q, ys))


def v70(world, rows):
    hid = world["hidden"]
    return g.verdict(g.admissible_idx(rows), hid["w"], hid["T"])


def reachable_full_states(world):
    """All (Q, ys) with |Q| = budget whose answers some initially admissible hypothesis could give."""
    hid, b = world["hidden"], world["public"]["remaining_query_budget"]
    for Q in combinations(hid["menu"], b):
        for ys in product(g.D.outputs, repeat=b):
            if g.admissible_idx(rows_of(world, Q, ys)):
                yield Q, ys


def cluster(world):
    return g.structure_group(world)


# ----------------------------------------------------------------------------------------------- transforms
ATTR = {"glyph": "cor", "setting": "forma", "partner": "tamanho", "phase": "textura"}
VAL = {"g": "c", "s": "f", "p": "m", "t": "x"}


def _rename_value(v):
    return VAL[v[0]] + v[1:]


def rename_attributes(st, system):
    def inp(d):
        return {ATTR[k]: _rename_value(v) for k, v in d.items()}
    st = json.loads(json.dumps(st))
    for key in ("observations", "new_evidence", "query_menu"):
        for o in st.get(key, []):
            o["input"] = inp(o["input"])
    st["held_out_inputs"] = [inp(x) for x in st["held_out_inputs"]]
    for c in st["candidate_models"]:
        c["table"] = {"|".join(_rename_value(t) for t in k.split("|")): v for k, v in c["table"].items()}
        for old, new in ATTR.items():
            c["statement"] = c["statement"].replace(old, new)
    sys_ = system.replace("(glyph, setting, partner, phase)", "(cor, forma, tamanho, textura)")
    return st, sys_


NEW_CODES = ["Zo", "Bi", "Fa", "Tu", "We", "Ha", "Ji", "Yo", "Xe"]


def rename_cards(st):
    st = json.loads(json.dumps(st))
    used = {c["id"] for c in st["candidate_models"]}
    pool = [c for c in NEW_CODES if c not in used]
    m = {c["id"]: pool[k] for k, c in enumerate(st["candidate_models"])}
    for c in st["candidate_models"]:
        c["id"] = m[c["id"]]
    st["working_model_id"] = m[st["working_model_id"]]
    return st


def permute_enum(user):
    return (user.replace("rejected|supported|undetermined|inconsistent", "undetermined|inconsistent|rejected|supported")
                .replace("rejected|supported|undetermined", "undetermined|rejected|supported"))


def reverse_menu(st):
    st = json.loads(json.dumps(st))
    inputs = [q["input"] for q in st["query_menu"]][::-1]
    st["query_menu"] = [{"id": f"q{n}", "input": x} for n, x in enumerate(inputs, 1)]
    return st


# ----------------------------------------------------------------------------------------------- item builders
def verdict_item(item_id, family, world, st, answer, system=H.SYSTEM_PROMPT_V31, user_fn=None, meta=None):
    user = H.render_state(st, cards_object=True)
    if user_fn:
        user = user_fn(user)
    return {"item_id": item_id, "family": family, "cluster": cluster(world), "world": world["uid"], "system": system,
            "user": user, "prefix": VERDICT_PREFIX, "candidates": [v + '"' for v in VERDICTS], "answer": answer + '"',
            "meta": meta or {}}


def strip_actions(user):
    return "\n".join(l for l in user.split("\n") if not l.startswith("AÇÕES"))


def probe_item(item_id, family, world, st, question, candidates, answer, meta):
    user = strip_actions(H.render_state(st, cards_object=True)) + "\nPERGUNTA: " + question
    return {"item_id": item_id, "family": family, "cluster": cluster(world), "world": world["uid"],
            "system": PROBE_SYSTEM, "user": user, "prefix": "", "candidates": candidates, "answer": answer, "meta": meta}


def fmt_input(d):
    return ", ".join(f"{k}={v}" for k, v in d.items())


def build():
    rng = random.Random("tronco01-v3-instrumento-F3")
    worlds = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    rng.shuffle(worlds)
    items = []

    # 1. minimal pairs: same Q, answers differ in exactly one query, verdicts differ
    by_type = defaultdict(list)
    for w in worlds:
        full = list(reachable_full_states(w))
        index = {(Q, ys): v70(w, rows_of(w, Q, ys)) for Q, ys in full}
        for (Q, ys), v in index.items():
            for k in range(len(Q)):
                flipped = list(ys)
                flipped[k] = "1" if ys[k] == "0" else "0"
                key2 = (Q, tuple(flipped))
                if key2 in index and index[key2] != v and (Q, ys) < key2:
                    by_type[tuple(sorted((v, index[key2])))].append((w, Q, ys, tuple(flipped), v, index[key2]))
    types = sorted(by_type)
    per_type = N_PER_FAMILY // len(types)
    pair_n = 0
    for t in types:
        pool = by_type[t]
        rng.shuffle(pool)
        seen_world = defaultdict(int)
        for (w, Q, ys, ys2, va, vb) in pool:
            if seen_world[w["uid"]] >= 2:
                continue
            seen_world[w["uid"]] += 1
            pid = f"par{pair_n:03d}"
            for side, (yy, vv) in (("A", (ys, va)), ("B", (ys2, vb))):
                items.append(verdict_item(f"{pid}{side}", "par_minimo", w, state(w, Q, yy), vv,
                                          meta={"pair": pid, "side": side, "transition": "|".join(t)}))
            pair_n += 1
            if sum(seen_world.values()) >= per_type:
                break

    # 2. metamorphoses on verdict states (balanced by verdict) and query-choice roots
    base = defaultdict(list)
    for w in worlds:
        cand = list(reachable_full_states(w))
        rng.shuffle(cand)
        for Q, ys in cand[:6]:
            base[v70(w, rows_of(w, Q, ys))].append((w, Q, ys))
    meta_n = 0
    for v in VERDICTS:
        rng.shuffle(base[v])
        used_w = set()
        for (w, Q, ys) in base[v]:
            if w["uid"] in used_w:
                continue
            used_w.add(w["uid"])
            st = state(w, Q, ys)
            mid = f"meta{meta_n:03d}"
            items.append(verdict_item(f"{mid}_orig", "meta_verdict", w, st, v, meta={"base": mid, "transform": "orig"}))
            items.append(verdict_item(f"{mid}_cards", "meta_verdict", w, rename_cards(st), v,
                                      meta={"base": mid, "transform": "cards"}))
            items.append(verdict_item(f"{mid}_enum", "meta_verdict", w, st, v, user_fn=permute_enum,
                                      meta={"base": mid, "transform": "enum"}))
            st2, sys2 = rename_attributes(st, H.SYSTEM_PROMPT_V31)
            items.append(verdict_item(f"{mid}_attr", "meta_verdict", w, st2, v, system=sys2,
                                      meta={"base": mid, "transform": "attr"}))
            meta_n += 1
            if len(used_w) >= N_META_BASE // 3 + 1:
                break
    # query-choice roots
    for n, w in enumerate(worlds[:N_META_BASE]):
        hid = w["hidden"]
        st = state(w, (), (), budget_left=w["public"]["remaining_query_budget"])
        A0 = g.admissible_idx(rows_of(w, (), ()))
        menu_ids = [q["id"] for q in st["query_menu"]]
        menu_inputs = [g.INPUTS.index(g.D.as_tuple(q["input"])) for q in st["query_menu"]]
        def p_det(A, i):
            return sum(g.verdict(frozenset(x for x in A if x[i] == h[i]), hid["w"], hid["T"]) != "undetermined"
                       for h in A) / len(A)

        def value2(i):
            tot = 0.0
            for y in {h[i] for h in A0}:
                Ay = frozenset(h for h in A0 if h[i] == y)
                if g.verdict(Ay, hid["w"], hid["T"]) != "undetermined":
                    tot += len(Ay)
                else:
                    tot += len(Ay) * max((p_det(Ay, j) for j in menu_inputs if j != i), default=0.0)
            return tot / len(A0)
        v1 = {i: p_det(A0, i) for i in menu_inputs}
        v2 = {i: value2(i) for i in menu_inputs}
        informative = [any(g.verdict(frozenset(h for h in A0 if h[i] == y), hid["w"], hid["T"]) != "undetermined"
                for y in {h[i] for h in A0}) for i in menu_inputs]
        for tr, s_ in (("orig", st), ("menu_reversed", reverse_menu(st))):
            ids = [q["id"] for q in s_["query_menu"]]
            inputs = [g.INPUTS.index(g.D.as_tuple(q["input"])) for q in s_["query_menu"]]
            info = {qid: informative[menu_inputs.index(i)] for qid, i in zip(ids, inputs)}
            user = H.render_state(s_, cards_object=True)
            items.append({"item_id": f"q{n:03d}_{tr}", "family": "query_choice", "cluster": cluster(w), "world": w["uid"],
                          "system": H.SYSTEM_PROMPT_V31, "user": user, "prefix": QUERY_PREFIX,
                          "candidates": [i + '"' for i in ids], "answer": None,
                          "meta": {"base": f"q{n:03d}", "transform": tr, "input_of": {i + '"': x for i, x in zip(ids, inputs)},
                                   "informative": {i + '"': info[i] for i in ids},
                                   "value1": {i + '"': v1[x] for i, x in zip(ids, inputs)},
                                   "value2": {i + '"': v2[x] for i, x in zip(ids, inputs)}, "position": {i + '"': k for k, i in enumerate(ids, 1)}}})

    # 3. probes
    def card_by(st, cid):
        return next(c for c in st["candidate_models"] if c["id"] == cid)

    def card_out(card, x):
        return next(v for k, v in card["table"].items() if all(t in x.values() for t in k.split("|")))

    def fits(card, obs):
        return all(card_out(card, o["input"]) == o["output"] for o in obs)

    probes = defaultdict(list)
    for w in worlds:
        cand = list(reachable_full_states(w))
        rng.shuffle(cand)
        for Q, ys in cand[:3]:
            st = state(w, Q, ys)
            cards = st["candidate_models"]
            # cell
            c = rng.choice(cards)
            x = dict(zip(g.D.features, rng.choice(g.INPUTS)))
            probes["sonda_celula"].append((w, st, f"Segundo a carta {c['id']}, qual é a saída para a entrada {fmt_input(x)}? "
                                                  "Responde 0 ou 1.", ["0", "1"], card_out(c, x)))
            # compatibility
            c = rng.choice(cards)
            probes["sonda_compat"].append((w, st, f"A carta {c['id']} reproduz todas as observações acima? Responde sim ou não.",
                                           ["sim", "não"], "sim" if fits(c, st["observations"]) else "não"))
            # separation
            if st["query_menu"]:
                c1, c2 = rng.sample(cards, 2)
                q = rng.choice(st["query_menu"])
                diff = card_out(c1, q["input"]) != card_out(c2, q["input"])
                probes["sonda_separa"].append((w, st, f"Na entrada da consulta {q['id']} ({fmt_input(q['input'])}), as cartas "
                                                      f"{c1['id']} e {c2['id']} dão saídas diferentes? Responde sim ou não.",
                                               ["sim", "não"], "sim" if diff else "não"))
            # verdict given the admissible set (stated explicitly)
            hid = w["hidden"]
            A = g.admissible_idx(rows_of(w, Q, ys))
            Wh, T = hid["w"], hid["T"]
            pats = sorted({"".join(h[t] for t in T) for h in A})
            wpat = "".join(Wh[t] for t in T)
            win = Wh in A
            ans = g.verdict(A, Wh, T)
            q_text = (f"Informação dada: W {'É' if win else 'NÃO é'} admissível. As regras admissíveis (entre as 70) dão, "
                      f"nas entradas retidas 1 a 4, estes padrões de saída: {', '.join(pats)}. W dá o padrão {wpat}. "
                      "Qual é o veredicto sobre W? Responde rejected, supported ou undetermined.")
            probes["sonda_veredicto"].append((w, st, q_text, ["rejected", "supported", "undetermined"], ans))
        # contradiction (revision state; direct conflict only)
        Q, ys = cand[0]
        st = state(w, Q, ys, new_block=True)
        seen = {g.D.as_tuple(o["input"]): o["output"] for o in st["observations"]}
        conflict = any(seen.get(g.D.as_tuple(o["input"]), o["output"]) != o["output"] for o in st["new_evidence"])
        probes["sonda_contradicao"].append((w, st, "Alguma entrada da EVIDÊNCIA NOVA aparece nas observações anteriores com "
                                                   "uma saída diferente? Responde sim ou não.", ["sim", "não"],
                                            "sim" if conflict else "não"))
    for fam, pool in probes.items():
        by_ans = defaultdict(list)
        for p in pool:
            by_ans[p[4]].append(p)
        k = N_PER_FAMILY // len(by_ans)
        chosen = []
        for ans_, lst in sorted(by_ans.items()):
            chosen += lst[:k]
        for n, (w, st, qtext, cands, ans_) in enumerate(chosen):
            items.append(probe_item(f"{fam}{n:03d}", fam, w, st, qtext, cands, ans_, {}))
    return items


def main(out: Path):
    items = build()
    txt = "\n".join(json.dumps(i, ensure_ascii=False, sort_keys=True) for i in items) + "\n"
    out.write_text(txt, encoding="utf-8")
    fams = defaultdict(int)
    for i in items:
        fams[i["family"]] += 1
    print(json.dumps({"items": len(items), "by_family": fams, "sha256": hashlib.sha256(txt.encode()).hexdigest()},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]))

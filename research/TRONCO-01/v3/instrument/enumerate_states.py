"""Fase 1: árvore completa de estados de informação nos mundos de desenvolvimento (sementes 91xxx; o piloto é subconjunto).

Um estado = estado público inicial + um conjunto Q de consultas do menu (|Q| <= orçamento) + respostas y_Q compatíveis com
alguma hipótese admissível no início (espaço de 70). Para cada estado: veredicto na leitura de 70 hipóteses, veredicto na
leitura só-cartas, consulta decisiva de 1 passo e de k passos (k = orçamento restante). Na raiz: alvo e alvos possíveis
(o alvo calculado para cada hipótese ainda admissível). Escreve também os estados em forma pública canónica para a
verificação independente em Node.js (verify_states.mjs).
"""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path[:0] = [str(V3), str(V3 / "pilot")]
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import scoring as sc  # noqa: E402


def verdict_cards(cards, rows, w, T):
    C = frozenset(c for c in cards if all(c[i] == y for i, y in rows))
    return g.verdict(C, w, T)


def decisive_k(A, w, T, free, k):
    if g.verdict(A, w, T) != "undetermined":
        return True
    if k == 0 or not A:
        return False
    for q in free:
        for y in {h[q] for h in A}:
            if decisive_k(frozenset(h for h in A if h[q] == y), w, T, [x for x in free if x != q], k - 1):
                return True
    return False


def public_node(world, rows):
    """Canonical public form: what the agent sees, with the hidden indices replaced by feature dictionaries."""
    pub = world["public"]
    wid = pub["working_model_id"]
    return {"rows": sorted([[list(g.INPUTS[i]), y] for i, y in rows]),
            "cards": sorted([c["table"] for c in pub["candidate_models"]], key=lambda t: json.dumps(t, sort_keys=True)),
            "working": next(c["table"] for c in pub["candidate_models"] if c["id"] == wid),
            "held_out": [list(g.D.as_tuple(x)) for x in pub["held_out_inputs"]]}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def main(out_dir: Path):
    worlds = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    by_public = collections.defaultdict(set)     # canonical public state -> verdicts (70) seen
    stats = collections.Counter()
    div = collections.Counter()
    roots = []
    nodes_out = []
    for w in worlds:
        hid = w["hidden"]
        W, T, menu, budget = hid["w"], hid["T"], hid["menu"], w["public"]["remaining_query_budget"]
        assert hid["w"] == g.hs.card_hypothesis(g.D, next(c for c in w["public"]["candidate_models"]
                                                         if c["id"] == w["public"]["working_model_id"]))
        base = [(i, hid["h"][i]) for i in hid["obs"]]
        A0 = g.admissible_idx(base)
        for r in range(budget + 1):
            for Q in combinations(menu, r):
                for ys in product(g.D.outputs, repeat=r):
                    rows = base + list(zip(Q, ys))
                    A = g.admissible_idx(rows)
                    if not A:                      # answers no admissible hypothesis could give: unreachable
                        continue
                    v70 = g.verdict(A, W, T)
                    vc = verdict_cards(hid["cards"], rows, W, T)
                    free = [q for q in menu if q not in Q]
                    left = budget - r
                    d1 = sc.can_still_determine(A, W, T, free) if left > 0 else False
                    dk = decisive_k(A, W, T, free, left) and v70 == "undetermined" if left > 0 else False
                    if v70 != "undetermined":
                        dk = False
                    stats["states"] += 1
                    div[(v70, vc)] += 1
                    if v70 == "undetermined" and left > 0:
                        stats["undetermined_with_budget"] += 1
                        stats["decisive_1_vs_k_disagree"] += (d1 != dk)
                    pn = public_node(w, rows)
                    key = canon(pn)
                    by_public[key].add(v70)
                    nodes_out.append({"world": w["uid"], "node": pn, "v70": v70, "vcards": vc})
        # target possibilities at the root: recompute the generator's oracle for every still-admissible hypothesis
        possible = collections.Counter(g.determination(h, hid["obs"], T, W, menu, budget)[0] for h in A0)
        roots.append({"uid": w["uid"], "target": w["reference"]["target_verdict"], "admissible_at_root": len(A0),
                      "possible_targets": dict(possible)})
    collisions = sum(1 for v in by_public.values() if len(v) > 1)
    multi_target = sum(1 for r in roots if len(r["possible_targets"]) > 1)
    report = {
        "worlds": len(worlds), "states": stats["states"], "distinct_public_states": len(by_public),
        "public_state_collisions_with_different_v70": collisions,
        "divergence_v70_vs_cards": {f"{k[0]}->{k[1]}": v for k, v in sorted(div.items())},
        "share_divergent": sum(v for k, v in div.items() if k[0] != k[1]) / stats["states"],
        "undetermined_states_with_budget": stats["undetermined_with_budget"],
        "decisive_1_vs_k_disagreements": stats["decisive_1_vs_k_disagree"],
        "roots_with_more_than_one_possible_target": multi_target,
        "roots": roots,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "F1_ENUMERACAO.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    nodes_txt = "\n".join(json.dumps(n, sort_keys=True) for n in nodes_out) + "\n"
    (out_dir / "F1_ESTADOS.jsonl").write_text(nodes_txt, encoding="utf-8")
    report_short = {k: v for k, v in report.items() if k != "roots"}
    report_short["states_sha256"] = hashlib.sha256(nodes_txt.encode()).hexdigest()
    print(json.dumps(report_short, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else V3 / "results" / "instrumento")

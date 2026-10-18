"""Alavanca da escolha de consulta (18/10). Métrica única para a linha de base e para qualquer variante do gerador:

v2(q) = P_{h~U(A0)}[ veredicto determinado depois de q e da melhor 2.ª consulta ]   (raiz do episódio, orçamento 2)
gap(mundo) = max_q v2(q) − média_q v2(q), sobre todas as consultas do menu (a "distribuição de consultas" é o menu
completo, uniforme). Reporta também dificuldade (1 − média v2), qualidade da evidência (max v2) e onde fica a melhor
consulta no menu (posição normalizada), para apanhar pistas de posição.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3)]
import generator_v3 as g  # noqa: E402


def p_det(A, i, W, T):
    return sum(g.verdict(frozenset(x for x in A if x[i] == h[i]), W, T) != "undetermined" for h in A) / len(A)


def values(world):
    hid = world["hidden"]
    W, T, menu = hid["w"], hid["T"], hid["menu"]
    A0 = g.admissible_idx([(i, hid["h"][i]) for i in hid["obs"]])
    out = {}
    for i in menu:
        tot = 0.0
        for y in {h[i] for h in A0}:
            Ay = frozenset(h for h in A0 if h[i] == y)
            if g.verdict(Ay, W, T) != "undetermined":
                tot += len(Ay)
            else:
                tot += len(Ay) * max((p_det(Ay, j, W, T) for j in menu if j != i), default=0.0)
        out[i] = tot / len(A0)
    return out


def leverage(worlds, threshold=0.25):
    gaps, best, mean, pos = [], [], [], []
    for w in worlds:
        v = values(w)
        menu = w["hidden"]["menu"]
        b = max(v.values())
        m = sum(v.values()) / len(v)
        gaps.append(b - m); best.append(b); mean.append(m)
        firsts = [k for k, q in enumerate(menu) if v[q] == b]
        pos.append(firsts[0] / max(1, len(menu) - 1))
    q = sorted(gaps)
    return {"worlds": len(worlds), "gap_mean": round(st.mean(gaps), 4), "gap_median": round(st.median(gaps), 4),
            "gap_quartiles": [round(q[len(q) // 4], 4), round(q[3 * len(q) // 4], 4)],
            "gap_min_max": [round(q[0], 4), round(q[-1], 4)],
            "share_worlds_gap_ge_threshold": round(sum(x >= threshold for x in gaps) / len(gaps), 4),
            "histogram_gap_0.05": {f"{k*0.05:.2f}": sum(k * 0.05 <= x < (k + 1) * 0.05 for x in gaps) for k in range(20)},
            "evidence_quality_best_mean": round(st.mean(best), 4), "difficulty_1_minus_uniform_mean": round(1 - st.mean(mean), 4),
            "best_query_position_normalised_mean": round(st.mean(pos), 4),
            "best_query_first_in_menu": round(sum(p == 0 for p in pos) / len(pos), 4)}


if __name__ == "__main__":
    import audit_v3 as a
    dev = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    print(json.dumps(leverage(dev), indent=1))

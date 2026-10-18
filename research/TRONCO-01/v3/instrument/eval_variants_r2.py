"""Ronda 2: V4, V5, V6 (docs/V3_CONSULTAS.md §8). Mesma métrica e mesmos critérios. Só desenvolvimento."""
import json
import statistics as st
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument")]
import generator_v3 as g  # noqa: E402
import query_leverage as QL  # noqa: E402
import variants as VA  # noqa: E402


def extra(ws, name):
    """Tie-corrected position, feature predictors and (V5) first-query value and second-query gain."""
    tie_pos, uniq_first, n_uniq, feats = [], [], 0, {"in_held_out": [], "not_observed": []}
    v1gap, gain_mean, gain_best = [], [], []
    for w in ws:
        hid = w["hidden"]
        v = QL.values(w)
        menu = hid["menu"]
        b = max(v.values())
        idx = [k for k, q in enumerate(menu) if v[q] == b]
        norm = lambda k: k / max(1, len(menu) - 1)
        tie_pos.append(st.mean(norm(k) for k in idx))
        if len(idx) == 1:
            n_uniq += 1
            uniq_first.append(idx[0] == 0)
        bests = {menu[k] for k in idx}
        chance = len(bests) / len(menu)
        for f, sel in (("in_held_out", [q for q in menu if q in hid["T"]]),
                       ("not_observed", [q for q in menu if q not in hid["obs"]])):
            if sel:
                feats[f].append((len(bests & set(sel)) / len(sel), chance))
        if name == "V5":
            A0 = g.admissible_idx([(i, hid["h"][i]) for i in hid["obs"]])
            v1 = {q: QL.p_det(A0, q, hid["w"], hid["T"]) for q in menu}
            v1gap.append(max(v1.values()) - st.mean(v1.values()))
            gain_mean.append(st.mean(v[q] - v1[q] for q in menu))
            qb = max(menu, key=lambda q: v[q])
            gain_best.append(v[qb] - v1[qb])
    out = {"position_tie_mean": round(st.mean(tie_pos), 4), "worlds_unique_best": n_uniq,
           "unique_best_first": round(st.mean(uniq_first), 4) if uniq_first else None,
           "feature_hit_vs_chance": {f: [round(st.mean(h for h, _ in x), 4), round(st.mean(c for _, c in x), 4)]
                                     for f, x in feats.items() if x}}
    if name == "V5":
        q = sorted(v1gap)
        out["V5_first_query_alone_gap_median"] = round(st.median(v1gap), 4)
        out["V5_second_query_gain_mean_over_menu"] = round(st.mean(gain_mean), 4)
        out["V5_second_query_gain_at_best"] = round(st.mean(gain_best), 4)
    return out


def criteria(r, x):
    n_menu = r["menu_size_mean"]
    cues = [h / c for h, c in list(r["surface_cue_hit_rate_vs_chance"].values()) + list(x["feature_hit_vs_chance"].values()) if c]
    return {
        "1_median_gap_ge_0.25": r["gap_median"] >= 0.25,
        "1_share_ge_0.5": r["share_worlds_gap_ge_threshold"] >= 0.5,
        "2_position_tie_mean_in_0.4_0.6": 0.40 <= x["position_tie_mean"] <= 0.60,
        "2_unique_best_first_le_1.5_over_menu": x["unique_best_first"] is None or x["unique_best_first"] <= 1.5 / n_menu,
        "3_evidence_quality_ge_0.8": r["evidence_quality_best_mean"] >= 0.80,
        "4_uniform_value_le_0.6": (1 - r["difficulty_1_minus_uniform_mean"]) <= 0.60,
        "5_targets_balanced": len(set(r["targets"].values())) == 1 and len(r["targets"]) == 3,
        "6_no_surface_cue_over_2x": max(cues) <= 2.0,
    }


out = {}
for name in ("V4", "V5", "V6"):
    ws, infeasible = VA.build(name)
    r = QL.leverage(ws)
    x = extra(ws, name)
    r.update(x)
    r["infeasible_cells"] = len(infeasible)
    r["criteria"] = criteria(r, x)
    r["all_met"] = all(r["criteria"].values())
    out[name] = r
    keep = ("worlds", "menu_size_mean", "gap_median", "gap_quartiles", "share_worlds_gap_ge_threshold",
            "evidence_quality_best_mean", "difficulty_1_minus_uniform_mean", "targets", "surface_cue_hit_rate_vs_chance",
            "infeasible_cells", "all_met") + tuple(x)
    print(name, json.dumps({k: r[k] for k in keep}), flush=True)
    print("   ", r["criteria"], flush=True)
(V3 / "results" / "instrumento" / "CONSULTAS_VARIANTES_R2.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")

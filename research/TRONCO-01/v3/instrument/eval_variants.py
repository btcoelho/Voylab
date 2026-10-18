"""Avalia V1, V2, V3 com a métrica e os critérios de docs/V3_CONSULTAS.md §2 e §4. Só desenvolvimento."""
import json
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument")]
import query_leverage as QL  # noqa: E402
import variants as VA  # noqa: E402


def criteria(r):
    n_menu = r["menu_size_mean"]
    t = r["targets"]
    cue = max(h / c if c else 0 for h, c in r["surface_cue_hit_rate_vs_chance"].values())
    return {
        "1_median_gap_ge_0.25": r["gap_median"] >= 0.25,
        "1_share_ge_0.5": r["share_worlds_gap_ge_threshold"] >= 0.5,
        "2_position_mean_in_0.4_0.6": 0.40 <= r["best_query_position_normalised_mean"] <= 0.60,
        "2_first_le_1.5_over_menu": r["best_query_first_in_menu"] <= 1.5 / n_menu,
        "3_evidence_quality_ge_0.8": r["evidence_quality_best_mean"] >= 0.80,
        "4_uniform_value_le_0.6": (1 - r["difficulty_1_minus_uniform_mean"]) <= 0.60,
        "5_targets_balanced": len(set(t.values())) == 1 and len(t) == 3,
        "6_surface_cue_le_2x_chance": cue <= 2.0,
    }


out = {}
for name in ("V1", "V2", "V3"):
    ws, infeasible = VA.build(name)
    r = QL.leverage(ws)
    r["infeasible_cells"] = len(infeasible)
    r["criteria"] = criteria(r)
    r["all_met"] = all(r["criteria"].values())
    out[name] = r
    print(name, json.dumps({k: r[k] for k in ("worlds", "gap_median", "share_worlds_gap_ge_threshold",
                                                "evidence_quality_best_mean", "difficulty_1_minus_uniform_mean",
                                                "best_query_position_normalised_mean", "best_query_first_in_menu",
                                                "menu_size_mean", "targets", "surface_cue_hit_rate_vs_chance",
                                                "infeasible_cells", "all_met")}), flush=True)
    print("   ", r["criteria"], flush=True)
(V3 / "results" / "instrumento" / "CONSULTAS_VARIANTES.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")

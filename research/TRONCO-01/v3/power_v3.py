"""Sample-size calculation for a paired difference in reach (80% power, two-sided alpha 0.05). Dev seeds only."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_v3 as a  # noqa: E402
import policies as P  # noqa: E402
import run_policies as R  # noqa: E402

Z = 1.96 + 0.8416


def sd_of_diff(x, y):
    d = [p - q for p, q in zip(x, y)]
    m = sum(d) / len(d)
    return math.sqrt(sum((u - m) ** 2 for u in d) / (len(d) - 1))


def main():
    worlds = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    per, meta = R.evaluate(worlds, [P.Aleatoria, P.Rival, P.BayesIG, P.SemConsultas])
    reach = {n: [r["reach"] for r in rows] for n, rows in per.items()}
    out = {"worlds_used": len(worlds), "seeds": list(a.DEV_SEEDS), "z": Z, "pairs": {}}
    for x, y in (("bayes_ig", "rival"), ("rival", "aleatoria"), ("bayes_ig", "aleatoria"), ("bayes_ig", "sem_consultas")):
        sd = sd_of_diff(reach[x], reach[y])
        diff = sum(p - q for p, q in zip(reach[x], reach[y])) / len(worlds)
        out["pairs"][f"{x} - {y}"] = {"observed_diff": diff, "sd_of_paired_diff": sd,
                                      "n_for_diff_0.05": math.ceil((Z * sd / 0.05) ** 2),
                                      "n_for_diff_0.10": math.ceil((Z * sd / 0.10) ** 2),
                                      "n_for_observed_diff": math.ceil((Z * sd / abs(diff)) ** 2) if diff else None}
    worst = max(v["n_for_diff_0.10"] for v in out["pairs"].values())
    out["recommended_worlds_per_partition_for_0.10_overall"] = worst
    out["recommended_worlds_per_partition_for_0.05_overall"] = max(v["n_for_diff_0.05"] for v in out["pairs"].values())
    print(json.dumps(out, indent=2))
    (HERE / "results" / "POTENCIA.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

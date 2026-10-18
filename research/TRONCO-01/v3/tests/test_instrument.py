from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path[:0] = [str(V3), str(V3 / "pilot"), str(V3 / "instrument")]
import apply_grid  # noqa: E402
import grid  # noqa: E402
import planted  # noqa: E402
import select_worlds as S  # noqa: E402


class PlantedPolicies(unittest.TestCase):
    def test_grid_labels_every_planted_policy_as_constructed(self):
        conf, rev, _ = planted.run(S.pilot_worlds())
        errors = {k: v for k, v in conf.items() if k[1] != k[2]}
        self.assertEqual(errors, {})
        self.assertTrue(all(ok for (_, ok) in rev))
        seen = {k[2] for k in conf}
        self.assertEqual(seen, set(grid.CATEGORIES))      # every category is exercised


class HistoricalRuns(unittest.TestCase):
    def test_grid_reproduces_recorded_classification(self):
        expected = json.loads((V3 / "results" / "instrumento" / "F2_GRELHA_HISTORICOS.json").read_text(encoding="utf-8"))
        ws = S.pilot_worlds()
        for label, d in apply_grid.RUNS[2:]:
            eps = [json.loads(l) for l in (V3 / "results" / d / "transcripts.jsonl").read_text().splitlines() if l]
            got = grid.summarise([grid.classify(w, apply_grid.replay(w, e["transcript"])) for w, e in zip(ws, eps)])
            self.assertEqual(json.loads(json.dumps(got)), expected[label], label)


if __name__ == "__main__":
    unittest.main()

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


class DecisiveQuery(unittest.TestCase):
    def test_one_step_decisive_matches_k_step_on_full_trees_including_non_decisive_states(self):
        import enumerate_states as ES
        import generator_v3 as g
        import scoring as sc
        from itertools import combinations, product
        import audit_v3 as a
        seen = {True: 0, False: 0}
        for w in a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True):   # 8 non-decisive states live here
            hid, b = w["hidden"], w["public"]["remaining_query_budget"]
            base = [(i, hid["h"][i]) for i in hid["obs"]]
            for r in range(b):
                for Q in combinations(hid["menu"], r):
                    for ys in product(g.D.outputs, repeat=r):
                        A = g.admissible_idx(base + list(zip(Q, ys)))
                        if not A or g.verdict(A, hid["w"], hid["T"]) != "undetermined":
                            continue
                        free = [q for q in hid["menu"] if q not in Q]
                        one = sc.can_still_determine(A, hid["w"], hid["T"], free)
                        self.assertEqual(one, ES.decisive_k(A, hid["w"], hid["T"], free, b - r))
                        seen[one] += 1
        self.assertGreater(seen[True], 0)
        self.assertGreater(seen[False], 0)      # the rare non-decisive states must be exercised


class FrozenReference(unittest.TestCase):
    def test_reference_artifacts_and_recomputed_summary_unchanged(self):
        import reference_manifest as RM
        self.assertEqual(RM.check(), [])

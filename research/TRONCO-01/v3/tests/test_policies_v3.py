from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import policies as P  # noqa: E402
import run_policies as R  # noqa: E402


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws = a.dev_set(seeds=(91001,), per_cell=1)
        cls.per, cls.meta = R.evaluate(cls.ws)

    def mean(self, name, key):
        rows = self.per[name]
        return sum(r[key] for r in rows) / len(rows)

    def test_oracle_reaches_target_everywhere(self):
        self.assertEqual(self.mean("oraculo", "reach"), 1.0)

    def test_no_invalid_actions(self):
        for n in self.per:
            self.assertEqual(self.mean(n, "invalid"), 0.0)

    def test_no_query_policy_reaches_only_undetermined_targets(self):
        share = sum(m["target"] == "undetermined" for m in self.meta) / len(self.meta)
        self.assertAlmostEqual(self.mean("sem_consultas", "reach"), share)

    def test_bayes_beats_no_queries_by_prespecified_margin(self):
        self.assertGreaterEqual(self.mean("bayes_ig", "reach") - self.mean("sem_consultas", "reach"), 0.25)

    def test_sticky_policy_fails_exactly_where_revision_is_required(self):
        for r_b, r_s, w in zip(self.per["bayes_ig"], self.per["pegajosa"], self.ws):
            self.assertEqual(r_b["revision_type_I"], 0.0)
            self.assertEqual(r_s["revision_type_I"], float(r_s["should_revise"]))

    def test_policies_read_only_public_fields(self):
        v = P.view(self.ws[0])
        self.assertEqual(set(v), {"rows", "cards", "w", "T", "menu", "budget"})
        self.assertFalse(set(v["T"]) & set(v["menu"]))


if __name__ == "__main__":
    unittest.main()

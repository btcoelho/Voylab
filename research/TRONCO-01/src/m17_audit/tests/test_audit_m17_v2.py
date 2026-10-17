from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import guard  # noqa: E402
import identifiability as I  # noqa: E402
import stats as S  # noqa: E402
import audit_m17_v2 as A  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_reserved_seeds_are_refused_directly_and_via_retry_chain(self):
        for seed in (64001, 64003, 64007, 75011, 75013, 75017, 64001 - guard.RETRY_STEP):
            with self.subTest(seed=seed):
                with self.assertRaises(guard.ReservedSeedError):
                    guard.build_world("NORMAL", "dev_table", seed, 1)

    def test_dev_and_substitute_are_allowed_and_disjoint_from_reserved(self):
        for seed, _ in guard.DEV + guard.SUBSTITUTE:
            self.assertFalse(guard.reachable_seeds(seed) & guard.RESERVED_SEEDS)


class IdentifiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = [guard.build_world(c, "dev_table", 53001, i) for c in guard.CATEGORIES for i in range(1, 6)]
        cls.res = [I.analyse(w) for w in cls.worlds]

    def test_no_world_is_non_identifiable_and_all_self_consistent(self):
        self.assertTrue(all(r["self_consistent"] for r in self.res))
        self.assertFalse(any(r["non_identifiable"] for r in self.res))
        self.assertTrue(all(r["budget_identifiable"] for r in self.res))

    def test_only_normal_change_is_ambiguous_at_start(self):
        for w, r in zip(self.worlds, self.res):
            if r["ambiguous_at_start"]:
                self.assertIn(w["category"], ("NORMAL", "CHANGE"))


class StatsTests(unittest.TestCase):
    def test_null_calibration_and_power(self):
        w = [guard.build_world(c, "dev_table", 53001, i) for c in guard.CATEGORIES for i in range(1, 13)]
        rows = [A.F.extract(x["public"]) for x in w]
        labels = [x["category"] for x in w]
        self.assertEqual(A.null_calibration(rows, labels, perms=20)["permutations"], 20)
        self.assertGreaterEqual(S.detection_rate(60, 5, 0.3, 100, sims=30), 0.9)
        self.assertLessEqual(S.detection_rate(60, 5, 0.0, 100, sims=30), 0.2)

    def test_planted_leak_is_detected_end_to_end(self):
        w = [guard.build_world(c, "dev_table", 53001, i) for c in guard.CATEGORIES for i in range(1, 31)]
        self.assertTrue(A.planted_end_to_end(w, 0.5)["detected"])
        self.assertFalse(A.planted_end_to_end(w, 0.0)["detected"])


class OutputTests(unittest.TestCase):
    def test_aggregate_only_and_reserved_never_requested(self):
        import json
        r = A.audit(perms=5)
        self.assertTrue(r["reserved_seeds_never_requested"])
        self.assertEqual(r["model_calls"], 0)
        text = json.dumps(r)
        for banned in ("world_id\":", "\"hidden\"", "pilot_"):
            self.assertNotIn(banned, text)
        self.assertEqual(r["duplicate_public_states"]["across_dev_and_substitute"], 0)


if __name__ == "__main__":
    unittest.main()

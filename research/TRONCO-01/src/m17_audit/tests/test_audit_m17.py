from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import audit_m17 as a  # noqa: E402
from generator import make_world  # noqa: E402


class M17AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = a.audit()

    def test_dev_split_only_and_no_model(self):
        self.assertEqual(self.result["split"], "dev")
        self.assertEqual(self.result["seeds"], [53001, 53003, 53009])
        self.assertEqual(self.result["worlds"], 300)
        self.assertEqual(self.result["model_calls"], 0)

    def test_output_is_aggregate_only(self):
        text = json.dumps(self.result)
        for banned in ("world_id", "\"hidden\"", "pilot_", "seed\":"):
            self.assertNotIn(banned, text)

    def test_public_state_has_no_hidden_fields(self):
        w = make_world("CHANGE", "dev_table", 53001, 60)
        self.assertEqual(set(w["public"]) & {"category", "family", "hidden", "seed", "index"}, set())

    def test_insufficiency_is_not_undetermined_under_v2_contract(self):
        c = self.result["by_category"]["INSUFFICIENCY"]
        self.assertEqual(c["initial_matches_expected"], 0)
        self.assertEqual(c["reachable_within_budget"], 0)

    def test_change_and_normal_share_one_initial_signature(self):
        mixed = self.result["signatures_with_conflicting_expected_verdicts"]
        self.assertEqual(len(mixed), 1)
        (counts,) = mixed.values()
        self.assertEqual(counts, {"supported": 60, "rejected": 60})

    def test_change_is_resolved_by_queries(self):
        c = self.result["by_category"]["CHANGE"]
        self.assertEqual(c["reachable_within_budget"], c["worlds"])
        self.assertGreater(c["menu_queries_contradicting_working_model"], 0)

    def test_deterministic(self):
        self.assertEqual(a.audit(), self.result)


if __name__ == "__main__":
    unittest.main()

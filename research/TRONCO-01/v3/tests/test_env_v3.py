from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import audit_v3 as a  # noqa: E402
import env_v3 as E  # noqa: E402
import generator_v3 as g  # noqa: E402
import policies as P  # noqa: E402


def w(target="rejected", kind="stable_uninformative", diff="facil"):
    return g.make_world(91001, diff, "mixed", 1, target, kind, k0=3)


class Protocol(unittest.TestCase):
    def test_state_never_contains_hidden_fields(self):
        ep = E.Episode(w())
        text = json.dumps(ep.state())
        for banned in ('"h"', '"h2"', "hidden", "target_verdict", "oracle", '"reference"'):
            self.assertNotIn(banned, text)

    def test_query_returns_row_and_consumes_budget_and_menu_entry(self):
        ep = E.Episode(w())
        qid = ep.state()["query_menu"][0]["id"]
        out = ep.step({"action": "query", "query_id": qid})
        self.assertTrue(out["ok"])
        self.assertEqual(out["remaining_query_budget"], 1)
        self.assertNotIn(qid, [q["id"] for q in ep.state()["query_menu"]])
        self.assertFalse(ep.step({"action": "query", "query_id": qid})["ok"])    # repeated

    def test_budget_is_enforced(self):
        ep = E.Episode(w())
        for q in ep.state()["query_menu"][:2]:
            self.assertTrue(ep.step({"action": "query", "query_id": q["id"]})["ok"])
        extra = ep.state()["query_menu"][0]["id"]
        self.assertFalse(ep.step({"action": "query", "query_id": extra})["ok"])

    def test_three_consecutive_invalid_actions_end_the_episode(self):
        ep = E.Episode(w())
        for _ in range(3):
            ep.step({"action": "dance"})
        self.assertTrue(ep.done and ep.forced_termination)
        self.assertFalse(ep.result()["complete"] if "complete" in ep.result() else False)

    def test_phase_gating_and_json_strings(self):
        ep = E.Episode(w())
        self.assertFalse(ep.step({"action": "keep"})["ok"])
        self.assertFalse(ep.step("not json")["ok"])
        self.assertTrue(ep.step('{"action": "suspend"}')["ok"])
        self.assertEqual(ep.phase, "revision")
        self.assertFalse(ep.step({"action": "query", "query_id": "q1"})["ok"])
        self.assertTrue(ep.step({"action": "keep"})["done"])

    def test_inconsistent_verdict_only_allowed_after_new_evidence(self):
        ep = E.Episode(w())
        bad = {"action": "commit", "verdict": "inconsistent", "admissible_cards": [], "predictions": {}}
        self.assertFalse(ep.step(bad)["ok"])
        ep.step({"action": "suspend"})
        self.assertTrue(ep.step({"action": "revise", "verdict": "inconsistent", "admissible_cards": []})["ok"])

    def test_new_evidence_appears_only_in_revision_phase(self):
        ep = E.Episode(w())
        self.assertNotIn("new_evidence", ep.state())
        ep.step({"action": "suspend"})
        self.assertEqual(len(ep.state()["new_evidence"]), len(ep.hid["block"]))

    def test_suspend_scoring(self):
        und = g.make_world(91001, "facil", "mixed", 1, "undetermined", "stable_uninformative", k0=3)
        ep = E.Episode(und)
        ep.step({"action": "suspend"})
        ep.step({"action": "keep"})
        r = ep.result()
        self.assertTrue(r["suspend_used"])
        self.assertFalse(r["suspend_correct"])           # budget left and a query could still determine the verdict
        ep2 = E.Episode(w("rejected"))
        ep2.step({"action": "suspend"})
        ep2.step({"action": "keep"})
        self.assertFalse(ep2.result()["suspend_correct"])


class Equivalence(unittest.TestCase):
    def test_protocol_harness_equals_direct_evaluator_for_every_reference_policy(self):
        ws = a.dev_set(seeds=(91001,), per_cell=1, with_indirect=True)[:30]
        keys = ("reach", "queries", "inference_error", "search_error", "evidence_ignored", "premature_stop",
                "revision_type_I", "revision_type_II")
        for cls in P.POLICIES_V2:
            pol = cls()
            for world in ws:
                d, e = P.run_episode(pol, world, 0), E.run_policy(pol, world, 0)
                self.assertEqual(e["invalid"], 0)
                for k in keys:
                    self.assertEqual(float(d[k]), float(e[k]), (pol.name, world["world_id"], k))


if __name__ == "__main__":
    unittest.main()

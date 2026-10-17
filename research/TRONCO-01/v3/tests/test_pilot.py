from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "pilot"))
import env_v3 as E  # noqa: E402
import fake_backends as F  # noqa: E402
import pilot_harness as H  # noqa: E402
import select_worlds as S  # noqa: E402


class PilotKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws = S.pilot_worlds()

    def test_selection_is_development_only_balanced_and_deterministic(self):
        self.assertEqual(len(self.ws), 48)
        self.assertEqual(S.worlds_sha(self.ws), S.worlds_sha(S.pilot_worlds()))
        for w in self.ws:
            self.assertTrue(91000 <= w["meta"]["seed"] < 92000)
        counts = {}
        for w in self.ws:
            counts[w["reference"]["target_verdict"]] = counts.get(w["reference"]["target_verdict"], 0) + 1
        self.assertEqual(set(counts.values()), {16})

    def test_prompt_never_leaks_hidden_information(self):
        for w in self.ws[:12]:
            ep = E.Episode(w)
            text = H.SYSTEM_PROMPT + H.render_state(ep.state())
            for banned in ("target", "oracle", "hidden", "reference", "h2", "should_revise"):
                self.assertNotIn(banned, text)
            ep.step({"action": "suspend"})
            self.assertIn("EVIDÊNCIA NOVA", H.render_state(ep.state()))

    def test_real_backend_signature_has_no_state_argument(self):
        import inspect
        import ast
        src = (HERE.parent / "pilot" / "hf_backend.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "generate")
        self.assertEqual([a.arg for a in fn.args.args], ["self", "system", "user", "schema"])

    def test_garbage_backend_is_terminated_and_counted(self):
        r = H.run_episode(self.ws[0], F.Garbage(), pass_state=True)
        self.assertTrue(r["result"]["forced_termination"])
        self.assertFalse(r["result"].get("complete", False))
        agg = H.aggregate([r])
        self.assertEqual(agg["actions_accepted"]["invalid_rate"], 1.0)
        self.assertEqual(agg["outputs_parseable_json"]["rate"], 0.0)

    def test_random_valid_backend_completes_every_episode_with_no_invalid_action(self):
        eps = [H.run_episode(w, F.RandomValid(i), pass_state=True) for i, w in enumerate(self.ws[:16])]
        agg = H.aggregate(eps)
        self.assertEqual(agg["complete"]["rate"], 1.0)
        self.assertEqual(agg["actions_accepted"]["invalid_rate"], 0.0)

    def test_commit_undetermined_reaches_exactly_the_undetermined_targets(self):
        eps = [H.run_episode(w, F.CommitUndetermined(), pass_state=True) for w in self.ws]
        reach = sum(e["result"]["reach"] for e in eps)
        self.assertEqual(reach, sum(w["reference"]["target_verdict"] == "undetermined" for w in self.ws))

    def test_schema_matches_phase_and_uses_const_for_actions(self):
        s = H.action_schema("explore")
        self.assertEqual({o["properties"]["action"]["const"] for o in s["anyOf"]}, {"query", "commit", "suspend"})
        s = H.action_schema("revision")
        self.assertEqual({o["properties"]["action"]["const"] for o in s["anyOf"]}, {"keep", "revise"})
        self.assertIn("inconsistent", json.dumps(s))
        self.assertNotIn("inconsistent", json.dumps(H.action_schema("explore")))


if __name__ == "__main__":
    unittest.main()

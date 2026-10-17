from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "pilot"))
import pilot_harness as H  # noqa: E402
import smoke_hf as SM  # noqa: E402


class SmokeValidator(unittest.TestCase):
    def test_valid_actions_match(self):
        ex, rv = H.action_schema("explore"), H.action_schema("revision")
        self.assertTrue(SM.matches({"action": "query", "query_id": "q1"}, ex))
        self.assertTrue(SM.matches({"action": "commit", "verdict": "undetermined", "admissible_cards": ["A"],
                                    "predictions": {"1": "0"}}, ex))
        self.assertTrue(SM.matches({"action": "suspend"}, ex))
        self.assertTrue(SM.matches({"action": "keep"}, rv))
        self.assertTrue(SM.matches({"action": "revise", "verdict": "inconsistent", "admissible_cards": []}, rv))

    def test_invalid_actions_do_not_match(self):
        ex, rv = H.action_schema("explore"), H.action_schema("revision")
        bad = [({"action": "query"}, ex), ({"action": "commit", "verdict": "inconsistent", "admissible_cards": [],
                                            "predictions": {}}, ex),
               ({"action": "commit", "verdict": "supported", "admissible_cards": [], "predictions": {"1": "2"}}, ex),
               ({"action": "suspend", "x": 1}, ex), ({"action": "keep"}, ex), ({"action": "query", "query_id": "q1"}, rv),
               ("texto", ex)]
        for value, schema in bad:
            with self.subTest(value=value):
                self.assertFalse(SM.matches(value, schema))


class CompatShim(unittest.TestCase):
    def test_shim_reexports_only_when_missing(self):
        import hf_backend
        saved = {k: sys.modules.get(k) for k in ("transformers", "transformers.tokenization_utils")}
        try:
            fake = types.ModuleType("transformers")
            fake.PreTrainedTokenizerBase = type("PreTrainedTokenizerBase", (), {})
            tu = types.ModuleType("transformers.tokenization_utils")
            fake.tokenization_utils = tu
            sys.modules["transformers"], sys.modules["transformers.tokenization_utils"] = fake, tu
            self.assertEqual(hf_backend._transformers_compat(), "reexported PreTrainedTokenizerBase")
            self.assertIs(tu.PreTrainedTokenizerBase, fake.PreTrainedTokenizerBase)
            self.assertEqual(hf_backend._transformers_compat(), "none")
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v


if __name__ == "__main__":
    unittest.main()

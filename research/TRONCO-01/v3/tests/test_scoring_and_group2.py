from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402
import policies as P  # noqa: E402
import scoring as sc  # noqa: E402
import text_audit_v3 as ta  # noqa: E402


def world(target, kind="stable_uninformative", fam="mixed", k0=3, diff="facil"):
    return g.make_world(93001, diff, fam, 1, target, kind, k0=k0)


class ScoringTests(unittest.TestCase):
    def answer(self, w, queried, verdict, stop="commit", cards=None):
        v = P.view(w)
        base = P.Policy().answer(v, tuple(v["rows"]) + tuple((q, w["hidden"]["h"][q]) for q in queried), 0)
        base.update({"verdict": verdict, "stop": stop})
        if cards is not None:
            base["admissible_cards"] = cards
        return base

    def test_exact_answer_has_no_errors(self):
        w = world("rejected")
        q = list(w["reference"]["oracle_queries"])
        r = sc.score(w, q, self.answer(w, q, "rejected"), 1)
        self.assertFalse(r["inference_error"] or r["search_error"] or r["evidence_ignored"])
        self.assertTrue(r["reach"])

    def test_ignoring_determined_evidence_is_inference_error_and_evidence_ignored(self):
        w = world("supported")
        q = list(w["reference"]["oracle_queries"])
        r = sc.score(w, q, self.answer(w, q, "undetermined"), 0)
        self.assertTrue(r["inference_error"] and r["evidence_ignored"])
        self.assertFalse(r["search_error"])

    def test_not_searching_is_search_error_not_inference_error(self):
        w = world("rejected")
        r = sc.score(w, [], self.answer(w, [], "undetermined"), 2)
        self.assertTrue(r["search_error"])
        self.assertFalse(r["inference_error"])
        self.assertTrue(r["premature_stop"])

    def test_stopping_with_budget_left_is_not_premature_when_verdict_is_determined(self):
        w = world("rejected")
        q = list(w["reference"]["oracle_queries"])
        r = sc.score(w, q, self.answer(w, q, "rejected"), 1)
        self.assertFalse(r["premature_stop"])

    def test_wrong_card_set_is_detected(self):
        w = world("supported")
        q = list(w["reference"]["oracle_queries"])
        r = sc.score(w, q, self.answer(w, q, "supported", cards=[]), 0)
        self.assertFalse(r["cards_exact"])


class Group2Tests(unittest.TestCase):
    def test_change_indirect_never_repeats_an_earlier_input_and_is_inconsistent(self):
        for fam in g.FAMILIES:
            w = world("supported", "change_indirect", fam, 4, "medio")
            hid = w["hidden"]
            self.assertFalse(set(hid["block"]) & (set(hid["obs"]) | set(w["reference"]["oracle_queries"])))
            self.assertEqual(w["reference"]["post_verdict"], "inconsistent")

    def test_policies_read_only_public_fields_including_new_ones(self):
        w = world("rejected")
        for cls in (P.Rival, P.PrimeiroDoMenu, P.CegaPegajosa, P.IgnoraEvidencia):
            r = P.run_episode(cls(), w, 0)
            self.assertEqual(r["invalid"], 0)

    def test_negative_controls_fail_where_they_should(self):
        w = world("supported", "stable_informative", "mixed", 3)
        self.assertEqual(P.run_episode(P.CegaPegajosa(), w, 0)["revision_type_I"], 1.0 if w["reference"]["kind"] else 0)
        self.assertTrue(P.run_episode(P.IgnoraEvidencia(), w, 0)["evidence_ignored"])
        self.assertFalse(P.run_episode(P.BayesIG(), w, 0)["inference_error"])

    def test_balance_trim_equalises_targets_in_every_group(self):
        ws = a.balance_trim(a.dev_set(seeds=(93001,), per_cell=3, with_indirect=True))
        groups = {}
        for w in ws:
            groups.setdefault((w["meta"]["difficulty"], w["meta"]["family"], len(w["hidden"]["obs"])), []).append(w["reference"]["target_verdict"])
        for k, v in groups.items():
            self.assertEqual(len({v.count(t) for t in g.VERDICTS}), 1, k)

    def test_prompt_is_deterministic_and_has_no_hidden_information(self):
        w = world("rejected")
        t = ta.render_prompt(w["public"])
        self.assertEqual(t, ta.render_prompt(w["public"]))
        for banned in ("hidden", "target", "category", "oracle"):
            self.assertNotIn(banned, t.lower())


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import generator_v3 as g  # noqa: E402
import audit_v3 as a  # noqa: E402


class Semantics(unittest.TestCase):
    def test_verdict_cases(self):
        h0, h1 = g.SPACE[0], g.SPACE[1]
        A = frozenset({h0, h1})
        i = next(j for j in range(g.N) if h0[j] != h1[j])
        self.assertEqual(g.verdict(frozenset(), h0, [i]), "inconsistent")
        self.assertEqual(g.verdict(frozenset({h1}), h0, [i]), "rejected")
        self.assertEqual(g.verdict(A, h0, [i]), "undetermined")
        j = next(j for j in range(g.N) if h0[j] == h1[j])
        self.assertEqual(g.verdict(A, h0, [j]), "supported")

    def test_rejected_is_absorbing(self):
        w = g.SPACE[3]
        h = next(c for c in g.SPACE if c != w)
        i = next(j for j in range(g.N) if w[j] != h[j])
        T = [j for j in range(g.N) if j != i][:2]
        A1 = g.admissible_idx([(i, h[i])])
        self.assertEqual(g.verdict(A1, w, T), "rejected")
        for j in range(g.N):
            if j != i:
                self.assertEqual(g.verdict(g.admissible_idx([(i, h[i]), (j, h[j])]), w, T), "rejected")


class Generator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws = [g.make_world(91001, d, f, 1, t, k, k0=3)
                  for d, f, t, k in [("facil", "single", "rejected", "stable_uninformative"),
                                     ("facil", "pair", "supported", "stable_informative"),
                                     ("medio", "mixed", "undetermined", "change"),
                                     ("medio", "mixed", "supported", "change")]]

    def test_deterministic(self):
        again = g.make_world(91001, "facil", "single", 1, "rejected", "stable_uninformative", k0=3)
        self.assertEqual(json.dumps(again, sort_keys=True), json.dumps(self.ws[0], sort_keys=True))

    def test_public_has_no_hidden_fields_and_menu_excludes_held_out(self):
        for w in self.ws:
            self.assertEqual(set(w["public"]), {"observations", "candidate_models", "working_model_id",
                                                "held_out_inputs", "query_menu", "remaining_query_budget"})
            menu = {json.dumps(q["input"], sort_keys=True) for q in w["public"]["query_menu"]}
            for t in w["public"]["held_out_inputs"]:
                self.assertNotIn(json.dumps(t, sort_keys=True), menu)
            obs = {json.dumps(o["input"], sort_keys=True) for o in w["public"]["observations"]}
            self.assertFalse(obs & menu)

    def test_working_card_fits_initial_rows_and_starts_undetermined(self):
        for w in self.ws:
            self.assertEqual(w["reference"]["initial_verdict"], "undetermined")
            self.assertEqual(a.public_verdict(w["public"]), "undetermined")

    def test_reference_is_recomputable_from_public_information(self):
        for w in self.ws:
            extra = [(q, w["hidden"]["h"][q]) for q in w["reference"]["oracle_queries"]]
            self.assertEqual(a.public_verdict(w["public"], extra), w["reference"]["target_verdict"])

    def test_change_worlds_contradict_an_earlier_row(self):
        for w in self.ws[2:]:
            r = g.revision_reference(w, w["reference"]["oracle_queries"])
            self.assertEqual(r["post_verdict"], "inconsistent")
            self.assertTrue(r["should_revise"])

    def test_reserved_seeds_refused(self):
        for seed in (64001, 75011, 64001 + g.DRAW_STRIDE):
            with self.assertRaises(g.ReservedSeedError):
                g.make_world(seed, "facil", "single", 1, "rejected", "stable_uninformative")


class Round1(unittest.TestCase):
    def test_audit_acceptance(self):
        ws = a.dev_set(seeds=(91001,), per_cell=3)
        r = a.audit(ws)
        self.assertEqual(r["model_calls"], 0)
        self.assertEqual(r["identifiability"]["public_recomputation_mismatches"], 0)
        self.assertEqual(r["duplicate_public_states"], 0)
        self.assertLessEqual(r["balance"]["max_share"], 0.6)
        self.assertEqual(r["R4_leakage"]["rejected_after_holm"], [])


if __name__ == "__main__":
    unittest.main()

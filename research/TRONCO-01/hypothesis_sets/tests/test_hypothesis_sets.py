from itertools import combinations, product
from math import comb
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import hypothesis_sets as hs  # noqa: E402
import worlds as wd  # noqa: E402

D = hs.TRONCO_V27
SPACE2 = hs.enumerate_hypotheses(D, 2)

A = {"id": "A", "statement": "Output depends only on glyph.", "table": {"g0": "0", "g1": "1"}}
B = {"id": "B", "statement": "Output depends only on setting.", "table": {"s0": "0", "s1": "1"}}
C = {"id": "C", "statement": "Output depends on glyph and phase.",
     "table": {"g0|t0": "0", "g0|t1": "1", "g1|t0": "1", "g1|t1": "0"}}


def obs(n, glyph, setting, partner, phase, output):
    return {"id": f"o{n}", "input": {"glyph": glyph, "setting": setting, "partner": partner,
                                     "phase": phase}, "output": output}


def state(rows, working="A"):
    cards = [A, B, C]
    return {"candidate_models": cards, "observations": rows, "query_menu": [],
            "remaining_query_budget": 0, "working_model": next(c for c in cards if c["id"] == working)}


def evidence_by_hand(inputs, h):
    """Evidence built without `worlds`: an independent route for the pair laws."""
    return hs.Evidence(tuple(sorted({(x, h[D.index(x)]) for x in inputs})))


class EnumerationTests(unittest.TestCase):
    def test_constructive_enumeration_matches_brute_force_filter(self):
        everything = list(product(D.outputs, repeat=len(D.inputs)))
        self.assertEqual(len(everything), 2 ** 16)
        sizes = [len(hs.essential_support(D, h)) for h in everything]
        for k in range(len(D.features) + 1):
            with self.subTest(max_support=k):
                expected = sum(1 for s in sizes if s <= k)
                self.assertEqual(len(hs.enumerate_hypotheses(D, k)), expected)

    def test_known_counts_for_binary_domain(self):
        # constants 2; one essential variable 4*2; two essential variables C(4,2)*10.
        self.assertEqual(len(hs.enumerate_hypotheses(D, 0)), 2)
        self.assertEqual(len(hs.enumerate_hypotheses(D, 1)), 10)
        self.assertEqual(len(SPACE2), 70)

    def test_identity_is_extensional(self):
        for h in SPACE2:
            self.assertEqual(len(h), len(D.inputs))
        # "depends only on glyph" with a constant table is the same hypothesis as a constant.
        const = hs.card_hypothesis(D, {"id": "K", "table": {"g0": "0", "g1": "0"}})
        self.assertEqual(hs.essential_support(D, const), frozenset())
        self.assertIn(const, hs.enumerate_hypotheses(D, 0))


class IndistinguishabilityLaws(unittest.TestCase):
    """Exhaustive over every observed set of up to three inputs and every hypothesis."""

    def setUp(self):
        self.subsets = [s for r in range(4) for s in combinations(D.inputs, r)]
        self.assertEqual(len(self.subsets), sum(comb(16, r) for r in range(4)))

    def test_admissible_set_equals_the_class_of_indistinguishable_worlds(self):
        for observed in self.subsets:
            classes = {}
            for h in SPACE2:
                classes.setdefault(evidence_by_hand(observed, h), set()).add(h)
            for ev, members in classes.items():
                self.assertEqual(hs.admissible(D, SPACE2, ev), frozenset(members))

    def test_pairs_are_exactly_the_same_evidence_pairs(self):
        for observed in self.subsets[::7]:
            classes = {}
            for h in SPACE2:
                classes.setdefault(evidence_by_hand(observed, h), set()).add(h)
            expected = sum(comb(len(m), 2) for m in classes.values())
            pairs = list(wd.indistinguishable_pairs(D, SPACE2, observed))
            self.assertEqual(len(pairs), expected)
            for a, b in pairs:
                self.assertNotEqual(a.hidden, b.hidden)
                self.assertEqual(evidence_by_hand(observed, a.hidden), evidence_by_hand(observed, b.hidden))
                self.assertTrue(wd.same_admissible(D, SPACE2, (a, b)))

    def test_only_discriminating_evidence_separates_a_pair(self):
        for observed in self.subsets[::11]:
            for a, b in wd.indistinguishable_pairs(D, SPACE2, observed):
                x = wd.separating_extension(D, a, b)
                wider = observed + (x,)
                adm_a = hs.admissible(D, SPACE2, evidence_by_hand(wider, a.hidden))
                self.assertIn(a.hidden, adm_a)
                self.assertNotIn(b.hidden, adm_a)
                # A non-discriminating extra input keeps them together.
                same = [y for y in D.inputs if y not in observed and a.hidden[D.index(y)] == b.hidden[D.index(y)]]
                if same:
                    adm_same = hs.admissible(D, SPACE2, evidence_by_hand(observed + (same[0],), a.hidden))
                    self.assertTrue({a.hidden, b.hidden} <= adm_same)
                break

    def test_public_view_never_contains_the_hidden_mechanism(self):
        h = sorted(SPACE2)[5]
        view = wd.World(hidden=h, observed=D.inputs[:2], cards=(A, B, C), working_id="A").public_view(D)
        self.assertEqual(set(view), {"observations", "candidate_models", "query_menu",
                                     "remaining_query_budget", "working_model"})
        self.assertNotIn("".join(h), repr(view))


class ConclusionTests(unittest.TestCase):
    def test_order_and_record_ids_do_not_change_conclusions(self):
        rng = random.Random(17)
        rows = [obs(1, "g0", "s0", "p0", "t0", "0"), obs(2, "g0", "s1", "p0", "t0", "0"),
                obs(3, "g0", "s0", "p0", "t1", "0")]
        base = hs.conclusion_set(D, SPACE2, state(rows))
        for _ in range(20):
            shuffled = [dict(r) for r in rows]
            rng.shuffle(shuffled)
            for n, r in enumerate(shuffled):
                r["id"] = f"z{rng.randrange(1000)}_{n}"
            self.assertEqual(hs.conclusion_set(D, SPACE2, state(shuffled)), base)

    def test_more_evidence_never_enlarges_the_admissible_set(self):
        rng = random.Random(3)
        for _ in range(200):
            h = rng.choice(sorted(SPACE2))
            xs = rng.sample(D.inputs, 5)
            sizes = [len(hs.admissible(D, SPACE2, evidence_by_hand(xs[:n], h))) for n in range(6)]
            self.assertEqual(sizes, sorted(sizes, reverse=True))
            self.assertIn(h, hs.admissible(D, SPACE2, evidence_by_hand(xs, h)))

    def test_contradictory_rows_are_inconsistency_not_none_fit(self):
        rows = [obs(1, "g0", "s0", "p0", "t0", "0"), obs(2, "g0", "s0", "p0", "t0", "1")]
        result = hs.conclusion_set(D, SPACE2, state(rows))
        self.assertEqual(result["status"], "inconsistent_observations")
        self.assertEqual(result["admissible_count"], 0)
        self.assertEqual(result["conflicting_inputs"], [["g0", "s0", "p0", "t0"]])

    def test_none_fit_among_declared_does_not_mean_no_explanation(self):
        rows = [obs(1, "g0", "s0", "p0", "t0", "0"), obs(2, "g0", "s1", "p0", "t0", "1"),
                obs(3, "g1", "s0", "p0", "t0", "1")]
        result = hs.conclusion_set(D, SPACE2, state(rows))
        self.assertEqual(result["declared"]["diagnosis"], "none_fit")
        self.assertEqual(result["admissible_count"], 2)  # XOR and OR of glyph, setting
        self.assertEqual(result["admissible_supports"], [["glyph", "setting"]])

    def test_identified_among_declared_is_not_mechanism_identified(self):
        rows = [obs(1, "g0", "s0", "p0", "t0", "0"), obs(2, "g0", "s1", "p0", "t0", "0"),
                obs(3, "g0", "s0", "p0", "t1", "0")]
        result = hs.conclusion_set(D, SPACE2, state(rows))
        self.assertEqual(result["declared"]["candidates"], ["A"])
        self.assertEqual(result["admissible_declared_cards"], ["A"])
        self.assertGreater(result["admissible_count"], 1)
        self.assertEqual(result["status"], "mechanism_underdetermined_in_space")

    def test_declared_labels_follow_the_v2_contract(self):
        cases = [
            ([], {"candidates": ["A", "B", "C"], "diagnosis": "ambiguous",
                  "sufficiency": "no_observations", "verdict": "undetermined"}),
            ([obs(1, "g0", "s0", "p0", "t0", "0"), obs(2, "g0", "s1", "p0", "t0", "1")],
             {"candidates": ["B"], "diagnosis": "identified",
              "sufficiency": "identity_resolved", "verdict": "rejected"}),
        ]
        for rows, expected in cases:
            self.assertEqual(hs.declared_labels(D, state(rows)), expected)


class CardDecodingTests(unittest.TestCase):
    def test_partial_table_is_not_completed(self):
        partial = {"id": "P", "table": {"g0|t0": "0", "g0|t1": "1", "g1|t0": "1"}}
        self.assertIsNone(hs.card_hypothesis(D, partial))
        ev = hs.Evidence.from_observations(D, [obs(1, "g1", "s0", "p0", "t1", "0")])
        self.assertFalse(hs.card_fits(D, partial, ev))

    def test_statement_must_match_table_keys(self):
        lying = {"id": "L", "statement": "Output depends only on setting.", "table": {"g0": "0", "g1": "1"}}
        with self.assertRaises(hs.CardError):
            hs.card_features(D, lying)

    def test_mixed_key_layouts_are_rejected(self):
        with self.assertRaises(hs.CardError):
            hs.card_features(D, {"id": "M", "table": {"g0": "0", "s1": "1"}})

    def test_declared_cards_decode_to_the_expected_supports(self):
        self.assertEqual(hs.essential_support(D, hs.card_hypothesis(D, A)), {"glyph"})
        self.assertEqual(hs.essential_support(D, hs.card_hypothesis(D, B)), {"setting"})
        self.assertEqual(hs.essential_support(D, hs.card_hypothesis(D, C)), {"glyph", "phase"})


class IdentifiabilityAndScoring(unittest.TestCase):
    def test_question_answer_differs_across_indistinguishable_worlds(self):
        rows = [obs(1, "g0", "s0", "p0", "t0", "0")]
        ev = hs.Evidence.from_observations(D, rows)
        observed = (("g0", "s0", "p0", "t0"),)
        a = hs.card_hypothesis(D, A)
        result = wd.identifiability(D, SPACE2, ev, observed, lambda w: w.hidden == a)
        self.assertFalse(result["identifiable"])
        self.assertEqual(len(result["possible_answers"]), 2)
        result = wd.identifiability(D, SPACE2, ev, observed, lambda w: w.hidden[0])
        self.assertTrue(result["identifiable"])

    def test_set_valued_score(self):
        adm = frozenset(sorted(SPACE2)[:4])
        self.assertTrue(hs.score_set_answer(adm, adm)["exact"])
        partial = hs.score_set_answer(adm, list(adm)[:2] + [sorted(SPACE2)[-1]])
        self.assertAlmostEqual(partial["validity"], 2 / 3)
        self.assertAlmostEqual(partial["recovery"], 2 / 4)
        self.assertFalse(partial["exact"])
        self.assertIsNone(hs.score_set_answer(adm, [])["validity"])


class ArchivedV27Audit(unittest.TestCase):
    def test_audit_of_exposed_states(self):
        import audit_v27
        result = audit_v27.audit()
        s = result["summary"]
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(s["episodes"], 10)
        self.assertEqual(s["distinct_public_states"], 9)
        self.assertEqual(s["duplicate_public_state_groups"], [["pilot_01", "pilot_02"]])
        self.assertEqual(s["duplicates_with_different_private_labels"], [])
        self.assertEqual(s["declared_labels_match_private_reference"], 10)
        self.assertEqual(s["declared_none_fit_but_some_mechanism_in_space_fits"], ["pilot_09", "pilot_10"])


if __name__ == "__main__":
    unittest.main()

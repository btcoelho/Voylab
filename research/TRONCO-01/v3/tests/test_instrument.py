from pathlib import Path
import json
import sys
import os
import unittest

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path[:0] = [str(V3), str(V3 / "pilot"), str(V3 / "instrument")]
import apply_grid  # noqa: E402
import grid  # noqa: E402
import planted  # noqa: E402
import select_worlds as S  # noqa: E402


# Exhaustive tests (full development trees, V4 build) run when TRONCO_SLOW=true: in CI on pull requests and on main.
SLOW = unittest.skipUnless(os.environ.get("TRONCO_SLOW", "true") == "true", "slow test (set TRONCO_SLOW=true)")


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


@SLOW
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


@SLOW
class FrozenReference(unittest.TestCase):
    def test_reference_artifacts_and_recomputed_summary_unchanged(self):
        import reference_manifest as RM
        self.assertEqual(RM.check(), [])


@SLOW
class V4Task(unittest.TestCase):
    def test_planted_policies_on_v4_worlds(self):
        import variants as VA
        ws, _ = VA.build("V4")
        conf, rev, _ = planted.run(ws[:90])
        self.assertEqual({k: v for k, v in conf.items() if k[1] != k[2]}, {})
        self.assertTrue(all(ok for (_, ok) in rev))


class PendingItemsDone(unittest.TestCase):
    """Itens que estavam pendentes para o congelamento (revisão de 18/10): falham se forem desfeitos."""

    def test_decisive_query_looks_k_steps_ahead(self):
        import inspect
        import scoring as sc
        self.assertIn("k", inspect.signature(sc.can_still_determine).parameters)

    def test_policy_seed_by_uid_separates_siblings(self):
        import policies as P
        ws = S.pilot_worlds()
        sib = [w for w in ws if w["world_id"] == ws[0]["world_id"]]
        self.assertGreater(len(sib), 1)
        P.SEED_MODE["mode"] = "uid"
        try:
            self.assertEqual(len({P.policy_seed_key(w) for w in sib}), len(sib))
        finally:
            P.SEED_MODE["mode"] = "legacy"
        self.assertEqual(len({P.policy_seed_key(w) for w in sib}), 1)   # legacy kept for recorded results

    @SLOW
    def test_partition_by_structure_group_never_splits_a_group(self):
        import audit_v3 as a
        import partition as PT
        ws = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
        parts = PT.partition(ws, "teste", {"treino": 0.6, "validacao": 0.2, "cega": 0.2})
        self.assertEqual(PT.crossing_groups(parts), set())
        self.assertEqual(sum(len(v) for v in parts.values()), len(ws))
        self.assertTrue(all(parts.values()))


@SLOW
class HumanPilotAnalysis(unittest.TestCase):
    """Participantes sintéticos com resultado conhecido, antes de haver respostas reais."""

    @classmethod
    def setUpClass(cls):
        import analyse_human as AH
        import generator_v3 as g
        import scoring as sc
        cls.AH = AH
        cls.eps = json.loads((V3 / "results" / "instrumento" / "PILOTO_HUMANO_EPISODIOS.json").read_text(encoding="utf-8"))
        cls.worlds = AH.load_worlds()
        import random
        rng = random.Random(3)

        def perfect(code):
            out = {}
            for e in cls.eps:
                w = cls.worlds[e["uid"]]
                hid = w["hidden"]
                oq = (w["reference"]["oracle_queries"] or [hid["menu"][0]])[0]
                qid = next(m["id"] for m in w["public"]["query_menu"] if g.INPUTS.index(g.D.as_tuple(m["input"])) == oq)
                own = g.verdict(g.admissible_idx(sc.history_rows(w, [oq])), hid["w"], hid["T"])
                post = g.revision_reference(w, [oq])["post_verdict"]
                out[e["uid"]] = {"query": qid, "commit": {"verdict": own, "cards": [], "predictions": {}},
                                 "final": {"action": "keep"} if post == own else {"action": "revise", "verdict": post, "cards": []},
                                 "t_total_ms": 120000}
            return {"code": code, "episodes": out}

        def randomp(code):
            out = {}
            for e in cls.eps:
                out[e["uid"]] = {"query": rng.choice(e["menu"])["id"],
                                 "commit": {"verdict": rng.choice(["rejected", "supported", "undetermined"]), "cards": [],
                                            "predictions": {}}, "final": {"action": "keep"}, "t_total_ms": 30000}
            return {"code": code, "episodes": out}
        cls.res_perfect = AH.analyse(cls.eps, [perfect("P1"), perfect("P2")], cls.worlds)
        cls.res_random = AH.analyse(cls.eps, [randomp("P1"), randomp("P2")], cls.worlds)

    def test_perfect_participants(self):
        agg = self.res_perfect["agregado"]
        for c in ("cond_A", "cond_B"):
            s = agg[c]["todos"]
            self.assertEqual(s["fundamentado"], [s["n"], s["n"]])
            self.assertEqual(s["kappa_vs_referencia"], 1.0)
            self.assertEqual(s["leitura_fundamentado"], "passa")       # pooled n = 20
            self.assertEqual(s["revisao_final_correta"], [s["n"], s["n"]])
            self.assertIn("qualidade_alta", agg[c])
            self.assertIn("qualidade_baixa", agg[c])
        # per person and condition n = 10: even 10/10 cannot clear 0.80 at the Wilson lower bound
        self.assertEqual(self.res_perfect["por_participante"]["P1"]["cond_A"]["todos"]["leitura_fundamentado"], "inconclusivo")

    def test_conditions_are_counterbalanced(self):
        rows = self.res_perfect["linhas"]
        for uid in {r["uid"] for r in rows}:
            conds = {r["code"]: r["condition"] for r in rows if r["uid"] == uid}
            self.assertNotEqual(conds["P1"], conds["P2"])

    def test_random_participants_fail(self):
        s = self.res_random["agregado"]["cond_A"]["todos"]
        self.assertLess(s["fundamentado"][0] / s["n"], 0.5)
        self.assertIn(s["leitura_fundamentado"], ("falha", "inconclusivo"))
        self.assertLess(s["kappa_vs_referencia"], 0.5)

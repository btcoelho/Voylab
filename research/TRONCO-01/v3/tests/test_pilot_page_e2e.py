"""Ponta a ponta da página do piloto humano: um participante simulado clica a página real (Chromium), o registo que a
página grava passa por analyse_human e tem de dar exatamente as mesmas linhas que o mesmo comportamento escrito à mão.
Verifica também a ordem alternada das condições, a ajuda na revisão (condição B) e o retorno nos episódios de treino.
Corre só com TRONCO_SLOW=true e com o Playwright disponível."""
import json
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument"), str(V3 / "pilot")]

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

SLOW = os.environ.get("TRONCO_SLOW", "true") == "true"
MOCK = """window.__store = {}; window.claude = {use: async (n) => n === 'user' ? {id: async () => 'u-test'} :
 {doc: (p) => ({get: async () => ({exists: p in window.__store, data: () => JSON.parse(window.__store[p])}),
               set: async (v) => { window.__store[p] = JSON.stringify(v); }})}};"""


def decisions(episodes, seed):
    rng = random.Random(seed)
    out = {}
    for e in episodes:
        cards = [c for c in e["cards"] if rng.random() < 0.5]
        fin = {"action": "keep"} if rng.random() < 0.5 else \
            {"action": "revise", "verdict": rng.choice(["rejected", "supported", "undetermined", "inconsistent"]),
             "cards": [c for c in e["cards"] if rng.random() < 0.5]}
        out[e["uid"]] = {"query": rng.choice(e["menu"])["id"],
                         "commit": {"verdict": rng.choice(["rejected", "supported", "undetermined"]), "cards": cards,
                                    "predictions": {str(k): rng.choice("01") for k in range(1, 5)}},
                         "final": fin}
    return out


@unittest.skipUnless(SLOW and sync_playwright is not None, "slow end-to-end test (TRONCO_SLOW=true, Playwright)")
class PilotPageEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import human_pilot as HP
        R = V3 / "results" / "instrumento"
        cls.eps = json.loads((R / "PILOTO_HUMANO_EPISODIOS.json").read_text(encoding="utf-8"))
        cls.tr = json.loads((R / "PILOTO_HUMANO_TREINO.json").read_text(encoding="utf-8"))
        here = V3 / "instrument"
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page = Path(cls.tmp.name) / "page.html"
        cls.page.write_text("<!doctype html><meta charset=utf-8>" +
                            HP.build_page(cls.eps, cls.tr, here / "piloto_humano_template.html", here / "piloto_humano_regras.txt"),
                            encoding="utf-8")

    def drive(self, code, plan):
        seen = {"conds": [], "help_on_revision": [], "feedback": []}
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
            pg = b.new_page()
            pg.add_init_script(MOCK)
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(self.page.as_uri())
            pg.wait_for_function("document.getElementById('savestate').className.includes('ok')")
            pg.fill("#code", code)
            pg.click("#start")
            for e in self.tr + self.eps:
                d = plan[e["uid"]]
                seen["conds"].append(pg.inner_text("#cond"))
                menu_txt = pg.inner_text("#menu")
                self.assertNotIn("[object", menu_txt)
                q0 = e["menu"][0]
                self.assertIn(q0["id"] + ": " + ", ".join(f"{k}={v}" for k, v in q0["input"].items())
                              if isinstance(q0["input"], dict) else q0["input"], menu_txt)
                self.assertNotIn("[object", pg.inner_text("#state") + pg.inner_text("#rules"))
                pg.click(f"#q_{d['query']}")
                pg.check(f"#v_{d['commit']['verdict']}")
                for c in d["commit"]["cards"]:
                    pg.check(f"#c_{c}")
                for k, v in d["commit"]["predictions"].items():
                    pg.check(f"#p{k}_{v}")
                pg.click("#commit")
                self.assertNotIn("[object", pg.inner_text("#ev") + pg.inner_text("#qres"))
                seen["help_on_revision"].append(pg.is_visible("#helpbox") and pg.inner_text("#helpbox"))
                f = d["final"]
                if f["action"] == "keep":
                    pg.click("#keep")
                else:
                    pg.check(f"#r_{f['verdict']}")
                    for c in f["cards"]:
                        pg.check(f"#rc_{c}")
                    pg.click("#revise")
                if "feedback" in e:
                    pg.wait_for_selector("#fb", state="visible")
                    seen["feedback"].append(pg.inner_text("#fbtext"))
                    pg.click("#fbnext")
            pg.wait_for_selector("#end", state="visible")
            rec = json.loads(pg.evaluate("window.__store['respostas/u-test']"))
            b.close()
        self.assertEqual(errors, [])
        return rec, seen

    def test_page_record_matches_hand_written_record(self):
        import analyse_human as AH
        worlds = AH.load_worlds()
        for code, seed in (("P1", 1), ("P2", 2)):
            plan = decisions(self.tr + self.eps, seed)
            rec, seen = self.drive(code, plan)
            hand = {"code": code, "episodes": {u: dict(d) for u, d in plan.items()}}
            a = AH.rows_for(rec, self.eps, worlds)
            h = AH.rows_for(hand, self.eps, worlds)
            strip = lambda rows: [{k: v for k, v in r.items() if k != "t_total_s"} for r in rows]  # noqa: E731
            self.assertEqual(strip(a), strip(h))
            # alternating conditions within the participant; odd codes start without help
            main = [c.split("·")[0].strip()[-1] for c in seen["conds"][len(self.tr):]]
            first = "A" if code == "P1" else "B"
            self.assertEqual(main, [first if k % 2 == 0 else ("B" if first == "A" else "A") for k in range(20)])
            self.assertEqual([r["condition"] for r in a], main)
            # help appears on the revision step exactly in condition B, and matches the precomputed evidence help
            for e, c, hv in zip(self.tr + self.eps, [s.split("·")[0].strip()[-1] for s in seen["conds"]], seen["help_on_revision"]):
                if c == "B":
                    exp = e["help"]["evidencia"][plan[e["uid"]]["query"]]
                    self.assertIn(f"Regras admissíveis (das 70): {exp['n_admissible']}", hv)
                else:
                    self.assertFalse(hv)
            self.assertEqual(len(seen["feedback"]), len(self.tr))
            for e, txt in zip(self.tr, seen["feedback"]):
                self.assertIn("era " + e["feedback"][plan[e["uid"]]["query"]]["commit"], txt)


if __name__ == "__main__":
    unittest.main()

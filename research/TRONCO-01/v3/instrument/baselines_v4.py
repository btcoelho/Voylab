"""Referências sem custo para a corrida de modelos na V4 (§15.2), nos mesmos 225 mundos e pela mesma grelha.
- aleatoria_leitor: consulta ao acaso (semente por uid), veredicto lido do próprio histórico, revisão correta.
- constante_undetermined: consulta ao acaso, compromete sempre 'undetermined', mantém sempre.
- aleatoria_total: consulta, veredicto e revisão ao acaso.
- oraculo: consultas do oráculo, veredicto próprio, revisão correta (teto).
As três primeiras foram fixadas depois de ver que M1-DS compromete quase sempre 'undetermined' (assinalado como post hoc)."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument")]
import generator_v3 as g  # noqa: E402
import grid  # noqa: E402
import planted as PL  # noqa: E402
import variants as VA  # noqa: E402
from analyse_human import wilson  # noqa: E402

R4 = ["rejected", "supported", "undetermined", "inconsistent"]


def run():
    ws, _ = VA.build("V4")
    res = {}
    for name in ("aleatoria_leitor", "constante_undetermined", "aleatoria_total", "oraculo"):
        rows = []
        for w in ws:
            rng = random.Random(f"{name}|{w['uid']}")
            q = [rng.choice(w["hidden"]["menu"])]
            if name == "oraculo":
                q = PL.oracle_queries(w)
                ep = PL.play(w, q, PL.own(w, q), PL.correct_revision)
            elif name == "aleatoria_leitor":
                ep = PL.play(w, q, PL.own(w, q), PL.correct_revision)
            elif name == "constante_undetermined":
                ep = PL.play(w, q, "undetermined", lambda c, post: c)
            else:
                ep = PL.play(w, q, rng.choice(R4[:3]), lambda c, post, r=rng: r.choice(R4))
            rows.append(grid.classify(w, ep))
        out = {}
        for t in (None, "rejected", "supported", "undetermined"):
            pool = [r for r in rows if t is None or r["target"] == t]
            k = sum(r["category"] == "fundamentado" for r in pool)
            rv = sum(r["revision_final_correct"] for r in pool)
            out[t or "total"] = {"fundamentado": [k, len(pool), wilson(k, len(pool))], "revisao": [rv, len(pool), wilson(rv, len(pool))]}
        res[name] = out
    return res


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))

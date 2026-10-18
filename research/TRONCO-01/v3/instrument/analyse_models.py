"""Análise da corrida de modelos na V4 (§15.3, §15.6, §16), escrita antes de ver resultados.

Repete cada episódio no ambiente a partir das ações aceites gravadas, classifica-o com a grelha ITT e reporta:
elegibilidade (esquema), categorias, fundamentado (Wilson), escolha de consulta (v2 escolhida vs média e melhor do menu,
diferença pareada com IC 95%), revisão final correta; tudo no total, por veredicto alvo e por estrato de qualidade.
Falhas de execução (registo do backend) são reportadas à parte e nunca entram como respostas do modelo.
"""
from __future__ import annotations

import collections
import json
import math
import statistics as st
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument"), str(V3 / "pilot")]
import env_v3 as E  # noqa: E402
import generator_v3 as g  # noqa: E402
import grid  # noqa: E402
import query_leverage as QL  # noqa: E402
from analyse_human import wilson  # noqa: E402


def mean_ci(xs):
    n = len(xs)
    if n < 2:
        return {"n": n, "mean": xs[0] if xs else None, "ci95": [None, None]}
    m, s = st.mean(xs), st.stdev(xs)
    h = 1.96 * s / math.sqrt(n)
    return {"n": n, "mean": round(m, 4), "ci95": [round(m - h, 4), round(m + h, 4)]}


def replay(world, transcript):
    ep = E.Episode(world)
    for t in transcript:
        if t.get("accepted") and "env_action" in t:
            ep.step(t["env_action"])
        elif "env_action" in t:          # rejected actions are replayed too, so the environment counts them the same way
            ep.step(t["env_action"])
    return ep


def rows(worlds_by_uid, episodes):
    out = []
    for e in episodes:
        w = worlds_by_uid[e["uid"]]
        ep = replay(w, e["transcript"])
        r = grid.classify(w, ep)
        v = QL.values(w)
        menu = {q["id"]: v[g.INPUTS.index(g.D.as_tuple(q["input"]))] for q in w["public"]["query_menu"]}
        q = next((t["env_action"].get("query_id") for t in e["transcript"]
                  if t.get("accepted") and t.get("env_action", {}).get("action") == "query"), None)
        out.append({"uid": e["uid"], "target": w["reference"]["target_verdict"],
                    "quality": "alta" if max(menu.values()) >= 0.80 else "baixa",
                    "category": r["category"], "fundamentado": r["category"] == "fundamentado",
                    "revision_final_correct": bool(r["revision_final_correct"]),
                    "query": q, "q_value": menu.get(q), "q_mean": st.mean(menu.values()), "q_best": max(menu.values()),
                    "complete": e["result"].get("complete", False)})
    return out


def block(rs):
    n = len(rs)
    if not n:
        return {"n": 0}
    k = sum(r["fundamentado"] for r in rs)
    rv = sum(r["revision_final_correct"] for r in rs)
    qs = [r for r in rs if r["q_value"] is not None]
    return {"n": n, "categorias": dict(collections.Counter(r["category"] for r in rs)),
            "fundamentado": {"k": k, "n": n, "ic95": wilson(k, n)},
            "revisao_final_correta": {"k": rv, "n": n, "ic95": wilson(rv, n)},
            "consultas_feitas": len(qs),
            "consulta_menos_media": mean_ci([r["q_value"] - r["q_mean"] for r in qs]),
            "consulta_menos_melhor": mean_ci([r["q_value"] - r["q_best"] for r in qs])}


def analyse(run_dir: Path, worlds) -> dict:
    eps = [json.loads(l) for l in (run_dir / "episodes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    turns = [t for e in eps for t in e["transcript"]]
    parsed, accepted = sum(t["parsed"] for t in turns), sum(t["accepted"] for t in turns)
    rs = rows({w["uid"]: w for w in worlds}, eps)
    elig = {"respostas_json": {"k": parsed, "n": len(turns), "ic95": wilson(parsed, len(turns))},
            "acoes_aceites": {"k": accepted, "n": len(turns), "ic95": wilson(accepted, len(turns))},
            "invalidas_taxa": round(1 - accepted / len(turns), 4) if turns else None,
            "elegivel": bool(turns) and parsed / len(turns) >= 0.98 and (1 - accepted / len(turns)) <= 0.01}
    out = {"episodios": len(eps), "elegibilidade": elig, "total": block(rs),
           "por_alvo": {t: block([r for r in rs if r["target"] == t]) for t in ("rejected", "supported", "undetermined")},
           "por_qualidade": {q: block([r for r in rs if r["quality"] == q]) for q in ("alta", "baixa")},
           "por_alvo_e_qualidade": {f"{t}|{q}": block([r for r in rs if r["target"] == t and r["quality"] == q])
                                    for t in ("rejected", "supported", "undetermined") for q in ("alta", "baixa")}}
    s = run_dir / "summary.json"
    if s.exists():
        d = json.loads(s.read_text(encoding="utf-8"))
        out["execucao"] = {"modelos_servidos": d.get("models_served"), "registo_execucao": d.get("execution_log")}
    return out


if __name__ == "__main__":
    import variants as VA
    ws, _ = VA.build("V4")
    print(json.dumps(analyse(Path(sys.argv[1]), ws), ensure_ascii=False, indent=1))

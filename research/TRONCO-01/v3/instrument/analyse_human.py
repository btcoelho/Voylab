"""Análise do piloto humano V4 (docs/V3_CONSULTAS.md §11 e §13). Escrita e testada antes de haver respostas.

Entrada: os episódios exportados (PILOTO_HUMANO_EPISODIOS.json) e os documentos dos participantes (um JSON por
participante, como a página os grava: {code, episodes: {uid: {query, commit, final, t_*}}}).
Cada episódio é repetido no ambiente real (env_v3.Episode) e classificado pela grelha (instrument/grid.py).
Saída: por participante, por condição (A sem ajuda, B com ajuda) e sempre também por estrato de qualidade.
"""
from __future__ import annotations

import collections
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument"), str(V3 / "pilot")]
import env_v3 as E  # noqa: E402
import generator_v3 as g  # noqa: E402
import grid  # noqa: E402
import scoring as sc  # noqa: E402

THRESH_FUND, THRESH_KAPPA = 0.80, 0.70
VERDICTS = ("rejected", "supported", "undetermined")


def condition(code: str, ep_set: str) -> str:
    """Odd codes (P1, P3): set X without help (A), Y with help (B); even codes the opposite."""
    n = int(code.strip().upper().lstrip("P"))
    without = "X" if n % 2 == 1 else "Y"
    return "A" if ep_set == without else "B"


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def kappa_ci(pairs, B=2000, seed=7):
    if len(pairs) < 2:
        return [None, None]
    rng = random.Random(seed)
    ks = sorted(k for k in (kappa([rng.choice(pairs) for _ in pairs]) for _ in range(B)) if k is not None)
    return [round(ks[int(0.025 * len(ks))], 3), round(ks[int(0.975 * len(ks)) - 1], 3)]


def read(lo, hi, thr):
    if lo is None:
        return "sem dados"
    return "passa" if lo >= thr else ("falha" if hi < thr else "inconclusivo")


def replay(world, rec):
    ep = E.Episode(world)
    if rec.get("query"):
        ep.step({"action": "query", "query_id": rec["query"]})
    c = rec.get("commit")
    if c:
        ep.step({"action": "commit", "verdict": c["verdict"], "admissible_cards": c.get("cards", []),
                 "predictions": {k: v for k, v in (c.get("predictions") or {}).items() if v in ("0", "1")}})
    f = rec.get("final")
    if f:
        if f["action"] == "keep":
            ep.step({"action": "keep"})
        else:
            ep.step({"action": "revise", "verdict": f["verdict"], "admissible_cards": f.get("cards", [])})
    return ep


def rows_for(participant: dict, episodes: list, worlds_by_uid: dict) -> list[dict]:
    out = []
    for e in episodes:
        rec = participant.get("episodes", {}).get(e["uid"], {})
        w = worlds_by_uid[e["uid"]]
        ep = replay(w, rec)
        r = grid.classify(w, ep)
        own = None
        if ep.committed is not None:
            hid = w["hidden"]
            own = g.verdict(g.admissible_idx(sc.history_rows(w, ep.queried)), hid["w"], hid["T"])
        v2 = {m["id"]: m["value2"] for m in e["menu"]}
        q = rec.get("query")
        out.append({"uid": e["uid"], "n": e["n"], "condition": condition(participant["code"], e["set"]),
                    "quality": "alta" if e["quality_hi"] else "baixa", "target": e["target"],
                    "category": r["category"], "fundamentado": r["category"] == "fundamentado",
                    "committed": r.get("committed"), "own": own, "revision_final_correct": r["revision_final_correct"],
                    "query_value": v2.get(q), "query_best": max(v2.values()), "query_mean": st.mean(v2.values()),
                    "t_total_s": (rec.get("t_total_ms") or 0) / 1000 or None})
    return out


def summary(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}
    k = sum(r["fundamentado"] for r in rows)
    lo, hi = wilson(k, n)
    pairs = [(r["committed"], r["own"]) for r in rows if r["committed"] is not None]
    kp = kappa(pairs)
    klo, khi = kappa_ci(pairs)
    qv = [r for r in rows if r["query_value"] is not None]
    times = [r["t_total_s"] for r in rows if r["t_total_s"]]
    return {"n": n, "categories": dict(collections.Counter(r["category"] for r in rows)),
            "fundamentado": [k, n], "fundamentado_ic95": [lo, hi], "leitura_fundamentado": read(lo, hi, THRESH_FUND),
            "concordancia_simples_vs_referencia": [sum(a == b for a, b in pairs), len(pairs)],
            "kappa_vs_referencia": None if kp is None else round(kp, 3), "kappa_ic95": [klo, khi],
            "leitura_kappa": read(klo, khi, THRESH_KAPPA),
            "revisao_final_correta": [sum(r["revision_final_correct"] for r in rows), n],
            "consulta_acima_da_media": [sum(r["query_value"] > r["query_mean"] for r in qv), len(qv)],
            "consulta_valor_medio_escolhido": round(st.mean(r["query_value"] for r in qv), 3) if qv else None,
            "consulta_valor_medio_menu": round(st.mean(r["query_mean"] for r in qv), 3) if qv else None,
            "consulta_valor_medio_melhor": round(st.mean(r["query_best"] for r in qv), 3) if qv else None,
            "tempo_mediano_s": round(st.median(times), 1) if times else None}


def analyse(episodes, participants, worlds_by_uid) -> dict:
    allrows = []
    per = {}
    for p in participants:
        rows = rows_for(p, episodes, worlds_by_uid)
        allrows += [dict(r, code=p["code"]) for r in rows]
        per[p["code"]] = {f"cond_{c}": {"todos": summary([r for r in rows if r["condition"] == c]),
                                        **{f"qualidade_{q}": summary([r for r in rows if r["condition"] == c and r["quality"] == q])
                                           for q in ("alta", "baixa")}} for c in "AB"}
    pooled = {f"cond_{c}": {"todos": summary([r for r in allrows if r["condition"] == c]),
                            **{f"qualidade_{q}": summary([r for r in allrows if r["condition"] == c and r["quality"] == q])
                               for q in ("alta", "baixa")}} for c in "AB"}
    inter = {}
    codes = [p["code"] for p in participants]
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            a = {r["uid"]: r for r in allrows if r["code"] == codes[i]}
            b = {r["uid"]: r for r in allrows if r["code"] == codes[j]}
            pairs = [(a[u]["committed"], b[u]["committed"]) for u in a if u in b and a[u]["committed"] and b[u]["committed"]]
            same = sum(a[u]["condition"] == b[u]["condition"] for u in a if u in b)
            inter[f"{codes[i]}|{codes[j]}"] = {"kappa": None if not pairs else round(kappa(pairs), 3), "n": len(pairs),
                                              "concordancia_simples": sum(a == b for a, b in pairs),
                                              "episodios_mesma_condicao": same}
    return {"por_participante": per, "agregado": pooled, "kappa_entre_pessoas": inter, "linhas": allrows}


def load_worlds():
    import variants as VA
    ws, _ = VA.build("V4")
    return {w["uid"]: w for w in ws}


if __name__ == "__main__":
    eps = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    parts = [json.loads(Path(f).read_text(encoding="utf-8")) for f in sys.argv[2:]]
    print(json.dumps(analyse(eps, parts, load_worlds()), ensure_ascii=False, indent=1))

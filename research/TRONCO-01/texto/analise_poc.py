"""Análise da prova de conceito (§9). Escrita antes de ver os resultados do agente."""
import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "resultados" / "poc"
FAM = ["LN", "SUB", "POL", "TRA", "VER", "NUL", "BAR", "TAB", "ALE"]


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def main():
    regra = {r["uid"]: r for r in json.loads((OUT / "regra.json").read_text())}
    eps = [json.loads(l) for l in (OUT / "episodios.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    n = len(eps)
    validos = [e for e in eps if e["relatorio"] is not None]
    ac_ag = sum(1 for e in eps if e["pontuacao"].get("acerto"))
    ac_rg = sum(1 for e in eps if regra[e["uid"]]["regra"] == e["familia"])
    afs = [x for e in validos for x in e["relatorio"].get("_verificacao", []) if not x["interpretacao"]]
    falsas = sum(1 for x in afs if x["verdadeira"] is False)
    afs_r0 = sum(e["log"]["rondas"][0]["afirmacoes"] for e in validos if e["log"]["rondas"])
    falsas_r0 = sum(len(e["log"]["rondas"][0]["falsas"]) for e in validos if e["log"]["rondas"])
    rej = sum(1 for e in eps if e["pontuacao"].get("verdadeira_rejeitada"))
    por = {}
    for f in FAM:
        es = [e for e in eps if e["familia"] == f]
        a = sum(1 for e in es if e["pontuacao"].get("acerto"))
        r = sum(1 for e in es if regra[e["uid"]]["regra"] == f)
        por[f] = {"n": len(es), "agente": a, "regra": r,
                  "agente_disse": dict(Counter(str(e["pontuacao"].get("mais_provavel")) for e in es)),
                  "regra_disse": dict(Counter(regra[e["uid"]]["regra"] for e in es))}
    med = Counter(m for e in eps for m in e["log"]["medidas"])
    res = {"episodios": n, "relatorios_validos": [len(validos), n, wilson(len(validos), n)],
           "erros": dict(Counter(e["log"]["erro"] for e in eps if e["log"]["erro"])),
           "acerto_agente": [ac_ag, n, wilson(ac_ag, n)], "acerto_regra": [ac_rg, n, wilson(ac_rg, n)],
           "indeterminada_agente": sum(1 for e in eps if e["pontuacao"].get("mais_provavel") == "indeterminada"),
           "afirmacoes_numericas_finais": len(afs), "falsas_finais": [falsas, len(afs), wilson(falsas, len(afs))],
           "falsas_primeira_ronda": [falsas_r0, afs_r0],
           "verdadeira_rejeitada": [rej, n], "medidas_pedidas": dict(med.most_common()),
           "medidas_por_episodio": round(sum(len(e["log"]["medidas"]) for e in eps) / n, 2) if n else None,
           "por_familia": por}
    (OUT / "ANALISE.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

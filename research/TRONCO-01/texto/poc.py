"""Prova de conceito TEXTO-01 (docs/TEXTO_ESPECIFICACAO.md §9).

8 obras do Perseus (4 latim, 4 inglês) × 9 famílias = 72 amostras de 2000 palavras. Para cada amostra: a regra simples
(fixada antes de ver qualquer medida) e o agente DeepSeek. Retoma por amostra (episodes.jsonl).
Uso: python poc.py --build | --regra | --run | --analise
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "v3" / "pilot"), str(HERE.parent / "v3" / "instrument")]
import agente as A  # noqa: E402
import medidas as M  # noqa: E402
import transformacoes as T  # noqa: E402

SRC = Path("/tmp/claude-0/-home-claude/51d32a62-a497-52d7-81e7-d806958770e0/scratchpad/perseus")
OUT = HERE / "resultados" / "poc"
FAMILIAS = ["LN", "SUB", "POL", "TRA", "VER", "NUL", "BAR", "TAB", "ALE"]
N_PALAVRAS = 2000
OBRAS = {"phi0448.phi001.perseus-lat2.xml": "la", "phi0474.phi013.perseus-lat2.xml": "la",
         "phi0959.phi006.perseus-lat2.xml": "la", "phi0690.phi003.perseus-lat2.xml": "la",
         "phi0448.phi001.perseus-eng2.xml": "en", "tlg0012.tlg001.perseus-eng3.xml": "en",
         "tlg0012.tlg002.perseus-eng3.xml": "en", "tlg0016.tlg001.perseus-eng2.xml": "en"}


def texto_simples(path, semente):
    x = path.read_text(encoding="utf-8")
    x = x[x.find("<body"):] if "<body" in x else x
    x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    x = re.sub(r"<[^>]+>", " ", x)
    x = re.sub(r"&[a-z]+;", " ", x).lower()
    ws = [w for w in re.sub(r"[^a-z]+", " ", x).split() if w]
    rng = random.Random(semente)
    i = rng.randrange(0, max(1, len(ws) - N_PALAVRAS))
    return [list(w) for w in ws[i:i + N_PALAVRAS]]


def nulos_em_palavras(words, semente, taxa=0.12):
    """Nulos clássicos: glifos do próprio alfabeto inseridos dentro das palavras, sobre uma substituição."""
    sub, _ = T.substituicao(words, semente)
    rng = random.Random(semente + 1)
    alfa = sorted({g for w in sub for g in w})
    out = []
    for w in sub:
        nw = []
        for g in w:
            if rng.random() < taxa:
                nw.append(rng.choice(alfa))
            nw.append(g)
        out.append(nw)
    return out


def tabela(comprimentos_n, semente):
    """Gerador por tabela (inspirado em Rugg): prefixo + meio + sufixo escolhidos por uma grelha que avança;
    palavras sem significado, com estrutura interna forte."""
    rng = random.Random(semente)
    letras = list("abcdefghiklmnopqrstu")

    def silabas(k, a, b):
        return ["".join(rng.choice(letras) for _ in range(rng.randint(a, b))) for _ in range(k)]
    pre, mei, suf = silabas(12, 1, 2), silabas(12, 1, 2) + [""] * 4, silabas(12, 1, 2)
    out, pos = [], 0
    for _ in range(comprimentos_n):
        pos = (pos + rng.choice([1, 2, 3, 5])) % 12
        w = pre[pos] + mei[(pos * 7 + rng.randrange(3)) % len(mei)] + suf[(pos * 5 + rng.randrange(4)) % 12]
        out.append(list(w))
    return out


def amostra(words, familia, semente):
    if familia == "LN":
        return words
    if familia == "SUB":
        return T.substituicao(words, semente)[0]
    if familia == "POL":
        return T.vigenere(words, semente)[0]
    if familia == "TRA":
        return T.transposicao(words, semente)[0]
    if familia == "VER":
        return T.verbosa(words, semente)[0]
    if familia == "NUL":
        return nulos_em_palavras(words, semente)
    if familia == "BAR":
        return T.baralhar_palavras(words, semente)[0]
    if familia == "TAB":
        return tabela(len(words), semente)
    if familia == "ALE":
        return T.ao_acaso([len(w) for w in words], semente)[0]
    raise ValueError(familia)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for k, (obra, lang) in enumerate(sorted(OBRAS.items())):
        plain = texto_simples(SRC / obra, 1000 + k)
        for j, fam in enumerate(FAMILIAS):
            s = 7000 + 100 * k + j
            rows.append({"uid": f"{k}-{fam}", "obra": obra, "lingua": lang, "familia": fam, "semente": s,
                         "palavras": ["".join(w) for w in amostra(plain, fam, s)]})
    with (OUT / "amostras.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "amostras", Counter(r["familia"] for r in rows))


def carregar():
    return [json.loads(l) for l in (OUT / "amostras.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


LETRAS_FREQ = set("etaoinsrhul")   # letras mais frequentes de latim e inglês (conhecimento de referência)


def regra(words):
    """Referência por limiares fixos, escrita antes de ver as medidas das amostras."""
    e, ic = M.entropia(words), M.coincidencia(words)
    alfa = M.alfabeto(words)
    dep = M.dependencia(words, permutacoes=50)
    z = M.zipf(words)
    top6 = {g for g, _ in alfa["top10"][:6]}
    if alfa["glifos_distintos"] <= 10:
        return "VER" if e["h2_palavra"] < e["h1"] - 0.3 else "ALE"
    if ic["ic"] < 0.05:
        return "POL"
    if e["h2_fluxo"] > e["h1"] - 0.25:
        return "TRA"
    if dep["p_empirico"] > 0.05:
        return "TAB" if (z["declive"] is not None and z["declive"] > -0.7) else "BAR"
    if len(top6 & LETRAS_FREQ) >= 5:
        return "LN"
    return "NUL" if ic["ic"] < 0.058 else "SUB"


def run_regra():
    res = []
    for r in carregar():
        w = [list(x) for x in r["palavras"]]
        res.append({"uid": r["uid"], "familia": r["familia"], "regra": regra(w)})
    (OUT / "regra.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    ok = sum(x["familia"] == x["regra"] for x in res)
    print("regra:", ok, "/", len(res))


def run_agente(workers=4, bateria=False, subconjunto=None, nome="episodios.jsonl"):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from deepseek_backend import DeepSeekBackend
    ep = OUT / nome
    done = {json.loads(l)["uid"] for l in ep.read_text(encoding="utf-8").splitlines() if l.strip()} if ep.exists() else set()
    lock = threading.Lock()

    def one(r):
        b = DeepSeekBackend("deepseek-chat", 0.0, 2048)
        w = [list(x) for x in r["palavras"]]
        try:
            rel, log = A.Analista(b, max_medidas=8, bateria=bateria).analisar(w)
        except Exception as ex:  # noqa: BLE001  falha de execução: registada à parte, a amostra fica por fazer
            with lock, (OUT / "falhas_execucao.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"uid": r["uid"], "erro": repr(ex)[:300]}) + "\n")
            return
        rec = {"uid": r["uid"], "familia": r["familia"], "relatorio": rel, "log": log,
               "pontuacao": A.pontuar(rel, r["familia"])}
        with lock, ep.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    with ThreadPoolExecutor(workers) as ex:
        rs = [r for r in carregar() if r["uid"] not in done and (subconjunto is None or r["uid"].split("-")[0] in subconjunto)]
        list(ex.map(one, rs))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--regra", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--bateria", action="store_true", help="§9.2: 18 amostras (obras 0 e 1), bateria completa")
    ap.add_argument("--programa", action="store_true", help="§9.3")
    a = ap.parse_args()
    if a.build:
        build()
    if a.regra:
        run_regra()
    if a.run:
        run_agente()
    if a.bateria:
        run_agente(bateria=True, subconjunto={"0", "1"}, nome="episodios_bateria.jsonl")


def run_programa(workers=4, subconjunto=("0", "1"), nome="episodios_programa.jsonl"):
    """§9.3: o modelo escreve classificar(m); o código executa-a e avalia as justificações."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    import programa as P
    from deepseek_backend import DeepSeekBackend
    ep = OUT / nome
    done = {json.loads(l)["uid"] for l in ep.read_text(encoding="utf-8").splitlines() if l.strip()} if ep.exists() else set()
    lock = threading.Lock()

    def one(r):
        try:
            rel, log = P.Programador(DeepSeekBackend("deepseek-chat", 0.0, 2048)).analisar([list(x) for x in r["palavras"]])
        except Exception as ex:  # noqa: BLE001
            with lock, (OUT / "falhas_execucao.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"uid": r["uid"], "modo": "programa", "erro": repr(ex)[:300]}) + "\n")
            return
        with lock, ep.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"uid": r["uid"], "familia": r["familia"], "relatorio": rel, "log": log,
                                 "acerto": bool(rel) and rel.get("mais_provavel") == r["familia"]},
                                ensure_ascii=False) + "\n")
    rs = [r for r in carregar() if r["uid"] not in done and r["uid"].split("-")[0] in subconjunto]
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, rs))


if __name__ == "__main__" and "--programa" in sys.argv:
    run_programa()

"""Medidas linguísticas determinísticas (docs/TEXTO_ESPECIFICACAO.md §3).

Entrada: uma lista de palavras, cada uma uma lista de glifos (strings). Sem dependências externas.
Nenhuma função lê verdade escondida; todas devolvem números com os parâmetros usados.
"""
from __future__ import annotations

import math
import random
from collections import Counter
from itertools import combinations

VOWELS_HINT = None  # Sukhotin não usa pistas externas


def flat(words):
    return [g for w in words for g in w]


def _entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c) if n else 0.0


def alfabeto(words):
    c = Counter(flat(words))
    n = sum(c.values())
    top = c.most_common(10)
    return {"glifos_distintos": len(c), "ocorrencias": n,
            "top10": [[g, k] for g, k in top],
            "cobertura_top10": round(sum(k for _, k in top) / n, 4) if n else None}


def entropia(words):
    """h0 (glifo), h1 (glifo), h2 condicional (glifo dado o anterior dentro da palavra e no fluxo)."""
    seq = flat(words)
    h0 = math.log2(len(set(seq))) if seq else 0.0   # máximo para o alfabeto observado
    h1 = _entropy(Counter(seq))
    pairs_in = Counter()
    for w in words:
        pairs_in.update(zip(w, w[1:]))
    pairs_flow = Counter(zip(seq, seq[1:]))
    firsts_in = Counter(g for w in words for g in w[:-1])
    firsts_flow = Counter(seq[:-1])
    h2_in = _cond(pairs_in, firsts_in)
    h2_flow = _cond(pairs_flow, firsts_flow)
    return {"h0": round(h0, 4), "h1": round(h1, 4), "h2_palavra": round(h2_in, 4), "h2_fluxo": round(h2_flow, 4)}


def _cond(pairs, firsts):
    n = sum(pairs.values())
    if not n:
        return 0.0
    return -sum(c / n * math.log2(c / firsts[a]) for (a, _), c in pairs.items() if c)


def coincidencia(words):
    """Índice de coincidência global e por período (Friedman, 1..20 para o período mais provável)."""
    seq = flat(words)
    return {"ic": round(_ic(seq), 4), "uniforme_ic": round(1 / max(1, len(set(seq))), 4),
            "ic_por_periodo": {p: round(_ic_period(seq, p), 4) for p in range(1, 21)}}


def _ic(seq):
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return sum(k * (k - 1) for k in c.values()) / (n * (n - 1))


def _ic_period(seq, p):
    vals = []
    for r in range(p):
        sub = seq[r::p]
        if len(sub) >= 2:
            vals.append(_ic(sub))
    return sum(vals) / len(vals) if vals else 0.0


def kasiski(words, n=3, top=5):
    """Distâncias entre trigramas repetidos e os divisores mais frequentes dessas distâncias."""
    seq = flat(words)
    pos = {}
    for i in range(len(seq) - n + 1):
        pos.setdefault(tuple(seq[i:i + n]), []).append(i)
    dists = []
    for ps in pos.values():
        for a, b in zip(ps, ps[1:]):
            dists.append(b - a)
    div = Counter()
    for d in dists:
        for k in range(2, 31):
            if d % k == 0:
                div[k] += 1
    return {"distancias": len(dists), "divisores_mais_frequentes": div.most_common(top)}


def palavras(words):
    lens = [len(w) for w in words]
    n = len(lens)
    cw = Counter(tuple(w) for w in words)
    return {"n_palavras": n, "comprimento_medio": round(sum(lens) / n, 4) if n else None,
            "tipos": len(cw), "hapax": sum(1 for v in cw.values() if v == 1),
            "razao_tipo_token": round(len(cw) / n, 4) if n else None}


def zipf(words):
    """Declive e R² da reta de log(frequência) contra log(posição) (Zipf). Língua natural ≈ −1."""
    c = sorted(Counter(tuple(w) for w in words).values(), reverse=True)
    if len(c) < 3:
        return {"declive": None, "r2": None}
    xs = [math.log(i + 1) for i in range(len(c))]
    ys = [math.log(v) for v in c]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    r2 = (sxy * sxy) / (sxx * syy) if syy else 0.0
    return {"declive": round(slope, 4), "r2": round(r2, 4)}


def posicional(words, top=15):
    """Por glifo (os `top` mais frequentes): fração em início, meio e fim de palavra (palavras de comprimento ≥ 2)."""
    cnt = {}
    for w in words:
        if len(w) < 2:
            continue
        for i, g in enumerate(w):
            k = "inicio" if i == 0 else "fim" if i == len(w) - 1 else "meio"
            cnt.setdefault(g, Counter())[k] += 1
    out = {}
    for g, c in sorted(cnt.items(), key=lambda x: -sum(x[1].values()))[:top]:
        n = sum(c.values())
        if n >= 20:
            out[g] = {k: round(c[k] / n, 4) for k in ("inicio", "meio", "fim")}
    return out


def repeticoes(words, dist_max=1):
    """Palavras repetidas seguidas; pares de palavras distintas a distância de edição ≤ dist_max; trigramas repetidos."""
    seq = flat(words)
    seguidas = sum(1 for a, b in zip(words, words[1:]) if a == b)
    quase = 0
    tipos = list({tuple(w) for w in words})
    for a, b in combinations(tipos, 2):
        if abs(len(a) - len(b)) <= dist_max and _edit(a, b) <= dist_max:
            quase += 1
    tri = Counter(tuple(seq[i:i + 3]) for i in range(len(seq) - 2))
    return {"palavras_repetidas_seguidas": seguidas, "pares_quase_iguais": quase,
            "trigramas_repetidos": sum(1 for v in tri.values() if v > 1)}


def _edit(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def _mi(pairs):
    n = len(pairs)
    if not n:
        return 0.0
    pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pab = Counter(pairs)
    return sum(c / n * math.log2((c / n) / ((pa[a] / n) * (pb[b] / n))) for (a, b), c in pab.items())


def dependencia(words, permutacoes=100, semente=0):
    """Informação mútua entre o último glifo de uma palavra e o primeiro da seguinte, e entre palavras consecutivas,
    comparada com a mesma medida após baralhar as palavras (semente fixa)."""
    ult_prim = [(w[-1], v[0]) for w, v in zip(words, words[1:]) if w and v]
    real = _mi(ult_prim)
    rng = random.Random(semente)
    ws = list(words)
    base = []
    for _ in range(permutacoes):
        rng.shuffle(ws)
        base.append(_mi([(w[-1], v[0]) for w, v in zip(ws, ws[1:]) if w and v]))
    base.sort()
    acima = sum(1 for b in base if b >= real)
    return {"mi_fronteira": round(real, 4), "mi_baralhado_media": round(sum(base) / len(base), 4),
            "p_empirico": round((acima + 1) / (len(base) + 1), 4), "permutacoes": permutacoes}


def sukhotin(words, iteracoes=20):
    """Heurística inspirada em Sukhotin (1962), NÃO é o algoritmo original completo: classifica como vogal
    o glifo com mais adjacências com os restantes, e recalcula retirando-o; é uma pista de estrutura silábica
    e só aparece como medida descritiva. Correspondência ao original fica por verificar com testes."""
    letters = sorted(set(flat(words)))
    idx = {g: i for i, g in enumerate(letters)}
    m = [[0] * len(letters) for _ in letters]
    for w in words:
        for a, b in zip(w, w[1:]):
            if a != b:
                m[idx[a]][idx[b]] += 1
                m[idx[b]][idx[a]] += 1
    remaining = set(range(len(letters)))
    vowels = []
    for _ in range(min(iteracoes, len(letters))):
        if not remaining:
            break
        h = {i: sum(m[i][j] for j in remaining) for i in remaining}
        pick = max(sorted(remaining), key=lambda i: h[i])
        if h[pick] == 0:
            break
        vowels.append(letters[pick])
        remaining.discard(pick)
    return {"vogais_candidatas": sorted(vowels), "letras": len(letters),
            "nota": "heuristica inspirada em Sukhotin; nao e o algoritmo original completo"}


def perfil(words, referencia):
    """Distância de Jensen-Shannon entre a distribuição de glifos ordenada e uma referência já ordenada
    (lista de frequências relativas). Invariante a substituição: diz quão parecido é o perfil, não quais os glifos."""
    c = sorted(Counter(flat(words)).values(), reverse=True)
    n = sum(c)
    p = [v / n for v in c]
    k = max(len(p), len(referencia))
    p = p + [0.0] * (k - len(p))
    q = sorted(referencia, reverse=True) + [0.0] * (k - len(referencia))
    m = [(a + b) / 2 for a, b in zip(p, q)]

    def kl(x, y):
        return sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)
    return {"js": round(0.5 * kl(p, m) + 0.5 * kl(q, m), 6)}


def tudo(words, referencia=None):
    out = {"alfabeto": alfabeto(words), "entropia": entropia(words), "coincidencia": coincidencia(words),
           "kasiski": kasiski(words), "palavras": palavras(words), "zipf": zipf(words),
           "posicional": posicional(words), "repeticoes": repeticoes(words), "dependencia": dependencia(words),
           "sukhotin": sukhotin(words), "gaskell": gaskell(words), "amancio": amancio(words)}
    if referencia is not None:
        out["perfil"] = perfil(words, referencia)
    return out


def gaskell(words):
    """Subconjunto das métricas de Gaskell & Bowern 2022 (CEUR Vol-3313, paper4): comprimento de palavra
    (média, desvio, assimetria, autocorrelação lag 1), compressão (zlib) e palavras repetidas seguidas."""
    import zlib
    lens = [len(w) for w in words]
    n = len(lens)
    m = sum(lens) / n
    sd = (sum((x - m) ** 2 for x in lens) / n) ** 0.5
    skew = (sum((x - m) ** 3 for x in lens) / n) / sd ** 3 if sd else 0.0
    ac = (sum((a - m) * (b - m) for a, b in zip(lens, lens[1:])) / (n - 1)) / sd ** 2 if sd and n > 1 else 0.0
    raw = " ".join("".join(w) for w in words).encode()
    return {"wordlen_media": round(m, 4), "wordlen_desvio": round(sd, 4), "wordlen_assimetria": round(skew, 4),
            "wordlen_autocorr": round(ac, 4), "compressao": round(len(zlib.compress(raw, 9)) / len(raw), 4),
            "palavras_repetidas_seguidas": sum(1 for a, b in zip(words, words[1:]) if a == b)}


def amancio(words, versoes=10, semente=0):
    """Normalização de Amancio et al. 2013 (arXiv 1303.0347): medida real a dividir pela média de versões com as
    palavras baralhadas. Perto de 1 = a ordem das palavras não traz informação. Medidas: bigramas de palavras
    repetidos e entropia condicional da palavra seguinte."""
    def stats(ws):
        bi = Counter(zip(map(tuple, ws), map(tuple, ws[1:])))
        rep = sum(1 for v in bi.values() if v > 1)
        first = Counter(map(tuple, ws[:-1]))
        h = _cond(bi, first)
        return rep, h
    rep, h = stats(words)
    rng = random.Random(semente)
    ws = list(words)
    rs, hs = [], []
    for _ in range(versoes):
        rng.shuffle(ws)
        a, b = stats(ws)
        rs.append(a)
        hs.append(b)
    mr, mh = sum(rs) / versoes, sum(hs) / versoes
    return {"bigramas_repetidos_razao": round(rep / mr, 4) if mr else None,
            "h_palavra_seguinte_razao": round(h / mh, 4) if mh else None}

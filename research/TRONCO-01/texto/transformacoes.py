"""Famílias de transformação com chave conhecida (docs/TEXTO_ESPECIFICACAO.md §6).

Cada função recebe texto simples (lista de palavras, cada uma lista de letras) e devolve (palavras cifradas, metadados).
Os metadados (chave, família, semente) são para o avaliador; o agente só vê as palavras cifradas.
Todas as transformações são invertíveis pelo respetivo `decifra_*`, testado nos testes.
"""
from __future__ import annotations

import random
import string

ALPHA = list(string.ascii_lowercase)


def flat(words):
    return [g for w in words for g in w]


def substituicao(words, semente):
    rng = random.Random(semente)
    perm = ALPHA[:]
    rng.shuffle(perm)
    key = dict(zip(ALPHA, perm))
    out = [[key.get(g, g) for g in w] for w in words]
    return out, {"familia": "SUB", "chave": key}


def decifra_substituicao(words, key):
    inv = {v: k for k, v in key.items()}
    return [[inv.get(g, g) for g in w] for w in words]


def vigenere(words, semente, periodo=None):
    rng = random.Random(semente)
    p = periodo or rng.randint(3, 12)
    k = [rng.randrange(26) for _ in range(p)]
    seq = flat(words)
    cif = [ALPHA[(ALPHA.index(g) + k[i % p]) % 26] for i, g in enumerate(seq)]
    return _reflow(cif, words), {"familia": "POL", "periodo": p, "chave": k}


def decifra_vigenere(words, k):
    seq = flat(words)
    dec = [ALPHA[(ALPHA.index(g) - k[i % len(k)]) % 26] for i, g in enumerate(seq)]
    return _reflow(dec, words)


def transposicao(words, semente, colunas=None):
    """Transposição colunar sobre o fluxo de letras; as fronteiras de palavra são reaplicadas aos comprimentos originais."""
    rng = random.Random(semente)
    seq = flat(words)
    c = colunas or rng.randint(3, 7)
    perm = list(range(c))
    rng.shuffle(perm)
    rows = [seq[i:i + c] for i in range(0, len(seq), c)]
    cols = [[r[j] for r in rows if j < len(r)] for j in range(c)]
    cif = [g for j in perm for g in cols[j]]
    return _reflow(cif, words), {"familia": "TRA", "colunas": c, "ordem": perm}


def decifra_transposicao(words, colunas, perm):
    seq = flat(words)
    n = len(seq)
    rows = (n + colunas - 1) // colunas
    lens = [len(range(j, n, colunas)) for j in range(colunas)]
    cols_lens = [lens[j] for j in perm]
    cols_seq = {}
    pos = 0
    for j, L in zip(perm, cols_lens):
        cols_seq[j] = seq[pos:pos + L]
        pos += L
    dec = []
    for r in range(rows):
        for j in range(colunas):
            if r < len(cols_seq[j]):
                dec.append(cols_seq[j][r])
    return _reflow(dec, words)


def nulos(words, semente, taxa=0.1):
    """Insere glifos nulos (letra fixa 'x') em posições aleatórias; metadados guardam as posições."""
    rng = random.Random(semente)
    seq = flat(words)
    out, pos = [], []
    for g in seq:
        if rng.random() < taxa:
            pos.append(len(out))
            out.append("x")
        out.append(g)
    lens = [len(w) for w in words]
    return _reflow_lens(out, lens), {"familia": "NUL", "taxa": taxa, "posicoes": pos, "comprimentos": lens}


def decifra_nulos(words, posicoes, comprimentos):
    """Remove as posições dos nulos e reparte pelos comprimentos originais das palavras."""
    seq = flat(words)
    drop = set(posicoes)
    keep = [g for i, g in enumerate(seq) if i not in drop]
    return _reflow_lens(keep, comprimentos)


def verbosa(words, semente):
    """Cifra verbosa: cada letra vira 1 a 3 glifos (tabela fixa)."""
    rng = random.Random(semente)
    tab = {g: [rng.choice(["a", "b", "c", "d", "e", "f"]) for _ in range(rng.randint(1, 3))] for g in ALPHA}
    out = []
    for w in words:
        nw = []
        for g in w:
            nw += tab.get(g, [g])
        out.append(nw)
    return out, {"familia": "VER", "tabela": tab}


def baralhar_palavras(words, semente):
    rng = random.Random(semente)
    ws = [list(w) for w in words]
    rng.shuffle(ws)
    return ws, {"familia": "BAR"}


def ao_acaso(comprimentos, semente):
    rng = random.Random(semente)
    return [[rng.choice(ALPHA[:8]) for _ in range(L)] for L in comprimentos], {"familia": "ALE"}


def _reflow(seq, words):
    return _reflow_lens(seq, [len(w) for w in words])


def _reflow_lens(seq, lens):
    out, i = [], 0
    for L in lens:
        out.append(list(seq[i:i + L]))
        i += L
    if i < len(seq):
        out.append(list(seq[i:]))
    return out

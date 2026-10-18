"""Partições por grupo de estrutura (mecanismo oculto + carta W): cada grupo vai inteiro para uma só partição.

A atribuição é determinística por hash(sal | grupo), sem olhar para resultados. O sal da partição cega será a ronda
drand anunciada no congelamento; aqui só se define e testa o mecanismo (nenhuma partição cega é gerada).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3)]
import generator_v3 as g  # noqa: E402


def assign(group: str, salt: str, fractions: dict[str, float]) -> str:
    u = int(hashlib.sha256(f"{salt}|{group}".encode()).hexdigest()[:12], 16) / 16 ** 12
    acc = 0.0
    for name, f in fractions.items():
        acc += f
        if u < acc:
            return name
    return list(fractions)[-1]


def partition(worlds, salt: str, fractions: dict[str, float]) -> dict[str, list]:
    if abs(sum(fractions.values()) - 1) > 1e-9:
        raise ValueError("fractions must sum to 1")
    out = {k: [] for k in fractions}
    for w in worlds:
        out[assign(g.structure_group(w), salt, fractions)].append(w)
    return out


def crossing_groups(parts: dict[str, list]) -> set[str]:
    seen, bad = {}, set()
    for name, ws in parts.items():
        for w in ws:
            k = g.structure_group(w)
            if seen.setdefault(k, name) != name:
                bad.add(k)
    return bad

"""Verificador de afirmações (docs/TEXTO_ESPECIFICACAO.md §4).

Uma afirmação verificável cita uma medida, os seus parâmetros e um campo, e compara com outra medida ou com um valor
fixo. O verificador recalcula tudo a partir do texto; não aceita números do modelo. Afirmações sem medida são
'interpretação' e não são pontuadas aqui.
"""
from __future__ import annotations

import medidas as M

OPS = {"<": lambda a, b: a < b, ">": lambda a, b: a > b,
       "≈": lambda a, b, tol: abs(a - b) <= tol}


def _valor(words, spec):
    fn = getattr(M, spec["medida"])
    res = fn(words, **spec.get("parametros", {})) if spec.get("parametros") else fn(words)
    cur = res
    for part in spec["campo"].split("."):
        cur = cur[part]
    return cur


def verifica(words, afirmacao):
    """Devolve dict com 'verdadeira' (bool), 'valor_a', 'valor_b' ou 'interpretacao' se não há medida."""
    if "medida" not in afirmacao:
        return {"id": afirmacao.get("id"), "interpretacao": True, "verdadeira": None}
    a = _valor(words, afirmacao)
    if "valor" in afirmacao:
        b = afirmacao["valor"]
        tol = afirmacao.get("tolerancia", 0.0)
        ok = abs(a - b) <= tol
    else:
        b = _valor(words, afirmacao["outra"])
        margem = afirmacao.get("margem", 0.0)
        op = afirmacao["op"]
        if op == "<":
            ok = a < b - margem
        elif op == ">":
            ok = a > b + margem
        else:
            raise ValueError(op)
    return {"id": afirmacao.get("id"), "interpretacao": False, "verdadeira": bool(ok), "valor_a": a, "valor_b": b}


def verifica_seguro(words, afirmacao):
    """Uma afirmação que não se consegue verificar (medida ou campo inexistente, valor não numérico) conta como
    falsa e malformada; nunca interrompe a corrida."""
    try:
        return verifica(words, afirmacao)
    except Exception as ex:  # noqa: BLE001
        return {"id": afirmacao.get("id") if isinstance(afirmacao, dict) else None, "interpretacao": False,
                "verdadeira": False, "malformada": True, "valor_a": f"não verificável ({type(ex).__name__})",
                "valor_b": afirmacao.get("valor") if isinstance(afirmacao, dict) else None}


def verifica_todas(words, afirmacoes):
    return [verifica_seguro(words, a) for a in (afirmacoes or [])]

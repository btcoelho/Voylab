"""Modo programa (docs/TEXTO_ESPECIFICACAO.md §9.3; base: Program of Thoughts, TableBench, Proof-Carrying Numbers).

O modelo recebe as medidas como um dicionário `m` de chaves planas (ids) e devolve:
  {"action":"programa", "codigo":"def classificar(m):\n    ...\n    return 'TRA'",
   "justificacao":["m['entropia.h2_fluxo'] > m['entropia.h1'] - 0.25", ...]}
O código executa `classificar(m)` num ambiente restrito (só expressões, comparações, if/return, abs/min/max/round/len);
a resposta em texto não conta. Cada justificação é uma expressão booleana avaliada pelo código (números citados
por referência, nunca copiados); as falsas voltam ao modelo, até 2 rondas.
"""
from __future__ import annotations

import ast
import json

import medidas as M

FAMILIAS = ["LN", "SUB", "POL", "TRA", "VER", "NUL", "BAR", "TAB", "ALE", "indeterminada"]
PERMITIDOS = (ast.Module, ast.Expression, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.If, ast.Compare, ast.BoolOp,
              ast.UnaryOp, ast.BinOp, ast.Name, ast.Load, ast.Store, ast.Constant, ast.Subscript, ast.Assign,
              ast.And, ast.Or, ast.Not, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq, ast.Add, ast.Sub,
              ast.Mult, ast.Div, ast.USub, ast.Call, ast.Expr, ast.IfExp, ast.Pass, ast.Index if hasattr(ast, "Index") else ast.Pass)
FUNCOES = {"abs": abs, "min": min, "max": max, "round": round, "len": len}

SYSTEM = (
    "Classificas um texto cifrado numa de 9 famílias: LN (língua natural), SUB (substituição simples), POL "
    "(polialfabética/Vigenère), TRA (transposição), VER (cifra verbosa: uma letra vira vários glifos), NUL (nulos "
    "inseridos), BAR (palavras reais em ordem aleatória), TAB (gerado por tabela, sem significado), ALE (glifos ao "
    "acaso); ou 'indeterminada'. Recebes as medidas como um dicionário Python `m`. NÃO escrevas números copiados das "
    "medidas: refere-te a elas por m['chave']. Escreve uma função `classificar(m)` que devolve o código da família, "
    "com as comparações explícitas que distinguem as famílias, e uma lista 'justificacao' de expressões booleanas "
    "sobre m que, segundo ti, são verdadeiras neste texto e sustentam a tua escolha. Só podes usar if, return, "
    "comparações, aritmética, and/or/not e abs/min/max/round. Responde só com JSON: "
    '{"action":"programa","codigo":"def classificar(m):\\n    ...","justificacao":["m[\'a\'] < m[\'b\']"]}'
)


def plano(d, prefixo=""):
    out = {}
    for k, v in d.items():
        key = f"{prefixo}{k}"
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            out[key] = v
        elif isinstance(v, dict):
            out.update(plano(v, key + "."))
    return out


def medidas_planas(words):
    return plano(M.tudo(words))


def _seguro(src, modo):
    tree = ast.parse(src, mode=modo)
    for n in ast.walk(tree):
        if not isinstance(n, PERMITIDOS):
            raise ValueError(f"construção não permitida: {type(n).__name__}")
        if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id in FUNCOES):
            raise ValueError("só abs/min/max/round/len")
        if isinstance(n, ast.Name) and n.id.startswith("__"):
            raise ValueError("nome não permitido")
    return tree


_CHILD = r"""
import json, sys
d = json.load(sys.stdin)
ns = {"__builtins__": {"abs": abs, "min": min, "max": max, "round": round, "len": len}}
exec(compile(d["codigo"], "<classificar>", "exec"), ns)
if "classificar" not in ns:
    raise ValueError("falta classificar(m)")
print(json.dumps({"r": ns["classificar"](d["m"])}))
"""


def executar(codigo, m, timeout=10):
    """Corre classificar(m) num processo filho isolado (-I), com tempo limite. Funciona em Windows (sem SIGALRM).
    A análise AST é feita antes: sem atributos, sem imports, só as funções de FUNCOES."""
    import subprocess
    import sys
    _seguro(codigo, "exec")
    try:
        p = subprocess.run([sys.executable, "-I", "-c", _CHILD],
                           input=json.dumps({"codigo": codigo, "m": dict(m)}),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ValueError("tempo limite excedido") from None
    if p.returncode != 0:
        linhas = (p.stderr or "falhou").strip().splitlines()
        raise ValueError(linhas[-1][:200] if linhas else "falhou")
    r = json.loads(p.stdout)["r"]
    if r not in FAMILIAS:
        raise ValueError(f"resposta fora das famílias: {r!r}")
    return r


def avaliar(expr, m):
    tree = _seguro(expr, "eval")
    return bool(eval(compile(tree, "<just>", "eval"), {"__builtins__": {}, **FUNCOES}, {"m": dict(m)}))  # noqa: S307


class Programador:
    def __init__(self, backend, max_rounds=2):
        self.backend, self.max_rounds = backend, max_rounds

    def analisar(self, words):
        m = medidas_planas(words)
        user = ("Texto cifrado: primeiras palavras: " + " ".join("".join(w) for w in words[:12])
                + "\nm = " + json.dumps(m, ensure_ascii=False))
        log = {"rondas": [], "erro": None, "n_chaves": len(m)}
        rel = None
        for r in range(self.max_rounds + 1):
            out = self.backend.generate(SYSTEM, user, {})
            try:
                a = json.loads(out)
                codigo, just = a["codigo"], list(a.get("justificacao") or [])
            except (ValueError, TypeError, KeyError):
                log["rondas"].append({"ronda": r, "erro": "formato"})
                user += "\nResposta inválida: responde só com o JSON pedido."
                continue
            try:
                fam = executar(codigo, m)
                exec_erro = None
            except Exception as ex:  # noqa: BLE001
                fam, exec_erro = None, f"{type(ex).__name__}: {str(ex)[:160]}"
            res = []
            for e in just:
                try:
                    res.append({"expr": e, "verdadeira": avaliar(e, m)})
                except Exception as ex:  # noqa: BLE001
                    res.append({"expr": e, "verdadeira": False, "malformada": f"{type(ex).__name__}"})
            falsas = [x for x in res if not x["verdadeira"]]
            log["rondas"].append({"ronda": r, "familia": fam, "erro_execucao": exec_erro,
                                  "justificacoes": len(res), "falsas": [x["expr"] for x in falsas]})
            rel = {"mais_provavel": fam, "hipoteses": {}, "codigo": codigo, "_justificacao": res,
                   "_verificacao": [{"verdadeira": x["verdadeira"], "interpretacao": False} for x in res]}
            if exec_erro is None and not falsas:
                return rel, log
            if r == self.max_rounds:
                break
            linhas = ["VERIFICAÇÃO (o código executou a tua função e avaliou as justificações sobre m):"]
            if exec_erro:
                linhas.append(f"- A função não correu: {exec_erro}")
            for x in falsas:
                linhas.append(f"- FALSA neste texto: {x['expr']}")
            linhas.append("Revê a função e as justificações e responde com o mesmo formato JSON.")
            user += "\n" + "\n".join(linhas)
        if rel is None:
            log["erro"] = "formato_invalido"
        return rel, log

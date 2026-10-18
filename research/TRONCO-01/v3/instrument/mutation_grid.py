"""Fase 2: testes de mutação sobre o código que a grelha usa. Cada mutante corre os testes do instrumento num
interpretador limpo, sobre uma cópia da árvore v3. Um mutante é morto se os testes falham por asserção; os que
fazem os testes rebentar com erro contam à parte, como mortos por erro."""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
TARGETS = {"instrument/grid.py": None, "scoring.py": {"can_still_determine", "history_rows"},
           "generator_v3.py": {"verdict", "admissible_idx", "revision_reference"}}
SWAP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Lt: ast.LtE, ast.LtE: ast.Lt,
        ast.Gt: ast.GtE, ast.GtE: ast.Gt}
VERDICT_SWAP = {"rejected": "supported", "supported": "undetermined", "undetermined": "rejected",
                "inconsistent": "rejected", "fundamentado": "pesquisa", "sorte": "inferencia",
                "prematuro_certo": "prematura", "prematura": "prematuro_certo", "inferencia": "sorte",
                "pesquisa": "fundamentado"}


def sites(tree, funcs):
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or (funcs is not None and fn.name not in funcs):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare):
                for k, op in enumerate(node.ops):
                    if type(op) in SWAP:
                        yield ("cmp", fn.name, node.lineno, k)
            elif isinstance(node, ast.BoolOp):
                yield ("bool", fn.name, node.lineno, 0)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                yield ("not", fn.name, node.lineno, 0)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in VERDICT_SWAP:
                yield ("str", fn.name, node.lineno, node.col_offset)


class Mutator(ast.NodeTransformer):
    def __init__(self, site):
        self.site, self.done = site, False

    def _hit(self, node, kind, k=0):
        s = self.site
        return not self.done and s[0] == kind and node.lineno == s[2] and (kind != "str" or node.col_offset == s[3])

    def visit_Compare(self, node):
        self.generic_visit(node)
        if self._hit(node, "cmp"):
            node.ops[self.site[3]] = SWAP[type(node.ops[self.site[3]])](); self.done = True
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if self._hit(node, "bool"):
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And(); self.done = True
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if self._hit(node, "not") and isinstance(node.op, ast.Not):
            self.done = True
            return node.operand
        return node

    def visit_Constant(self, node):
        if self._hit(node, "str"):
            self.done = True
            return ast.copy_location(ast.Constant(VERDICT_SWAP[node.value]), node)
        return node


def run_one(args):
    rel, site, src = args
    tmp = Path(tempfile.mkdtemp())
    try:
        root = tmp / "TRONCO-01"
        shutil.copytree(V3.parent, root, ignore=shutil.ignore_patterns("*.jsonl.gz", "__pycache__", "packages"))
        tree = ast.parse(src)
        m = Mutator(site)
        new = ast.unparse(ast.fix_missing_locations(m.visit(tree)))
        if not m.done:
            return {"file": rel, "site": site, "status": "not_applied"}
        (root / "v3" / rel).write_text(new, encoding="utf-8")
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_instrument"], cwd=root / "v3",
                           capture_output=True, text=True, timeout=900)
        if p.returncode == 0:
            status = "survived"
        else:
            status = "killed_by_error" if "Error: " in p.stderr and "AssertionError" not in p.stderr else "killed"
        return {"file": rel, "site": site, "status": status}
    except subprocess.TimeoutExpired:
        return {"file": rel, "site": site, "status": "killed_by_timeout"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    jobs = []
    for rel, funcs in TARGETS.items():
        src = (V3 / rel).read_text(encoding="utf-8")
        for s in sites(ast.parse(src), funcs):
            jobs.append((rel, s, src))
    with ThreadPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        res = list(ex.map(run_one, jobs))
    summary = {}
    for r in res:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    print(json.dumps({"mutants": len(res), "summary": summary, "results": res}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

"""Referência determinística (18/10): hashes do código de referência e dos artefactos, mais um resumo recalculável.

`python instrument/reference_manifest.py --write` grava results/instrumento/REFERENCIA.json; sem --write, compara
o que recalcula com o ficheiro gravado e sai com erro se algo mudou. Os testes chamam check().
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
CODE = ["generator_v3.py", "scoring.py", "env_v3.py", "audit_v3.py", "instrument/grid.py", "instrument/planted.py",
        "instrument/enumerate_states.py", "instrument/verify_states.mjs", "instrument/verify_items.mjs",
        "instrument/items.py", "instrument/run_items.py", "instrument/analyse_items.py", "pilot/pilot_harness.py",
        "pilot/select_worlds.py"]
ARTIFACTS = ["results/instrumento/F3/ITENS.jsonl.gz", "results/instrumento/F1_ronda2/F1_ENUMERACAO.json",
             "results/instrumento/F2_GRELHA_HISTORICOS.json", "results/PILOTO_REFERENCIAS.json"]
OUT = V3 / "results" / "instrumento" / "REFERENCIA.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recompute() -> dict:
    sys.path[:0] = [str(V3), str(V3 / "pilot")]
    import audit_v3 as a
    import generator_v3 as g
    import select_worlds as S
    dev = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    return {"dev_worlds": len(dev), "dev_content_sha256": hashlib.sha256(
                "".join(sorted(g.content_sha(w) for w in dev)).encode()).hexdigest(),
            "pilot_worlds_sha256": S.worlds_sha(S.pilot_worlds()), "hypothesis_space": len(g.SPACE)}


def build() -> dict:
    return {"code_sha256": {c: sha(V3 / c) for c in CODE}, "artifacts_sha256": {f: sha(V3 / f) for f in ARTIFACTS},
            "recomputed": recompute()}


def check() -> list[str]:
    ref = json.loads(OUT.read_text(encoding="utf-8"))
    now = build()
    diffs = []
    for sect in ("artifacts_sha256", "recomputed"):
        for k, v in ref[sect].items():
            if now[sect].get(k) != v:
                diffs.append(f"{sect}:{k}")
    return diffs


if __name__ == "__main__":
    if "--write" in sys.argv:
        OUT.write_text(json.dumps(build(), indent=1) + "\n", encoding="utf-8")
        print("gravado", OUT)
    else:
        d = check()
        print("diferenças:", d or "nenhuma")
        sys.exit(1 if d else 0)

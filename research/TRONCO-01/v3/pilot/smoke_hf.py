"""Smoke test of the real HF backend on hand-written text only. It never reads pilot worlds, so it spends nothing.

Checks: the stack imports, the model loads from the local snapshot, constrained decoding returns JSON that
parses and matches each protocol schema (explore and revision phase). Writes one JSON report.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot_harness as H  # noqa: E402

USER_EXPLORE = """OBSERVAÇÕES
- o1: glyph=g0, setting=s0, partner=p0, phase=t0 -> 0
CARTAS
- A (Output depends only on glyph.)
    g0 -> 0
    g1 -> 1
CARTA DE TRABALHO: A
ENTRADAS RETIDAS (previsões 1 a 4, por esta ordem)
- 1: glyph=g1, setting=s0, partner=p0, phase=t0
CONSULTAS DISPONÍVEIS (orçamento restante 1)
- q1: glyph=g1, setting=s1, partner=p0, phase=t0
AÇÕES: {"action":"query","query_id":"qN"} | {"action":"commit","verdict":"rejected|supported|undetermined","admissible_cards":["ids"],"predictions":{"1":"0|1"}} | {"action":"suspend"}"""

USER_REVISION = USER_EXPLORE.split("CONSULTAS")[0] + """AÇÕES: {"action":"keep"} | {"action":"revise","verdict":"rejected|supported|undetermined|inconsistent","admissible_cards":["ids"]}"""


def matches(value, schema) -> bool:
    """Small validator for exactly the schema features action_schema uses."""
    if "anyOf" in schema:
        return any(matches(value, s) for s in schema["anyOf"])
    if "const" in schema:
        return value == schema["const"]
    if "enum" in schema:
        return value in schema["enum"]
    t = schema.get("type")
    if t == "string":
        return isinstance(value, str)
    if t == "array":
        return isinstance(value, list) and all(matches(v, schema.get("items", {})) for v in value)
    if t == "object":
        if not isinstance(value, dict) or any(k not in value for k in schema.get("required", [])):
            return False
        props, extra = schema.get("properties", {}), schema.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                if not matches(v, props[k]):
                    return False
            elif extra is False or (isinstance(extra, dict) and not matches(v, extra)):
                return False
        return True
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    report = {"python": platform.python_version(), "cases": []}
    from hf_backend import HFBackend
    t0 = time.time()
    backend = HFBackend(a.snapshot)
    report["load_seconds"] = round(time.time() - t0, 1)
    report["compat"] = backend.compat
    import lmformatenforcer, torch, transformers
    report["versions"] = {"torch": torch.__version__, "transformers": transformers.__version__,
                          "lm-format-enforcer": getattr(lmformatenforcer, "__version__", "?"),
                          "cuda": torch.cuda.is_available(), "device": str(backend.model.device)}
    toy = {"candidate_models": [{"id": "A"}], "query_menu": [{"id": "q1"}], "held_out_inputs": [{}],
           "remaining_query_budget": 1}
    for phase, user, st, obj in (("explore", USER_EXPLORE, None, False), ("revision", USER_REVISION, None, False),
                                 ("explore", USER_EXPLORE, toy, False), ("revision", USER_REVISION, toy, False),
                                 ("explore", USER_EXPLORE.replace('["ids"]', '{"A":true|false}'), toy, True),
                                 ("revision", USER_REVISION.replace('["ids"]', '{"A":true|false}'), toy, True)):
        schema = H.action_schema(phase, st, cards_object=obj)
        t0 = time.time()
        raw = backend.generate(H.SYSTEM_PROMPT, user, schema)
        case = {"phase": phase, "state_schema": st is not None, "cards_object": obj, "seconds": round(time.time() - t0, 1), "raw": raw}
        try:
            case["parsed"] = json.loads(raw)
            case["matches_schema"] = matches(case["parsed"], schema)
        except json.JSONDecodeError as e:
            case["parse_error"] = str(e)
            case["matches_schema"] = False
        report["cases"].append(case)
    report["ok"] = all(c["matches_schema"] for c in report["cases"])
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

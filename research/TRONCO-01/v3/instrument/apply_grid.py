"""Aplica instrument/grid.py às transcrições registadas (sem as reescrever) e às políticas de referência do piloto."""
from __future__ import annotations

import json
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "pilot"), str(V3 / "instrument")]
import env_v3 as E  # noqa: E402
import grid  # noqa: E402
import select_worlds as S  # noqa: E402

RUNS = [("0.5B R1", "piloto_R1"), ("0.5B R2", "piloto_R2"), ("0.5B R3", "piloto_R3"), ("1.5B L1", "piloto_L1"),
        ("3B L2", "piloto_L2"), ("7B L3", "piloto_L3")]


def replay(world, transcript):
    ep = E.Episode(world)
    for t in transcript:
        act = t.get("env_action", json.loads(t["output"]) if t["parsed"] else {"action": "__unparseable__"})
        ep.step(act)
    return ep


def main():
    ws = S.pilot_worlds()
    out = {}
    for label, d in RUNS:
        eps = [json.loads(l) for l in (V3 / "results" / d / "transcripts.jsonl").read_text(encoding="utf-8").splitlines() if l]
        rows = [grid.classify(w, replay(w, e["transcript"])) for w, e in zip(ws, eps)]
        out[label] = grid.summarise(rows)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

"""Deterministic selection of the pilot worlds: development seeds only (91xxx), balanced, 16 per verdict."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import audit_v3 as a  # noqa: E402
import generator_v3 as g  # noqa: E402

PER_TARGET = 16


def pilot_worlds():
    ws = a.dev_set(seeds=a.DEV_SEEDS, with_indirect=True, balanced=True)
    out = []
    for t in g.VERDICTS:
        sel = sorted((w for w in ws if w["reference"]["target_verdict"] == t),
                     key=lambda w: hashlib.sha256((w["world_id"] + w["reference"]["kind"] + "pilot").encode()).hexdigest())
        out += sel[:PER_TARGET]
    return out


def worlds_sha(ws):
    return hashlib.sha256("\n".join(json.dumps(w["public"], sort_keys=True) for w in ws).encode()).hexdigest()


if __name__ == "__main__":
    ws = pilot_worlds()
    print(len(ws), worlds_sha(ws))

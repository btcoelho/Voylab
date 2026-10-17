"""Reference policies on the same 48 pilot worlds, through the real protocol (env_v3.run_policy). No model involved."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import env_v3 as E  # noqa: E402
import pilot_harness as H  # noqa: E402
import policies as P  # noqa: E402
import select_worlds as S  # noqa: E402

KEYS = ("reach", "inference_error", "search_error", "premature_stop", "revision_type_I", "cards_exact")


def main():
    ws = S.pilot_worlds()
    out = {"worlds": len(ws), "worlds_sha256": S.worlds_sha(ws), "policies": {}}
    for cls in P.POLICIES_V2:
        pol = cls()
        R = [E.run_policy(pol, w, seed=0) for w in ws]
        done = [r for r in R if r.get("complete")]
        out["policies"][pol.name] = {k: {"k": sum(bool(r.get(k)) for r in done), "n": len(done),
                                         "ci95": H.wilson(sum(bool(r.get(k)) for r in done), len(done))} for k in KEYS}
        out["policies"][pol.name]["queries_mean"] = sum(r["queries"] for r in done) / len(done)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

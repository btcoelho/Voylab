"""Piloto humano V4 (docs/V3_CONSULTAS.md §11): seleção determinística dos 20 episódios e exportação para a página."""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "instrument"), str(V3 / "pilot")]
import generator_v3 as g  # noqa: E402
import pilot_harness as H  # noqa: E402
import query_leverage as QL  # noqa: E402
import variants as VA  # noqa: E402

QUOTA = {"supported": 7, "rejected": 7, "undetermined": 6}


def select():
    ws, _ = VA.build("V4")
    rng = random.Random("tronco01-v4-piloto-humano")
    rng.shuffle(ws)
    rows = []
    for w in ws:
        v = QL.values(w)
        rev = g.revision_reference(w, [])
        rows.append((w, max(v.values()) >= 0.80, v))
    chosen, count, hi = [], {k: 0 for k in QUOTA}, 0
    # pass 1: fill target quotas, alternating quality strata so that 10/10 is reached
    for want_hi in [True, False] * 20:
        for w, q_hi, v in rows:
            t = w["reference"]["target_verdict"]
            if w in [c[0] for c in chosen] or count[t] >= QUOTA[t] or q_hi != want_hi:
                continue
            if (q_hi and hi >= 10) or (not q_hi and len(chosen) - hi >= 10):
                continue
            chosen.append((w, q_hi, v)); count[t] += 1; hi += q_hi
            break
        if len(chosen) == 20:
            break
    return chosen


def export(chosen):
    out = []
    for n, (w, q_hi, v) in enumerate(chosen, 1):
        hid = w["hidden"]
        st = {"observations": list(w["public"]["observations"]), "candidate_models": w["public"]["candidate_models"],
              "working_model_id": w["public"]["working_model_id"], "held_out_inputs": w["public"]["held_out_inputs"],
              "phase": "explore", "remaining_query_budget": 1, "query_menu": w["public"]["query_menu"]}
        out.append({"n": n, "uid": w["uid"], "target": w["reference"]["target_verdict"], "quality_hi": q_hi,
                    "user_text": H.render_state(st, cards_object=True),
                    "menu": [{"id": q["id"], "input": q["input"], "answer": hid["h"][g.INPUTS.index(g.D.as_tuple(q["input"]))],
                              "value2": round(v[g.INPUTS.index(g.D.as_tuple(q["input"]))], 4)} for q in w["public"]["query_menu"]],
                    "new_evidence": [{"input": dict(zip(g.D.features, g.INPUTS[i])), "output": hid["h2"][i]} for i in hid["block"]],
                    "cards": [c["id"] for c in w["public"]["candidate_models"]]})
    return out


if __name__ == "__main__":
    ch = select()
    data = export(ch)
    txt = json.dumps(data, ensure_ascii=False, indent=1)
    Path(sys.argv[1]).write_text(txt + "\n", encoding="utf-8")
    import collections
    print(len(data), dict(collections.Counter(d["target"] for d in data)), "qualidade alta", sum(d["quality_hi"] for d in data),
          "sha", hashlib.sha256(txt.encode()).hexdigest()[:16])

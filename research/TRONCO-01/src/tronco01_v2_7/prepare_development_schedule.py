"""Derive an offline, no-query development schedule from archived public states."""
import hashlib
import json
from pathlib import Path

import replay

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "fixtures/v23/public_schedule.jsonl"
SCHEDULE = ROOT / "development_schedule.jsonl"
REFERENCE = ROOT / "development_reference_private.jsonl"
PREREG = ROOT / "preregistration_draft.json"

source = replay.load_jsonl(SOURCE)
public, reference = [], []
for item in source:
    state = json.loads(json.dumps(item["public_state"]))
    state["query_menu"] = []
    state["remaining_query_budget"] = 0
    public.append({"episode_id": item["episode_id"], "stratum": item["design_stratum"], "public_state": state})
    independently_replayed = replay.labels(state)
    if independently_replayed != item["expected_initial"]:
        raise AssertionError(f"saved reference disagrees with independent replay for {item['episode_id']}")
    reference.append({"episode_id": item["episode_id"], "expected": item["expected_initial"],
                      "crosscheck": "independent replay matches saved expected_initial"})

render = lambda items: "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in items)
SCHEDULE.write_text(render(public), encoding="utf-8")
REFERENCE.write_text(render(reference), encoding="utf-8")
prereg = json.loads(PREREG.read_text(encoding="utf-8"))
prereg["schedule"]["schedule_sha256"] = hashlib.sha256(SCHEDULE.read_bytes()).hexdigest()
PREREG.write_text(json.dumps(prereg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"episodes": len(public), "schedule_sha256": prereg["schedule"]["schedule_sha256"],
                  "private_reference_separate": True, "model_calls": 0}, indent=2))

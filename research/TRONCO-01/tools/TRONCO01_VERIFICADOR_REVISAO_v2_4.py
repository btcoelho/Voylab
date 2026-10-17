"""Read-only review of v2.4, with synthetic counterexamples; never invokes a model."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "work/TRONCO01_TRIAL_v2_4"
sys.path.insert(0, str(PACKAGE))
import harness
import replay


def report():
    return {"action": "report", "verdict": "undetermined", "candidate_model_codes": ["A"],
            "diagnosis": "identified", "sufficiency": "no_observations", "evidence_ids": [],
            "location": {"feature": "none", "values": []}}


def state():
    return {"candidate_models": [{"id": "A"}, {"id": "B"}],
            "observations": [{"id": "o1", "input": {"glyph": "g0"}, "output": "0"},
                             {"id": "o2", "input": {"glyph": "g1"}, "output": "1"}],
            "query_menu": [{"id": "q0", "input": {"glyph": "g0"}}],
            "remaining_query_budget": 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grammar", action="store_true")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    saved_status = json.loads((ROOT / "outputs/TRONCO01_STATUS_VERIFICACAO_v2_4_2026-10-17.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(ROOT / "outputs/TRONCO01_TRIAL_V2_4_REPRODUCIBLE_2026-10-17.zip") as z:
        manifest = json.loads(z.read("ARCHIVE_MANIFEST.json"))
        hashes = {name: hashlib.sha256(z.read(name)).hexdigest() == expected
                  for name, expected in manifest["archive_contents_sha256"].items()}
        disk = {name: (ROOT / name).is_file() and hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
                for name, expected in manifest["archive_contents_sha256"].items()}
        archive = {"crc_ok": z.testzip() is None, "hash_count": len(hashes),
                   "all_archive_hashes_match": all(hashes.values()), "disk_matches_archive": all(disk.values())}
    historical = replay.replay(PACKAGE / "fixtures/v23")
    events = replay.load_jsonl(PACKAGE / "fixtures/v23/run_20261017/events.jsonl")
    states = {e["episode_id"]: e["public_state"] for e in events if e["kind"] == "episode_start"}
    raw_by_seq = {e["sequence"]: e for e in events if e["kind"] == "raw_action"}
    rejected = []
    for event in events:
        if event["kind"] != "action_result" or event["result"].get("accepted"):
            continue
        ep = event.get("episode_id")
        if ep is None:
            ep = next(e["episode_id"] for e in reversed(events[:event["sequence"] - 1]) if e["kind"] == "episode_start")
        action = copy.deepcopy(event["action"])
        # Explanation was intentionally removed in v2.4. Test ID constraints after removing it.
        action.pop("explanation", None)
        try:
            harness.validate_action_shape(action, states[ep])
            blocked = False
        except harness.ModelOutputError:
            blocked = True
        missing_ids = sorted(set(action.get("evidence_ids", [])) - {x["id"] for x in states[ep]["observations"]})
        rejected.append({"episode_id": ep, "illegal_evidence_ids": missing_ids,
                         "rejected_by_v24_shape_after_explanation_removed": blocked,
                         "raw_sequence_present": event["raw_sequence"] in raw_by_seq})

    empty = {"candidate_models": [{"id": "A"}], "observations": [],
             "query_menu": [], "remaining_query_budget": 0}
    with tempfile.TemporaryDirectory() as scratch:
        base = Path(scratch)
        frozen = base / "schedule.json"
        initial = [{"episode_id": "same-id", "public_state": empty}]
        frozen.write_text(json.dumps(initial), encoding="utf-8")
        manifest_path = base / "manifest.json"
        manifest_path.write_text(json.dumps({"files": [{"path": "schedule.json", "sha256": hashlib.sha256(frozen.read_bytes()).hexdigest()}]}), encoding="utf-8")
        real_guard = harness.FrozenManifestGuard(manifest_path)
        guard_calls = []
        generations = []
        def guard():
            guard_calls.append(1)
            real_guard.verify()
        def generate(prompt, schema):
            generations.append(prompt)
            return json.dumps(report())
        kwargs = dict(generate=generate,
                      apply=lambda s, a: {"accepted": True, "terminal": True, "evaluation": {"joint_success": True}},
                      prompt_for=lambda s: json.dumps(s), event_path=base / "events.jsonl",
                      outcomes_path=base / "outcomes.json", summary_path=base / "summary.json",
                      generation_guard=guard)
        harness.execute_trial(initial, **kwargs)
        changed = copy.deepcopy(initial)
        changed[0]["public_state"]["remaining_query_budget"] = 99
        frozen.write_text(json.dumps(changed), encoding="utf-8")
        try:
            real_guard.verify()
            changed_source_detected = False
        except harness.ResumeIntegrityError:
            changed_source_detected = True
        before_guard, before_calls = len(guard_calls), len(generations)
        try:
            returned = harness.execute_trial(changed, **kwargs)
            resume_accepted = True
        except harness.ResumeIntegrityError:
            returned, resume_accepted = None, False
        resume = {"changed_frozen_schedule_detected_by_guard_when_called": changed_source_detected,
                  "resume_with_same_id_and_changed_state_returned_summary": resume_accepted,
                  "additional_guard_checks_on_completed_resume": len(guard_calls) - before_guard,
                  "additional_model_calls": len(generations) - before_calls,
                  "interpretation": "Completed-only resume bypasses the guard and never compares stored public states with the supplied schedule. This does not change old scores or demonstrate that a changed file passes the guard before a new generation."}
    grammar = None
    if args.grammar:
        import transformers.tokenization_utils as tokenization_utils
        from transformers import PreTrainedTokenizerBase
        tokenization_utils.PreTrainedTokenizerBase = PreTrainedTokenizerBase
        from lmformatenforcer import JsonSchemaParser
        cases = {}
        for field in ("candidate_model_codes", "evidence_ids", "location_values"):
            action = report()
            if field == "candidate_model_codes":
                action[field] = ["A", "A"]
            elif field == "evidence_ids":
                action[field] = ["o1", "o1"]
            else:
                action["location"] = {"feature": "glyph", "values": ["g0", "g0"]}
            parser = JsonSchemaParser(harness.public_action_schema(state())["oneOf"][-1])
            payload = json.dumps(action, separators=(",", ":"))
            allowed = True
            for char in payload:
                if char not in parser.get_allowed_characters():
                    allowed = False
                    break
                parser = parser.add_character(char)
            try:
                harness.validate_action_shape(action, state())
                validator_rejected = False
            except harness.ModelOutputError:
                validator_rejected = True
            cases[field] = {"duplicate_payload": action, "grammar_accepts_complete_payload": allowed and parser.can_end(),
                            "python_validator_rejects": validator_rejected}
        grammar = {"level": "character parser; not model generation or token-level test", "cases": cases}
    result = {"new_model_calls": 0, "model_weights_loaded": False, "historical_files_modified": False,
              "archive": archive, "saved_summary_matches_independent_replay": saved_status["historical_v23_replay"] == historical["summary"],
              "historical_summary": historical["summary"], "historical_rejections_checked": rejected,
              "resume_counterexample": resume, "grammar_duplicate_probes": grammar}
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

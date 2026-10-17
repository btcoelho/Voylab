"""Offline-testable TRONCO-01 interaction and recovery harness v2.4."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
from typing import Callable


class ModelOutputError(ValueError):
    """Model returned malformed JSON or an action outside the public schema."""


class ResumeIntegrityError(RuntimeError):
    """Saved trial state is ambiguous; do not silently repeat a model call."""


class FrozenManifestGuard:
    def __init__(self, manifest_path: Path):
        self.manifest_path=Path(manifest_path).resolve()
        self.root=self.manifest_path.parent

    def verify(self, allow_draft: bool = False) -> dict[str, str]:
        manifest=json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "frozen_before_inference" and not allow_draft:
            raise ResumeIntegrityError("manifest is not frozen for inference")
        failures=[]
        verified={}
        for entry in manifest.get("files",[]):
            path=(self.root/entry["path"]).resolve()
            if self.root not in path.parents:
                failures.append({"path":entry["path"],"error":"path escapes manifest root"})
            elif not path.is_file():
                failures.append({"path":entry["path"],"error":"missing frozen file"})
            else:
                actual=hashlib.sha256(path.read_bytes()).hexdigest()
                if actual!=entry["sha256"]:
                    failures.append({"path":entry["path"],"error":"hash mismatch"})
                else:
                    verified[entry["path"]]=actual
        for entry in manifest.get("external_files",[]):
            path=Path(entry["path"]).expanduser().resolve()
            if not path.is_file():
                failures.append({"path":str(path),"error":"missing declared external frozen file"})
                continue
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            if actual!=entry["sha256"]:
                failures.append({"path":str(path),"error":"external frozen file hash mismatch"})
            else:
                verified[f"external:{path}"]=actual
        if failures or not manifest.get("files"):
            raise ResumeIntegrityError(f"frozen input check failed: {failures or 'manifest is empty'}")
        return {"__manifest_status__":manifest.get("status"), **verified}


def strict_json_object(raw: str) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ModelOutputError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ModelOutputError(f"non-finite JSON value: {value}")

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except ModelOutputError:
        raise
    except (json.JSONDecodeError, TypeError) as exc:
        raise ModelOutputError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelOutputError("action must be a JSON object")
    return value


def public_action_schema(state: dict) -> dict:
    """Schema constrains syntax and state-visible IDs, never semantic answers."""
    candidate_ids = sorted(c["id"] for c in state["candidate_models"])
    evidence_ids = sorted(o["id"] for o in state["observations"])
    query_ids = sorted(q["id"] for q in state["query_menu"])
    observed_values = sorted({value for observation in state["observations"]
                              for value in observation["input"].values()})
    branches = []
    if state.get("remaining_query_budget", 0) > 0 and query_ids:
        branches.append({"type": "object", "properties": {
            "action": {"const": "query"}, "query_id": {"type": "string", "enum": query_ids}},
            "required": ["action", "query_id"], "additionalProperties": False})
    branches.append({"type": "object", "properties": {
            "action": {"const": "report"},
            "verdict": {"enum": ["supported", "rejected", "undetermined"]},
            "candidate_model_codes": {"type": "array", "items": {"type": "string", "enum": candidate_ids},
                                       "uniqueItems": True, "maxItems": len(candidate_ids)},
            "diagnosis": {"enum": ["none_fit", "identified", "ambiguous"]},
            "sufficiency": {"enum": ["no_observations", "no_candidate_fits",
                                       "identity_ambiguous", "identity_resolved"]},
            "evidence_ids": {"type": "array", "items": {"type": "string", "enum": evidence_ids},
                             "uniqueItems": True, "maxItems": len(evidence_ids)},
            "location": {"type": "object", "properties": {
                "feature": {"enum": ["none", "glyph", "setting", "partner", "phase"]},
                "values": {"type": "array", "items": {"type": "string", "enum": observed_values},
                           "uniqueItems": True, "maxItems": 2}},
                "required": ["feature", "values"], "additionalProperties": False}},
         "required": ["action", "verdict", "candidate_model_codes", "diagnosis",
                      "sufficiency", "evidence_ids", "location"],
         "additionalProperties": False})
    return {"oneOf": branches}


def validate_action_shape(action: dict, state: dict) -> None:
    if not isinstance(action, dict):
        raise ModelOutputError("action must be an object")
    schema = public_action_schema(state)
    candidate_ids = {c["id"] for c in state["candidate_models"]}
    evidence_ids = {o["id"] for o in state["observations"]}
    observed_values = {value for observation in state["observations"]
                       for value in observation["input"].values()}
    report_schema = next(x for x in schema["oneOf"]
                         if x["properties"]["action"].get("const") == "report")
    matches = 0
    for branch in schema["oneOf"]:
        props = branch["properties"]
        if set(action) != set(branch["required"]):
            continue
        if any(key not in props or ("const" in rule and action[key] != rule["const"])
               or ("enum" in rule and action[key] not in rule["enum"])
               for key, rule in props.items() if key in action):
            continue
        if branch["properties"]["action"]["const"] == "query":
            matches += 1
            continue
        if action["action"] != "report":
            continue
        if (not isinstance(action["candidate_model_codes"], list)
                or len(action["candidate_model_codes"]) > len(state["candidate_models"])
                or not all(isinstance(x, str) for x in action["candidate_model_codes"])
                or len(set(action["candidate_model_codes"])) != len(action["candidate_model_codes"])
                or not all(x in candidate_ids for x in action["candidate_model_codes"])):
            continue
        if (not isinstance(action["evidence_ids"], list)
                or len(action["evidence_ids"]) > len(state["observations"])
                or not all(isinstance(x, str) for x in action["evidence_ids"])
                or len(set(action["evidence_ids"])) != len(action["evidence_ids"])
                or not all(x in evidence_ids for x in action["evidence_ids"])):
            continue
        location = action["location"]
        if (not isinstance(location, dict) or set(location) != {"feature", "values"}
                or location["feature"] not in report_schema["properties"]["location"]["properties"]["feature"]["enum"]
                or not isinstance(location["values"], list) or len(location["values"]) > 2
                or not all(isinstance(x, str) for x in location["values"])
                or len(set(location["values"])) != len(location["values"])
                or not all(x in observed_values for x in location["values"])):
            continue
        matches += 1
    if matches != 1:
        raise ModelOutputError("action does not match exactly one public action shape")


class Journal:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sequence = 0
        if self.path.exists():
            for expected, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
                event = json.loads(line)
                if event.get("sequence") != expected:
                    raise ResumeIntegrityError("journal sequence is not contiguous")
                self.sequence = expected

    def append(self, event: dict) -> dict:
        self.sequence += 1
        item = {"sequence": self.sequence, **event}
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return item


def completed_episodes(events: list[dict], scheduled_ids: list[str]) -> set[str]:
    scheduled = set(scheduled_ids)
    starts, ends = Counter(), Counter()
    active = set()
    for event in events:
        ep = event.get("episode_id")
        if event.get("kind") == "episode_start":
            starts[ep] += 1
            active.add(ep)
        elif event.get("kind") == "episode_outcome":
            outcome = event.get("outcome", {})
            ends[outcome.get("episode_id")] += 1
    if (set(starts) - scheduled) or (set(ends) - scheduled):
        raise ResumeIntegrityError("journal contains episode IDs outside the frozen schedule")
    if any(starts[x] != 1 for x in starts) or any(ends[x] != 1 for x in ends):
        raise ResumeIntegrityError("duplicate episode start or completion; manual reconciliation required")
    if set(starts) != set(ends):
        raise ResumeIntegrityError("episode start/outcome records do not pair exactly")
    incomplete = set(starts) - set(ends)
    if incomplete:
        raise ResumeIntegrityError(f"interrupted episodes require review; refusing blind replay: {sorted(incomplete)}")
    return set(ends)


def preflight_trial_identity(schedule: list[dict], max_calls: int, preregistration_sha256: str,
                             event_path: Path, resume_after_sentinel: bool = False) -> tuple[dict, str, list[dict], set[str]]:
    """Check the durable trial identity and completion state before loading a backend."""
    if (not isinstance(preregistration_sha256, str) or len(preregistration_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in preregistration_sha256)):
        raise ResumeIntegrityError("a frozen preregistration SHA-256 is required to start or resume a trial")
    ids = [item["episode_id"] for item in schedule]
    if len(set(ids)) != len(ids):
        raise ResumeIntegrityError("frozen schedule has duplicate episode IDs")
    canonical_schedule = json.dumps(schedule, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    identity = {"schedule_sha256": hashlib.sha256(canonical_schedule.encode("utf-8")).hexdigest(),
                "max_calls_per_episode": max_calls, "preregistration_sha256": preregistration_sha256}
    fingerprint = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True,
                                             separators=(",", ":")).encode("utf-8")).hexdigest()
    path = Path(event_path)
    if not path.exists():
        return identity, fingerprint, [], set()
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    Journal(path)  # validates contiguous event sequence
    starts = [event for event in events if event.get("kind") == "trial_start"]
    if len(starts) != 1 or not events or events[0] != starts[0]:
        raise ResumeIntegrityError("journal lacks one initial trial identity; manual reconciliation required")
    if starts[0].get("trial_fingerprint") != fingerprint:
        raise ResumeIntegrityError("protocol, schedule, or call budget differs from the journaled trial identity")
    if any(event.get("kind") == "sentinel_stop" for event in events) and not resume_after_sentinel:
        raise ResumeIntegrityError("sentinel stop is recorded; inspect and amend the protocol before resuming")
    completed = completed_episodes(events, ids)
    return identity, fingerprint, events, completed


def outcomes_from_journal(events: list[dict], scheduled_ids: list[str]) -> list[dict]:
    completed_episodes(events, scheduled_ids)
    outcomes = [json.loads(json.dumps(e["outcome"])) for e in events
                if e.get("kind") == "episode_outcome"]
    attempted = [e for e in events if e.get("kind") == "generation_attempt"]
    generations = Counter(e.get("episode_id") for e in attempted) if attempted else Counter(
        e.get("episode_id") for e in events if e.get("kind") == "generation")
    accepted_queries = Counter(e.get("episode_id") for e in events
                               if e.get("kind") == "action_result"
                               and e.get("result", {}).get("accepted")
                               and "observation" in e.get("result", {}))
    model_output_failures = {e.get("episode_id") for e in events
                             if e.get("kind") == "model_output_failure"}
    decode_errors = {e.get("episode_id") for e in events if e.get("kind") == "episode_error"
                     and "JSONDecodeError" in str(e.get("error", ""))}
    for item in outcomes:
        ep = item["episode_id"]
        item["calls"] = generations[ep]
        item["queries"] = accepted_queries[ep]
        if ep in model_output_failures or ep in decode_errors:
            item["status"] = "model_output_failure"
        elif item.get("status") == "call_limit_no_report":
            item["status"] = "call_limit_no_valid_terminal_action"
    return outcomes


def summarize(events: list[dict], outcomes: list[dict], planned_ids: list[str]) -> dict:
    if len({x.get("episode_id") for x in outcomes}) != len(outcomes):
        raise ResumeIntegrityError("duplicate outcomes")
    by_id = {x["episode_id"]: x for x in outcomes}
    if set(by_id) - set(planned_ids):
        raise ResumeIntegrityError("outcomes contain IDs outside frozen schedule")
    statuses = Counter(x["status"] for x in outcomes)
    calls = sum(int(x.get("calls", 0)) for x in outcomes)
    queries = sum(int(x.get("queries", 0)) for x in outcomes)
    joint = sum(bool(x.get("evaluation", {}).get("joint_success", False)) for x in outcomes)
    sentinel_events = [e for e in events if e.get("kind") == "sentinel_stop"]
    return {"episodes_attempted": len(outcomes), "episodes_planned": len(planned_ids),
            "generation_calls": calls, "reported": statuses["reported"],
            "model_output_failures": statuses["model_output_failure"],
            "technical_failures": statuses["technical_failure"],
            "call_limit_no_valid_terminal_action": statuses["call_limit_no_valid_terminal_action"],
            "joint_successes": joint,
            "joint_success_rate_completed": joint / len(outcomes) if outcomes else None,
            "joint_success_rate_planned": (joint / len(planned_ids)
                if planned_ids and set(by_id) == set(planned_ids) else None),
            "mean_queries": queries / len(outcomes) if outcomes else None,
            "sentinel_stop_events": len(sentinel_events),
            "sentinel_stop_reasons": [e.get("reason") for e in sentinel_events]}


def atomic_write_json(path: Path, value: dict | list) -> None:
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def execute_trial(schedule: list[dict], generate: Callable[[str, dict], str],
                  apply: Callable[[dict, dict], dict], prompt_for: Callable[[dict], str],
                  event_path: Path, outcomes_path: Path, summary_path: Path,
                  generation_guard: Callable[[], dict[str, str]],
                  max_calls: int = 4, resume_after_sentinel: bool = False,
                  preregistration_sha256: str | None = None,
                  allow_draft_for_offline_test: bool = False) -> dict:
    # Check provenance even when the journal already contains every planned outcome.
    if (not isinstance(preregistration_sha256, str) or len(preregistration_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in preregistration_sha256)):
        raise ResumeIntegrityError("a frozen preregistration SHA-256 is required to start or resume a trial")
    verified_inputs = generation_guard()
    allowed_status = "offline_smoke" if allow_draft_for_offline_test else "frozen_before_inference"
    if not isinstance(verified_inputs, dict) or verified_inputs.get("__manifest_status__") != allowed_status:
        raise ResumeIntegrityError(f"trial entry requires manifest status {allowed_status}")
    prereg_hashes = ({digest for path, digest in verified_inputs.items()
                      if Path(path).name in {"preregistration_draft.json", "preregistration.json"}}
                     if isinstance(verified_inputs, dict) else set())
    if preregistration_sha256 not in prereg_hashes:
        raise ResumeIntegrityError("a verified manifest must include this exact preregistration hash")
    identity, trial_fingerprint, events, completed = preflight_trial_identity(
        schedule, max_calls, preregistration_sha256, event_path, resume_after_sentinel)
    journal = Journal(event_path)
    if not events:
        journal.append({"kind": "trial_start", "trial_fingerprint": trial_fingerprint,
                        "identity": identity})
        events = [json.loads(line) for line in Path(event_path).read_text(encoding="utf-8").splitlines()]
    ids = [item["episode_id"] for item in schedule]
    for item in schedule:
        ep = item["episode_id"]
        if ep in completed:
            continue
        journal.append({"kind": "episode_start", "episode_id": ep,
                        "public_state": item["public_state"]})
        execute_episode(ep, item["public_state"], generate, apply, prompt_for, journal,
                        generation_guard,
                        max_calls=max_calls)
        events = [json.loads(line) for line in Path(event_path).read_text(encoding="utf-8").splitlines()]
        outcomes = outcomes_from_journal(events, ids)
        atomic_write_json(outcomes_path, outcomes)
        atomic_write_json(summary_path, summarize(events, outcomes, ids))
        latest = outcomes[-1]
        if latest["status"] == "technical_failure":
            journal.append({"kind": "sentinel_stop", "episode_id": ep,
                            "reason": latest.get("error", "technical failure")})
            break
    events = [json.loads(line) for line in Path(event_path).read_text(encoding="utf-8").splitlines()]
    outcomes = outcomes_from_journal(events, ids)
    atomic_write_json(outcomes_path, outcomes)
    summary = summarize(events, outcomes, ids)
    atomic_write_json(summary_path, summary)
    return summary


def execute_episode(episode_id: str, initial_state: dict, generate: Callable[[str, dict], str],
                    apply: Callable[[dict, dict], dict], prompt_for: Callable[[dict], str],
                    journal: Journal, generation_guard: Callable[[], None],
                    max_calls: int = 4) -> dict:
    state = json.loads(json.dumps(initial_state))
    feedback = None
    calls, queries, rejected = 0, 0, 0
    for call_index in range(1, max_calls + 1):
        request_state = json.loads(json.dumps(state))
        if feedback is not None:
            request_state["action_feedback"] = feedback
        try:
            prompt = prompt_for(request_state)
        except Exception as exc:
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": f"prompt construction: {exc!r}"}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        schema = public_action_schema(request_state)
        schema_text = json.dumps(schema, sort_keys=True, separators=(",", ":"))
        journal.append({"kind": "prompt", "episode_id": episode_id, "call_index": call_index,
                        "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                        "request_state": request_state, "action_schema": schema,
                        "action_schema_sha256": hashlib.sha256(schema_text.encode("utf-8")).hexdigest()})
        try:
            generation_guard()
        except Exception as exc:
            journal.append({"kind": "frozen_run_gate_failure", "episode_id": episode_id,
                            "call_index": call_index, "error": repr(exc)})
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": f"frozen run gate: {exc!r}"}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        journal.append({"kind": "generation_attempt", "episode_id": episode_id,
                        "call_index": call_index})
        calls += 1
        try:
            generated = generate(prompt, schema)
        except Exception as exc:
            journal.append({"kind": "generation_error", "episode_id": episode_id,
                            "call_index": call_index, "error": repr(exc)})
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": repr(exc)}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        if isinstance(generated, tuple):
            raw, metadata = generated
        else:
            raw, metadata = generated, {}
        if not isinstance(raw, str):
            raw = str(raw)
        if not isinstance(metadata, dict):
            metadata = {}
        journal.append({"kind": "generation", "episode_id": episode_id,
                        "call_index": call_index, "output_char_count": len(raw), **metadata})
        raw_event = journal.append({"kind": "raw_action", "episode_id": episode_id,
                                    "call_index": call_index, "raw": raw})
        try:
            action = strict_json_object(raw)
            validate_action_shape(action, state)
        except ModelOutputError as exc:
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "model_output_failure",
                       "error": str(exc)}
            journal.append({"kind": "model_output_failure", "episode_id": episode_id,
                            "call_index": call_index, "raw_sequence": raw_event["sequence"],
                            "error": str(exc)})
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        try:
            result = apply(state, action)
        except Exception as exc:
            journal.append({"kind": "environment_error", "episode_id": episode_id,
                            "call_index": call_index, "error": repr(exc)})
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": f"action application: {exc!r}"}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        journal.append({"kind": "action_result", "episode_id": episode_id,
                        "call_index": call_index, "raw_sequence": raw_event["sequence"],
                        "action": action, "result": result})
        if not result.get("accepted"):
            rejected += 1
            feedback = {"code": "invalid_action", "messages": list(result.get("legal_errors", [])),
                        "instruction": "Correct the action using the current public state. No scientific answer is supplied."}
            continue
        if action["action"] == "query" and "observation" not in result:
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": "accepted query returned no observation"}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        if action["action"] == "report" and not result.get("terminal"):
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "technical_failure",
                       "error": "accepted report did not terminate episode"}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
        if "observation" in result:
            queries += 1
            state.setdefault("observations", []).append(result["observation"])
            qid = action["query_id"]
            state["query_menu"] = [q for q in state["query_menu"] if q["id"] != qid]
            state["remaining_query_budget"] -= 1
            feedback = None
        if result.get("terminal"):
            outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
                       "rejected_actions": rejected, "status": "reported",
                       "evaluation": result.get("evaluation"), "final_state": state}
            journal.append({"kind": "episode_outcome", "outcome": outcome})
            return outcome
    outcome = {"episode_id": episode_id, "calls": calls, "queries": queries,
               "rejected_actions": rejected, "status": "call_limit_no_valid_terminal_action"}
    journal.append({"kind": "episode_outcome", "outcome": outcome})
    return outcome


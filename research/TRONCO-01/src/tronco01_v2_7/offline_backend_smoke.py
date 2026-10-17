"""Pass fixed actions through the v2.5 harness and tokenizer grammar; never loads model weights."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from importlib.metadata import version
import transformers
from functools import partial

import transformers.tokenization_utils as tokenization_utils
from transformers import AutoTokenizer, PreTrainedTokenizerBase
tokenization_utils.PreTrainedTokenizerBase = PreTrainedTokenizerBase
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.characterlevelparser import UnionParser
from lmformatenforcer.tokenenforcer import TokenEnforcer, TokenEnforcerTokenizerData

from harness import FrozenManifestGuard, execute_trial
from model_backend import build_chat_prompt


def make_enforcer(tokenizer, prompt, schema):
    token_0 = tokenizer.encode("0")[-1]
    regular = []
    for token_id in range(len(tokenizer)):
        if token_id in tokenizer.all_special_ids:
            continue
        decoded = tokenizer.decode([token_id])
        decoded_after_0 = tokenizer.decode([token_0, token_id])[1:]
        regular.append((token_id, decoded_after_0, len(decoded_after_0) > len(decoded)))
    data = TokenEnforcerTokenizerData(regular, lambda ids: tokenizer.decode(ids).rstrip("�"),
                                     tokenizer.eos_token_id, use_bitmask=False,
                                     vocab_size=len(tokenizer))
    parser = UnionParser([JsonSchemaParser(branch) for branch in schema["oneOf"]])
    enforcer = TokenEnforcer(data, parser)
    prefix = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    return enforcer, prefix


def main():
    ap = argparse.ArgumentParser()
    default_tokenizer = os.environ.get("TRONCO_TOKENIZER_PATH")
    ap.add_argument("--tokenizer", type=Path, default=Path(default_tokenizer) if default_tokenizer else None)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.tokenizer is None or not args.tokenizer.is_dir():
        raise FileNotFoundError("Pass --tokenizer or set TRONCO_TOKENIZER_PATH to the cached tokenizer directory")
    tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer), local_files_only=True)
    state = {"candidate_models": [{"id": "A"}, {"id": "B"}], "observations": [],
             "query_menu": [{"id": "q0", "input": {"glyph": "g0"}}],
             "remaining_query_budget": 1}
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        schedule = [{"episode_id": "smoke-01", "public_state": state}]
        schedule_path = temp_root / "schedule.json"
        prereg_path = temp_root / "preregistration_draft.json"
        prompt_path = temp_root / "system_prompt.txt"
        schedule_path.write_text(json.dumps(schedule), encoding="utf-8")
        prereg_path.write_text('{"protocol":"scripted-offline-smoke"}', encoding="utf-8")
        prompt_path.write_text((Path(__file__).parent / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8"), encoding="utf-8")
        prereg_hash = hashlib.sha256(prereg_path.read_bytes()).hexdigest()
        manifest_path = temp_root / "frozen_inputs.json"
        frozen_files = []
        for file in (prereg_path, schedule_path, prompt_path):
            frozen_files.append({"path": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
        manifest_path.write_text(json.dumps({"status": "offline_smoke", "files": frozen_files}), encoding="utf-8")
        guard = FrozenManifestGuard(manifest_path)
        call_number = 0
        system_prompt = (Path(__file__).parent / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8")

        def prompt_for(current):
            return build_chat_prompt(tokenizer, system_prompt, current)

        def generate(prompt, schema):
            nonlocal call_number
            call_number += 1
            # Read the public state from the same JSON user message that the real chat-template path creates.
            state_payload = prompt.split("<|im_start|>user\n", 1)[1].split("<|im_end|>", 1)[0]
            current_state = json.loads(state_payload)
            if not current_state["observations"] and current_state["remaining_query_budget"]:
                action = {"action": "query", "query_id": current_state["query_menu"][0]["id"]}
            else:
                # Intentionally fixed demonstration output. It does not consult any expected labels.
                action = {"action": "report", "verdict": "undetermined",
                          "candidate_model_codes": [x["id"] for x in current_state["candidate_models"]],
                          "diagnosis": "ambiguous", "sufficiency": "no_observations",
                          "evidence_ids": [], "location": {"feature": "none", "values": []}}
            raw = json.dumps(action, separators=(",", ":"))
            enforcer, prefix = make_enforcer(tokenizer, prompt, schema)
            ids = list(prefix)
            payload_ids = tokenizer(raw, add_special_tokens=False)["input_ids"]
            for token_id in payload_ids:
                allowed = enforcer.get_allowed_tokens(ids).allowed_tokens
                if token_id not in allowed:
                    raise AssertionError(f"scripted token {token_id} is outside the active grammar")
                ids.append(token_id)
            eos = tokenizer.eos_token_id
            if eos is None or eos not in enforcer.get_allowed_tokens(ids).allowed_tokens:
                raise AssertionError("EOS is not allowed after the complete scripted action")
            return raw, {"backend": "scripted_tokenizer_path", "weights_loaded": False,
                         "model_inference": False, "generated_token_count": len(payload_ids),
                         "eos_terminated": True}

        def apply(current_state, action):
            if action["action"] == "query":
                q = next(q for q in current_state["query_menu"] if q["id"] == action["query_id"])
                return {"accepted": True,
                        "observation": {"id": "o-smoke", "input": q["input"], "output": "0"}}
            return {"accepted": True, "terminal": True,
                    "evaluation": {"joint_success": False, "source": "fixed smoke fixture"}}

        events_path = temp_root / "events.jsonl"
        outcome = execute_trial(schedule, generate, apply, prompt_for,
                                events_path, temp_root / "outcomes.json", temp_root / "summary.json",
                                partial(guard.verify, allow_draft=True), max_calls=2,
                                preregistration_sha256=prereg_hash,
                                allow_draft_for_offline_test=True)
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    result = {"episodes_attempted": outcome["episodes_attempted"],
              "generation_calls": outcome["generation_calls"], "queries": outcome["mean_queries"],
              "model_weights_loaded": False, "model_inference": False,
              "tokenizer": tokenizer.name_or_path, "transformers": transformers.__version__,
              "lm_format_enforcer": version("lm-format-enforcer"),
              "event_kinds": [event["kind"] for event in events],
              "query_was_recorded": any(e.get("kind") == "action_result" and e.get("action", {}).get("action") == "query" for e in events),
              "report_was_recorded": any(e.get("kind") == "action_result" and e.get("action", {}).get("action") == "report" for e in events),
              "all_generation_records_marked_simulated": all(e.get("backend") == "scripted_tokenizer_path" and e.get("weights_loaded") is False for e in events if e.get("kind") == "generation")}
    assert result["episodes_attempted"] == 1 and result["generation_calls"] == 2 and result["queries"] == 1.0
    assert result["query_was_recorded"] and result["report_was_recorded"] and result["all_generation_records_marked_simulated"]
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    output = args.output or (Path(__file__).parent / "results/offline_backend_smoke_v2_5.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

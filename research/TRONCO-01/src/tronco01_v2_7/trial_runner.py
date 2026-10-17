"""Draft v2.7 runner. Importing it never loads the checkpoint or runs inference."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import harness
import model_backend
import replay
from runtime_environment import verify_runtime as verify_runtime_environment


def load_schedule(path: Path) -> list[dict]:
    items = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]
    if not items or len({x.get("episode_id") for x in items}) != len(items):
        raise ValueError("schedule is empty or contains duplicate episode IDs")
    if any(not isinstance(x.get("public_state"), dict) for x in items):
        raise ValueError("every schedule entry must contain a public_state object")
    return [{"episode_id": x["episode_id"], "public_state": x["public_state"]} for x in items]


def prompt_for_state(system_prompt: str, tokenizer):
    def build(state: dict) -> str:
        return model_backend.build_chat_prompt(tokenizer, system_prompt, state)
    return build


def load_verified_system_prompt(path: Path, prereg: dict, verified: dict) -> str:
    expected_name = prereg["experimental_condition"]["system_prompt"]
    if Path(path).name != expected_name:
        raise harness.ResumeIntegrityError("system prompt path differs from preregistration")
    raw = Path(path).read_bytes()
    if verified.get(expected_name) != hashlib.sha256(raw).hexdigest():
        raise harness.ResumeIntegrityError("system prompt bytes are not the prompt covered by the frozen manifest")
    return raw.decode("utf-8").strip()


def apply_scientific_action(state: dict, action: dict) -> dict:
    """Apply the fixed no-query protocol and score reports with independent replay.score."""
    if action.get("action") != "report":
        return {"accepted": False, "legal_errors": ["queries are disabled in this protocol"]}
    evaluation = replay.score(state, action)
    if not evaluation["legal"]:
        return {"accepted": False, "legal_errors": ["report cites IDs outside the public state"]}
    return {"accepted": True, "terminal": True, "evaluation": evaluation}


def run(schedule_path: Path, system_prompt_path: Path, model_path: Path,
        manifest_path: Path, output_dir: Path,
        expected_weights_sha256: str, expected_tokenizer_sha256: str,
        expected_tokenizer_config_sha256: str, preregistration_path: Path,
        max_calls: int = 1) -> dict:
    guard = harness.FrozenManifestGuard(manifest_path)
    verified = guard.verify()
    prereg = json.loads(Path(preregistration_path).read_text(encoding="utf-8"))
    prereg_hash = hashlib.sha256(Path(preregistration_path).read_bytes()).hexdigest()
    if prereg.get("status") != "frozen_before_inference" or not prereg.get("frozen"):
        raise harness.ResumeIntegrityError("preregistration is not frozen_before_inference")
    if prereg_hash not in verified.values():
        raise harness.ResumeIntegrityError("frozen manifest does not cover this exact preregistration")
    schedule = load_schedule(schedule_path)
    condition = prereg["experimental_condition"]
    if hashlib.sha256(Path(schedule_path).read_bytes()).hexdigest() != prereg["schedule"]["schedule_sha256"]:
        raise harness.ResumeIntegrityError("schedule bytes do not match the preregistered schedule hash")
    if (condition["weights_sha256"] != expected_weights_sha256
            or condition["tokenizer_json_sha256"] != expected_tokenizer_sha256
            or condition["tokenizer_config_sha256"] != expected_tokenizer_config_sha256):
        raise harness.ResumeIntegrityError("checkpoint hashes differ from the preregistered hashes")
    if max_calls != prereg["experimental_condition"]["max_calls_per_episode"]:
        raise harness.ResumeIntegrityError("max_calls differs from the preregistered protocol")
    if condition.get("queries_enabled") is not False or condition.get("query_budget_per_episode") != 0:
        raise harness.ResumeIntegrityError("v2.7 runner requires the preregistered no-query condition")
    verify_runtime_environment(prereg["software_environment"])
    artifacts = condition.get("checkpoint_artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise harness.ResumeIntegrityError("preregistration lacks complete checkpoint artifact hashes")
    if (artifacts.get("model.safetensors") != expected_weights_sha256
            or artifacts.get("tokenizer.json") != expected_tokenizer_sha256
            or artifacts.get("tokenizer_config.json") != expected_tokenizer_config_sha256):
        raise harness.ResumeIntegrityError("checkpoint artifact manifest disagrees with required primary hashes")
    system_prompt = load_verified_system_prompt(system_prompt_path, prereg, verified)
    event_path = output_dir / "events.jsonl"
    harness.preflight_trial_identity(schedule, max_calls, prereg_hash, event_path)
    generator = model_backend.Qwen25Generator.from_verified_checkpoint(
        model_path=model_path,
        expected_weights_sha256=expected_weights_sha256,
        expected_tokenizer_sha256=expected_tokenizer_sha256,
        expected_tokenizer_config_sha256=expected_tokenizer_config_sha256,
        generation_guard=guard.verify,
        expected_preregistration_sha256=prereg_hash,
        max_new_tokens=int(prereg["experimental_condition"]["generation"]["max_new_tokens"]),
        max_context_tokens=int(prereg["experimental_condition"]["generation"]["max_context_tokens"]),
        expected_artifact_hashes=artifacts)
    output_dir.mkdir(parents=True, exist_ok=True)
    return harness.execute_trial(
        schedule=schedule,
        generate=generator,
        apply=apply_scientific_action,
        prompt_for=prompt_for_state(system_prompt, generator.tokenizer),
        event_path=event_path,
        outcomes_path=output_dir / "outcomes.json",
        summary_path=output_dir / "summary.json",
        generation_guard=guard.verify,
        max_calls=max_calls,
        preregistration_sha256=prereg_hash)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--system-prompt", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--weights-sha256", required=True)
    parser.add_argument("--tokenizer-sha256", required=True)
    parser.add_argument("--tokenizer-config-sha256", required=True)
    parser.add_argument("--max-calls", type=int, default=1)
    args = parser.parse_args()
    result = run(args.schedule, args.system_prompt, args.model_path, args.manifest,
                 args.output_dir, args.weights_sha256, args.tokenizer_sha256,
                 args.tokenizer_config_sha256, args.preregistration, args.max_calls)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

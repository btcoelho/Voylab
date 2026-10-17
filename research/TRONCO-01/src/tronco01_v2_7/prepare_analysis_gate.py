"""Hash every checkpoint artifact and runtime input; leave documents in draft."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--weights", type=Path, required=True,
                    help="Exact model.safetensors path; read for SHA-256 only, never loaded")
args = parser.parse_args()
weights = args.weights.expanduser().absolute()
if weights.name != "model.safetensors" or not weights.is_file():
    raise FileNotFoundError(f"expected an existing model.safetensors: {weights}")
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

prereg_path = ROOT / "preregistration_draft.json"
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
schedule = ROOT / "development_schedule.jsonl"
prereg["schedule"]["schedule_sha256"] = sha(schedule)
expected_artifacts = prereg["experimental_condition"]["checkpoint_artifacts"]
artifact_paths = {p.name: p for p in weights.parent.iterdir() if p.is_file()}
if set(artifact_paths) != set(expected_artifacts):
    raise RuntimeError(f"checkpoint file set differs from preregistration: actual={sorted(artifact_paths)}, expected={sorted(expected_artifacts)}")
actual_artifact_hashes = {name: sha(path) for name, path in artifact_paths.items()}
if actual_artifact_hashes != expected_artifacts:
    raise RuntimeError("at least one checkpoint artifact differs from its preregistered hash")
prereg_path.write_text(json.dumps(prereg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

internal_names = [
    "preregistration_draft.json", "development_schedule.jsonl", "development_reference_private.jsonl",
    "SYSTEM_PROMPT.txt", "harness.py", "model_backend.py", "replay.py", "trial_runner.py",
    "mutation_check.py", "prepare_analysis_gate.py", "adapter_fake_model_smoke.py",
    "requirements-tokenizer.txt", "README.md",
    "ANALYSIS_GATE.md", "protocol_status.json", "tests/test_harness.py", "tests/test_replay.py",
    "tests/test_runner.py", "verify_draft_manifest.py", "runtime_environment.py",
    "fixtures/v23/public_schedule.jsonl",
]
files = [{"path": name, "sha256": sha(ROOT / name)} for name in internal_names]
external = [{"path": str(path.absolute()), "sha256": actual_artifact_hashes[name]}
            for name, path in sorted(artifact_paths.items())]
manifest = {
    "protocol": prereg["protocol"], "status": "draft_not_frozen",
    "preregistration_sha256": sha(prereg_path), "files": files, "external_files": external,
    "private_reference_sha256_not_for_model_prompt": sha(ROOT / "development_reference_private.jsonl"),
    "checkpoint_artifacts_expected": expected_artifacts,
    "checkpoint_hashes_match": actual_artifact_hashes == expected_artifacts,
    "inference_performed": False,
}
if not manifest["checkpoint_hashes_match"]:
    raise RuntimeError("checkpoint or tokenizer bytes differ from the candidate preregistration")
manifest_path = ROOT / "analysis_manifest_draft.json"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"manifest": str(manifest_path), "status": manifest["status"],
                  "internal_files": len(files), "external_files": len(external),
    "checkpoint_hashes_match": True, "checkpoint_artifacts": len(external), "model_weights_loaded": False,
                  "inference_performed": False}, indent=2))

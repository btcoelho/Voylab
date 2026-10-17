"""Verify the candidate manifest's hashes and prove draft status blocks entry."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from harness import FrozenManifestGuard, ResumeIntegrityError

manifest_path = ROOT / "analysis_manifest_draft.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
guard = FrozenManifestGuard(manifest_path)
verified = guard.verify(allow_draft=True)
assert manifest["status"] == "draft_not_frozen"
assert verified["__manifest_status__"] == "draft_not_frozen"
assert verified["preregistration_draft.json"] == manifest["preregistration_sha256"]
prereg = json.loads((ROOT / "preregistration_draft.json").read_text(encoding="utf-8"))
expected = prereg["experimental_condition"]["checkpoint_artifacts"]
external_entries = manifest["external_files"]
assert {Path(entry["path"]).name for entry in external_entries} == set(expected)
assert sum(name.startswith("external:") for name in verified) == len(expected)
try:
    guard.verify()
    production_blocked = False
except ResumeIntegrityError:
    production_blocked = True
assert production_blocked
result = {"status": manifest["status"], "internal_files_verified": len(manifest["files"]),
          "external_files_verified": len(manifest["external_files"]),
          "all_preregistered_artifacts_covered": True,
          "all_hashes_match": True, "production_guard_blocks_draft": production_blocked,
          "weights_loaded": False, "inference_performed": False}
out = ROOT / "results/manifest_preflight_v2_7.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))

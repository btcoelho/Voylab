"""Run targeted mutants only after their unmodified regression test passes."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
SOURCE = (PACKAGE / "harness.py").read_text(encoding="utf-8")
RUNNER = '''import io,json,sys,unittest
stream=io.StringIO()
suite=unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
print(json.dumps({"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"successful":result.wasSuccessful(),"log":stream.getvalue()}))
'''
MUTANTS = {
    "duplicate_candidate_check_removed": (
        'or len(set(action["candidate_model_codes"])) != len(action["candidate_model_codes"])',
        "or False", "test_duplicate_candidate_evidence_and_location_values_are_rejected"),
    "resume_fingerprint_check_removed": (
        '    if starts[0].get("trial_fingerprint") != fingerprint:\n',
        "    if False:\n", "test_changed_in_memory_schedule_is_blocked_by_journal_fingerprint"),
    "entry_manifest_guard_skipped_on_resume": (
        "    verified_inputs = generation_guard()\n",
        '    verified_inputs = (generation_guard() if not Path(event_path).exists() else {"__manifest_status__":"frozen_before_inference", "preregistration_draft.json":preregistration_sha256})\n',
        "test_complete_resume_runs_guard_even_when_schedule_is_unchanged"),
}
REPLAY_MUTATION = ("elif v=='rejected': cert=any(not prediction(working,r) for r in cited)",
                   "elif v=='rejected': cert=True",
                   "test_manual_semantic_certificate_and_component_cases")


def run_source(source: str, test: str) -> dict:
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        (root / "harness.py").write_text(source, encoding="utf-8")
        shutil.copy2(PACKAGE / "model_backend.py", root / "model_backend.py")
        shutil.copy2(PACKAGE / "tests/test_harness.py", root / "test_harness.py")
        proc = subprocess.run([sys.executable, "-c", RUNNER, f"test_harness.HarnessTests.{test}"],
                              cwd=root, capture_output=True, text=True)
        if proc.returncode:
            raise RuntimeError(proc.stdout + proc.stderr)
        return json.loads(proc.stdout)


def main() -> dict:
    cases = {}
    for name, (old, new, test) in MUTANTS.items():
        if SOURCE.count(old) != 1:
            raise RuntimeError(f"non-unique mutation anchor: {name}")
        baseline = run_source(SOURCE, test)
        if baseline["tests_run"] != 1 or not baseline["successful"] or baseline["errors"]:
            raise AssertionError(f"baseline invalid: {name}: {baseline}")
        mutant = run_source(SOURCE.replace(old, new, 1), test)
        killed = mutant["tests_run"] == 1 and mutant["errors"] == 0 and mutant["failures"] > 0
        cases[name] = {"test": test, "baseline": baseline, "mutant": mutant,
                       "killed_by_assertion": killed}
    old, new, test = REPLAY_MUTATION
    replay_source = (PACKAGE / "replay.py").read_text(encoding="utf-8")
    if replay_source.count(old) != 1:
        raise RuntimeError("non-unique replay mutation anchor")
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / "package"
        shutil.copytree(PACKAGE, root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_runner.py"],
                              cwd=root, capture_output=True, text=True)
        baseline_replay = {"exit_code": proc.returncode, "log": proc.stdout + proc.stderr}
        if proc.returncode:
            raise AssertionError("manual semantic baseline failed: " + baseline_replay["log"])
        mutated_source = replay_source.replace(old, new, 1)
        (root / "replay.py").write_text(mutated_source, encoding="utf-8")
        proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_runner.py"],
                              cwd=root, capture_output=True, text=True)
        semantic_mutant = {"exit_code": proc.returncode, "failures_are_assertions": "AssertionError" in proc.stderr,
                           "errors": "ERROR:" in proc.stderr, "log": proc.stdout + proc.stderr}
    semantic_killed = (baseline_replay["exit_code"] == 0 and semantic_mutant["exit_code"] != 0
                       and semantic_mutant["failures_are_assertions"] and not semantic_mutant["errors"])
    result = {"protocol": "TRONCO-01-v2.7-offline-preflight",
              "original_v25_result_valid": False,
              "original_error": "The archived v2.5 mutation runs failed to import model_backend and were incorrectly counted as kills.",
              "method": "Copy required dependencies; verify each unmodified target passes; count a kill only for an assertion failure with zero errors.",
              "new_model_calls": 0, "model_weights_loaded": False,
              "baselines_pass": all(x["baseline"]["successful"] for x in cases.values()),
              "valid_kills": sum(x["killed_by_assertion"] for x in cases.values()), "cases": cases,
              "semantic_refutation_certificate_mutation": {"test": test,"baseline": baseline_replay,
                    "mutant": semantic_mutant,"killed_by_assertion": semantic_killed}}
    result["total_valid_kills"] = result["valid_kills"] + int(semantic_killed)
    out = PACKAGE / "results/mutation_check_v2_7.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["valid_kills"] != len(cases) or not semantic_killed:
        raise AssertionError("a targeted mutant survived or the run was inconclusive")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))

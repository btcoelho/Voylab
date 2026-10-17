"""Run the v3 pilot once on development worlds. One attempt only (lock file); results and transcripts are written, never overwritten."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot_harness as H  # noqa: E402
import select_worlds as S  # noqa: E402


def file_hashes():
    names = ["pilot_harness.py", "select_worlds.py", "run_pilot.py", "hf_backend.py", "../env_v3.py", "../generator_v3.py",
             "../scoring.py", "../audit_v3.py"]
    return {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--backend", choices=["hf", "fake_random", "fake_garbage", "fake_undetermined"], required=True)
    ap.add_argument("--snapshot", help="HF snapshot directory (hf backend)")
    ap.add_argument("--limit", type=int, default=None, help="dry runs only")
    ap.add_argument("--schema", choices=["state", "phase"], default="state",
                    help="state: ids restricted to the shown state (round 2 on); phase: round-1 schema")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    lock = a.out / "attempt_once.lock"
    if a.backend == "hf":
        if lock.exists():
            sys.exit("a real run was already attempted in this folder; refusing to run again")
        lock.write_text("attempt 1\n")
    worlds = S.pilot_worlds()[: a.limit]
    pass_state = a.backend != "hf"
    if a.backend == "hf":
        from hf_backend import HFBackend
        backend = HFBackend(a.snapshot)
    else:
        import fake_backends as F
        backend = {"fake_random": F.RandomValid(0), "fake_garbage": F.Garbage(), "fake_undetermined": F.CommitUndetermined()}[a.backend]
    eps = [H.run_episode(w, backend, pass_state=pass_state, state_schema=a.schema == "state") for w in worlds]
    summary = {"backend": backend.name, "worlds": len(worlds), "schema": a.schema, "worlds_sha256": S.worlds_sha(worlds),
               "code_sha256": file_hashes(), "python": platform.python_version(), "aggregate": H.aggregate(eps)}
    (a.out / "transcripts.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in eps) + "\n", encoding="utf-8", newline="\n")
    (a.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

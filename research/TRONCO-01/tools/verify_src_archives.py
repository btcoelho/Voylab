"""Check that src/ is a byte-exact extraction of the archived packages (read-only).

The archives are only opened for reading; their SHA-256 is computed before and after
and must not change. Each entry of MAPPING says: files under `inner` inside `archive`
must exist under `src_dir` with identical bytes. `src_dir` may hold no other files
(ignoring __pycache__), so a silent addition or deletion is also detected.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAPPING = [
    {"src_dir": "src/tronco01_v2_7",
     "archive": "packages/TRONCO01_ENSAIO_MODELO_V2_7_REPRODUCIBLE_2026-10-17.zip",
     "inner": "work/TRONCO01_TRIAL_v2_7/"},
    {"src_dir": "src/m17",
     "archive": "packages/TRONCO01_G2_SENTINELA_REPRODUCIBLE_2026-10-17.zip",
     "inner": "work/M17_DESCOBERTA_DIAGNOSTICO/"},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root: Path = ROOT, mapping=MAPPING) -> dict:
    report = {"mappings": [], "failures": []}
    for entry in mapping:
        archive = root / entry["archive"]
        src = root / entry["src_dir"]
        before = sha(archive)
        identical, different, missing = 0, [], []
        with zipfile.ZipFile(archive, "r") as z:
            names = [n for n in z.namelist()
                     if n.startswith(entry["inner"]) and not n.endswith("/") and "__pycache__" not in n]
            expected = set()
            for name in names:
                rel = name[len(entry["inner"]):]
                expected.add(rel)
                path = src / rel
                if not path.is_file():
                    missing.append(rel)
                elif path.read_bytes() != z.read(name):
                    different.append(rel)
                else:
                    identical += 1
        present = {p.relative_to(src).as_posix() for p in src.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts}
        extra = sorted(present - expected)
        after = sha(archive)
        item = {"src_dir": entry["src_dir"], "archive": entry["archive"], "archive_sha256": before,
                "archive_unchanged_by_check": before == after, "archive_files": len(names),
                "identical": identical, "different": sorted(different), "missing_in_src": sorted(missing),
                "extra_in_src": extra}
        report["mappings"].append(item)
        if different or missing or extra or before != after or not names:
            report["failures"].append(entry["src_dir"])
    return report


def main() -> int:
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

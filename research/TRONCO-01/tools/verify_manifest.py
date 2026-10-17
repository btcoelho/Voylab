"""Verify SHA256SUMS.txt without modifying it, and say exactly how each file matched.

Statuses:
  exact                 current bytes hash to the manifest value.
  cr_only_difference    the manifest value is reproduced from the current bytes only after
                        re-inserting carriage returns (all lines CRLF, or one stray CR).
                        The text is identical apart from CR characters.
  MISMATCH / MISSING    the content differs, or the file is absent. These fail the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def classify(data: bytes, expected: str) -> str:
    if sha(data) == expected:
        return "exact"
    lf = data.replace(b"\r\n", b"\n")
    if sha(lf.replace(b"\n", b"\r\n")) == expected:
        return "cr_only_difference"
    for i, c in enumerate(lf):
        if c == 10 and sha(lf[:i] + b"\r" + lf[i:]) == expected:
            return "cr_only_difference"
    return "MISMATCH"


def verify(manifest: Path) -> dict:
    results = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip().lstrip("*")
        path = (manifest.parent / rel).resolve()
        if manifest.parent.resolve() not in path.parents:
            results[rel] = "MISMATCH"
        elif not path.is_file():
            results[rel] = "MISSING"
        else:
            results[rel] = classify(path.read_bytes(), digest)
    counts = Counter(results.values())
    return {"manifest": manifest.name, "files": len(results), "counts": dict(counts),
            "cr_only_difference": sorted(k for k, v in results.items() if v == "cr_only_difference"),
            "failures": sorted(k for k, v in results.items() if v in {"MISMATCH", "MISSING"})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "SHA256SUMS.txt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.manifest)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

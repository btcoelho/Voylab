"""READ-ONLY inventory of the machine that will run the pilot. Standard library only. Prints JSON; changes nothing.

Run it where the model will run (for the v2.7 pilot that was a WSL distribution): python check_local_env.py > env.json
"""
import hashlib
import importlib.metadata as md
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

PKGS = ["torch", "transformers", "lm-format-enforcer", "llguidance", "xgrammar", "unsloth", "bitsandbytes", "peft", "accelerate", "numpy", "tokenizers"]


def ver(p):
    try:
        return md.version(p)
    except md.PackageNotFoundError:
        return None


def sha(path, limit=50_000_000):
    if path.stat().st_size > limit:
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_hf(root):
    out = []
    for snap in sorted(Path(root).glob("models--*/snapshots/*")):
        files = {}
        for f in snap.iterdir():
            if f.is_file() or f.is_symlink():
                try:
                    files[f.name] = {"bytes": f.stat().st_size, "sha256_if_small": sha(f) if f.suffix in (".json", ".txt", ".model") else None}
                except OSError as e:
                    files[f.name] = {"error": str(e)}
        out.append({"snapshot": str(snap), "files": files})
    return out


def find_adapters(roots, maxdepth=6):
    found = []
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        base = len(root.parts)
        for dp, dn, fn in os.walk(root):
            if len(Path(dp).parts) - base > maxdepth:
                dn[:] = []
                continue
            if "adapter_config.json" in fn:
                found.append(dp)
    return found[:20]


def nvidia():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or r.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unavailable: {e}"


if __name__ == "__main__":
    hf = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
    print(json.dumps({"python": sys.version, "platform": platform.platform(), "in_wsl": "microsoft" in platform.release().lower(),
                      "packages": {p: ver(p) for p in PKGS}, "gpu": nvidia(),
                      "hf_cache": scan_hf(hf) if hf.exists() else "no HF cache at " + str(hf),
                      "adapter_dirs_under_home": find_adapters([Path.home()])}, indent=2))

"""V4 model run (docs/V3_CONSULTAS.md §15): 225 development worlds, one episode per world, resumable without duplicate calls.

Resumption: every model call is appended to calls.jsonl, keyed by (uid, turn, prompt sha256, system sha256), and
flushed before the episode continues. On restart, a key already present is answered from the log instead of the API, so an
interrupted episode is replayed exactly and no call is ever made twice. Finished episodes go to episodes.jsonl.
Guards: the frozen pre-registration (PREREGISTO_CONGELADO.json) must match the current §15 text and code hashes, or the
run refuses to start; a run folder that already has summary.json is never run again.
Never touches validation or blind seeds: the worlds come from variants.build("V4") (development seeds 91xxx) and every
world id is checked against that range.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
REPO = V3.parent.parent.parent
sys.path[:0] = [str(HERE), str(V3), str(V3 / "instrument")]
import pilot_harness as H  # noqa: E402

FROZEN_DIR = V3 / "results" / "modelos_v4"
FROZEN = FROZEN_DIR / "PREREGISTO_CONGELADO.json"            # Claude M1 (§15); kept as it was frozen
PROVIDERS = {"anthropic": "PREREGISTO_CONGELADO.json", "deepseek": "PREREGISTO_CONGELADO_DEEPSEEK.json",
             "deepseek_v32": "PREREGISTO_CONGELADO_DEEPSEEK_V32.json"}
PROMPT_OF = {"anthropic": "v3.1", "deepseek": "v3.1", "deepseek_v32": "v3.2"}
CODE = ["pilot/pilot_harness.py", "pilot/anthropic_backend.py", "pilot/deepseek_backend.py", "pilot/run_v4_models.py", "env_v3.py", "generator_v3.py",
        "scoring.py", "instrument/variants.py", "instrument/grid.py"]
DEV_SEED_RANGE = range(91000, 92000)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def section(n: int = 15) -> str:
    t = (REPO / "docs" / "V3_CONSULTAS.md").read_text(encoding="utf-8")
    i = t.index(f"## {n}. ")
    j = t.find(f"\n## {n + 1}. ", i)
    return t[i:] if j < 0 else t[i:j]


def section15() -> str:
    return section(15)


def prereg_text(provider: str) -> str:
    """Claude: §15. DeepSeek: §15 plus the deviation §16 (both frozen together)."""
    if provider == "anthropic":
        return section15()
    if provider == "deepseek":
        return section15() + section(16)
    return section15() + section(16) + section(18)


def code_hashes() -> dict:
    return {n: sha((V3 / n).read_bytes()) for n in CODE}


def freeze(model: str, commit: str, provider: str = "anthropic") -> dict:
    d = {"preregisto": "docs/V3_CONSULTAS.md §15" + (" + §16" if provider != "anthropic" else ""), "provider": provider,
         "section15_sha256": sha(prereg_text(provider).encode()), "commit": commit,
         "model_requested": model, "temperature": 0.0, "max_tokens": 1024, "prompt": PROMPT_OF[provider], "mode": "state_cards_object",
         "worlds": "variants.build('V4'), 225 development worlds", "code_sha256": code_hashes()}
    path = FROZEN_DIR / PROVIDERS[provider]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


def check_frozen(model: str, provider: str = "anthropic") -> dict:
    path = FROZEN_DIR / PROVIDERS[provider]
    if not path.exists():
        sys.exit("pre-registration not frozen; refusing to run")
    f = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    if f["section15_sha256"] != sha(prereg_text(provider).encode()):
        problems.append("§15 changed after freezing")
    if f["model_requested"] != model:
        problems.append(f"model {model} differs from frozen {f['model_requested']}")
    for n, h in code_hashes().items():
        if f["code_sha256"].get(n) != h:
            problems.append(f"{n} changed after freezing")
    if problems:
        sys.exit("refusing to run: " + "; ".join(problems) + " (document a deviation and re-freeze first)")
    return f


def worlds():
    import variants as VA
    ws, _ = VA.build("V4")
    for w in ws:
        seed = int(str(w["world_id"]).split("-")[1]) if str(w["world_id"]).count("-") else None
        assert seed is None or seed in DEV_SEED_RANGE, f"non-development world {w['world_id']}"
    assert len(ws) == 225
    return ws


class Logged(H.Backend):
    """Wraps a backend: answers from calls.jsonl when the same call was already made, otherwise calls and logs first."""

    def __init__(self, inner, log: Path):
        self.inner, self.log, self.name = inner, log, inner.name
        self.cache = {}
        if log.exists():
            for line in log.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.cache[r["key"]] = r
        self.uid, self.turn, self.fresh_calls = None, 0, 0

    def generate(self, system, user, schema, state=None):
        key = f"{self.uid}|{self.turn}|{sha(system.encode())[:16]}|{sha(user.encode())[:16]}"
        self.turn += 1
        if key in self.cache:
            return self.cache[key]["output"]
        out = self.inner.generate(system, user, schema)
        rec = {"key": key, "uid": self.uid, "output": out, "meta": getattr(self.inner, "last_meta", {})}
        with self.log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
        self.cache[key] = rec
        self.fresh_calls += 1
        return out


def run(out: Path, backend, limit=None, prompt: str = "v3.1") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    if (out / "summary.json").exists():
        sys.exit("this run folder is already finished; refusing to run again")
    lb = Logged(backend, out / "calls.jsonl")
    done = set()
    ep_file = out / "episodes.jsonl"
    if ep_file.exists():
        done = {json.loads(l)["uid"] for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip()}
    ws = worlds()[:limit]
    for w in ws:
        if w["uid"] in done:
            continue
        lb.uid, lb.turn = w["uid"], 0
        e = H.run_episode(w, lb, mode="state_cards_object", prompt=prompt)
        e["uid"] = w["uid"]
        with ep_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
            fh.flush()
    eps = [json.loads(l) for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"episodes": len(eps), "fresh_calls_this_session": lb.fresh_calls, "aggregate": H.aggregate(eps)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--provider", choices=list(PROVIDERS), default="anthropic")
    ap.add_argument("--freeze", metavar="COMMIT", help="write the frozen pre-registration (no calls) and exit")
    a = ap.parse_args()
    if a.freeze:
        print(json.dumps(freeze(a.model, a.freeze, a.provider), indent=1))
        return
    f = check_frozen(a.model, a.provider)
    if a.provider == "anthropic":  # noqa: SIM114
        from anthropic_backend import AnthropicBackend
        b = AnthropicBackend(a.model, temperature=f["temperature"], max_tokens=f["max_tokens"])
    else:  # deepseek, deepseek_v32
        from deepseek_backend import DeepSeekBackend
        b = DeepSeekBackend(a.model, temperature=f["temperature"], max_tokens=f["max_tokens"])
    res = run(a.out, b, prompt=f["prompt"])
    served = sorted({json.loads(l)["meta"].get("model_served") for l in (a.out / "calls.jsonl").read_text().splitlines() if l.strip()} - {None})
    res.update({"model_requested": a.model, "models_served": served, "frozen": f, "execution_log": b.execution_log})
    if res["episodes"] == 225:
        (a.out / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("episodes", "fresh_calls_this_session", "models_served")}, indent=1))


if __name__ == "__main__":
    main()

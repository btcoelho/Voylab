"""Ronda 3 (§20): o mesmo modelo DeepSeek com modo de raciocínio, prompt v3.1, num subconjunto equilibrado de 45 mundos.
Paralelo (5 episódios ao mesmo tempo, cada um com o seu backend), retoma sem duplicar chamadas (mesmo registo calls.jsonl),
paragem automática se o saldo da conta descer abaixo do limite. O raciocínio do modelo não é guardado (só o seu tamanho)."""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import pilot_harness as H  # noqa: E402
import run_v4_models as R  # noqa: E402

FROZEN = R.FROZEN_DIR / "PREREGISTO_CONGELADO_DEEPSEEK_RACIOCINIO.json"
CODE = R.CODE + ["pilot/run_v4_reasoning.py"]
PARAMS = {"model": "deepseek-chat", "temperature": 0.0, "max_tokens": 32000, "extra_body": {"thinking": {"type": "enabled"}},
          "prompt": "v3.1", "subset": "15 por veredicto alvo, random.Random('tronco01-v4-raciocinio-45')", "workers": 5,
          "stop_if_balance_below_usd": 3.0}


def subset(ws):
    rng = random.Random("tronco01-v4-raciocinio-45")
    out = []
    for t in ("rejected", "supported", "undetermined"):
        pool = sorted([w for w in ws if w["reference"]["target_verdict"] == t], key=lambda w: w["uid"])
        out += rng.sample(pool, 15)
    return out


def prereg():
    return R.section15() + R.section(16) + R.section(20)


def code_hashes():
    return {n: R.sha((R.V3 / n).read_bytes()) for n in CODE}


def freeze(commit):
    d = {"preregisto": "docs/V3_CONSULTAS.md §15 + §16 + §20", "sha256": R.sha(prereg().encode()), "commit": commit,
         "params": PARAMS, "uids": [w["uid"] for w in subset(R.worlds())], "code_sha256": code_hashes()}
    FROZEN.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


def check():
    f = json.loads(FROZEN.read_text(encoding="utf-8"))
    bad = [n for n, h in code_hashes().items() if f["code_sha256"].get(n) != h]
    if f["sha256"] != R.sha(prereg().encode()) or bad or f["params"] != PARAMS:
        sys.exit(f"refusing to run: pre-registration or code changed {bad}")
    return f


def balance():
    import requests
    r = requests.get("https://api.deepseek.com/user/balance", timeout=30, verify="/root/.ccr/ca-bundle.crt",
                     headers={"Authorization": "Bearer " + os.environ["DEEPSEEK_API_KEY"]})
    return float(r.json()["balance_infos"][0]["total_balance"])


class EpisodeLogged(H.Backend):
    def __init__(self, inner, log, cache, lock, uid):
        self.inner, self.log, self.cache, self.lock, self.uid, self.turn, self.fresh = inner, log, cache, lock, uid, 0, 0
        self.name = inner.name

    def generate(self, system, user, schema, state=None):
        key = f"{self.uid}|{self.turn}|{R.sha(system.encode())[:16]}|{R.sha(user.encode())[:16]}"
        self.turn += 1
        if key in self.cache:
            return self.cache[key]["output"]
        out = self.inner.generate(system, user, schema)
        rec = {"key": key, "uid": self.uid, "output": out, "meta": self.inner.last_meta}
        with self.lock:
            with self.log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self.cache[key] = rec
        self.fresh += 1
        return out


def run(out: Path, make_backend, worlds, workers=5, balance_fn=None, floor=3.0):
    out.mkdir(parents=True, exist_ok=True)
    log, ep_file = out / "calls.jsonl", out / "episodes.jsonl"
    cache = {}
    if log.exists():
        for l in log.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                cache[r["key"]] = r
    done = set()
    if ep_file.exists():
        done = {json.loads(l)["uid"] for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip()}
    lock, stop, stats = threading.Lock(), threading.Event(), {"fresh": 0, "execution_log": []}

    def one(w):
        if stop.is_set():
            return
        if balance_fn is not None and balance_fn() < floor:
            stop.set()
            return
        b = make_backend()
        lb = EpisodeLogged(b, log, cache, lock, w["uid"])
        e = H.run_episode(w, lb, mode="state_cards_object", prompt=PARAMS["prompt"])
        e["uid"] = w["uid"]
        with lock:
            with ep_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
            stats["fresh"] += lb.fresh
            stats["execution_log"] += b.execution_log

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, [w for w in worlds if w["uid"] not in done]))
    n = sum(1 for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip()) if ep_file.exists() else 0
    return {"episodes": n, "fresh_calls_this_session": stats["fresh"], "stopped_by_balance": stop.is_set(),
            "execution_log": stats["execution_log"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--freeze", metavar="COMMIT")
    a = ap.parse_args()
    if a.freeze:
        print(json.dumps({k: v for k, v in freeze(a.freeze).items() if k != "code_sha256"}, indent=1))
        return
    f = check()
    from deepseek_backend import DeepSeekBackend
    ws = [w for w in R.worlds() if w["uid"] in set(f["uids"])]
    res = run(a.out, lambda: DeepSeekBackend(PARAMS["model"], PARAMS["temperature"], PARAMS["max_tokens"], timeout=900,
                                             extra_body=PARAMS["extra_body"]),
              ws, PARAMS["workers"], balance, PARAMS["stop_if_balance_below_usd"])
    res["balance_end_usd"] = balance()
    if res["episodes"] == 45:
        (a.out / "summary.json").write_text(json.dumps({**res, "frozen": f}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

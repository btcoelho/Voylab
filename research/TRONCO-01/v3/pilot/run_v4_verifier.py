"""Experiência agente + verificador (§23): os mesmos 45 mundos de §20, DeepSeek sem raciocínio como agente, dois braços:
verificador por código (exato) e verificador por modelo (DeepSeek sem raciocínio, chamada separada por afirmação).
Retoma: cada episódio terminado fica em episodes.jsonl; um episódio interrompido repete-se do início (as chamadas desse
episódio voltam a ser feitas e ficam registadas como repetidas)."""
from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / "instrument")]
import pilot_harness as H  # noqa: E402
import run_v4_models as R  # noqa: E402
import run_v4_reasoning as RR  # noqa: E402
import verified_agent as VA  # noqa: E402

FROZEN = R.FROZEN_DIR / "PREREGISTO_CONGELADO_VERIFICADOR.json"
CODE = R.CODE + ["pilot/run_v4_reasoning.py", "pilot/verified_agent.py", "pilot/run_v4_verifier.py"]
PARAMS = {"agent_model": "deepseek-chat", "verifier_model": "deepseek-chat", "temperature": 0.0, "agent_max_tokens": 1024,
          "verifier_max_tokens": 8, "prompt": "v3.1", "max_rounds": 3, "workers": 5, "worlds": "os 45 de §20",
          "arms": ["code", "llm"], "stop_if_balance_below_usd": 1.0}


def prereg():
    return R.section15() + R.section(16) + R.section(23)


def code_hashes():
    return {n: R.sha((R.V3 / n).read_bytes()) for n in CODE}


def freeze(commit):
    f20 = json.loads(RR.FROZEN.read_text(encoding="utf-8"))
    d = {"preregisto": "docs/V3_CONSULTAS.md §15 + §16 + §23", "sha256": R.sha(prereg().encode()), "commit": commit,
         "params": PARAMS, "uids": f20["uids"], "code_sha256": code_hashes()}
    FROZEN.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


def check():
    f = json.loads(FROZEN.read_text(encoding="utf-8"))
    bad = [n for n, h in code_hashes().items() if f["code_sha256"].get(n) != h]
    if f["sha256"] != R.sha(prereg().encode()) or bad or f["params"] != PARAMS:
        sys.exit(f"refusing: pre-registration or code changed {bad}")
    return f


def run_arm(out: Path, arm: str, worlds, make_agent, make_verifier_backend, workers=5, balance_fn=None, floor=1.0):
    out.mkdir(parents=True, exist_ok=True)
    ep_file = out / "episodes.jsonl"
    done = set()
    if ep_file.exists():
        done = {json.loads(l)["uid"] for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip()}
    lock, stop = threading.Lock(), threading.Event()

    def one(w):
        if stop.is_set() or (balance_fn is not None and balance_fn() < floor):
            stop.set()
            return
        agent = make_agent()
        ver = VA.CodeVerifier() if arm == "code" else VA.LLMVerifier(make_verifier_backend())
        va = VA.VerifiedAgent(agent, ver, PARAMS["max_rounds"])
        e = H.run_episode(w, va, mode="state_cards_object", prompt=PARAMS["prompt"], pass_state=True)
        e.update({"uid": w["uid"], "arm": arm, "rounds": va.rounds_log, "verifier_log": ver.log,
                  "agent_execution_log": getattr(agent, "execution_log", [])})
        with lock:
            with ep_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, [w for w in worlds if w["uid"] not in done]))
    n = sum(1 for l in ep_file.read_text(encoding="utf-8").splitlines() if l.strip())
    return {"arm": arm, "episodes": n, "stopped_by_balance": stop.is_set()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="COMMIT")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        print(json.dumps({k: v for k, v in freeze(a.freeze).items() if k not in ("code_sha256", "uids")}, indent=1))
        return
    f = check()
    from deepseek_backend import DeepSeekBackend
    ws = [w for w in R.worlds() if w["uid"] in set(f["uids"])]
    base = R.FROZEN_DIR / "M1-DS-VER"
    res = []
    for arm in PARAMS["arms"]:
        res.append(run_arm(base / arm, arm, ws,
                           lambda: DeepSeekBackend(PARAMS["agent_model"], PARAMS["temperature"], PARAMS["agent_max_tokens"]),
                           lambda: DeepSeekBackend(PARAMS["verifier_model"], PARAMS["temperature"], PARAMS["verifier_max_tokens"]),
                           PARAMS["workers"], RR.balance, PARAMS["stop_if_balance_below_usd"]))
    res_all = {"arms": res, "balance_end_usd": RR.balance()}
    (base / "summary.json").write_text(json.dumps(res_all, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res_all, indent=1))


if __name__ == "__main__":
    main()

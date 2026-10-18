"""Validação V4 (§22): o mesmo modelo DeepSeek com raciocínio, prompt v3.1, nos mundos de validação gerados do beacon.
Passos: --freeze (anuncia a ronda futura do beacon; sem chamadas ao modelo) -> --generate (depois de a ronda sair: busca o
valor, gera os mundos, grava a lista) -> --run (corrida única). Retoma sem duplicar; pára se o saldo descer do limite."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / "instrument")]
import run_v4_models as R  # noqa: E402
import run_v4_reasoning as RR  # noqa: E402
import validation_v4 as VV  # noqa: E402

OUT = R.FROZEN_DIR / "VALIDACAO"
FROZEN = R.FROZEN_DIR / "PREREGISTO_CONGELADO_VALIDACAO.json"
CODE = RR.CODE + ["pilot/run_v4_validation.py", "instrument/validation_v4.py"]
CHAIN = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"   # drand quicknet
PARAMS = {"model": "deepseek-chat", "temperature": 0.0, "max_tokens": 64000, "extra_body": {"thinking": {"type": "enabled"}},
          "prompt": "v3.1", "workers": 5, "stop_if_balance_below_usd": 1.0, "drand_chain": CHAIN,
          "seeds_rule": "validation_v4.derive_seeds(randomness), 3 seeds", "sample_rule": "≤ 75 por veredicto alvo"}


def prereg():
    return R.section15() + R.section(16) + R.section(20) + R.section(22)


def code_hashes():
    return {n: R.sha((R.V3 / n).read_bytes()) for n in CODE}


def freeze(commit, minutes_ahead=30):
    import requests
    info = requests.get(f"{VV.DRAND}/{CHAIN}/info", timeout=30, verify="/root/.ccr/ca-bundle.crt").json()
    now_round = int((time.time() - info["genesis_time"]) // info["period"]) + 1
    rnd = now_round + int(minutes_ahead * 60 // info["period"])
    d = {"preregisto": "docs/V3_CONSULTAS.md §15 + §16 + §20 + §22", "sha256": R.sha(prereg().encode()), "commit": commit,
         "params": PARAMS, "drand_round": rnd, "drand_round_time_utc": info["genesis_time"] + (rnd - 1) * info["period"],
         "round_at_freeze": now_round, "code_sha256": code_hashes()}
    FROZEN.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


def check():
    f = json.loads(FROZEN.read_text(encoding="utf-8"))
    bad = [n for n, h in code_hashes().items() if f["code_sha256"].get(n) != h]
    if f["sha256"] != R.sha(prereg().encode()) or bad or f["params"] != PARAMS:
        sys.exit(f"refusing: pre-registration or code changed {bad}")
    return f


def generate():
    f = check()
    b = VV.fetch_round(CHAIN, f["drand_round"])
    assert int(b["round"]) == f["drand_round"]
    ws, info = VV.build(b["randomness"])
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"drand": b, **info, "uids": [w["uid"] for w in ws]}
    (OUT / "PARTICAO.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {k: v for k, v in rec.items() if k != "uids"}


def worlds():
    rec = json.loads((OUT / "PARTICAO.json").read_text(encoding="utf-8"))
    ws, _ = VV.build(rec["drand"]["randomness"])
    assert [w["uid"] for w in ws] == rec["uids"]
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="COMMIT")
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        print(json.dumps({k: v for k, v in freeze(a.freeze).items() if k != "code_sha256"}, indent=1))
    elif a.generate:
        print(json.dumps(generate(), indent=1))
    elif a.run:
        check()
        if (OUT / "summary.json").exists():
            sys.exit("validation already run once; refusing")
        from deepseek_backend import DeepSeekBackend
        ws = worlds()
        RR.PARAMS["prompt"] = PARAMS["prompt"]
        res = RR.run(OUT, lambda: DeepSeekBackend(PARAMS["model"], PARAMS["temperature"], PARAMS["max_tokens"], timeout=1800,
                                                  extra_body=PARAMS["extra_body"]),
                     ws, PARAMS["workers"], RR.balance, PARAMS["stop_if_balance_below_usd"])
        res["balance_end_usd"] = RR.balance()
        if res["episodes"] == len(ws):
            (OUT / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

"""Corrida no PC do Bruno: modo programa com raciocínio (docs/TEXTO_ESPECIFICACAO.md §9.4) num modelo local via Ollama.

Só biblioteca padrão do Python. Usa as mesmas 18 amostras (obras 0 e 1) do teste do DeepSeek e grava
resultados_pc.jsonl numa linha por amostra. Retoma se for interrompido.

Uso (no PowerShell, dentro da pasta):  python rodar_pc.py qwen3.5:9b
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import programa as P  # noqa: E402

MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3.5:9b"
BASE = "http://localhost:11434"
OUT = HERE / "resultados_pc.jsonl"
SUBCONJUNTO = ("0", "1")


def extrair_json(texto: str) -> str:
    """Tira cercas de markdown e fica com o trecho entre a primeira { e a última }."""
    t = texto.strip()
    i, j = t.find("{"), t.rfind("}")
    if i == -1 or j == -1:
        return t
    return t[i:j + 1]


class Ollama:
    name = f"ollama:{MODEL}"

    def generate(self, system, user, schema, state=None):
        body = {"model": MODEL, "stream": False, "think": True,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "options": {"temperature": 0, "num_ctx": 16384, "num_predict": 12000}}
        req = urllib.request.Request(f"{BASE}/api/chat", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=1200) as r:
            d = json.loads(r.read())
        self.last_meta = {"done_reason": d.get("done_reason"), "tokens_saida": d.get("eval_count")}
        return extrair_json(d["message"]["content"])


def verificar_servidor():
    try:
        with urllib.request.urlopen(f"{BASE}/api/tags", timeout=10) as r:
            tags = [m["name"] for m in json.loads(r.read()).get("models", [])]
    except (urllib.error.URLError, OSError):
        sys.exit("O Ollama não responde em localhost:11434. Abre a aplicação Ollama e tenta de novo.")
    if MODEL not in tags:
        sys.exit(f"O modelo {MODEL} não está instalado. Corre: ollama pull {MODEL}\nInstalados: {tags}")


def main():
    verificar_servidor()
    amostras = [json.loads(l) for l in (HERE / "amostras.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    sub = [a for a in amostras if a["uid"].split("-")[0] in SUBCONJUNTO]
    feitas = set()
    if OUT.exists():
        feitas = {json.loads(l)["uid"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
    print(f"Modelo {MODEL}: {len(sub)} amostras, {len(feitas)} já feitas.", flush=True)
    for a in sub:
        if a["uid"] in feitas:
            continue
        t0 = time.time()
        erro, rel, log = None, None, {}
        try:
            rel, log = P.Programador(Ollama()).analisar([list(w) for w in a["palavras"]])
        except Exception as ex:  # noqa: BLE001  falha de execução fica registada, não interrompe a corrida
            erro = repr(ex)[:300]
        acerto = bool(rel) and rel.get("mais_provavel") == a["familia"]
        rec = {"uid": a["uid"], "familia": a["familia"], "modelo": MODEL,
               "mais_provavel": rel.get("mais_provavel") if rel else None, "acerto": acerto, "erro": erro,
               "segundos": round(time.time() - t0, 1), "codigo": rel.get("codigo") if rel else None,
               "justificacoes": rel.get("_justificacao") if rel else None, "log": log}
        with OUT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"{a['uid']:8s} família={a['familia']:4s} modelo={str(rec['mais_provavel']):14s} "
              f"{'OK' if acerto else '--'} {rec['segundos']}s {'ERRO' if erro else ''}", flush=True)
    recs = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    ac = sum(r["acerto"] for r in recs)
    print(f"\nTOTAL: {ac}/{len(recs)} acertos. Envia o ficheiro {OUT.name}.", flush=True)


if __name__ == "__main__":
    main()

"""§10.4: métricas relativas em textos longos. Língua (Perseus), artificial (Timm & Schinner), cifrado (Naibbe)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import medidas as M  # noqa: E402
import poc  # noqa: E402

E = Path("/tmp/claude-0/-home-claude/51d32a62-a497-52d7-81e7-d806958770e0/scratchpad/ext")
OUT = HERE / "resultados" / "fase1"
N = 5000


def excerto(obra, semente):
    old = poc.N_PALAVRAS
    poc.N_PALAVRAS = N
    try:
        return poc.texto_simples(poc.SRC / obra, semente)
    finally:
        poc.N_PALAVRAS = old


def amostras():
    rows = []
    for k, (obra, lang) in enumerate(sorted(poc.OBRAS.items())):
        rows.append({"classe": "lingua", "id": f"L-{k}", "grupo": obra, "palavras": excerto(obra, 2000 + k)})
    for s in range(1, 9):
        txt = (E / "timm" / f"s{s}" / "generate" / "generated_text.txt").read_text(encoding="utf-8")
        ws = [w for line in txt.splitlines() if not line.startswith("#") for w in line.replace(".", " ").split()]
        rows.append({"classe": "artificial", "id": f"T-{s}", "grupo": f"timm{s}", "palavras": [list(w) for w in ws[:N]]})
    latinas = [o for o, l in sorted(poc.OBRAS.items()) if l == "la"]
    for k, obra in enumerate(latinas):
        for j in range(2):
            plain = ["".join(w) for w in excerto(obra, 3000 + 10 * k + j)]
            tmp_in = E / f"nb_in_{k}_{j}.json"
            tmp_out = E / f"nb_out_{k}_{j}.json"
            tmp_in.write_text(json.dumps(plain))
            subprocess.run([sys.executable, str(E / "naibbe_run.py"), str(E / "naibbe-cipher"), str(tmp_in), str(tmp_out),
                            str(500 + 10 * k + j)], check=True, capture_output=True, text=True)
            ws = json.loads(tmp_out.read_text())
            rows.append({"classe": "cifrado", "id": f"N-{k}{j}", "grupo": obra, "palavras": [list(w) for w in ws[:N]]})
    return rows


def metricas(w):
    e, ic, am = M.entropia(w), M.coincidencia(w), M.amancio(w)
    dep, z, g, mi = M.dependencia(w, permutacoes=50), M.zipf(w), M.gaskell(w), M.mi_decaimento(w)
    per = max(v for p, v in ic["ic_por_periodo"].items() if int(p) > 1)
    return {"h2_h1_palavra": e["h2_palavra"] / e["h1"], "h2_h1_fluxo": e["h2_fluxo"] / e["h1"],
            "ic_periodo_max_sobre_ic": per / ic["ic"],
            "amancio_bigramas": am["bigramas_repetidos_razao"], "amancio_h_seguinte": am["h_palavra_seguinte_razao"],
            "mi_fronteira_sobre_baralhado": dep["mi_fronteira"] / dep["mi_baralhado_media"] if dep["mi_baralhado_media"] else None,
            "mi_razao_I8_I1": mi["razao_I8_I1"], "zipf_declive": z["declive"], "zipf_r2": z["r2"],
            "wordlen_autocorr": g["wordlen_autocorr"], "compressao": g["compressao"]}


def auc(a, b):
    return sum((x > y) + 0.5 * (x == y) for x in a for y in b) / (len(a) * len(b))


def main():
    rows = amostras()
    for r in rows:
        r["m"] = metricas(r["palavras"])
        r["n_palavras"] = len(r["palavras"])
    nomes = list(rows[0]["m"])
    res = {}
    for p, q in (("lingua", "artificial"), ("lingua", "cifrado"), ("cifrado", "artificial")):
        lst = []
        for c in nomes:
            a = [r["m"][c] for r in rows if r["classe"] == p and r["m"][c] is not None]
            b = [r["m"][c] for r in rows if r["classe"] == q and r["m"][c] is not None]
            u = auc(a, b)
            lst.append({"metrica": c, "auc": round(max(u, 1 - u), 3), "maior_em": p if u >= 0.5 else q,
                        "completa": u in (0.0, 1.0)})
        lst.sort(key=lambda x: -x["auc"])
        res[f"{p}_vs_{q}"] = lst
    valores = [{"id": r["id"], "classe": r["classe"], "n_palavras": r["n_palavras"],
                **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r["m"].items()}} for r in rows]
    (OUT / "relativas.json").write_text(json.dumps({"auc": res, "valores": valores}, ensure_ascii=False, indent=1))
    for k, v in res.items():
        print(k, "completas:", [x["metrica"] for x in v if x["completa"]])
        for x in v[:4]:
            print("   ", x)


if __name__ == "__main__":
    main()

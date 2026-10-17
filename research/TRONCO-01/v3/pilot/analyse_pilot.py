"""Re-derive the pilot numbers from transcripts.jsonl alone (replaying every logged output through a fresh Episode),
then compare with summary.json, the ex-ante predictions and the reference policies on the same worlds."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import env_v3 as E  # noqa: E402
import pilot_harness as H  # noqa: E402
import select_worlds as S  # noqa: E402


def replay(world, transcript):
    ep = E.Episode(world)
    for t in transcript:
        # Round 3 logs the converted action; recompute it from the raw output and check it matches the log.
        st = ep.state()
        user = H.render_state(st, cards_object="env_action" in t)
        assert H.hashlib.sha256(user.encode()).hexdigest() == t["prompt_sha256"], ("prompt differs", world["world_id"], t["turn"])
        act = json.loads(t["output"]) if t["parsed"] else {"action": "__unparseable__"}
        if "env_action" in t:
            act = H.to_env_action(act, st, "state_cards_object")
            assert act == t["env_action"], (world["world_id"], t["turn"])
        out = ep.step(act)
        assert out["ok"] == t["accepted"], (world["world_id"], t["turn"])
    res = ep.result()
    res["turns"] = len(transcript)
    res["hit_turn_limit"] = not ep.done
    return res, ep


def main(folder: Path, refs: Path):
    # world_id is NOT unique (48 worlds, 20 ids: it omits target, kind and k0), so pair by order, as run_pilot wrote them.
    ws = S.pilot_worlds()
    eps = [json.loads(l) for l in (folder / "transcripts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    replayed, positions, cards, verdicts, rev = [], collections.Counter(), collections.Counter(), collections.Counter(), []
    assert len(ws) == len(eps)
    for w, e in zip(ws, eps):
        assert w["world_id"] == e["world_id"]
        res, ep = replay(w, e["transcript"])
        replayed.append({"world_id": e["world_id"], "result": res, "transcript": e["transcript"]})
        menu = [q["id"] for q in w["public"]["query_menu"]]
        for t in e["transcript"]:
            a = json.loads(t["output"])
            if a.get("action") == "query" and t["accepted"]:
                positions[menu.index(a["query_id"]) + 1] += 1
            if a.get("action") in ("commit", "revise"):
                c = t.get("env_action", a).get("admissible_cards", [])
                cards[tuple(c) if isinstance(c, list) else ("?",)] += 1
            if a.get("action") == "commit":
                verdicts[(a["verdict"], res.get("reference_verdict"), w["reference"]["target_verdict"])] += 1
        if res.get("complete"):
            rev.append((res["should_revise"], res["revision_type_I"], res["revision_type_II"],
                        e["transcript"][-1] and json.loads(e["transcript"][-1]["output"])["action"]))
    agg = H.aggregate(replayed)
    same = json.dumps(agg, sort_keys=True) == json.dumps(summary["aggregate"], sort_keys=True)
    should = [r for r in rev if r[0]]
    ref = json.loads(refs.read_text(encoding="utf-8"))
    done = [r["result"] for r in replayed if r["result"].get("complete")]
    report = {
        "replay_matches_summary": same,
        "aggregate": agg,
        "revision_among_should_revise": {"n": len(should), "type_I": sum(r[1] for r in should),
                                         "ci95": H.wilson(sum(r[1] for r in should), len(should))},
        "revision_among_should_keep": {"n": len(rev) - len(should), "type_II": sum(r[2] for r in rev if not r[0])},
        "final_action": dict(collections.Counter(r[3] for r in rev)),
        "query_menu_positions": dict(sorted(positions.items())),
        "cards_given": {",".join(k) or "(nenhuma)": v for k, v in cards.most_common()},
        "commit_verdict__ref_from_own_history__target": {"|".join(map(str, k)): v for k, v in verdicts.most_common()},
        "suspend": sum(1 for r in done if r.get("suspend_used")),
        "reach_vs_references": {p: v["reach"]["k"] for p, v in ref["policies"].items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "results" / "PILOTO_REFERENCIAS.json")

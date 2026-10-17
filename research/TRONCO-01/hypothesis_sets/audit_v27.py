"""Offline audit of the ten exposed v2.7 states with admissible hypothesis sets.

No model is loaded and no new data are generated. The public schedule and the
private reference are read from the archived ENSAIO_MODELO_V2_7 package after
checking its SHA-256 against the TRONCO-01 manifest. The private reference is
opened only after every public conclusion set has been computed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from hypothesis_sets import (TRONCO_V27, Evidence, card_hypothesis, conclusion_set,
                             enumerate_hypotheses)
from worlds import identifiability

HERE = Path(__file__).resolve().parent
TRONCO = HERE.parent
PACKAGE = TRONCO / "packages" / "TRONCO01_ENSAIO_MODELO_V2_7_REPRODUCIBLE_2026-10-17.zip"
SCHEDULE = "work/TRONCO01_TRIAL_v2_7/development_schedule.jsonl"
REFERENCE = "work/TRONCO01_TRIAL_v2_7/development_reference_private.jsonl"
MAX_SUPPORT = 2


def manifest_hash(path: Path) -> str:
    rel = path.relative_to(TRONCO).as_posix()
    for line in (TRONCO / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == rel:
            return parts[0]
    raise SystemExit(f"{rel} is not in SHA256SUMS.txt")


def read_jsonl(archive: zipfile.ZipFile, name: str) -> list[dict]:
    return [json.loads(line) for line in archive.read(name).decode("utf-8").splitlines() if line]


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def audit(package: Path = PACKAGE) -> dict:
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != manifest_hash(package):
        raise SystemExit("package hash differs from SHA256SUMS.txt; refusing to audit")
    domain = TRONCO_V27
    space = enumerate_hypotheses(domain, MAX_SUPPORT)

    with zipfile.ZipFile(package) as archive:
        schedule = read_jsonl(archive, SCHEDULE)
        episodes = []
        by_public: dict[str, list[str]] = {}
        for item in schedule:
            state = item["public_state"]
            ev = Evidence.from_observations(domain, state["observations"])
            observed = tuple(domain.as_tuple(o["input"]) for o in state["observations"])
            conclusions = conclusion_set(domain, space, state)
            cards = {c["id"]: card_hypothesis(domain, c) for c in state["candidate_models"]}
            working = state["working_model"]["id"]
            questions = {
                "working_model_is_hidden_mechanism":
                    identifiability(domain, space, ev, observed, lambda w: w.hidden == cards[working]),
                "declared_card_equal_to_hidden_mechanism":
                    identifiability(domain, space, ev, observed,
                                    lambda w: sorted(k for k, h in cards.items() if h == w.hidden)),
            }
            episodes.append({"episode_id": item["episode_id"], "stratum": item["stratum"],
                             "observations": len(state["observations"]),
                             "conclusions": conclusions,
                             "hidden_mechanism_questions": {
                                 k: {"identifiable": v["identifiable"],
                                     "possible_answers": len(v["possible_answers"])}
                                 for k, v in questions.items()}})
            by_public.setdefault(canonical(state), []).append(item["episode_id"])

        # Evaluator side: only now read the private labels and compare.
        reference = {r["episode_id"]: r["expected"] for r in read_jsonl(archive, REFERENCE)}

    for ep in episodes:
        ep["declared_labels_match_private_reference"] = (
            ep["conclusions"]["declared"] == reference[ep["episode_id"]])

    duplicate_groups = [ids for ids in by_public.values() if len(ids) > 1]
    contradictory_duplicates = [ids for ids in duplicate_groups
                                if len({canonical(reference[i]) for i in ids}) > 1]
    identified_but_open = [e["episode_id"] for e in episodes
                           if e["conclusions"]["declared"]["diagnosis"] == "identified"
                           and e["conclusions"]["admissible_count"] > 1]
    none_fit_but_explainable = [e["episode_id"] for e in episodes
                                if e["conclusions"]["declared"]["diagnosis"] == "none_fit"
                                and e["conclusions"]["admissible_count"] > 0]
    return {
        "audit": "TRONCO-01 step 4 — admissible hypothesis sets on the v2.7 exposed states",
        "package": package.name, "package_sha256": actual,
        "hypothesis_space": {"domain_inputs": len(domain.inputs), "max_essential_support": MAX_SUPPORT,
                             "size": len(space)},
        "model_calls": 0,
        "summary": {
            "episodes": len(episodes),
            "distinct_public_states": len(by_public),
            "duplicate_public_state_groups": duplicate_groups,
            "duplicates_with_different_private_labels": contradictory_duplicates,
            "declared_labels_match_private_reference":
                sum(e["declared_labels_match_private_reference"] for e in episodes),
            "declared_identified_but_mechanism_open_in_space": identified_but_open,
            "declared_none_fit_but_some_mechanism_in_space_fits": none_fit_but_explainable,
            "hidden_mechanism_identifiable_episodes": sum(
                all(q["identifiable"] for q in e["hidden_mechanism_questions"].values()) for e in episodes),
        },
        "episodes": episodes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()

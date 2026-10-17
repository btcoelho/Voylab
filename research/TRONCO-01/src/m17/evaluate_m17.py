"""Aggregate-only M17 benchmark; individual labels and world IDs never leave process memory."""
import argparse
import gc
import json
import math
from collections import defaultdict
from pathlib import Path

from agents import (FixedQueryControl, RandomQueryControl, StatisticalAnomalyDetector,
                    SymbolicActiveControl)
from environment import Episode
from generator import audit_world, make_world

CATEGORIES = ("NORMAL", "CONTRADICTION", "INSUFFICIENCY", "CHANGE", "HYPOTHESIS_ABSENT")
DEV = ((53001, "dev_table"), (53003, "dev_table"), (53009, "dev_table"))
DIAGNOSTIC = ((64001, "relational"), (64003, "multiphase"), (64007, "compositional"))
CONFIRMATION = ((75011, "relational"), (75013, "multiphase"), (75017, "compositional"))
PER_CATEGORY = 20


def wilson(successes, n, z=1.96):
    if n == 0:
        return {"estimate": None, "low95": None, "high95": None, "n": 0}
    p = successes / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {"estimate": p, "low95": max(0.0, center - radius), "high95": min(1.0, center + radius), "n": n}


def _rate(rows, predicate):
    n = len(rows)
    return wilson(sum(bool(predicate(r)) for r in rows), n)


def _calibration(rows, bins=10):
    if not rows:
        return {"brier": None, "ece10": None}
    brier = sum((r["confidence"] - int(r["decision_correct"])) ** 2 for r in rows) / len(rows)
    ece = 0.0
    for i in range(bins):
        low, high = i / bins, (i + 1) / bins
        members = [r for r in rows if low <= r["confidence"] < high or (i == bins - 1 and r["confidence"] == 1)]
        if members:
            conf = sum(r["confidence"] for r in members) / len(members)
            acc = sum(bool(r["decision_correct"]) for r in members) / len(members)
            ece += len(members) / len(rows) * abs(conf - acc)
    return {"brier": brier, "ece10": ece}


def summarize(rows):
    problems = [r for r in rows if r["category"] in {"CONTRADICTION", "CHANGE", "HYPOTHESIS_ABSENT"}]
    normal = [r for r in rows if r["category"] == "NORMAL"]
    insufficient = [r for r in rows if r["category"] == "INSUFFICIENCY"]
    localization_cases = [r for r in rows if r["category"] in {"CONTRADICTION", "CHANGE", "HYPOTHESIS_ABSENT"}]
    qn = sum(r["query_count"] for r in rows)
    expected_ig = [v for r in rows for v in r["expected_information_gain"]]
    actual_ig = [v for r in rows for v in r["actual_information_gain"]]
    by_category = {}
    for category in CATEGORIES:
        subset = [r for r in rows if r["category"] == category]
        by_category[category] = {
            "n": len(subset),
            "decision_accuracy": _rate(subset, lambda r: r["decision_correct"]),
            "evidence_diagnosis_accuracy": _rate(subset, lambda r: r["diagnosis_correct"]),
            "localization_accuracy": _rate(subset, lambda r: r["localized_correct"]),
        }
    return {
        "episodes": len(rows),
        "sensitivity": _rate(problems, lambda r: r["verdict"] == "rejected"),
        "specificity": _rate(normal, lambda r: r["verdict"] == "supported"),
        "insufficiency_recognition": _rate(
            insufficient, lambda r: r["verdict"] == "undetermined" and not r["forced_termination"]
        ),
        "evidence_localization": _rate(localization_cases, lambda r: r["localized_correct"]),
        "five_way_evidence_diagnosis": _rate(rows, lambda r: r["diagnosis_correct"]),
        "status_decision_accuracy": _rate(rows, lambda r: r["decision_correct"]),
        "explicit_report_rate": _rate(rows, lambda r: not r["forced_termination"]),
        "forced_terminations": sum(r["forced_termination"] for r in rows),
        "mean_queries": qn / len(rows) if rows else None,
        "mean_redundant_queries": sum(r["redundant_queries"] for r in rows) / len(rows) if rows else None,
        "expected_information_gain_per_query": sum(expected_ig) / len(expected_ig) if expected_ig else 0.0,
        "actual_candidate_information_gain_per_query": sum(actual_ig) / len(actual_ig) if actual_ig else 0.0,
        "invalid_actions": sum(r["invalid_actions"] for r in rows),
        "action_count": sum(r["action_count"] for r in rows),
        "invalid_action_rate": (sum(r["invalid_actions"] for r in rows)
                                / sum(r["action_count"] for r in rows)
                                if sum(r["action_count"] for r in rows) else 0.0),
        "calibration": _calibration(rows),
        "by_category": by_category,
    }


def build_worlds(split, pilot_per_category=None):
    if split == "dev":
        seed_families = DEV
    elif split == "diagnostic":
        seed_families = DIAGNOSTIC
    elif split == "confirmation":
        seed_families = CONFIRMATION
    else:
        raise ValueError(split)
    worlds_by_seed = {}
    for seed, family in seed_families:
        worlds = []
        for ci, category in enumerate(CATEGORIES):
            for i in range(PER_CATEGORY):
                index = ci * PER_CATEGORY + i
                world = make_world(category, family, seed, index)
                audit = audit_world(world)
                if not audit["identified"]:
                    raise RuntimeError(f"hidden-side identifiability audit failed: {audit}")
                worlds.append(world)
        worlds_by_seed[str(seed)] = (family, worlds)
    if pilot_per_category is not None:
        if split != "dev" or not 1 <= pilot_per_category < PER_CATEGORY:
            raise ValueError("pilot_per_category must be between 1 and 19 and is available only on dev")
        import random
        selected = set()
        rng = random.Random(0x17A2026)
        for category in CATEGORIES:
            candidates = [w["world_id"] for _, worlds in worlds_by_seed.values()
                          for w in worlds if w["category"] == category]
            selected.update(rng.sample(candidates, pilot_per_category))
        for seed, (family, worlds) in list(worlds_by_seed.items()):
            worlds = [w for w in worlds if w["world_id"] in selected]
            random.Random(int(seed) ^ 0x5A17).shuffle(worlds)
            worlds_by_seed[seed] = (family, worlds)
    else:
        import random
        for seed, (family, worlds) in list(worlds_by_seed.items()):
            random.Random(int(seed) ^ 0x5A17).shuffle(worlds)
    return worlds_by_seed


def _evaluate_agent(agent, worlds, seed):
    rows = []
    for world in worlds:
        # Assert the public observation channel cannot reveal the hidden category/family.
        state = world["public"]
        if any(k in state for k in ("category", "family", "hidden", "truth", "seed", "index")):
            raise RuntimeError("hidden metadata leaked into public state")
        result = Episode(world).run(agent)
        rows.append(result)
    return rows


def run_controls(worlds_by_seed):
    output = {}
    factories = {
        "statistical_detector": lambda seed, world: StatisticalAnomalyDetector(),
        "random_query": lambda seed, world: RandomQueryControl(seed ^ int(world["world_id"][:8], 16)),
        "fixed_query": lambda seed, world: FixedQueryControl(seed),
        "symbolic_active": lambda seed, world: SymbolicActiveControl(),
    }
    for seed, (family, worlds) in worlds_by_seed.items():
        output[seed] = {"family": family, "agents": {}}
        for name, factory in factories.items():
            rows = [Episode(w).run(factory(int(seed), w)) for w in worlds]
            output[seed]["agents"][name] = summarize(rows)
    return output


def run_llm(name, model_path, worlds_by_seed):
    from llm_agents import BaseQwenAgent, M16AdapterAgent
    agent = BaseQwenAgent() if name == "base_model" else M16AdapterAgent(model_path)
    output = {}
    for seed, (family, worlds) in worlds_by_seed.items():
        rows = _evaluate_agent(agent, worlds, int(seed))
        output[seed] = {"family": family, "metrics": summarize(rows)}
    del agent
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("dev", "diagnostic", "confirmation"), required=True)
    parser.add_argument("--agent", choices=("controls", "base_model", "m16_adapter"), default="controls")
    parser.add_argument("--m16-adapter", type=Path,
                        default=Path.home() / "voynich-lab/experiencias/M16_CURRICULO/runs/m16-l4l5-r1/adapter")
    parser.add_argument("--pilot-per-category", type=int, default=None,
                        help="dev-only pilot size across development seeds; 10 gives 50 worlds")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    worlds = build_worlds(args.split, pilot_per_category=args.pilot_per_category)
    metadata = {"split": args.split,
                "pilot_cases_per_category_total": args.pilot_per_category,
                "cases_per_category_per_seed": PER_CATEGORY if args.pilot_per_category is None else None,
                "episodes_total": sum(len(seed_worlds) for _, seed_worlds in worlds.values()),
                "public_category_names_or_proportions_in_prompt": False,
                "per_world_labels_or_ids_exported": False,
                "identifiability_audited_before_agent_run": True}
    if args.agent == "controls":
        results = {"controls": run_controls(worlds)}
    else:
        name = "base_model" if args.agent == "base_model" else "m16_adapter"
        path = None if name == "base_model" else args.m16_adapter
        results = {name: run_llm(name, path, worlds)}
    result = {"metadata": metadata, **results}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

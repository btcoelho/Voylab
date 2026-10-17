"""Inject known defects and confirm the test suite catches each one.

Each mutant runs in a fresh interpreter so patches cannot leak between runs.
A mutant "survives" if the full suite still passes; any survivor is a gap.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

MUTANTS = {
    "leaky_public_view":
        "Public evidence also reveals the hidden output at one unobserved input.",
    "drop_last_observation":
        "Evidence silently ignores the last public row.",
    "syntactic_identity":
        "Hypotheses counted per (support, table) description instead of by extension.",
    "wildcard_missing_key":
        "A card with a missing table key is completed with a default output.",
    "ignore_conflicts":
        "Contradictory rows are reduced to the first output seen.",
    "statement_trusted_over_keys":
        "Card features taken from the statement text without checking the keys.",
}

PATCHES = r'''
import hypothesis_sets as hs, worlds as wd
from itertools import combinations, product
name = sys.argv[1]
if name == "leaky_public_view":
    orig = wd.public_evidence
    def leaky(domain, world):
        ev = orig(domain, world)
        extra = next(x for x in domain.inputs if x not in world.observed)
        return ev.with_row(extra, world.hidden[domain.index(extra)])
    wd.public_evidence = leaky
elif name == "drop_last_observation":
    orig = hs.Evidence.from_observations.__func__
    hs.Evidence.from_observations = classmethod(lambda cls, d, o: orig(cls, d, list(o)[:-1]))
elif name == "syntactic_identity":
    def enum(domain, k):
        found = []
        for size in range(min(k, len(domain.features)) + 1):
            for subset in combinations(range(len(domain.features)), size):
                keys = list(product(*(domain.values[i] for i in subset)))
                for outs in product(domain.outputs, repeat=len(keys)):
                    t = dict(zip(keys, outs))
                    found.append(tuple(t[tuple(x[i] for i in subset)] for x in domain.inputs) + (str(subset),))
        return frozenset(found)
    hs.enumerate_hypotheses = enum
elif name == "wildcard_missing_key":
    orig_hyp = hs.card_hypothesis
    def filled(domain, card):
        features = hs.card_features(domain, card)
        idx = [domain.features.index(f) for f in features]
        return tuple(str(card["table"].get("|".join(x[i] for i in idx), domain.outputs[0])) for x in domain.inputs)
    hs.card_hypothesis = filled
    orig_fit = hs.card_fits
    def fit(domain, card, ev):
        h = filled(domain, card)
        return all(h[domain.index(x)] == y for x, y in ev.rows)
    hs.card_fits = fit
elif name == "ignore_conflicts":
    orig = hs.Evidence.from_observations.__func__
    def first_only(cls, d, observations):
        ev = orig(cls, d, observations)
        kept = {}
        for x, y in ev.rows:
            kept.setdefault(x, y)
        return cls(tuple(sorted(kept.items())))
    hs.Evidence.from_observations = classmethod(first_only)
elif name == "statement_trusted_over_keys":
    orig = hs.card_features
    def trusting(domain, card):
        stated = hs._STATEMENT_FEATURES.get(str(card.get("statement", "")).strip().lower())
        return stated if stated is not None else orig(domain, card)
    hs.card_features = trusting
else:
    raise SystemExit(f"unknown mutant {name}")
import unittest
suite = unittest.defaultTestLoader.discover(str(HERE / "tests"))
result = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(suite)
print(json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}))
'''


def run(name: str) -> dict:
    prelude = (f"import json, os, sys; from pathlib import Path; HERE = Path({str(HERE)!r}); "
               f"sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'tests'))\n")
    proc = subprocess.run([sys.executable, "-c", prelude + PATCHES, name], cwd=HERE,
                          capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        return {"tests": None, "failures": None, "errors": None, "crash": proc.stderr.strip()[-400:]}
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main() -> int:
    results = {}
    for name, description in MUTANTS.items():
        outcome = run(name)
        killed = outcome.get("crash") is not None or (outcome["failures"] + outcome["errors"]) > 0
        results[name] = {"description": description, **outcome, "killed": killed}
    summary = {"mutants": len(results), "killed": sum(r["killed"] for r in results.values()),
               "survivors": [k for k, r in results.items() if not r["killed"]], "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not summary["survivors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

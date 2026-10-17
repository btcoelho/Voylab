"""Seed guard: this audit never generates a reserved world.

Reserved = the M17 diagnostic and confirmation seeds. The generator re-seeds itself
(seed + 7919) when a world cannot be built, so every seed reachable from a requested
seed is checked, not just the requested one. Worlds are only built through
`build_world`, which enforces the guard and records every seed it was asked for.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "m17"))

from generator import make_world  # noqa: E402

RESERVED_SEEDS = frozenset({64001, 64003, 64007,      # diagnostic
                            75011, 75013, 75017})     # confirmation
RETRY_STEP = 7919
MAX_RETRIES = 40
DEV = ((53001, "dev_table"), (53003, "dev_table"), (53009, "dev_table"))
# Substitute families: fresh seeds, far above every reserved seed and its retry chain.
SUBSTITUTE = ((200003, "dev_table"), (200009, "relational"),
              (200017, "multiphase"), (200023, "compositional"))
CATEGORIES = ("NORMAL", "CONTRADICTION", "INSUFFICIENCY", "CHANGE", "HYPOTHESIS_ABSENT")
PER_CATEGORY = 20

REQUESTED: list[tuple[int, str, str, int]] = []


class ReservedSeedError(RuntimeError):
    pass


def reachable_seeds(seed: int) -> set[int]:
    return {seed + RETRY_STEP * k for k in range(MAX_RETRIES + 1)}


def assert_not_reserved(seed: int) -> None:
    hit = reachable_seeds(seed) & RESERVED_SEEDS
    if hit:
        raise ReservedSeedError(f"seed {seed} can reach a reserved seed ({sorted(hit)}); refusing")


def build_world(category: str, family: str, seed: int, index: int) -> dict:
    assert_not_reserved(seed)
    REQUESTED.append((seed, family, category, index))
    return make_world(category, family, seed, index)


def build_set(seed_families) -> list[dict]:
    worlds = []
    for seed, family in seed_families:
        for ci, category in enumerate(CATEGORIES):
            for i in range(PER_CATEGORY):
                worlds.append(build_world(category, family, seed, ci * PER_CATEGORY + i))
    return worlds

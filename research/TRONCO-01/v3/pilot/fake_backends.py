"""Fake backends for tests and dry runs. They may read `state`; real backends must not."""
from __future__ import annotations

import json
import random

from pilot_harness import Backend


class Garbage(Backend):
    name = "garbage"

    def generate(self, system, user, schema, state=None):
        return "isto não é JSON"


class RandomValid(Backend):
    name = "random_valid"

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def generate(self, system, user, schema, state=None):
        if state["phase"] == "explore":
            if state["remaining_query_budget"] > 0 and self.rng.random() < 0.7:
                return json.dumps({"action": "query", "query_id": self.rng.choice(state["query_menu"])["id"]})
            return json.dumps({"action": "commit", "verdict": self.rng.choice(["rejected", "supported", "undetermined"]),
                               "admissible_cards": [c["id"] for c in state["candidate_models"] if self.rng.random() < .5],
                               "predictions": {str(i): self.rng.choice("01") for i in (1, 2, 3, 4)}})
        return json.dumps({"action": "keep"})


class CommitUndetermined(Backend):
    name = "commit_undetermined"

    def generate(self, system, user, schema, state=None):
        if state["phase"] == "explore":
            return json.dumps({"action": "commit", "verdict": "undetermined", "admissible_cards": [],
                               "predictions": {"1": "0", "2": "0", "3": "0", "4": "0"}})
        return json.dumps({"action": "keep"})

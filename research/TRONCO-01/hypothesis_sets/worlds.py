"""Evaluator-side worlds: a hidden mechanism plus what the agent is allowed to see.

A world's public view never contains the hidden mechanism. Two worlds are
publicly indistinguishable when their public views carry the same evidence;
the tests check that they then receive the same admissible set, and that any
question whose answer differs between them is reported as not identifiable
instead of being scored against one hidden label.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Iterator

from hypothesis_sets import (Domain, Evidence, Hypothesis, admissible, discriminating_inputs)


@dataclass(frozen=True)
class World:
    hidden: Hypothesis                    # evaluator only
    observed: tuple[tuple[str, ...], ...]  # inputs the agent saw, in presentation order
    cards: tuple[dict, ...] = ()
    working_id: str | None = None

    def public_view(self, domain: Domain, id_prefix: str = "o") -> dict:
        rows = [{"id": f"{id_prefix}{n}", "input": dict(zip(domain.features, x)),
                 "output": self.hidden[domain.index(x)]}
                for n, x in enumerate(self.observed, 1)]
        state = {"observations": rows, "candidate_models": [dict(c) for c in self.cards],
                 "query_menu": [], "remaining_query_budget": 0}
        if self.working_id is not None:
            state["working_model"] = next(dict(c) for c in self.cards if c["id"] == self.working_id)
        return state


def public_evidence(domain: Domain, world: World) -> Evidence:
    return Evidence.from_observations(domain, world.public_view(domain)["observations"])


def worlds_consistent_with(domain: Domain, space: frozenset[Hypothesis], evidence: Evidence,
                           observed: tuple[tuple[str, ...], ...]) -> Iterator[World]:
    """Every hidden mechanism in `space` that could have produced this public evidence.

    Computed by regenerating each candidate world and comparing its public evidence,
    which is deliberately a different route from `admissible`'s direct filter.
    """
    for h in sorted(space):
        w = World(hidden=h, observed=observed)
        if public_evidence(domain, w) == evidence:
            yield w


def indistinguishable_pairs(domain: Domain, space: frozenset[Hypothesis],
                            observed: tuple[tuple[str, ...], ...]) -> Iterator[tuple[World, World]]:
    """Pairs of worlds with different hidden mechanisms and identical public evidence."""
    groups: dict[Evidence, list[Hypothesis]] = {}
    for h in sorted(space):
        groups.setdefault(public_evidence(domain, World(h, observed)), []).append(h)
    for members in groups.values():
        for a, b in combinations(members, 2):
            yield World(a, observed), World(b, observed)


def separating_extension(domain: Domain, a: World, b: World) -> tuple[str, ...]:
    """First unobserved input on which the two hidden mechanisms disagree."""
    for x in discriminating_inputs(domain, a.hidden, b.hidden):
        if x not in a.observed:
            return x
    raise ValueError("worlds are identical on every unobserved input")


# --------------------------------------------------------------------------- identifiability


Question = Callable[[World], object]


def identifiability(domain: Domain, space: frozenset[Hypothesis], evidence: Evidence,
                    observed: tuple[tuple[str, ...], ...], question: Question) -> dict:
    """Is the answer to `question` fixed by the public evidence?

    If consistent hidden worlds give different answers, a scorer that expects one
    of them is grading information the agent never had.
    """
    answers = sorted({repr(question(w)) for w in worlds_consistent_with(domain, space, evidence, observed)})
    return {"identifiable": len(answers) == 1, "possible_answers": answers}


def same_admissible(domain: Domain, space: frozenset[Hypothesis], pair: Iterable[World]) -> bool:
    a, b = list(pair)
    return admissible(domain, space, public_evidence(domain, a)) == admissible(
        domain, space, public_evidence(domain, b))

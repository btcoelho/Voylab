"""Independent enumeration of admissible hypothesis sets for TRONCO-01 (step 4).

Stdlib only. Inspired by the set-valued method described for HypoSpace
(arXiv:2510.15614); no HypoSpace code is copied or imported.

Idea: instead of one hidden "correct" answer, a public history H induces a
finite set A(H) of hypotheses that agree with every observation. Two worlds
that the agent cannot tell apart must receive the same A(H), and therefore the
same set of admissible conclusions. Only discriminating evidence may shrink it.

Nothing in this module accepts a hidden mechanism as input to `admissible`.
Hidden mechanisms appear only in `worlds.py`, on the evaluator side.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable

# --------------------------------------------------------------------------- domain


@dataclass(frozen=True)
class Domain:
    """Finite, fully observed input space with a finite output alphabet."""

    features: tuple[str, ...]
    values: tuple[tuple[str, ...], ...]  # values[i] are the levels of features[i]
    outputs: tuple[str, ...]

    def __post_init__(self):
        if len(self.features) != len(self.values):
            raise ValueError("one value list per feature is required")
        if len(set(self.features)) != len(self.features):
            raise ValueError("duplicate feature")
        for levels in self.values:
            if len(levels) < 1 or len(set(levels)) != len(levels):
                raise ValueError("feature levels must be non-empty and unique")
        if len(self.outputs) < 1 or len(set(self.outputs)) != len(self.outputs):
            raise ValueError("outputs must be non-empty and unique")

    @property
    def inputs(self) -> tuple[tuple[str, ...], ...]:
        """All complete inputs, ordered canonically (feature order, level order)."""
        return tuple(product(*self.values))

    def index(self, row: tuple[str, ...]) -> int:
        try:
            return self.inputs.index(tuple(row))
        except ValueError as exc:
            raise ValueError(f"input outside the declared domain: {row}") from exc

    def as_tuple(self, inp: dict) -> tuple[str, ...]:
        if set(inp) != set(self.features):
            raise ValueError(f"incomplete or extra input fields: {sorted(inp)}")
        return tuple(inp[f] for f in self.features)


#: Domain used by the TRONCO-01 v2.3 – v2.7 synthetic tables.
TRONCO_V27 = Domain(
    features=("glyph", "setting", "partner", "phase"),
    values=(("g0", "g1"), ("s0", "s1"), ("p0", "p1"), ("t0", "t1")),
    outputs=("0", "1"),
)

# --------------------------------------------------------------------------- hypotheses

# A hypothesis is identified *extensionally*: the tuple of its outputs over
# domain.inputs. Two descriptions that predict the same thing everywhere are the
# same hypothesis; syntactic variants must never be counted twice.
Hypothesis = tuple[str, ...]


def essential_support(domain: Domain, h: Hypothesis) -> frozenset[str]:
    """Features whose change, holding all others fixed, changes the output somewhere."""
    inputs = domain.inputs
    pos = {x: i for i, x in enumerate(inputs)}
    support = set()
    for fi, feature in enumerate(domain.features):
        for x in inputs:
            for level in domain.values[fi]:
                if level == x[fi]:
                    continue
                y = x[:fi] + (level,) + x[fi + 1:]
                if h[pos[x]] != h[pos[y]]:
                    support.add(feature)
                    break
            if feature in support:
                break
    return frozenset(support)


def enumerate_hypotheses(domain: Domain, max_support: int) -> frozenset[Hypothesis]:
    """All total functions whose essential support has at most `max_support` features.

    Built constructively: for each feature subset S and each table over S, expand
    to the full input space; duplicates collapse because identity is extensional.
    """
    if max_support < 0:
        raise ValueError("max_support must be non-negative")
    found: set[Hypothesis] = set()
    k = min(max_support, len(domain.features))
    for size in range(k + 1):
        for subset in combinations(range(len(domain.features)), size):
            keys = list(product(*(domain.values[i] for i in subset)))
            for outs in product(domain.outputs, repeat=len(keys)):
                table = dict(zip(keys, outs))
                found.add(tuple(table[tuple(x[i] for i in subset)] for x in domain.inputs))
    return frozenset(found)


# --------------------------------------------------------------------------- public evidence


@dataclass(frozen=True)
class Evidence:
    """Public history reduced to what can matter: input -> set of observed outputs."""

    rows: tuple[tuple[tuple[str, ...], str], ...]

    @classmethod
    def from_observations(cls, domain: Domain, observations: Iterable[dict]) -> "Evidence":
        rows = sorted({(domain.as_tuple(o["input"]), str(o["output"])) for o in observations})
        for x, y in rows:
            domain.index(x)
            if y not in domain.outputs:
                raise ValueError(f"output outside the declared alphabet: {y}")
        return cls(tuple(rows))

    @property
    def conflicts(self) -> tuple[tuple[str, ...], ...]:
        """Inputs observed with more than one output (impossible for a noise-free function)."""
        seen: dict[tuple[str, ...], set[str]] = {}
        for x, y in self.rows:
            seen.setdefault(x, set()).add(y)
        return tuple(sorted(x for x, ys in seen.items() if len(ys) > 1))

    def with_row(self, x: tuple[str, ...], y: str) -> "Evidence":
        return Evidence(tuple(sorted(set(self.rows) | {(tuple(x), y)})))


def admissible(domain: Domain, space: frozenset[Hypothesis], evidence: Evidence) -> frozenset[Hypothesis]:
    """A(H): every hypothesis in `space` that reproduces every public row.

    Under the noise-free assumption, contradictory rows leave nothing admissible.
    Callers must report that case as `inconsistent_observations`, never as
    `none_fit`: no candidate could fit, whatever the candidate list.
    """
    checks = [(domain.index(x), y) for x, y in evidence.rows]
    return frozenset(h for h in space if all(h[i] == y for i, y in checks))


def prediction_set(domain: Domain, hypotheses: Iterable[Hypothesis], x: tuple[str, ...]) -> frozenset[str]:
    i = domain.index(x)
    return frozenset(h[i] for h in hypotheses)


def undetermined_inputs(domain: Domain, hypotheses: frozenset[Hypothesis]) -> tuple[tuple[str, ...], ...]:
    """Inputs on which admissible hypotheses still disagree (where a new query could inform)."""
    return tuple(x for x in domain.inputs if len(prediction_set(domain, hypotheses, x)) > 1)


def discriminating_inputs(domain: Domain, a: Hypothesis, b: Hypothesis) -> tuple[tuple[str, ...], ...]:
    return tuple(x for i, x in enumerate(domain.inputs) if a[i] != b[i])


# --------------------------------------------------------------------------- declared candidate cards

# Card tables use keys such as "g0" or "g0|t1". The feature of each key token is
# recovered from the declared domain levels, NOT from the free-text statement.
# The statement is only cross-checked; a mismatch is an error, not a guess.

_STATEMENT_FEATURES = {
    "output depends only on glyph.": ("glyph",),
    "output depends only on setting.": ("setting",),
    "output depends only on partner.": ("partner",),
    "output depends only on phase.": ("phase",),
    "output depends on glyph and phase.": ("glyph", "phase"),
}


class CardError(ValueError):
    pass


def card_features(domain: Domain, card: dict) -> tuple[str, ...]:
    level_owner = {}
    for feature, levels in zip(domain.features, domain.values):
        for level in levels:
            if level in level_owner:
                raise CardError(f"level {level} belongs to two features; keys are ambiguous")
            level_owner[level] = feature
    table = card.get("table")
    if not isinstance(table, dict) or not table:
        raise CardError(f"card {card.get('id')} has no table")
    layouts = set()
    for key in table:
        tokens = key.split("|")
        try:
            layouts.add(tuple(level_owner[t] for t in tokens))
        except KeyError as exc:
            raise CardError(f"card {card.get('id')}: unknown level in key {key!r}") from exc
    if len(layouts) != 1:
        raise CardError(f"card {card.get('id')}: keys do not share one feature layout")
    features = layouts.pop()
    if len(set(features)) != len(features):
        raise CardError(f"card {card.get('id')}: repeated feature in key")
    stated = _STATEMENT_FEATURES.get(str(card.get("statement", "")).strip().lower())
    if stated is not None and stated != features:
        raise CardError(f"card {card.get('id')}: statement says {stated}, table keys say {features}")
    return features


def card_hypothesis(domain: Domain, card: dict) -> Hypothesis | None:
    """Extensional form of a card, or None when its table does not cover every input.

    A partial table makes no prediction on missing inputs. It is not admissible as a
    total hypothesis and must not be completed silently (no wildcard, no default).
    """
    features = card_features(domain, card)
    idx = [domain.features.index(f) for f in features]
    out = []
    for x in domain.inputs:
        key = "|".join(x[i] for i in idx)
        if key not in card["table"]:
            return None
        value = str(card["table"][key])
        if value not in domain.outputs:
            raise CardError(f"card {card.get('id')}: output {value!r} outside alphabet")
        out.append(value)
    return tuple(out)


def card_fits(domain: Domain, card: dict, evidence: Evidence) -> bool:
    """Literal reading of the v2 contract: a card fits when it predicts every public row.

    Unlike `card_hypothesis`, this only needs the table on observed inputs.
    """
    features = card_features(domain, card)
    idx = [domain.features.index(f) for f in features]
    for x, y in evidence.rows:
        key = "|".join(x[i] for i in idx)
        if key not in card["table"] or str(card["table"][key]) != y:
            return False
    return True


# --------------------------------------------------------------------------- conclusions


def declared_labels(domain: Domain, state: dict) -> dict:
    """v2 contract labels, recomputed from the public state with this module's decoder."""
    ev = Evidence.from_observations(domain, state["observations"])
    cards = {c["id"]: c for c in state["candidate_models"]}
    fit = sorted(cid for cid, c in cards.items() if card_fits(domain, c, ev))
    working = cards[state["working_model"]["id"]]
    if not ev.rows:
        verdict = "undetermined"
    else:
        verdict = "supported" if card_fits(domain, working, ev) else "rejected"
    diagnosis = "none_fit" if not fit else "identified" if len(fit) == 1 else "ambiguous"
    if not ev.rows:
        sufficiency = "no_observations"
    else:
        sufficiency = ("no_candidate_fits" if not fit else
                       "identity_resolved" if len(fit) == 1 else "identity_ambiguous")
    return {"candidates": fit, "diagnosis": diagnosis, "sufficiency": sufficiency, "verdict": verdict}


def conclusion_set(domain: Domain, space: frozenset[Hypothesis], state: dict) -> dict:
    """Everything a defensible report may conclude from the public state alone.

    Returns plain data (sorted lists) so it can be compared, hashed and journaled.
    """
    ev = Evidence.from_observations(domain, state["observations"])
    adm = admissible(domain, space, ev)
    cards = {c["id"]: card_hypothesis(domain, c) for c in state["candidate_models"]}
    admissible_cards = sorted(cid for cid, h in cards.items() if h is not None and h in adm)
    supports = sorted({tuple(sorted(essential_support(domain, h))) for h in adm})
    open_inputs = undetermined_inputs(domain, adm)
    if ev.conflicts:
        status = "inconsistent_observations"
    elif not adm:
        status = "no_hypothesis_in_space"
    elif len(adm) == 1:
        status = "mechanism_identified_in_space"
    else:
        status = "mechanism_underdetermined_in_space"
    return {
        "declared": declared_labels(domain, state),
        "space_size": len(space),
        "admissible_count": len(adm),
        "admissible_digest": digest(adm),
        "admissible_declared_cards": admissible_cards,
        "admissible_supports": [list(s) for s in supports],
        "undetermined_input_count": len(open_inputs),
        "conflicting_inputs": [list(x) for x in ev.conflicts],
        "status": status,
    }


def digest(hypotheses: Iterable[Hypothesis]) -> str:
    """Order-independent fingerprint of a hypothesis set."""
    import hashlib

    text = "\n".join(sorted("".join(h) for h in hypotheses))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- set-valued scoring


def score_set_answer(admissible_set: frozenset[Hypothesis], answer: Iterable[Hypothesis]) -> dict:
    """HypoSpace-style metrics for an answer that is itself a set of hypotheses.

    validity: share of proposed hypotheses that are admissible.
    recovery: share of the admissible set that was proposed.
    exact:    the proposed set equals the admissible set.
    """
    proposed = frozenset(answer)
    hits = proposed & admissible_set
    return {
        "proposed": len(proposed),
        "admissible": len(admissible_set),
        "validity": (len(hits) / len(proposed)) if proposed else None,
        "recovery": (len(hits) / len(admissible_set)) if admissible_set else None,
        "exact": proposed == admissible_set,
    }

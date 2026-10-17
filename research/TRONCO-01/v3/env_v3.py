"""Action protocol and episode state machine for task v3 (what a language-model agent actually talks to).

Phase "explore": query (<= budget) | commit | suspend.   Phase "revision": keep | revise.
All actions are JSON objects. Invalid actions are counted and answered with an error, never silently fixed.
The environment reads hidden fields only to answer queries and to score; it never returns them.
"""
from __future__ import annotations

import json
import random

import generator_v3 as g
import scoring

VERDICTS_ALLOWED = ("rejected", "supported", "undetermined")
REVISION_VERDICTS = VERDICTS_ALLOWED + ("inconsistent",)   # only after new evidence: the history no longer fits any hypothesis
MAX_CONSECUTIVE_INVALID = 3

SCHEMA = {
    "explore": {"query": {"query_id": "q<N> from query_menu"},
                "commit": {"verdict": "|".join(VERDICTS_ALLOWED), "admissible_cards": ["card ids"],
                           "predictions": {"1..4": "output for held_out_inputs[k-1]"}},
                "suspend": {}},
    "revision": {"keep": {}, "revise": {"verdict": "|".join(REVISION_VERDICTS), "admissible_cards": ["card ids"]}},
}


class Episode:
    def __init__(self, world: dict):
        self.w = world
        self.hid = world["hidden"]
        self.pub = world["public"]
        self.phase = "explore"
        self.left = self.pub["remaining_query_budget"]
        self.queried: list[int] = []
        self.invalid = 0
        self.consecutive_invalid = 0
        self.forced_termination = False
        self.committed = None            # dict(verdict, stop, cards, predictions)
        self.final = None                # dict(action, verdict)
        self.done = False
        self.log: list[dict] = []
        self._menu_ids = {q["id"]: g.INPUTS.index(g.D.as_tuple(q["input"])) for q in self.pub["query_menu"]}
        self._card_hyp = {c["id"]: g.hs.card_hypothesis(g.D, c) for c in self.pub["candidate_models"]}

    # ----------------------------------------------------------------- what the agent sees
    def state(self) -> dict:
        used = {self._menu_ids_inv(i) for i in self.queried}
        shown = dict(self.pub)
        shown["query_menu"] = [q for q in self.pub["query_menu"] if q["id"] not in used]
        shown["remaining_query_budget"] = self.left
        shown["phase"] = self.phase
        shown["observations"] = list(self.pub["observations"]) + [
            {"id": f"n{k}", "input": dict(zip(g.D.features, g.INPUTS[i])), "output": self.hid["h"][i]}
            for k, i in enumerate(self.queried, 1)]
        if self.phase == "revision":
            shown["new_evidence"] = [{"id": f"b{k}", "input": dict(zip(g.D.features, g.INPUTS[i])),
                                      "output": self.hid["h2"][i]} for k, i in enumerate(self.hid["block"], 1)]
        return shown

    def _menu_ids_inv(self, idx):
        return next(k for k, v in self._menu_ids.items() if v == idx)

    # ----------------------------------------------------------------- validation
    def _reject(self, why: str) -> dict:
        self.invalid += 1
        self.consecutive_invalid += 1
        if self.consecutive_invalid >= MAX_CONSECUTIVE_INVALID:
            self.forced_termination = self.done = True
        self.log.append({"invalid": why})
        return {"ok": False, "error": why, "done": self.done}

    def _verdict_ok(self, a):
        allowed = REVISION_VERDICTS if self.phase == "revision" else VERDICTS_ALLOWED
        return a.get("verdict") in allowed

    def _cards_ok(self, a):
        c = a.get("admissible_cards")
        return isinstance(c, list) and all(isinstance(x, str) and x in self._card_hyp for x in c) and len(set(c)) == len(c)

    # ----------------------------------------------------------------- step
    def step(self, action) -> dict:
        if self.done:
            return {"ok": False, "error": "episode finished", "done": True}
        if isinstance(action, str):
            try:
                action = json.loads(action)
            except ValueError:
                return self._reject("not valid JSON")
        if not isinstance(action, dict) or "action" not in action:
            return self._reject("missing 'action'")
        kind = action["action"]
        if self.phase == "explore":
            if kind == "query":
                if self.left <= 0:
                    return self._reject("no query budget left")
                qid = action.get("query_id")
                if qid not in self._menu_ids or self._menu_ids[qid] in self.queried:
                    return self._reject("query_id not available")
                i = self._menu_ids[qid]
                self.queried.append(i)
                self.left -= 1
                self.consecutive_invalid = 0
                row = {"input": dict(zip(g.D.features, g.INPUTS[i])), "output": self.hid["h"][i]}
                self.log.append({"query": qid})
                return {"ok": True, "result": row, "remaining_query_budget": self.left, "done": False}
            if kind == "commit":
                if not (self._verdict_ok(action) and self._cards_ok(action)):
                    return self._reject("commit needs verdict and admissible_cards (valid card ids)")
                preds = action.get("predictions", {})
                if not isinstance(preds, dict) or any(k not in {"1", "2", "3", "4"} or v not in g.D.outputs
                                                      for k, v in preds.items()):
                    return self._reject("predictions must map '1'..'4' to an output")
                self.committed = {"verdict": action["verdict"], "stop": "commit",
                                  "cards": action["admissible_cards"], "predictions": preds}
            elif kind == "suspend":
                self.committed = {"verdict": "undetermined", "stop": "suspend", "cards": [], "predictions": {}}
            else:
                return self._reject(f"action {kind!r} not allowed in phase explore")
            self.phase = "revision"
            self.consecutive_invalid = 0
            self.log.append({kind: self.committed["verdict"]})
            return {"ok": True, "phase": "revision", "state": self.state(), "done": False}
        # revision phase
        if kind == "keep":
            self.final = {"action": "keep", "verdict": self.committed["verdict"]}
        elif kind == "revise":
            if not (self._verdict_ok(action) and self._cards_ok(action)):
                return self._reject("revise needs verdict and admissible_cards")
            self.final = {"action": "revise", "verdict": action["verdict"]}
        else:
            return self._reject(f"action {kind!r} not allowed in phase revision")
        self.done = True
        self.log.append({kind: self.final["verdict"]})
        return {"ok": True, "done": True}

    # ----------------------------------------------------------------- scoring
    def result(self) -> dict:
        if self.committed is None:        # forced termination before any commitment
            return {"complete": False, "invalid": self.invalid, "forced_termination": True}
        T = self.hid["T"]
        ans = {"stop": self.committed["stop"], "verdict": self.committed["verdict"],
               "admissible_cards": [self._card_hyp[c] for c in self.committed["cards"]],
               "predictions": {T[int(k) - 1]: v for k, v in self.committed["predictions"].items()}}
        detail = scoring.score(self.w, self.queried, ans, self.left)
        ref = g.revision_reference(self.w, self.queried)
        final_v = self.final["verdict"] if self.final else self.committed["verdict"]
        revised = bool(self.final) and self.final["action"] == "revise" and final_v != self.committed["verdict"]
        return {**detail, "complete": self.final is not None, "invalid": self.invalid,
                "forced_termination": self.forced_termination, "queries": len(self.queried),
                "should_revise": ref["should_revise"],
                "revision_type_I": ref["should_revise"] and not revised,
                "revision_type_II": revised and not ref["should_revise"]}


def run_policy(policy, world: dict, seed: int = 0) -> dict:
    """Drive a reference policy through the real protocol (used to prove the harness equals the direct evaluator)."""
    import policies as P
    rng = random.Random(f"{policy.name}|{world['world_id']}|{seed}")
    ep = Episode(world)
    v = P.view(world)
    rows = list(v["rows"])
    id_of = {idx: qid for qid, idx in ep._menu_ids.items()}
    for left in range(v["budget"], 0, -1):
        q = policy.choose(v, tuple(rows), left, rng, world["hidden"])
        if q is None:
            break
        out = ep.step({"action": "query", "query_id": id_of.get(q, "invalid")})
        if not out["ok"]:
            break
        rows.append((q, world["hidden"]["h"][q]))
    ans = policy.answer(v, tuple(rows), v["budget"] - len(ep.queried))
    ids = {h: cid for cid, h in ep._card_hyp.items()}
    cards = [ids[c] for c in ans["admissible_cards"]]
    T = world["hidden"]["T"]
    inv = {t: str(k) for k, t in enumerate(T, 1)}
    if ans["stop"] == "suspend":
        ep.step({"action": "suspend"})
    else:
        ep.step({"action": "commit", "verdict": ans["verdict"], "admissible_cards": cards,
                 "predictions": {inv[t]: y for t, y in ans["predictions"].items()}})
    post = rows + [(i, world["hidden"]["h2"][i]) for i in world["hidden"]["block"]]
    final_v = g.verdict(g.admissible_idx(post), v["w"], v["T"])
    if policy.revises and final_v != ans["verdict"]:
        ep.step({"action": "revise", "verdict": final_v,
                 "admissible_cards": [] if final_v == "inconsistent" else
                 [ids[c] for c in v["cards"] if c in g.admissible_idx(post) and c in ids]})
    else:
        ep.step({"action": "keep"})
    return ep.result()

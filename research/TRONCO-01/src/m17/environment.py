"""Stateful oracle and evidence-based scoring for M17."""
from __future__ import annotations

import math
from copy import deepcopy

from generator import QUERY_BUDGET, _compatible, _hidden_predict, _input_key, _predict


class Episode:
    def __init__(self, world):
        self.world = world
        self.public = deepcopy(world["public"])
        self.cards = world["cards"]
        self.hidden = world["hidden"]
        self.observations = deepcopy(self.public["observations"])
        self.query_menu = deepcopy(self.public["query_menu"])
        self.remaining = QUERY_BUDGET
        self.invalid_actions = 0
        self.terminal = False
        self.report = None
        self.query_records = []
        self.query_ig = []
        self.redundant_queries = 0
        self.contradicted_model_commit = False

    def state(self):
        s = deepcopy(self.public)
        s["observations"] = deepcopy(self.observations)
        s["query_menu"] = deepcopy(self.query_menu)
        s["remaining_query_budget"] = self.remaining
        return s

    def compatible_ids(self):
        return _compatible(self.cards, self.observations)

    def query_expected_ig(self, query):
        compatible = [c for c in self.cards if c["id"] in self.compatible_ids()]
        if len(compatible) < 2:
            return 0.0
        counts = {}
        for card in compatible:
            y = _predict(card, query["input"])
            counts[y] = counts.get(y, 0) + 1
        n = len(compatible)
        entropy_before = math.log2(n)
        entropy_after = sum((count / n) * math.log2(count) for count in counts.values())
        return max(0.0, entropy_before - entropy_after)

    def apply(self, action):
        if self.terminal:
            raise RuntimeError("episode already finished")
        if not isinstance(action, dict) or not isinstance(action.get("action"), str):
            self.invalid_actions += 1
            return {"accepted": False, "error": "return one JSON object with an action"}
        kind = action["action"]
        if kind == "query":
            qid = action.get("query_id")
            query = next((q for q in self.query_menu if q["id"] == qid), None)
            if query is None or self.remaining <= 0:
                self.invalid_actions += 1
                return {"accepted": False, "error": "query_id is unavailable or budget is exhausted"}
            expected_ig = self.query_expected_ig(query)
            before_ids = self.compatible_ids()
            y = _hidden_predict(self.hidden, query["input"])
            row_id = f"o{len(self.observations) + 1}"
            row = {"id": row_id, "input": dict(query["input"]), "output": y}
            self.observations.append(row)
            after_ids = self.compatible_ids()
            actual_gain = math.log2(max(1, len(before_ids))) - math.log2(max(1, len(after_ids)))
            self.query_ig.append({"expected": expected_ig, "actual": max(0.0, actual_gain)})
            self.redundant_queries += int(expected_ig <= 1e-12)
            self.query_records.append({"id": row_id, "query_id": qid, "input": dict(query["input"]), "output": y})
            self.query_menu.remove(query)
            self.remaining -= 1
            return {"accepted": True, "observation": row}
        if kind == "report":
            verdict = action.get("verdict")
            if verdict not in {"supported", "rejected", "undetermined"}:
                self.invalid_actions += 1
                return {"accepted": False, "error": "verdict must be supported, rejected, or undetermined"}
            confidence = action.get("confidence")
            if not isinstance(confidence, (float, int)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
                self.invalid_actions += 1
                return {"accepted": False, "error": "confidence must be numeric from zero to one"}
            evidence = action.get("evidence_ids", [])
            if not isinstance(evidence, list) or any(not isinstance(x, str) for x in evidence):
                self.invalid_actions += 1
                return {"accepted": False, "error": "evidence_ids must be a list of observation IDs"}
            available_evidence = {row["id"] for row in self.observations}
            if not set(evidence).issubset(available_evidence):
                self.invalid_actions += 1
                return {"accepted": False, "error": "evidence_ids must refer to observed records"}
            model_codes = action.get("candidate_model_codes", [])
            if not isinstance(model_codes, list) or any(not isinstance(x, str) for x in model_codes):
                self.invalid_actions += 1
                return {"accepted": False, "error": "candidate_model_codes must be a list of strings"}
            available_models = {card["id"] for card in self.cards}
            if not set(model_codes).issubset(available_models):
                self.invalid_actions += 1
                return {"accepted": False, "error": "candidate_model_codes must refer to listed hypotheses"}
            location = action.get("location", {})
            if not isinstance(location, dict):
                self.invalid_actions += 1
                return {"accepted": False, "error": "location must be an object"}
            explanation = action.get("explanation", "")
            if not isinstance(explanation, str):
                self.invalid_actions += 1
                return {"accepted": False, "error": "explanation must be a string"}
            self.report = {
                "verdict": verdict, "confidence": float(confidence),
                "candidate_model_codes": model_codes,
                "evidence_ids": evidence, "location": location,
                "explanation": explanation,
            }
            self.terminal = True
            return {"accepted": True, "terminal": True}
        self.invalid_actions += 1
        return {"accepted": False, "error": "action must be query or report"}

    def run(self, agent, max_actions=10):
        reset_episode = getattr(agent, "reset_episode", None)
        if callable(reset_episode):
            reset_episode()
        states, actions = [], []
        for _ in range(max_actions):
            if self.terminal:
                break
            s = self.state()
            states.append(s)
            action = agent.act(s)
            actions.append(action)
            response = self.apply(action)
            if not response.get("accepted"):
                agent.feedback(response)
        forced_termination = not self.terminal
        if forced_termination:
            self.report = {"verdict": "undetermined", "confidence": 0.0,
                           "candidate_model_codes": [], "evidence_ids": [], "location": {},
                           "explanation": "forced report after action limit"}
            self.terminal = True
        scored = score_report(self.world, self.observations, self.report)
        if forced_termination:
            scored = {"decision_correct": False, "diagnosis_correct": False,
                      "localized_correct": False}
        return {
            "category": self.world["category"], "family": self.world["family"],
            "verdict": self.report["verdict"], "confidence": self.report["confidence"],
            "query_count": len(self.query_records), "invalid_actions": self.invalid_actions,
            "action_count": len(actions), "forced_termination": forced_termination,
            "redundant_queries": self.redundant_queries,
            "expected_information_gain": [x["expected"] for x in self.query_ig],
            "actual_information_gain": [x["actual"] for x in self.query_ig],
            "decision_correct": scored["decision_correct"],
            "diagnosis_correct": scored["diagnosis_correct"],
            "localized_correct": scored["localized_correct"],
            "candidate_set_size": len(self.compatible_ids()),
            "query_history": self.query_records,
            "report": self.report,
            "world_id": self.world["world_id"],
        }


def _rows_by_id(rows):
    return {r["id"]: r for r in rows}


def _same_input_conflict(rows):
    groups = {}
    for row in rows:
        groups.setdefault(_input_key(row["input"]), []).append(row)
    for key, group in groups.items():
        if len({r["output"] for r in group}) > 1:
            return key, group
    return None, None


def _has_pair_effect(rows):
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            ia, ib = a["input"], b["input"]
            if ((ia["glyph"], ia["setting"], ia["phase"])
                    == (ib["glyph"], ib["setting"], ib["phase"])
                    and ia["partner"] != ib["partner"] and a["output"] != b["output"]):
                return a, b
    return None, None


def _has_phase_effect(rows):
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            ia, ib = a["input"], b["input"]
            if (ia["glyph"] == ib["glyph"] and ia["phase"] != ib["phase"]
                    and a["output"] != b["output"]):
                return a, b
    return None, None


def score_report(world, rows, report):
    category = world["category"]
    expected = {"NORMAL": "supported", "CONTRADICTION": "rejected",
                "INSUFFICIENCY": "undetermined", "CHANGE": "rejected",
                "HYPOTHESIS_ABSENT": "rejected"}[category]
    decision_correct = report["verdict"] == expected
    declared = report.get("candidate_model_codes", [])
    if not isinstance(declared, list):
        declared = []
    evidence_ids = set(report.get("evidence_ids", []))
    by_id = _rows_by_id(rows)
    evidence = [by_id[x] for x in evidence_ids if x in by_id]
    location = report.get("location") if isinstance(report.get("location"), dict) else {}
    compatible = _compatible(world["cards"], rows)

    if category == "NORMAL":
        localized = (report["verdict"] == "supported"
                     and world["working_model_id"] in declared
                     and len(evidence) >= 2
                     and all(_predict(next(c for c in world["cards"] if c["id"] == world["working_model_id"]), r["input"]) == r["output"] for r in evidence))
        # A normal world can remain observationally ambiguous: the generating
        # account is coherent even when another listed account fits the same rows.
        # Requiring uniqueness incorrectly scores a cautious, evidence-backed
        # supported report as a diagnosis failure.
        diagnosis = localized and all(
            _predict(next(c for c in world["cards"] if c["id"] == world["working_model_id"]), r["input"]) == r["output"]
            for r in rows
        )
    elif category == "CONTRADICTION":
        key, group = _same_input_conflict(rows)
        conflict_ids = {r["id"] for r in (group or [])}
        declared_location = location.get("value")
        key_dict = dict(zip(("glyph", "setting", "partner", "phase"), key or ()))
        localized = (report["verdict"] == "rejected" and bool(key)
                     and conflict_ids.issubset(evidence_ids)
                     and location.get("feature") == "input"
                     and (declared_location == key_dict or declared_location == list(key or ())))
        diagnosis = localized
    elif category == "INSUFFICIENCY":
        true_compatible = set(_compatible(world["cards"], rows))
        declared_cards = [c for c in world["cards"] if c["id"] in declared]
        localized = (report["verdict"] == "undetermined" and len(true_compatible) >= 2
                     and true_compatible.issubset(set(declared)) and len(evidence) >= 2
                     and len(declared_cards) >= 2
                     and all(_predict(c, r["input"]) == r["output"]
                             for c in declared_cards for r in evidence))
        diagnosis = localized
    elif category == "CHANGE":
        pair = _has_phase_effect(rows)
        pair_ids = {r["id"] for r in pair if r} if pair[0] else set()
        phase_card = next(c for c in world["cards"] if c["kind"] == "glyph_phase")
        localized = (report["verdict"] == "rejected" and phase_card["id"] in declared
                     and location.get("feature") == "phase" and pair_ids.issubset(evidence_ids)
                     and bool(pair_ids))
        diagnosis = localized and compatible == [phase_card["id"]]
    else:
        pair = _has_pair_effect(rows)
        pair_ids = {r["id"] for r in pair if r} if pair[0] else set()
        localized = (report["verdict"] == "rejected" and len(compatible) == 0
                     and location.get("feature") == "partner" and pair_ids.issubset(evidence_ids)
                     and bool(pair_ids))
        diagnosis = localized
    return {"decision_correct": decision_correct,
            "diagnosis_correct": bool(diagnosis),
            "localized_correct": bool(localized)}


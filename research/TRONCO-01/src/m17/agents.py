"""Non-trained reference and control policies for M17."""
import random

from generator import _compatible, _input_key, _predict


def _conflict(rows):
    groups = {}
    for row in rows:
        groups.setdefault(_input_key(row["input"]), []).append(row)
    for key, group in groups.items():
        if len({r["output"] for r in group}) > 1:
            return key, group
    return None, None


def _pair_effect(rows):
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            x, y = a["input"], b["input"]
            if ((x["glyph"], x["setting"], x["phase"])
                    == (y["glyph"], y["setting"], y["phase"])
                    and x["partner"] != y["partner"] and a["output"] != b["output"]):
                return a, b
    return None, None


def _phase_effect(rows):
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            x, y = a["input"], b["input"]
            if x["glyph"] == y["glyph"] and x["phase"] != y["phase"] and a["output"] != b["output"]:
                return a, b
    return None, None


class StatisticalAnomalyDetector:
    """Simple residual detector: checks duplicate conflicts and the working account."""

    def feedback(self, value):
        pass

    def report(self, state):
        rows = state["observations"]
        key, group = _conflict(rows)
        if key:
            key_dict = dict(zip(("glyph", "setting", "partner", "phase"), key))
            return {"action": "report", "verdict": "rejected", "candidate_model_codes": [],
                    "evidence_ids": [r["id"] for r in group],
                    "location": {"feature": "input", "value": key_dict},
                    "confidence": 0.95, "explanation": "Repeated input has conflicting outputs."}
        working = state["working_model"]
        # The three published model forms are fixed by the environment contract.
        if "only on glyph" in working["statement"]:
            kind = "glyph"
        elif "only on setting" in working["statement"]:
            kind = "setting"
        else:
            kind = "glyph_phase"
        card = {"kind": kind, "table": working["table"]}
        residuals = [r for r in rows if _predict(card, r["input"]) != r["output"]]
        if not residuals:
            return {"action": "report", "verdict": "supported",
                    "candidate_model_codes": [working["id"]],
                    "evidence_ids": [r["id"] for r in rows[:3]], "location": {"feature": None, "value": None},
                    "confidence": 0.65, "explanation": "No residual against the working account."}
        phase_pair = _phase_effect(rows)
        pair_pair = _pair_effect(rows)
        if phase_pair[0]:
            evidence = list(phase_pair)
            location = {"feature": "phase", "value": [r["input"]["phase"] for r in evidence]}
        elif pair_pair[0]:
            evidence = list(pair_pair)
            location = {"feature": "partner", "value": [r["input"]["partner"] for r in evidence]}
        else:
            evidence = residuals[:3]
            location = {"feature": None, "value": None}
        return {"action": "report", "verdict": "rejected",
                "candidate_model_codes": [], "evidence_ids": [r["id"] for r in evidence],
                "location": location, "confidence": 0.7,
                "explanation": "The working account has residuals."}

    def act(self, state):
        return self.report(state)


class RandomQueryControl:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.detector = StatisticalAnomalyDetector()

    def feedback(self, value):
        pass

    def act(self, state):
        if state["remaining_query_budget"] > 0 and state["query_menu"]:
            return {"action": "query", "query_id": self.rng.choice(state["query_menu"])["id"]}
        return self.detector.report(state)


class FixedQueryControl:
    def __init__(self, seed=0):
        self.detector = StatisticalAnomalyDetector()

    def feedback(self, value):
        pass

    def act(self, state):
        if state["remaining_query_budget"] > 0 and state["query_menu"]:
            return {"action": "query", "query_id": state["query_menu"][0]["id"]}
        return self.detector.report(state)


class SymbolicActiveControl:
    """Public-data-only reference that fits listed tables and tests disagreements."""

    def feedback(self, value):
        pass

    @staticmethod
    def _cards(state):
        cards = []
        for public in state["candidate_models"]:
            statement = public["statement"]
            if "only on glyph" in statement:
                kind = "glyph"
            elif "only on setting" in statement:
                kind = "setting"
            else:
                kind = "glyph_phase"
            cards.append({**public, "kind": kind})
        return cards

    def act(self, state):
        rows = state["observations"]
        conflict_key, conflict_rows = _conflict(rows)
        if conflict_key:
            value = dict(zip(("glyph", "setting", "partner", "phase"), conflict_key))
            return {"action": "report", "verdict": "rejected", "candidate_model_codes": [],
                    "evidence_ids": [r["id"] for r in conflict_rows],
                    "location": {"feature": "input", "value": value}, "confidence": 1.0,
                    "explanation": "Repeated input has conflicting outputs."}

        cards = self._cards(state)
        compatible = [c for c in cards if all(_predict(c, r["input"]) == r["output"] for r in rows)]
        if not compatible:
            pair = _pair_effect(rows)
            if pair[0]:
                evidence = list(pair)
                return {"action": "report", "verdict": "rejected", "candidate_model_codes": [],
                        "evidence_ids": [r["id"] for r in evidence],
                        "location": {"feature": "partner", "value": [r["input"]["partner"] for r in evidence]},
                        "confidence": 1.0, "explanation": "No listed account fits; output changes with partner."}
            return {"action": "report", "verdict": "undetermined", "candidate_model_codes": [],
                    "evidence_ids": [r["id"] for r in rows], "location": {}, "confidence": 0.5,
                    "explanation": "No listed account fits the observations."}

        working_id = state["working_model"]["id"]
        phase_cards = [c for c in compatible if c["kind"] == "glyph_phase"]
        stable_working = any(c["id"] == working_id and c["kind"] != "glyph_phase" for c in compatible)
        if phase_cards and stable_working and state["remaining_query_budget"] > 0:
            phase_card = phase_cards[0]
            for query in state["query_menu"]:
                for row in rows:
                    if (query["input"]["glyph"] == row["input"]["glyph"]
                            and query["input"]["phase"] != row["input"]["phase"]
                            and _predict(phase_card, query["input"]) != row["output"]):
                        return {"action": "query", "query_id": query["id"]}
            for i, first in enumerate(state["query_menu"]):
                for second in state["query_menu"][i + 1:]:
                    a, b = first["input"], second["input"]
                    if (a["glyph"] == b["glyph"] and a["phase"] != b["phase"]
                            and _predict(phase_card, a) != _predict(phase_card, b)):
                        return {"action": "query", "query_id": first["id"]}

        # Query a public measurement only when the surviving listed accounts disagree.
        if state["remaining_query_budget"] > 0:
            informative = []
            for query in state["query_menu"]:
                outputs = {_predict(card, query["input"]) for card in compatible}
                if len(outputs) > 1:
                    informative.append((len(outputs), query))
            if informative:
                query = max(informative, key=lambda item: item[0])[1]
                return {"action": "query", "query_id": query["id"]}

        working = next((card for card in compatible if card["id"] == working_id), None)
        if len(compatible) == 1 and compatible[0]["id"] != working_id:
            target = compatible[0]
            phase_pair = _phase_effect(rows)
            if phase_pair[0]:
                evidence = list(phase_pair)
                location = {"feature": "phase", "value": [r["input"]["phase"] for r in evidence]}
                codes = [target["id"]]
            else:
                evidence = rows
                location = {}
                codes = [target["id"]]
            return {"action": "report", "verdict": "rejected", "candidate_model_codes": codes,
                    "evidence_ids": [r["id"] for r in evidence], "location": location,
                    "confidence": 0.9, "explanation": "Evidence supports a listed account other than the provisional one."}
        if len(compatible) == 1 and working is not None:
            return {"action": "report", "verdict": "supported", "candidate_model_codes": [working_id],
                    "evidence_ids": [r["id"] for r in rows], "location": {}, "confidence": 0.9,
                    "explanation": "The provisional account predicts the observations."}
        return {"action": "report", "verdict": "undetermined",
                "candidate_model_codes": [c["id"] for c in compatible],
                "evidence_ids": [r["id"] for r in rows], "location": {}, "confidence": 0.5,
                "explanation": "Multiple listed accounts remain compatible."}


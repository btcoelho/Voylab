"""Model-facing harness for the v3 pilot (no training). A backend turns text into text; everything else is deterministic.

The backend receives only the system prompt, the user text and a JSON schema. `state` is passed to fake backends for tests;
real backends MUST ignore it (the real backend in hf_backend.py does not accept it).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import env_v3 as E  # noqa: E402
import generator_v3 as g  # noqa: E402

SYSTEM_PROMPT = """Investigas um sistema com quatro atributos (glyph, setting, partner, phase), cada um com dois valores. A saída é sempre 0 ou 1.
Tens observações, três cartas que descrevem possíveis regras, e uma carta de trabalho W.
Uma carta é admissível se reproduz todas as observações. Veredictos sobre W:
- rejected: W não reproduz as observações.
- supported: W reproduz as observações e todas as regras admissíveis dão a W a mesma saída nas entradas retidas.
- undetermined: W reproduz as observações mas há regras admissíveis que discordam de W nas entradas retidas.
Podes consultar entradas do menu (cada consulta revela a saída) até esgotar o orçamento, depois comprometes-te.
Depois de comprometeres, chega evidência nova: mantém ou revê. Se a evidência nova contradiz as observações anteriores, o veredicto de revisão é inconsistent.
Responde SEMPRE com um único objeto JSON, sem texto adicional."""

# v3.1 (18/10/2026, fase 1 do instrumento): o espaço de regras passa a ser dito. O texto v3 acima fica intacto
# (as corridas R1-R3 e L1-L3 usaram-no); o veredicto de referência não muda, só deixa de ser ambíguo.
SYSTEM_PROMPT_V31 = """Investigas um sistema com quatro atributos (glyph, setting, partner, phase), cada um com dois valores. A saída é sempre 0 ou 1.
REGRAS POSSÍVEIS: qualquer regra que dê 0 ou 1 a cada uma das 16 entradas e dependa de no máximo dois dos quatro atributos. São 70 regras ao todo.
As três cartas são apenas exemplos dessas regras; a regra verdadeira pode não ser nenhuma delas. W é a carta de trabalho.
Uma regra é admissível se reproduz todas as observações (as iniciais e as que consultaste). Veredictos sobre W:
- rejected: W não reproduz as observações.
- supported: W reproduz as observações e TODAS as regras admissíveis, entre as 70 e não só as cartas, dão a mesma saída que W em cada entrada retida.
- undetermined: W reproduz as observações, mas pelo menos uma regra admissível, entre as 70, discorda de W numa entrada retida.
Em admissible_cards indica quais das três cartas são admissíveis.
Podes consultar entradas do menu (cada consulta revela a saída) até esgotar o orçamento, depois comprometes-te.
Depois de comprometeres, chega evidência nova: mantém ou revê, aplicando as mesmas definições a todas as observações juntas (as anteriores e as novas).
- inconsistent: nenhuma das 70 regras reproduz todas as observações juntas. Isto inclui a mesma entrada aparecer com saídas diferentes, mas também pode acontecer sem isso.
Responde SEMPRE com um único objeto JSON, sem texto adicional."""
PROMPTS = {"v3": SYSTEM_PROMPT, "v3.1": SYSTEM_PROMPT_V31}


def action_schema(phase: str, state: dict | None = None, cards_object: bool = False) -> dict:
    """JSON schema of a legal action. With `state` (pilot round 2 onwards) the ids are restricted to what the state
    shows: query ids to the current menu (and no query branch when the budget is spent), card ids to the cards,
    prediction keys to the held-out positions. These ids are already in the prompt; the backend still never sees `state`."""
    if state is None:
        cards = {"type": "array", "items": {"type": "string"}}
        qid = {"type": "string"}
        preds = {"type": "object", "additionalProperties": {"enum": ["0", "1"]}}
        can_query = True
    else:
        ids = [c["id"] for c in state["candidate_models"]]
        if cards_object:   # round 3: one required true/false per card, so a card cannot be repeated
            cards = {"type": "object", "properties": {i: {"type": "boolean"} for i in ids}, "required": ids,
                     "additionalProperties": False}
        else:
            cards = {"type": "array", "items": {"enum": ids}}
        qid = {"enum": [q["id"] for q in state.get("query_menu", [])]}
        preds = {"type": "object", "properties": {str(i): {"enum": ["0", "1"]}
                                                  for i in range(1, len(state["held_out_inputs"]) + 1)},
                 "additionalProperties": False}
        can_query = state.get("remaining_query_budget", 0) > 0 and bool(qid["enum"])
    if phase == "explore":
        options = []
        if can_query:
            options.append({"type": "object", "properties": {"action": {"const": "query"}, "query_id": qid},
                            "required": ["action", "query_id"], "additionalProperties": False})
        options += [
            {"type": "object", "properties": {"action": {"const": "commit"},
                                              "verdict": {"enum": list(E.VERDICTS_ALLOWED)}, "admissible_cards": cards,
                                              "predictions": preds},
             "required": ["action", "verdict", "admissible_cards", "predictions"], "additionalProperties": False},
            {"type": "object", "properties": {"action": {"const": "suspend"}}, "required": ["action"],
             "additionalProperties": False}]
        return {"anyOf": options}
    return {"anyOf": [
        {"type": "object", "properties": {"action": {"const": "keep"}}, "required": ["action"], "additionalProperties": False},
        {"type": "object", "properties": {"action": {"const": "revise"}, "verdict": {"enum": list(E.REVISION_VERDICTS)},
                                          "admissible_cards": cards},
         "required": ["action", "verdict", "admissible_cards"], "additionalProperties": False}]}


def render_state(s: dict, cards_object: bool = False) -> str:
    L = ["OBSERVAÇÕES"]
    L += [f"- {o['id']}: " + ", ".join(f"{k}={v}" for k, v in o["input"].items()) + f" -> {o['output']}" for o in s["observations"]]
    if s.get("new_evidence"):
        L.append("EVIDÊNCIA NOVA")
        L += [f"- {o['id']}: " + ", ".join(f"{k}={v}" for k, v in o["input"].items()) + f" -> {o['output']}" for o in s["new_evidence"]]
    L.append("CARTAS")
    for c in s["candidate_models"]:
        L.append(f"- {c['id']} ({c['statement']})")
        L += [f"    {k} -> {v}" for k, v in c["table"].items()]
    L.append(f"CARTA DE TRABALHO: {s['working_model_id']}")
    L.append("ENTRADAS RETIDAS (previsões 1 a 4, por esta ordem)")
    L += [f"- {i}: " + ", ".join(f"{k}={v}" for k, v in x.items()) for i, x in enumerate(s["held_out_inputs"], 1)]
    cards_tpl = ("{" + ",".join(f'"{c["id"]}":true|false' for c in s["candidate_models"]) + "}"
                 if cards_object else '["ids"]')
    if s["phase"] == "explore":
        L.append(f"CONSULTAS DISPONÍVEIS (orçamento restante {s['remaining_query_budget']})")
        L += [f"- {q['id']}: " + ", ".join(f"{k}={v}" for k, v in q["input"].items()) for q in s["query_menu"]]
        L.append('AÇÕES: {"action":"query","query_id":"qN"} | {"action":"commit","verdict":"rejected|supported|undetermined",'
                 '"admissible_cards":' + cards_tpl + ',"predictions":{"1":"0|1","2":"0|1","3":"0|1","4":"0|1"}} | {"action":"suspend"}')
    else:
        L.append('AÇÕES: {"action":"keep"} | {"action":"revise","verdict":"rejected|supported|undetermined|inconsistent",'
                 '"admissible_cards":' + cards_tpl + '}')
    return "\n".join(L)


class Backend:
    name = "base"

    def generate(self, system: str, user: str, schema: dict, state: dict | None = None) -> str:
        raise NotImplementedError


MODES = ("phase", "state", "state_cards_object")   # pilot rounds 1, 2, 3


def to_env_action(action, state: dict, mode: str):
    """Round 3 only: {"A": true, "B": false, ...} -> ["A"], in the order the cards are shown. Anything else unchanged."""
    if mode == "state_cards_object" and isinstance(action, dict) and isinstance(action.get("admissible_cards"), dict):
        chosen = action["admissible_cards"]
        action = {**action, "admissible_cards": [c["id"] for c in state["candidate_models"] if chosen.get(c["id"]) is True]}
    return action


def run_episode(world: dict, backend: Backend, max_turns: int = 10, pass_state: bool = False,
                mode: str = "state_cards_object", prompt: str = "v3") -> dict:
    assert mode in MODES
    system = PROMPTS[prompt]
    ep = E.Episode(world)
    turns = []
    for t in range(max_turns):
        if ep.done:
            break
        st = ep.state()
        obj = mode == "state_cards_object"
        user = render_state(st, cards_object=obj)
        schema = action_schema(st["phase"], st if mode != "phase" else None, cards_object=obj)
        raw = backend.generate(system, user, schema, st) if pass_state else backend.generate(system, user, schema)
        try:
            action = json.loads(raw)
            parsed = True
        except (ValueError, TypeError):
            action, parsed = None, False
        env_action = to_env_action(action, st, mode) if parsed else {"action": "__unparseable__"}
        out = ep.step(env_action)
        turns.append({"turn": t, "phase": st["phase"], "prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
                      "output": raw, "parsed": parsed, "accepted": out["ok"], "error": out.get("error"),
                      **({"env_action": env_action} if mode == "state_cards_object" else {})})
    res = ep.result()
    res["turns"] = len(turns)
    res["hit_turn_limit"] = not ep.done
    return {"world_id": world["world_id"], "result": res, "transcript": turns}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [c - h, c + h]


def aggregate(episodes: list[dict]) -> dict:
    n = len(episodes)
    R = [e["result"] for e in episodes]
    done = [r for r in R if r.get("complete")]
    turns = [t for e in episodes for t in e["transcript"]]
    parsed = sum(t["parsed"] for t in turns)
    accepted = sum(t["accepted"] for t in turns)

    def rate(key, pool):
        k = sum(bool(r.get(key)) for r in pool)
        return {"k": k, "n": len(pool), "rate": k / len(pool) if pool else None, "ci95": wilson(k, len(pool))}
    return {"episodes": n, "complete": rate("complete", R), "forced_termination": rate("forced_termination", R),
            "turn_limit": rate("hit_turn_limit", R),
            "outputs_parseable_json": {"k": parsed, "n": len(turns), "rate": parsed / len(turns) if turns else None},
            "actions_accepted": {"k": accepted, "n": len(turns), "rate": accepted / len(turns) if turns else None,
                                 "invalid_rate": 1 - accepted / len(turns) if turns else None},
            "among_complete": {k: rate(k, done) for k in ("reach", "inference_error", "search_error", "evidence_ignored",
                                                         "premature_stop", "suspend_used", "suspend_correct",
                                                         "revision_type_I", "revision_type_II", "cards_exact")},
            "queries_mean": (sum(r["queries"] for r in done) / len(done)) if done else None}

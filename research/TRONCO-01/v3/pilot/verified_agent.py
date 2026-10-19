"""Agente + verificador (§23). O agente propõe; cada afirmação atómica que a proposta implica é verificada contra a fonte
pública (observações e cartas visíveis); se alguma for falsa, o agente recebe só os factos falsificados e responde de novo.

Afirmações verificadas: para cada carta e cada observação visível, "a carta dá nesta entrada a saída observada".
Uma carta é admissível se e só se todas as suas afirmações forem verdadeiras. A proposta do agente é contestada quando a sua
lista de cartas admissíveis discorda do que o verificador apurou. Não se verifica supported vs undetermined (exige raciocinar
sobre as 70 regras) nem a escolha da consulta: essa limitação está pré-registada.

O verificador nunca vê o estado escondido do mundo: só o que o agente vê. Dois verificadores:
- CodeVerifier: exato (referência);
- LLMVerifier: um modelo, uma chamada por afirmação, resposta VERDADEIRA/FALSA; cada resposta é comparada com a verdade
  calculada por código e gravada, para medir a taxa de erro do próprio verificador.
"""
from __future__ import annotations

import json

from pilot_harness import Backend

VERIFIER_SYSTEM = ("Verificas uma única afirmação contra uma fonte. A carta é uma tabela: cada linha diz a saída para as "
                   "entradas que têm esses valores, seja qual for o valor dos outros atributos. Responde só com uma palavra: "
                   "VERDADEIRA ou FALSA.")


def card_output(card: dict, inp: dict) -> str | None:
    vals = set(inp.values())
    hits = [v for k, v in card["table"].items() if all(t in vals for t in k.split("|"))]
    return hits[0] if len(hits) == 1 else None


def visible_observations(state: dict) -> list[dict]:
    return list(state["observations"]) + list(state.get("new_evidence") or [])


def claim_text(card: dict, obs: dict) -> str:
    tab = "\n".join(f"    {k} -> {v}" for k, v in card["table"].items())
    inp = ", ".join(f"{k}={v}" for k, v in obs["input"].items())
    return (f"CARTA {card['id']} ({card['statement']})\n{tab}\nOBSERVAÇÃO {obs['id']}: {inp} -> {obs['output']}\n"
            f"AFIRMAÇÃO: a carta {card['id']} dá, nesta entrada, a saída observada ({obs['output']}).")


class CodeVerifier:
    name = "code"

    def __init__(self):
        self.log = []

    def check(self, card, obs) -> bool:
        return card_output(card, obs["input"]) == obs["output"]


class LLMVerifier:
    def __init__(self, backend):
        self.backend, self.name, self.log = backend, "llm:" + backend.name, []

    def check(self, card, obs) -> bool:
        out = self.backend.generate(VERIFIER_SYSTEM, claim_text(card, obs), {})
        word = (out or "").strip().upper()
        verdict = word.startswith("VERDADEIRA")
        truth = card_output(card, obs["input"]) == obs["output"]
        self.log.append({"card": card["id"], "obs": obs["id"], "raw": (out or "")[:40], "said_true": verdict,
                         "parsed": word.startswith(("VERDADEIRA", "FALSA")), "truth": truth,
                         "meta": getattr(self.backend, "last_meta", {})})
        return verdict


class VerifiedAgent(Backend):
    """Wraps the agent backend. Needs the public state (pass_state=True); the agent itself only ever receives text."""

    def __init__(self, agent, verifier, max_rounds: int = 3):
        self.agent, self.verifier, self.max_rounds = agent, verifier, max_rounds
        self.name = f"{agent.name}+verificador:{verifier.name}"
        self.rounds_log = []

    def _verify(self, state):
        cache, adm, false_facts = {}, {}, []
        for c in state["candidate_models"]:
            ok_all = True
            for o in visible_observations(state):
                key = (c["id"], o["id"])
                if key not in cache:
                    cache[key] = self.verifier.check(c, o)
                if not cache[key]:
                    ok_all = False
                    false_facts.append(f"- A carta {c['id']} NÃO dá a saída observada em {o['id']} "
                                       f"(observado {o['output']}).")
            adm[c["id"]] = ok_all
        return adm, false_facts

    def generate(self, system, user, schema, state=None):
        out = self.agent.generate(system, user, schema)
        if state is None:
            return out
        verified = None
        for r in range(self.max_rounds):
            try:
                a = json.loads(out)
            except (ValueError, TypeError):
                return out                                  # format failure: left to the environment, as before
            if not isinstance(a, dict) or a.get("action") not in ("commit", "revise") or not isinstance(a.get("admissible_cards"), dict):
                return out
            if verified is None:
                verified = self._verify(state)
            adm, facts = verified
            claimed = {k: bool(v) for k, v in a["admissible_cards"].items()}
            disagree = [cid for cid in adm if claimed.get(cid) != adm[cid]]
            self.rounds_log.append({"phase": state["phase"], "round": r, "disagree": disagree})
            if not disagree:
                return out
            lines = ["VERIFICAÇÃO INDEPENDENTE DA TUA RESPOSTA (contra as observações visíveis):"]
            for cid in disagree:
                lines.append(f"- Marcaste a carta {cid} como {'admissível' if claimed.get(cid) else 'não admissível'}; "
                             f"o verificador apurou que {'é' if adm[cid] else 'não é'} admissível.")
            lines += [f for f in facts if any(f"carta {cid} " in f for cid in disagree)]
            lines.append("Revê a tua resposta com base nisto e responde de novo com uma única ação JSON.")
            out = self.agent.generate(system, user + "\n" + "\n".join(lines), schema)
        return out

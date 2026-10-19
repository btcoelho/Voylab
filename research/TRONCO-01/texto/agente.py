"""Agente analista com relatório verificado (docs/TEXTO_ESPECIFICACAO.md §4–5).

Fluxo: o agente recebe o texto cifrado (só as palavras) e a lista de medidas disponíveis. Pode pedir medidas
(`medir`) e, no fim, entrega um relatório: para cada hipótese, um veredicto (rejeitada | compativel | indeterminada)
e as afirmações verificáveis que o sustentam. O verificador recalcula cada afirmação. Afirmações falsas devolvem
ao agente só os factos que falharam, até MAX_ROUNDS rondas.

O agente nunca vê a família verdadeira nem a chave. Backends são objetos com .generate(system, user) -> str.
"""
from __future__ import annotations

import json

import medidas as M
import verificador as V

HIPOTESES = ["LN", "SUB", "POL", "TRA", "VER", "NUL", "BAR", "TAB", "ALE"]
VEREDICTOS = {"rejeitada", "compativel", "indeterminada"}
MAX_ROUNDS = 2

SYSTEM = (
    "Analisas um texto cifrado. Só podes basear-te nas medidas que pedires e nos resultados que o verificador "
    "devolve. Para cada hipótese (" + ", ".join(HIPOTESES) + ") dá um veredicto (rejeitada, compativel ou "
    "indeterminada) e cita as afirmações numéricas que o sustentam, com os seus ids. Uma afirmação sem medida é "
    "interpretação e não conta como prova. Indica em 'mais_provavel' a hipótese que achas mais provável, ou "
    "'indeterminada' se as medidas não a distinguem. Usa os números exatamente como o resultado os deu. Responde só com JSON: "
    '{"action":"medir","medida":"..."} ou {"action":"relatorio","mais_provavel":"...","hipoteses":{"LN":{"veredicto":"...","afirmacoes":["A1"]}},'
    '"afirmacoes":[{"id":"A1","medida":"...","parametros":{},"campo":"...","valor":0.0,"tolerancia":0.0}]}'
)


def medidas_disponiveis():
    return ["alfabeto", "entropia", "coincidencia", "kasiski", "palavras", "zipf", "posicional",
            "repeticoes", "dependencia", "sukhotin"]


def run_medida(words, nome):
    fn = getattr(M, nome)
    return fn(words)


class Analista:
    """Ciclo de um texto. Devolve o relatório final verificado e o registo completo."""

    def __init__(self, backend, max_rounds=MAX_ROUNDS, max_medidas=12):
        self.backend = backend
        self.max_rounds = max_rounds
        self.max_medidas = max_medidas

    def analisar(self, words):
        log = {"medidas": [], "rondas": [], "erro": None}
        user = self._prompt_inicial(words)
        pedidos = 0
        while pedidos < self.max_medidas:
            out = self.backend.generate(SYSTEM, user, {})
            try:
                a = json.loads(out)
            except (ValueError, TypeError):
                log["erro"] = "formato_invalido"
                return None, log
            if a.get("action") == "medir":
                nome = a.get("medida")
                if nome not in medidas_disponiveis():
                    user += f"\nMedida desconhecida: {nome}. Disponíveis: {medidas_disponiveis()}."
                else:
                    res = run_medida(words, nome)
                    log["medidas"].append(nome)
                    user += f"\nRESULTADO {nome}: {json.dumps(res, ensure_ascii=False)}"
                pedidos += 1
                continue
            if a.get("action") != "relatorio":
                log["erro"] = "acao_invalida"
                return None, log
            return self._verificar(words, a, user, log)
        log["erro"] = "limite_medidas"
        return None, log

    def _verificar(self, words, rel, user, log):
        for r in range(self.max_rounds + 1):
            afs = rel.get("afirmacoes", [])
            res = V.verifica_todas(words, afs)
            falsas = [x for x in res if x["verdadeira"] is False]
            log["rondas"].append({"ronda": r, "afirmacoes": len(afs), "falsas": [x["id"] for x in falsas]})
            if not falsas or r == self.max_rounds:
                rel["_verificacao"] = res
                return rel, log
            linhas = ["VERIFICAÇÃO (recalculada a partir do texto):"]
            for x in falsas:
                linhas.append(f"- A afirmação {x['id']} é FALSA: valor calculado {x['valor_a']}, "
                              f"afirmado {x.get('valor_b')}.")
            linhas.append("Corrige o relatório e responde com uma única ação JSON 'relatorio'.")
            out = self.backend.generate(SYSTEM, user + "\n" + "\n".join(linhas), {})
            try:
                rel = json.loads(out)
            except (ValueError, TypeError):
                log["erro"] = "formato_invalido_na_correcao"
                return None, log
        return rel, log

    def _prompt_inicial(self, words):
        n = sum(len(w) for w in words)
        return (f"Texto cifrado: {len(words)} palavras, {n} glifos. Primeiras palavras: "
                + " ".join("".join(w) for w in words[:12])
                + ". Medidas disponíveis: " + ", ".join(medidas_disponiveis()) + ".")


def pontuar(relatorio, verdade):
    """Compara com a família verdadeira. Pontua: família nunca 'rejeitada' se for a verdadeira; veredicto da verdadeira."""
    if relatorio is None:
        return {"valido": False}
    h = relatorio.get("hipoteses", {})
    v_verd = h.get(verdade, {}).get("veredicto")
    return {"valido": True, "verdadeira_veredicto": v_verd, "mais_provavel": relatorio.get("mais_provavel"),
            "acerto": relatorio.get("mais_provavel") == verdade,
            "verdadeira_rejeitada": v_verd == "rejeitada",
            "afirmacoes_falsas": sum(1 for x in relatorio.get("_verificacao", []) if x["verdadeira"] is False)}

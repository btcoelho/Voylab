import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import agente as A  # noqa: E402
import transformacoes as T  # noqa: E402

TEXTO = [list(w) for w in ["abcdef", "fedcb", "abcabc", "bca", "cab", "aabbcc", "dcba", "abc", "cba", "bbb"]]


class Scripted:
    def __init__(self, outs):
        self.outs, self.seen = list(outs), []

    def generate(self, system, user, schema):
        self.seen.append(user)
        return self.outs.pop(0)


class Ciclo(unittest.TestCase):
    def test_medir_e_relatorio_verdadeiro(self):
        rel = {"action": "relatorio", "hipoteses": {"LN": {"veredicto": "compativel", "afirmacoes": ["A1"]}},
               "afirmacoes": [{"id": "A1", "medida": "palavras", "campo": "n_palavras", "valor": 10, "tolerancia": 0}]}
        b = Scripted([json.dumps({"action": "medir", "medida": "palavras"}), json.dumps(rel)])
        out, log = A.Analista(b).analisar(TEXTO)
        self.assertIsNotNone(out)
        self.assertEqual(log["medidas"], ["palavras"])
        self.assertTrue(out["_verificacao"][0]["verdadeira"])

    def test_falsa_recebe_so_o_facto_falso_e_corrige(self):
        falso = {"action": "relatorio", "hipoteses": {},
                 "afirmacoes": [{"id": "A1", "medida": "palavras", "campo": "n_palavras", "valor": 99, "tolerancia": 0}]}
        certo = {"action": "relatorio", "hipoteses": {},
                 "afirmacoes": [{"id": "A1", "medida": "palavras", "campo": "n_palavras", "valor": 10, "tolerancia": 0}]}
        b = Scripted([json.dumps(falso), json.dumps(certo)])
        out, log = A.Analista(b).analisar(TEXTO)
        self.assertIn("FALSA", b.seen[1])
        self.assertIn("A1", b.seen[1])
        self.assertEqual(log["rondas"][0]["falsas"], ["A1"])
        self.assertEqual(log["rondas"][1]["falsas"], [])

    def test_so_factos_visiveis_no_feedback(self):
        falso = {"action": "relatorio", "hipoteses": {},
                 "afirmacoes": [{"id": "A1", "medida": "palavras", "campo": "n_palavras", "valor": 99, "tolerancia": 0}]}
        b = Scripted([json.dumps(falso), json.dumps(falso), json.dumps(falso)])
        out, log = A.Analista(b, max_rounds=2).analisar(TEXTO)
        self.assertEqual(len(log["rondas"]), 3)
        self.assertNotIn("SUB", b.seen[1])

    def test_formato_invalido_para_sem_inventar(self):
        out, log = A.Analista(Scripted(["texto livre"])).analisar(TEXTO)
        self.assertIsNone(out)
        self.assertEqual(log["erro"], "formato_invalido")

    def test_medida_desconhecida_nao_executa(self):
        b = Scripted([json.dumps({"action": "medir", "medida": "magia"}),
                      json.dumps({"action": "relatorio", "hipoteses": {}, "afirmacoes": []})])
        out, log = A.Analista(b).analisar(TEXTO)
        self.assertEqual(log["medidas"], [])
        self.assertIn("Medida desconhecida", b.seen[1])

    def test_agente_nao_ve_a_familia(self):
        c, _meta = T.vigenere(TEXTO, 5)
        b = Scripted([json.dumps({"action": "relatorio", "hipoteses": {}, "afirmacoes": []})])
        A.Analista(b).analisar(c)
        self.assertNotIn("POL", b.seen[0])
        self.assertNotIn("periodo", b.seen[0])


if __name__ == "__main__":
    unittest.main()

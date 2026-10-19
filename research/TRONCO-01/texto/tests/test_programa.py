import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import programa as P  # noqa: E402

M = {"entropia.h1": 4.0, "entropia.h2_fluxo": 3.9, "alfabeto.glifos_distintos": 26}


class Sandbox(unittest.TestCase):
    def test_executa_funcao_simples(self):
        c = "def classificar(m):\n    if m['entropia.h2_fluxo'] > m['entropia.h1'] - 0.25:\n        return 'TRA'\n    return 'SUB'"
        self.assertEqual(P.executar(c, M), "TRA")

    def test_recusa_import_e_atributos(self):
        for c in ["import os\ndef classificar(m):\n    return 'LN'",
                  "def classificar(m):\n    return m.__class__",
                  "def classificar(m):\n    return open('x')"]:
            with self.assertRaises(ValueError):
                P.executar(c, M)

    def test_justificacao_avaliada_por_referencia(self):
        self.assertTrue(P.avaliar("m['entropia.h2_fluxo'] < m['entropia.h1']", M))
        self.assertFalse(P.avaliar("m['alfabeto.glifos_distintos'] <= 10", M))


class Ciclo(unittest.TestCase):
    def test_justificacao_falsa_volta_e_corrige(self):
        outs = [json.dumps({"action": "programa", "codigo": "def classificar(m):\n    return 'VER'",
                            "justificacao": ["m['alfabeto.glifos_distintos'] <= 10"]}),
                json.dumps({"action": "programa", "codigo": "def classificar(m):\n    return 'SUB'",
                            "justificacao": ["m['alfabeto.glifos_distintos'] > 20"]})]

        class B:
            seen = []

            def generate(self, s, u, sc):
                B.seen.append(u)
                return outs.pop(0)
        words = [list("abcdefghij"), list("klmnopqrst"), list("uvwxyz")] * 30
        rel, log = P.Programador(B()).analisar(words)
        self.assertEqual(rel["mais_provavel"], "SUB")
        self.assertIn("FALSA", B.seen[1])
        self.assertEqual(len(log["rondas"]), 2)


if __name__ == "__main__":
    unittest.main()

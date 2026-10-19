import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import transformacoes as T  # noqa: E402
import verificador as V  # noqa: E402

TEXTO = [list(w) for w in ["abcdef", "fedcb", "abcabc", "bca", "cab", "aabbcc", "dcba"]]


def igual(a, b):
    return [list(x) for x in a] == [list(x) for x in b]


class Inversas(unittest.TestCase):
    def test_substituicao(self):
        c, m = T.substituicao(TEXTO, 7)
        self.assertTrue(igual(T.decifra_substituicao(c, m["chave"]), TEXTO))

    def test_vigenere(self):
        c, m = T.vigenere(TEXTO, 3)
        self.assertTrue(igual(T.decifra_vigenere(c, m["chave"]), TEXTO))

    def test_transposicao(self):
        c, m = T.transposicao(TEXTO, 5)
        self.assertTrue(igual(T.decifra_transposicao(c, m["colunas"], m["ordem"]), TEXTO))

    def test_nulos(self):
        c, m = T.nulos(TEXTO, 11, taxa=0.3)
        self.assertTrue(igual(T.decifra_nulos(c, m["posicoes"], m["comprimentos"]), TEXTO))

    def test_comprimentos_preservados_na_substituicao(self):
        c, _ = T.substituicao(TEXTO, 1)
        self.assertEqual([len(w) for w in c], [len(w) for w in TEXTO])


class Verificador(unittest.TestCase):
    def test_afirmacao_falsa_detetada(self):
        afs = [{"id": "A1", "medida": "palavras", "campo": "comprimento_medio", "valor": 99.0, "tolerancia": 0.01}]
        r = V.verifica_todas(TEXTO, afs)[0]
        self.assertFalse(r["verdadeira"])

    def test_comparacao_entre_medidas(self):
        afs = [{"id": "A2", "medida": "entropia", "campo": "h0", "op": ">",
                "outra": {"medida": "entropia", "campo": "h2_fluxo"}, "margem": 0.0}]
        r = V.verifica_todas(TEXTO, afs)[0]
        self.assertIn("verdadeira", r)

    def test_sem_medida_e_interpretacao(self):
        r = V.verifica(TEXTO, {"id": "A3", "texto": "parece cifra"})
        self.assertTrue(r["interpretacao"])
        self.assertIsNone(r["verdadeira"])


if __name__ == "__main__":
    unittest.main()


class Malformada(unittest.TestCase):
    def test_campo_dict_conta_como_falsa(self):
        r = V.verifica_todas(TEXTO, [{"id": "A9", "medida": "entropia", "campo": "h1", "valor": {"x": 1}}])[0]
        self.assertFalse(r["verdadeira"])
        self.assertTrue(r["malformada"])

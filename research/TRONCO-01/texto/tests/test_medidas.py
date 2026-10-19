import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import medidas as M  # noqa: E402


def W(*ws):
    return [list(w) for w in ws]


class Entropia(unittest.TestCase):
    def test_uniform_two_glyphs_is_one_bit(self):
        e = M.entropia(W("ab", "ba", "ab", "ba"))
        self.assertAlmostEqual(e["h0"], 1.0, places=4)

    def test_deterministic_successor_has_zero_h2(self):
        # a -> b sempre; b -> a sempre dentro da palavra
        e = M.entropia(W("abab", "abab"))
        self.assertAlmostEqual(e["h2_palavra"], 0.0, places=4)


class Coincidencia(unittest.TestCase):
    def test_ic_of_single_letter_is_one(self):
        self.assertAlmostEqual(M._ic(list("aaaa")), 1.0)

    def test_ic_uniform_four_letters(self):
        # 4 letras distintas, 4 ocorrências cada uma: IC = 4*(4*3)/(16*15) = 0.2
        s = list("abcd" * 4)
        self.assertAlmostEqual(M._ic(s), 4 * 3 * 4 / (16 * 15), places=6)


class Zipf(unittest.TestCase):
    def test_perfect_zipf_slope_minus_one(self):
        words = []
        for rank in range(1, 30):
            words += [[f"w{rank}"]] * int(1000 / rank)
        z = M.zipf([[w] for w in [x[0] for x in words]])
        self.assertAlmostEqual(z["declive"], -1.0, delta=0.05)


class Repeticoes(unittest.TestCase):
    def test_edit_distance(self):
        self.assertEqual(M._edit(list("kitten"), list("sitting")), 3)
        self.assertEqual(M._edit(list("ab"), list("ab")), 0)

    def test_repeated_adjacent_words(self):
        r = M.repeticoes(W("ab", "ab", "cd"))
        self.assertEqual(r["palavras_repetidas_seguidas"], 1)


class Dependencia(unittest.TestCase):
    def test_mutual_information_deterministic(self):
        # fronteira sempre 'a'->'b': MI = H(pares) = 0 se só há um par
        self.assertAlmostEqual(M._mi([("a", "b")] * 10), 0.0, places=6)
        # dois pares equiprováveis: MI = 1 bit
        self.assertAlmostEqual(M._mi([("a", "x"), ("b", "y")] * 5), 1.0, places=6)

    def test_result_has_permutation_baseline(self):
        d = M.dependencia(W("ab", "ba", "ab", "ba", "ab"), permutacoes=20)
        self.assertIn("p_empirico", d)
        self.assertEqual(d["permutacoes"], 20)


class Perfil(unittest.TestCase):
    def test_same_distribution_zero_js(self):
        words = W("abc", "abc")
        ref = [1 / 3, 1 / 3, 1 / 3]
        self.assertAlmostEqual(M.perfil(words, ref)["js"], 0.0, places=6)


class Tudo(unittest.TestCase):
    def test_runs_on_small_input(self):
        out = M.tudo(W("abcde", "fgh", "abc", "de"), referencia=[0.2, 0.2, 0.2, 0.2, 0.2])
        for k in ("alfabeto", "entropia", "coincidencia", "kasiski", "palavras", "zipf",
                  "posicional", "repeticoes", "dependencia", "sukhotin", "perfil"):
            self.assertIn(k, out)
        self.assertTrue(all(isinstance(v, float) and not math.isnan(v) for v in
                            [out["entropia"]["h0"], out["coincidencia"]["ic"]]))


if __name__ == "__main__":
    unittest.main()

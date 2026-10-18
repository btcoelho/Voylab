from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "pilot")]
import generator_v3 as g  # noqa: E402
import select_worlds as S  # noqa: E402


class WorldIdentity(unittest.TestCase):
    def test_pilot_selection_and_hash_unchanged(self):
        ws = S.pilot_worlds()
        self.assertEqual(S.worlds_sha(ws), "cdf242859c37a6ab330e374d8873122d89d6f120e1f2f263a49271d2639cc452")
        self.assertEqual(len({w["world_id"] for w in ws}), 20)       # legacy id kept as it was
        self.assertEqual(len({w["uid"] for w in ws}), 48)
        self.assertEqual(len({g.content_sha(w) for w in ws}), 48)

    def test_uid_is_the_generation_key(self):
        w = S.pilot_worlds()[0]
        k = w["generation_key"]
        again = g.make_world(k["seed"], k["difficulty"], k["family"], k["index"], k["target"], k["kind"],
                             budget=k["budget"], k0=k["k0"], max_tries=1500)
        self.assertEqual(again["uid"], w["uid"])
        self.assertEqual(g.content_sha(again), g.content_sha(w))
        other = dict(k, target="rejected" if k["target"] != "rejected" else "supported")
        self.assertNotEqual(g.world_uid(other), w["uid"])


if __name__ == "__main__":
    unittest.main()

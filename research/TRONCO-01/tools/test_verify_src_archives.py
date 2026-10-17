import hashlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify_src_archives as v  # noqa: E402


def make_tree(tmp: Path, files: dict[str, bytes], inner="work/pkg/"):
    (tmp / "packages").mkdir(parents=True)
    with zipfile.ZipFile(tmp / "packages/a.zip", "w") as z:
        for rel, data in files.items():
            z.writestr(inner + rel, data)
    for rel, data in files.items():
        p = tmp / "src/x" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return [{"src_dir": "src/x", "archive": "packages/a.zip", "inner": inner}]


class SrcArchiveTests(unittest.TestCase):
    def test_real_repository_src_matches_archives(self):
        report = v.check()
        self.assertEqual(report["failures"], [], report)
        for m in report["mappings"]:
            self.assertTrue(m["archive_unchanged_by_check"])
            self.assertGreater(m["archive_files"], 0)

    def test_check_never_modifies_the_archives(self):
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (v.ROOT / "packages").glob("*.zip")}
        v.check()
        after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before}
        self.assertEqual(before, after)

    def test_detects_changed_missing_and_extra_files(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mapping = make_tree(tmp, {"a.py": b"A\r\n", "b.py": b"B\n"})
            self.assertEqual(v.check(tmp, mapping)["failures"], [])
            (tmp / "src/x/a.py").write_bytes(b"A\n")           # CRLF normalised: must be caught
            self.assertEqual(v.check(tmp, mapping)["failures"], ["src/x"])
            (tmp / "src/x/a.py").write_bytes(b"A\r\n")
            (tmp / "src/x/b.py").unlink()
            self.assertIn("b.py", v.check(tmp, mapping)["mappings"][0]["missing_in_src"])
            (tmp / "src/x/b.py").write_bytes(b"B\n")
            (tmp / "src/x/new.py").write_bytes(b"x")
            self.assertEqual(v.check(tmp, mapping)["mappings"][0]["extra_in_src"], ["new.py"])

    def test_empty_inner_prefix_is_a_failure(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mapping = make_tree(tmp, {"a.py": b"A"})
            mapping[0]["inner"] = "work/does-not-exist/"
            self.assertEqual(v.check(tmp, mapping)["failures"], ["src/x"])


if __name__ == "__main__":
    unittest.main()

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "package_digest.py"
spec = importlib.util.spec_from_file_location("package_digest", SCRIPT)
digest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digest_module)


class PackageDigestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "package"
        self.root.mkdir()
        self.write("SKILL.md", b"skill")

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def digest(self):
        return digest_module.package_digest(self.root)["digest"]

    def test_all_declared_input_groups_affect_digest(self):
        previous = self.digest()
        for name in ("README.md", "CHANGELOG.md", "requirements-dev.txt", "references/r.md", "schemas/s.json", "examples/e.json", "agents/a.yaml", "scripts/s.py", "tests/evals/cases.jsonl"):
            with self.subTest(name=name):
                self.write(name, b"data")
                current = self.digest()
                self.assertNotEqual(previous, current)
                previous = current

    def test_metadata_and_cache_do_not_change_digest(self):
        original = self.digest()
        for name in (".git/config", ".idea/workspace.xml", "scripts/__pycache__/a.pyc", "tests/.pytest_cache/state", "scripts/loose.pyc"):
            self.write(name, b"cache")
        (self.root / "SKILL.md").chmod(0o700)
        self.assertEqual(original, self.digest())

    def test_sorted_paths_and_relocation_are_stable(self):
        self.write("references/z.md", b"z")
        self.write("references/a.md", b"a")
        original = digest_module.package_digest(self.root)
        self.assertEqual([f["path"] for f in original["files"]], ["SKILL.md", "references/a.md", "references/z.md"])
        other = self.root.parent / "other"
        other.mkdir()
        for entry in reversed(original["files"]):
            target = other / entry["path"]
            target.parent.mkdir(exist_ok=True)
            target.write_bytes((self.root / entry["path"]).read_bytes())
        self.assertEqual(original, digest_module.package_digest(other))

    def test_rename_and_content_changes_are_detected(self):
        path = self.write("references/one.md", b"payload")
        initial = self.digest()
        renamed = path.rename(path.with_name("two.md"))
        self.assertNotEqual(initial, self.digest())
        previous = self.digest()
        renamed.write_bytes(b"changed")
        self.assertNotEqual(previous, self.digest())

    def test_length_framing_and_unusual_names(self):
        # Naive path + content concatenation produces the same byte stream.
        first = self.write("references/a", b"bc")
        before = self.digest()
        first.unlink()
        self.write("references/ab", b"c")
        self.assertNotEqual(before, self.digest())
        self.write("references/space unicode \u03b1\nfile.md", b"\x00\n")
        self.assertEqual(self.digest(), self.digest())

    def test_file_and_directory_symlinks_fail_even_when_broken(self):
        (self.root / "references").mkdir()
        for target in (self.root / "SKILL.md", self.root, self.root / "missing"):
            with self.subTest(target=str(target)):
                link = self.root / "references" / "link"
                link.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "Symlink"):
                    self.digest()
                link.unlink()

    def test_missing_skill_and_symlink_root_fail(self):
        link = self.root.parent / "link"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            digest_module.package_digest(link)
        (self.root / "SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing SKILL"):
            self.digest()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires named pipes")
    def test_non_regular_input_fails_without_reading(self):
        (self.root / "references").mkdir()
        os.mkfifo(self.root / "references" / "pipe")
        with self.assertRaisesRegex(ValueError, "Non-regular"):
            self.digest()

    def test_cli_compare_exit_statuses_and_read_only(self):
        other = self.root.parent / "other"
        other.mkdir()
        (other / "SKILL.md").write_bytes(b"skill")
        command = [sys.executable, str(SCRIPT), str(self.root), "--compare", str(other)]
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        (other / "SKILL.md").write_bytes(b"different")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        (other / "SKILL.md").unlink()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

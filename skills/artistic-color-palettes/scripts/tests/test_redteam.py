"""Red-team fixes (notes/4L-review.md, sources branch): B1 forged provenance, S1 missing kasane names, S5 kept 'no', S6 protected folders."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from common import run_script, temp_project
import build_tokens as bt
import handoff as ho

HEX = "Ivory=#f0e6d2,Indigo=#1f2f5a,Vermilion=#d2452b"


class TestForgedProvenance(unittest.TestCase):
    REFUSED = ["Wada plate 400 (*A Dictionary of Color Combinations*, 1933)", "Wada plate 218", "wada PLATE 5", "Plate 12 of something",
               "Editorial palette by colorcombinations.org, inspired by Wada's method", "Sampled from The Kiss, Gustav Klimt, 1907-08",
               "Kasane no irome: Fuji", "kasane: fuji", "Palette from the colorcombinations.org site"]
    ALLOWED = ["Original composition by this skill (not a plate)", "Refined from Impeccable's palette", "Acme brand colours (supplied by the user)",
               "Original composition (colours supplied by the user)"]

    def test_handoff_refuses_a_forged_label_and_writes_nothing(self):
        for label in ("Wada plate 400 (*A Dictionary of Color Combinations*, 1933)", "Wada plate 218"):
            with temp_project() as tmp:
                p = run_script("handoff.py", "--hex", HEX, "--provenance", label, "--project-dir", tmp)
                self.assertEqual(p.returncode, 2, p.stdout_text + p.stderr_text)
                self.assertIn("provenance labels for data sources come from data/palettes.csv; use --palette <id>", p.stderr_text)
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_build_tokens_refuses_and_writes_nothing(self):
        with temp_project() as tmp:
            out = Path(tmp) / "t.json"
            p = run_script("build_tokens.py", "--hex", HEX, "--provenance", "Wada plate 400", "--out", str(out))
            self.assertEqual(p.returncode, 2, p.stderr_text)
            self.assertIn("use --palette <id>", p.stderr_text)
            self.assertFalse(out.exists())
            self.assertEqual(p.stdout_text, "")

    def test_every_pattern_is_refused_and_honest_labels_pass(self):
        for label in self.REFUSED:
            with self.assertRaises(SystemExit, msg=label):
                bt.build_tokens(hexes=HEX, provenance_label=label)
        for label in self.ALLOWED:
            t = bt.build_tokens(hexes=HEX, provenance_label=label)
            self.assertEqual(t["palette"]["label"], label)

    def test_a_forged_label_inside_a_tokens_file_is_refused_too(self):
        t = bt.build_tokens(hexes=HEX)
        t["palette"]["label"] = "Wada plate 400 (*A Dictionary of Color Combinations*, 1933)"
        with temp_project() as tmp:
            tok = Path(tmp) / "t.json"
            tok.write_text(bt.dump_tokens(t), encoding="utf-8")
            proj = Path(tmp) / "proj"
            proj.mkdir()
            p = run_script("handoff.py", "--tokens", str(tok), "--project-dir", str(proj))
            self.assertEqual(p.returncode, 2, p.stderr_text)
            self.assertEqual(list(proj.iterdir()), [])


class TestMissingKasaneName(unittest.TestCase):
    def test_unknown_patterns_exit_2_with_no_rows(self):
        for q in ("yanagi-gasane", "Kōri-gasane", "kasane sakura-gasane", "Sakura no nioi", "ume no usuyo"):
            p = run_script("search.py", q)
            self.assertEqual(p.returncode, 2, (q, p.stdout_text))
            self.assertIn("is not in the data. Nothing was substituted.", p.stderr_text)
            self.assertNotIn("1. ", p.stdout_text)
            j = run_script("search.py", q, "--json")
            self.assertEqual(json.loads(j.stdout_text)["results"], [])

    def test_real_patterns_still_found_with_or_without_macrons(self):
        for q, want in (("matsu-gasane", "kasane-matsu-gasane"), ("Kōbai no nioi", "kasane-kobai-no-nioi"), ("ume-gasane", "kasane-ume-gasane")):
            p = run_script("search.py", q, "--json")
            self.assertEqual(p.returncode, 0, q)
            self.assertEqual(json.loads(p.stdout_text)["results"][0]["id"], want)

    def test_quoted_title_without_a_match_is_not_substituted(self):
        p = run_script("search.py", '"Mona Lisa"')
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("1. ", p.stdout_text)
        self.assertEqual(run_script("search.py", '"Great Wave"').returncode, 0)

    def test_unknown_words_are_always_reported(self):
        p = run_script("search.py", "calm", "blue", "zzzword", "--json")
        data = json.loads(p.stdout_text)
        self.assertEqual(p.returncode, 0)
        self.assertTrue(data["results"])
        self.assertTrue(any("Words not found in the data: zzzword" in n for n in data["notes"]))
        t = run_script("search.py", "calm", "blue", "zzzword")
        self.assertIn("Words not found in the data: zzzword", t.stdout_text)


class TestKeptNo(unittest.TestCase):
    def test_a_recorded_no_survives_a_rerun_without_the_flag(self):
        for value, stored in (("no", False), ("declined", "declined")):
            with temp_project() as tmp:
                pj = Path(tmp) / "design" / "palette.json"
                run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--claude-md", value)
                self.assertEqual(json.loads(pj.read_text(encoding="utf-8"))["handoff"]["claude_md"], stored)
                run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
                self.assertEqual(json.loads(pj.read_text(encoding="utf-8"))["handoff"]["claude_md"], stored, value)

    def test_only_a_missing_answer_becomes_not_asked(self):
        with temp_project() as tmp:
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            pj = Path(tmp) / "design" / "palette.json"
            self.assertEqual(json.loads(pj.read_text(encoding="utf-8"))["handoff"]["claude_md"], "not_asked")


class TestProtectedFolders(unittest.TestCase):
    def _run(self, fake_home: Path, project: Path, *extra: str):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("pathlib.Path.home", return_value=fake_home), redirect_stdout(out), redirect_stderr(err):
            code = ho.main(["--palette", "wada-229", "--project-dir", str(project), *extra])
        return code, err.getvalue()

    def test_home_ancestors_and_global_agent_folders_are_refused(self):
        with tempfile.TemporaryDirectory(prefix="acp fake root ") as root:
            home = Path(root) / "users" / "someone"
            for sub in (".claude", ".codex", ".agents", ".claude/nested"):
                (home / sub).mkdir(parents=True, exist_ok=True)
            targets = [home, home.parent, Path(root), home / ".claude", home / ".codex", home / ".agents", home / ".claude" / "nested"]
            for target in targets:
                before = sorted(p.relative_to(root).as_posix() for p in Path(root).rglob("*"))
                code, err = self._run(home, target, "--claude-md", "yes", "--user-confirmed")
                self.assertEqual(code, 4, (str(target), err))
                self.assertIn("Nothing was written", err)
                self.assertEqual(sorted(p.relative_to(root).as_posix() for p in Path(root).rglob("*")), before, str(target))

    def test_an_ordinary_project_inside_home_is_fine(self):
        with tempfile.TemporaryDirectory(prefix="acp fake root ") as root:
            home = Path(root) / "someone"
            proj = home / "work" / "my app"
            proj.mkdir(parents=True)
            code, err = self._run(home, proj, "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(code, 0, err)
            self.assertTrue((proj / "CLAUDE.md").exists())
            self.assertFalse((home / "CLAUDE.md").exists())

    def test_claude_md_resolving_into_a_protected_folder_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="acp fake root ") as root:
            home = Path(root) / "someone"
            proj = home / "work"
            proj.mkdir(parents=True)
            (home / ".claude").mkdir()
            real = proj / "CLAUDE.md"
            try:
                real.symlink_to(home / ".claude" / "CLAUDE.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available here")
            code, err = self._run(home, proj, "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(code, 4, err)
            self.assertFalse((home / ".claude" / "CLAUDE.md").exists())

    def test_cli_with_a_fake_home_environment(self):
        with tempfile.TemporaryDirectory(prefix="acp fake home ") as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir()
            env = {"USERPROFILE": str(home), "HOME": str(home), "HOMEDRIVE": home.drive, "HOMEPATH": str(home)[len(home.drive):]}
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(home / ".claude"), env_extra=env)
            self.assertEqual(p.returncode, 4, p.stdout_text + p.stderr_text)
            self.assertEqual(sorted(x.name for x in home.iterdir()), [".claude"])
            self.assertEqual(list((home / ".claude").iterdir()), [])


if __name__ == "__main__":
    unittest.main()

"""preview.py: self-contained HTML, three candidates, light/dark/greyscale, provenance labels."""
import re
import unittest
from pathlib import Path

from common import run_script, temp_project


class TestPreview(unittest.TestCase):
    def test_writes_self_contained_page(self):
        with temp_project("acp preview ") as tmp:
            out = Path(tmp) / "out dir" / "preview.html"
            p = run_script("preview.py", "--palette", "wada-229", "--palette", "paint-the-great-wave-off-kanagawa",
                           "--palette", "kasane-kobai-no-nioi", "--strategy", "full-palette", "--mode", "persuade", "--out", str(out))
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertEqual(Path(p.stdout_text.strip()).resolve(), out.resolve())
            html = out.read_text(encoding="utf-8")
            self.assertEqual(html.count('class="cand"'), 3)
            for kind in ("light", "dark", "grey"):
                self.assertEqual(len(re.findall(rf'class="panel {kind}"', html)), 3, kind)
            self.assertIn("Wada plate 229 (*A Dictionary of Color Combinations*, 1933)", html)
            self.assertIn("Sampled from Under the Wave off Kanagawa (The Great Wave), Katsushika Hokusai, c. 1831 by colorcombinations.org", html)
            self.assertIn("not the artist&#x27;s original colours", html)
            self.assertIn("Kasane no irome: Kōbai no nioi", html)
            self.assertIn("<table>", html)
            self.assertIn('class="chart"', html)
            self.assertIn('class="tag"', html)
            # no network, no external fonts or scripts
            self.assertNotRegex(html, r"(src|href)\s*=")
            self.assertNotIn("<script", html)
            self.assertNotIn("<link", html)
            self.assertNotIn("@import", html)
            self.assertNotRegex(html, r"url\(")

    def test_candidate_count_is_enforced(self):
        p = run_script("preview.py", "--palette", "wada-229", "--palette", "wada-1")
        self.assertEqual(p.returncode, 2)
        self.assertIn("3 to 5", p.stderr_text)
        p = run_script("preview.py", *sum((["--palette", f"wada-{i}"] for i in range(1, 7)), []))
        self.assertEqual(p.returncode, 2)

    def test_unknown_palette_is_an_error(self):
        p = run_script("preview.py", "--palette", "wada-1", "--palette", "wada-2", "--palette", "wada-999")
        self.assertEqual(p.returncode, 2)
        self.assertIn("not in the data", p.stderr_text)

    def test_strategies_and_hex_candidates(self):
        with temp_project("acp preview ") as tmp:
            for strat in ("restrained", "committed", "drenched"):
                out = Path(tmp) / f"{strat}.html"
                p = run_script("preview.py", "--palette", "wada-100", "--palette", "ed-kurenai-kon", "--hex", "#9a2a2a,#1b2a4e,#f4eee0",
                               "--strategy", strat, "--out", str(out))
                self.assertEqual(p.returncode, 0, p.stderr_text)
                html = out.read_text(encoding="utf-8")
                self.assertIn("Original composition (colours supplied by the user)", html)
                self.assertIn(f"{strat.capitalize()} / Operate", html)


class TestScriptsHaveHelp(unittest.TestCase):
    def test_help_for_every_script(self):
        for name in ("colorlib.py", "build_data.py", "search.py", "build_tokens.py", "validate.py", "preview.py", "handoff.py"):
            p = run_script(name, "--help")
            self.assertEqual(p.returncode, 0, name)
            self.assertIn("usage:", p.stdout_text, name)


if __name__ == "__main__":
    unittest.main()

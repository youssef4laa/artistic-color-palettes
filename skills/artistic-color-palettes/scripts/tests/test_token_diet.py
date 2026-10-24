"""Token diet (v0.1.1): compact script output on the common path, with the full detail still one flag away."""
import json
import unittest
from pathlib import Path

from common import run_script, temp_project
import build_tokens as bt
import validate as vd


class TestSearchListing(unittest.TestCase):
    def test_default_listing_omits_source_licence_and_score(self):
        p = run_script("search.py", "slate", "blue")
        self.assertEqual(p.returncode, 0, p.stderr_text)
        self.assertIn("label: Wada plate", p.stdout_text)
        self.assertNotIn("source:", p.stdout_text)
        self.assertNotIn("licence:", p.stdout_text)
        self.assertNotIn("score:", p.stdout_text)
        self.assertIn("note: read 'slate blue' as", p.stdout_text)  # the reading line stays

    def test_full_restores_them_and_json_keeps_every_field(self):
        p = run_script("search.py", "slate", "blue", "--full")
        self.assertIn("source: https://colorcombinations.org/", p.stdout_text)
        self.assertIn("licence: PD+MIT+CC-BY-4.0", p.stdout_text)
        self.assertIn("score:", p.stdout_text)
        j = run_script("search.py", "slate", "blue", "--json", "--limit", "2")
        data = json.loads(j.stdout_text)
        self.assertEqual(j.stdout_text.count("\n"), 1)  # compact: one line
        for r in data["results"]:
            self.assertTrue(r["source_url"].startswith("https://"))
            self.assertTrue(r["licence"])
            self.assertIn("score", r)

    def test_drift_note_still_printed_by_default(self):
        p = run_script("search.py", "sunflowers")
        self.assertIn("drift:", p.stdout_text)
        self.assertNotIn("source:", p.stdout_text)


class TestHandoffDryRun(unittest.TestCase):
    def test_new_project_dry_run_is_a_summary_unless_diff(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--dry-run")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertIn("DESIGN.md: would be created (", p.stdout_text)
            self.assertIn("provenance: Wada plate 229", p.stdout_text)
            self.assertIn("acp:begin tokens", p.stdout_text)
            self.assertNotIn("+++ DESIGN.md", p.stdout_text)
            self.assertLess(len(p.stdout_text), 900)
            self.assertEqual(list(proj.iterdir()), [])
            q = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--dry-run", "--diff")
            self.assertEqual(q.returncode, 0, q.stderr_text)
            self.assertIn("+++ DESIGN.md (proposed)", q.stdout_text)
            self.assertIn("<!-- acp:begin colors v1 -->", q.stdout_text)
            self.assertEqual(list(proj.iterdir()), [])

    def test_existing_file_dry_run_still_diffs(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            w = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj))
            self.assertEqual(w.returncode, 0, w.stderr_text)
            same = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--dry-run")
            self.assertIn("DESIGN.md: unchanged (no changes)", same.stdout_text)
            other = run_script("handoff.py", "--palette", "wada-218", "--project-dir", str(proj), "--dry-run")
            self.assertEqual(other.returncode, 0, other.stderr_text)
            self.assertIn("+++ DESIGN.md (proposed)", other.stdout_text)
            self.assertIn("DESIGN.md: markers", other.stdout_text)  # only our marker regions change

    def test_error_prefix_is_not_doubled(self):
        p = run_script("preview.py", "--palette", "wada-229", "--out", "x.html")
        self.assertEqual(p.returncode, 2)
        self.assertTrue(p.stderr_text.startswith("error: "))
        self.assertNotIn("error: error:", p.stderr_text)
        h = run_script("handoff.py", "--palette", "wada-999", "--project-dir", ".", "--dry-run")
        self.assertNotEqual(h.returncode, 0)
        self.assertNotIn("error: error:", h.stderr_text)


class TestValidateReport(unittest.TestCase):
    def test_many_apca_shortfalls_collapse_by_family_and_all_expands(self):
        t = bt.build_tokens(palette="wada-218", strategy="restrained", mode="operate")
        vd.validate_tokens(t, do_fix=True)
        short = vd.text_report(t, False)
        full = vd.text_report(t, True)
        self.assertIn("(--all lists every pair)", short)
        self.assertIn("pairs:", short)  # a family line such as "[dark] status roles (14 pairs: ...)"
        self.assertNotIn("(--all lists every pair)", full)
        self.assertIn("ALL PAIRS", full)
        self.assertLess(len(short), len(full))
        # every per-role shortfall is still in the annotated JSON
        misses = [p for p in t["contrast"]["pairs"] if not p["apca_pass"]]
        self.assertEqual(len(misses), t["contrast"]["summary"]["apca_below_target"])
        # flags and adjustments are printed in full in both forms
        for section in ("FLAGS", "ADJUSTMENTS"):
            self.assertIn(section, short)
            self.assertEqual(short.count(f"\n  [light] vibrating"), full.count(f"\n  [light] vibrating"))

    def test_role_family(self):
        self.assertEqual(vd.role_family("danger-text"), "status roles")
        self.assertEqual(vd.role_family("on-warning"), "status roles")
        self.assertEqual(vd.role_family("voice-2-mark"), "voice roles")
        self.assertEqual(vd.role_family("border-strong"), "borders")
        self.assertEqual(vd.role_family("accent-text"), "accent roles")
        self.assertEqual(vd.role_family("text-muted"), "text")


if __name__ == "__main__":
    unittest.main()

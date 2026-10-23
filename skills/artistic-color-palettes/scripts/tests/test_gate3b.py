"""Iteration-2 gate fixes: --claude-md yes needs --user-confirmed; kasane hitoe equal to a layer colour."""
import json
import unittest
from pathlib import Path

from common import run_script, temp_project
import colorlib as cl
import build_tokens as bt
import validate as vd


class TestUserConfirmed(unittest.TestCase):
    def test_yes_without_confirmation_is_refused_and_writes_nothing(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--claude-md", "yes")
            self.assertEqual(p.returncode, 4, p.stdout_text + p.stderr_text)
            self.assertIn("--user-confirmed", p.stderr_text)
            self.assertEqual(list(Path(tmp).iterdir()), [])  # nothing at all: no DESIGN.md, no design/, no pointer files

    def test_yes_with_confirmation_writes_the_pointer(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertTrue((Path(tmp) / "CLAUDE.md").exists())
            pj = json.loads((Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertIs(pj["handoff"]["claude_md"], True)

    def test_no_and_declined_need_no_confirmation(self):
        for value in ("no", "declined"):
            with temp_project() as tmp:
                p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--claude-md", value)
                self.assertEqual(p.returncode, 0, (value, p.stderr_text))
                self.assertFalse((Path(tmp) / "CLAUDE.md").exists())

    def test_user_confirmed_alone_does_not_write_a_pointer(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--user-confirmed")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertFalse((Path(tmp) / "CLAUDE.md").exists())
            self.assertIn("only matters with --claude-md yes", p.stderr_text)

    def test_help_explains_the_flag(self):
        h = run_script("handoff.py", "--help").stdout_text
        self.assertIn("--user-confirmed", h)
        self.assertIn("explicitly said yes", h)


class TestKasaneHitoeEqualsLayer(unittest.TestCase):
    def test_kurenai_momiji_drenched_persuade(self):
        t = bt.build_tokens(palette="kasane-kurenai-momiji", strategy="drenched", mode="persuade")
        vd.validate_tokens(t, do_fix=True)
        self.assertEqual(t["kasane_note"], "hitoe equals layer 5; accent taken from layer 3")
        self.assertEqual(t["palette"]["kasane_note"], t["kasane_note"])
        members = {m["hex"]: m for m in t["palette"]["members"]}
        shared = members["#c91f37"]
        self.assertEqual(shared["roles"], ["hitoe", "layer5"])
        edge = members["#f3c13a"]
        self.assertEqual(edge["name"], "ki (layer 3)")
        self.assertNotIn("hitoe", edge["roles"])  # no other colour is called hitoe
        self.assertEqual(sum("hitoe" in m["roles"] for m in t["palette"]["members"]), 1)
        self.assertEqual(t["assignment"]["drench"], "kurenai")
        self.assertEqual(t["assignment"]["accent"], "ki")
        # the accent is the layer that separates best from the page colour among those passing 3:1
        shared_L = cl.hex_to_oklch("#c91f37")[0]
        passing = [m for m in t["palette"]["members"] if m["hex"] != "#c91f37" and cl.wcag_contrast(m["hex"], "#c91f37") >= 3.0]
        best = max(passing, key=lambda m: abs(m["oklch"][0] - shared_L))
        self.assertEqual(best["hex"], "#f3c13a")
        self.assertEqual(t["roles"]["light"]["accent"]["hex"], "#f3c13a")
        self.assertTrue(t["contrast"]["gate_pass"])

    def test_note_is_surfaced_in_the_handoff_region(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "kasane-kurenai-momiji", "--strategy", "drenched", "--mode", "persuade", "--project-dir", tmp)
            self.assertEqual(p.returncode, 0, p.stderr_text)
            text = (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("Kasane note: hitoe equals layer 5; accent taken from layer 3", text)
            self.assertIn("ki (layer 3)", text)
            pj = json.loads((Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["palette"]["kasane_note"], "hitoe equals layer 5; accent taken from layer 3")

    def test_no_note_when_the_shared_colour_is_not_the_page(self):
        t = bt.build_tokens(palette="kasane-kurenai-momiji")  # restrained: the page is neutral
        self.assertIsNone(t["kasane_note"])
        t = bt.build_tokens(palette="kasane-kobai-no-nioi", strategy="drenched", mode="persuade")  # hitoe ao is distinct from every layer
        self.assertIsNone(t["kasane_note"])

    def test_explicit_accent_wins(self):
        t = bt.build_tokens(palette="kasane-kurenai-momiji", strategy="drenched", mode="persuade", roles={"accent": "asaki kuchiba"})
        self.assertIsNone(t["kasane_note"])
        self.assertEqual(t["assignment"]["accent"], "asaki-kuchiba")


if __name__ == "__main__":
    unittest.main()

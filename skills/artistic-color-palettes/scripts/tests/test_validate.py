"""validate.py: gate, flags, --fix adjusts lightness only and reports exactly what moved."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from common import run_script
import colorlib as cl
import build_tokens as bt
import validate as vd


def broken_tokens():
    t = bt.build_tokens(palette="wada-229")
    # a known failing pair: muted text far too light for the page (about 2.8:1)
    role = t["roles"]["light"]["text-muted"]
    role["hex"] = "#999999"
    role["L"] = round(cl.hex_to_oklch("#999999")[0], 4)
    return t


class TestValidate(unittest.TestCase):
    def test_clean_build_passes_after_fix_and_reports_measurements(self):
        t = bt.build_tokens(palette="wada-229")
        block = vd.validate_tokens(t, do_fix=True)
        self.assertTrue(block["gate_pass"])
        self.assertGreater(block["summary"]["pairs"], 80)
        pair = next(p for p in block["pairs"] if (p["mode"], p["fg"], p["bg"]) == ("light", "text", "bg"))
        self.assertAlmostEqual(pair["wcag"], cl.wcag_contrast(pair["fg_hex"], pair["bg_hex"]), places=2)
        self.assertAlmostEqual(abs(pair["apca"]), abs(cl.apca_lc(pair["fg_hex"], pair["bg_hex"])), delta=0.1)
        self.assertEqual(pair["apca_target"], 75)

    def test_known_failing_pair_is_flagged(self):
        t = broken_tokens()
        block = vd.validate_tokens(t, do_fix=False)
        self.assertFalse(block["gate_pass"])
        fails = [(p["mode"], p["fg"], p["bg"]) for p in block["pairs"] if p["gate"] and not p["wcag_pass"]]
        self.assertIn(("light", "text-muted", "bg"), fails)

    def test_fix_report_names_exactly_what_moved(self):
        t = broken_tokens()
        before = copy.deepcopy(t["roles"])
        vd.validate_tokens(t, do_fix=True)
        self.assertTrue(t["contrast"]["gate_pass"])
        adj = [a for a in t["adjustments"] if a["role"] == "text-muted" and a["mode"] == "light"]
        self.assertGreaterEqual(len(adj), 1)  # the gate fix, optionally followed by a small APCA nudge
        a = adj[0]
        self.assertEqual(a["before_hex"], "#999999")
        self.assertNotEqual(a["after_hex"], "#999999")
        self.assertEqual(a["reason"], "WCAG gate")
        self.assertEqual(adj[-1]["after_hex"], t["roles"]["light"]["text-muted"]["hex"])
        self.assertLess(a["before_ratio"], 4.5)
        self.assertGreaterEqual(a["after_ratio"], 4.5)
        self.assertLess(a["after_L"], a["before_L"])  # moved darker, away from the light page
        self.assertAlmostEqual(a["before_L"], cl.hex_to_oklch("#999999")[0], places=3)
        self.assertAlmostEqual(a["after_L"], cl.hex_to_oklch(a["after_hex"])[0], places=3)
        # hue kept, chroma not increased
        self.assertAlmostEqual(cl.hex_to_oklch(a["after_hex"])[2], cl.hex_to_oklch("#999999")[2], delta=8)
        # every role that changed is named in the report, and nothing else changed
        moved = {(m, k) for m in ("light", "dark") for k in t["roles"][m] if t["roles"][m][k]["hex"] != before[m][k]["hex"]}
        reported = {(x["mode"], x["role"]) for x in t["adjustments"]}
        self.assertEqual(moved, reported)
        # the surfaces were never touched
        for m in ("light", "dark"):
            for k in vd.SURFACES:
                self.assertEqual(t["roles"][m][k]["hex"], before[m][k]["hex"])

    def test_fix_changes_lightness_only(self):
        for pid, strat in (("wada-100", "drenched"), ("kasane-shiragiku", "drenched"), ("paint-the-scream", "full-palette")):
            t = bt.build_tokens(palette=pid, strategy=strat, mode="persuade")
            vd.validate_tokens(t, do_fix=True)
            for a in t["adjustments"]:
                if a.get("moved_step"):
                    continue
                h0, h1 = cl.hex_to_oklch(a["before_hex"])[2], cl.hex_to_oklch(a["after_hex"])[2]
                c0 = cl.hex_to_oklch(a["before_hex"])[1]
                if c0 > 0.03:  # hue is only meaningful for coloured roles
                    self.assertLess(cl.hue_diff(h0, h1), 10, f"{pid} {a['role']}")

    def test_cli_exit_codes_without_and_with_fix(self):
        with tempfile.TemporaryDirectory(prefix="acp validate ") as tmp:
            path = Path(tmp) / "bad tokens.json"
            path.write_text(bt.dump_tokens(broken_tokens()), encoding="utf-8")
            p = run_script("validate.py", str(path))
            self.assertEqual(p.returncode, 1)
            self.assertIn("GATE FAILURES", p.stdout_text)
            self.assertIn("text-muted", p.stdout_text)
            self.assertIn("RESULT: FAIL", p.stdout_text)
            out = Path(tmp) / "fixed.json"
            p = run_script("validate.py", str(path), "--fix", "--out", str(out))
            self.assertEqual(p.returncode, 0, p.stdout_text)
            self.assertIn("ADJUSTMENTS", p.stdout_text)
            self.assertIn("#999999 ->", p.stdout_text)
            self.assertIn("RESULT: PASS", p.stdout_text)
            fixed = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(fixed["contrast"]["gate_pass"])
            self.assertTrue(any(a["role"] == "text-muted" for a in fixed["adjustments"]))

    def test_stdin_and_json_output(self):
        tok = bt.dump_tokens(bt.build_tokens(palette="wada-1"))
        p = run_script("validate.py", "-", "--fix", "--json", input_text=tok)
        self.assertEqual(p.returncode, 0, p.stderr_text)
        self.assertTrue(json.loads(p.stdout_text)["contrast"]["gate_pass"])

    def test_flags_vibrating_vanishing_cvd_and_midlightness(self):
        t = bt.build_tokens(palette="wada-229")
        # force two vivid, complementary, equal-lightness fills next to each other
        for mode in ("light", "dark"):
            L = 0.55 if mode == "light" else 0.55
            t["roles"][mode]["accent"]["hex"] = cl.oklch_to_hex(L, 0.14, 25)
            t["roles"][mode]["voice-1"]["hex"] = cl.oklch_to_hex(L, 0.14, 160)
        block = vd.validate_tokens(t, do_fix=False)
        kinds = {f["type"] for f in block["flags"]}
        self.assertIn("vibrating", kinds)
        self.assertIn("mid_lightness_fill", kinds)
        self.assertIn("cvd", kinds)
        vanish = bt.build_tokens(palette="wada-229")
        for mode in ("light", "dark"):
            vanish["roles"][mode]["voice-1"]["hex"] = cl.oklch_to_hex(0.55, 0.10, 62)
            vanish["roles"][mode]["accent"]["hex"] = cl.oklch_to_hex(0.58, 0.10, 70)
        kinds = {f["type"] for f in vd.validate_tokens(vanish)["flags"]}
        self.assertIn("vanishing", kinds)

    def test_ramp_step_check_flags_a_collapsed_ramp(self):
        t = bt.build_tokens(palette="wada-229")
        t["ramps"]["accent"]["light"]["300"] = t["ramps"]["accent"]["light"]["400"]
        block = vd.validate_tokens(t)
        self.assertFalse(block["gate_pass"])
        self.assertTrue(any(r["ramp"] == "accent" and r["mode"] == "light" for r in block["ramp_failures"]))

    def test_ramp_checks_pass_for_generated_ramps(self):
        for pid in ("wada-229", "kasane-fuji", "paint-the-kiss"):
            t = bt.build_tokens(palette=pid)
            self.assertEqual(vd.ramp_checks(t), [], pid)


if __name__ == "__main__":
    unittest.main()

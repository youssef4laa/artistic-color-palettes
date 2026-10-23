"""Iteration-2 fixes: --on-accent, --action-style, pinned colours, voice split, proportion rule, --text-min, not_asked."""
import json
import re
import unittest
from pathlib import Path

from common import run_script, temp_project
import colorlib as cl
import build_tokens as bt
import validate as vd
import handoff as ho


def fixed(pid, **kw):
    t = bt.build_tokens(palette=pid, **kw)
    vd.validate_tokens(t, do_fix=True)
    return t


class TestOnAccent(unittest.TestCase):
    def test_forced_light_label_moves_the_fill_and_fix_does_not_flip_it(self):
        auto = fixed("kasane-kurenai-momiji", strategy="drenched", mode="persuade")
        self.assertNotEqual(auto["roles"]["light"]["on-accent"]["hex"], "#ffffff")  # the pale pinned accent takes a dark label
        t = fixed("kasane-kurenai-momiji", strategy="drenched", mode="persuade", on_accent="light")
        self.assertTrue(t["contrast"]["gate_pass"])
        for mode in ("light", "dark"):
            r = t["roles"][mode]
            self.assertEqual(r["on-accent"]["hex"], "#ffffff", mode)
            self.assertGreaterEqual(cl.wcag_contrast("#ffffff", r["accent"]["hex"]), 4.5, mode)
        self.assertNotEqual(t["roles"]["light"]["accent"]["ref"], "accent:300")  # the role moved (darker) ...
        self.assertEqual(t["ramps"]["accent"]["light"]["300"], "#f3c13a")  # ... the pinned value did not
        self.assertTrue(any("seed fails the fill gate" in n or "accent fill moved" in n for n in t["notes"]))  # the report says the plate colour was not used
        dark = fixed("wada-1", on_accent="dark")
        for mode in ("light", "dark"):
            r = dark["roles"][mode]
            self.assertNotEqual(r["on-accent"]["hex"], "#ffffff")
            self.assertGreaterEqual(cl.wcag_contrast(r["on-accent"]["hex"], r["accent"]["hex"]), 4.5)

    def test_forced_polarity_survives_validate_fix_on_a_broken_fill(self):
        t = bt.build_tokens(palette="ed-kurenai-kon", on_accent="light")
        t["roles"]["light"]["accent"]["hex"] = "#c8a060"  # too light for a white label
        vd.validate_tokens(t, do_fix=True)
        self.assertEqual(t["roles"]["light"]["on-accent"]["hex"], "#ffffff")
        self.assertGreaterEqual(cl.wcag_contrast("#ffffff", t["roles"]["light"]["accent"]["hex"]), 4.5)
        self.assertTrue(t["contrast"]["gate_pass"])

    def test_on_accent_cli_flag(self):
        p = run_script("build_tokens.py", "--palette", "wada-1", "--on-accent", "dark")
        self.assertEqual(p.returncode, 0, p.stderr_text)
        data = json.loads(p.stdout_text)
        self.assertEqual(data["policy"]["on_accent"], "dark")
        self.assertNotEqual(data["roles"]["light"]["on-accent"]["hex"], "#ffffff")
        self.assertIn("--on-accent", run_script("handoff.py", "--help").stdout_text)
        self.assertNotEqual(run_script("build_tokens.py", "--palette", "wada-1", "--on-accent", "purple").returncode, 0)


class TestActionStyle(unittest.TestCase):
    def test_action_tokens_exist_in_every_style(self):
        for style in ("solid", "tinted", "outline"):
            t = fixed("wada-229", action_style=style)
            for mode in ("light", "dark"):
                for tok in ("action", "action-hover", "on-action", "action-border"):
                    self.assertIn(tok, t["roles"][mode], (style, tok))
            self.assertTrue(t["contrast"]["gate_pass"], style)
        solid = fixed("wada-229")
        for tok, src in (("action", "accent"), ("action-hover", "accent-hover"), ("on-action", "on-accent"), ("action-border", "accent")):
            self.assertEqual(solid["roles"]["light"][tok]["hex"], solid["roles"]["light"][src]["hex"])
            self.assertEqual(solid["roles"]["light"][tok]["alias_of"], src)

    def test_tinted_style(self):
        for pid in ("wada-229", "paint-the-great-wave-off-kanagawa", "kasane-fuji", "ed-kurenai-kon"):
            t = fixed(pid, action_style="tinted")
            for mode in ("light", "dark"):
                r = t["roles"][mode]
                self.assertEqual(r["action"]["hex"], r["accent-subtle"]["hex"], (pid, mode))
                self.assertEqual(r["on-accent"]["hex"], r["text"]["hex"])
                self.assertEqual(r["on-action"]["hex"], r["text"]["hex"])
                self.assertEqual(r["action-border"]["hex"], r["accent"]["hex"])
                self.assertLessEqual(cl.hex_to_oklch(r["action-hover"]["hex"])[1], 0.04, (pid, mode))
                self.assertGreaterEqual(cl.wcag_contrast(r["action-border"]["hex"], r["bg"]["hex"]), 3.0)
                self.assertGreaterEqual(cl.wcag_contrast(r["on-action"]["hex"], r["action-hover"]["hex"]), 4.5)
            pairs = {(p["fg"], p["bg"]) for p in t["contrast"]["pairs"] if p["gate"]}
            self.assertIn(("action-border", "bg"), pairs)
            self.assertIn(("on-action", "action"), pairs)

    def test_outline_style_and_css(self):
        t = fixed("wada-229", action_style="outline")
        self.assertTrue(t["roles"]["light"]["action"]["transparent"])
        self.assertEqual(t["roles"]["light"]["on-action"]["hex"], t["roles"]["light"]["accent-text"]["hex"])
        with temp_project() as tmp:
            for style, want in (("outline", "--color-action: transparent;"), ("solid", "--color-action: var(--color-accent);"),
                                ("tinted", "--color-action: var(--color-accent-subtle);")):
                p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--action-style", style)
                self.assertEqual(p.returncode, 0, p.stderr_text)
                css = (Path(tmp) / "design" / "tokens.css").read_text(encoding="utf-8")
                self.assertIn(want, css, style)
                self.assertIn("--color-action-border:", css)

    def test_design_md_wording_follows_the_action_style(self):
        with temp_project() as tmp:
            for style in ("solid", "tinted", "outline"):
                run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--action-style", style)
                text = (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")
                self.assertIn("The Action Style Rule", text)
                if style == "solid":
                    self.assertIn("the one solid action colour", text)
                else:
                    self.assertNotIn("the one solid action colour", text)
                    self.assertIn("no saturated colour sits behind text", text)
                if style == "tinted":
                    self.assertIn("Action Tint", text)
                if style == "outline":
                    self.assertIn("Action Outline", text)


class TestPinnedAndVoices(unittest.TestCase):
    def test_pinned_ki_stays_exact_in_the_light_accent_role(self):
        t = fixed("kasane-kurenai-momiji", strategy="drenched", mode="persuade")
        self.assertEqual(t["roles"]["light"]["accent"]["hex"], "#f3c13a")
        self.assertFalse([a for a in t["adjustments"] if a["before_hex"] == "#f3c13a" and a["mode"] == "light" and a["role"] == "accent"])
        ramp = t["ramps"]["accent"]
        self.assertEqual(ramp["light"][ramp["pinned"]["light"]], "#f3c13a")

    def test_fix_never_alters_a_pinned_ramp_value(self):
        for pid, strat in (("kasane-kurenai-momiji", "drenched"), ("wada-100", "drenched"), ("paint-the-scream", "full-palette"), ("wada-247", "drenched")):
            t = bt.build_tokens(palette=pid, strategy=strat, mode="persuade")
            seeds = {(n, m): r[m][r["pinned"][m]] for n, r in t["ramps"].items() if "pinned" in r for m in ("light", "dark") if r["pinned"][m]}
            vd.validate_tokens(t, do_fix=True)
            for (n, m), hx in seeds.items():
                self.assertEqual(t["ramps"][n][m][t["ramps"][n]["pinned"][m]], hx, (pid, n, m))
            self.assertTrue(t["contrast"]["gate_pass"], pid)

    def test_voice_is_the_exact_region_colour_and_mark_passes_3_to_1(self):
        t = fixed("wada-122", strategy="full-palette", mode="persuade")
        creams = [k for k, v in t["roles"]["light"].items() if v["hex"] == "#fdbf68"]
        vname = next(k for k in creams if k.startswith("voice-") and not k.endswith("-mark"))
        self.assertEqual(t["assignment"]["voices"][int(vname.split("-")[1]) - 1], "cream-yellow")
        for mode in ("light", "dark"):
            mark = t["roles"][mode][f"{vname}-mark"]["hex"]
            for bg in ("bg", "surface"):
                self.assertGreaterEqual(cl.wcag_contrast(mark, t["roles"][mode][bg]["hex"]), 3.0, (mode, bg))
        gated = {(p["fg"], p["bg"]) for p in t["contrast"]["pairs"] if p["gate"]}
        self.assertNotIn((vname, "bg"), gated)  # the region fill is not gated against the page
        self.assertIn((f"{vname}-mark", "bg"), gated)
        self.assertTrue(t["contrast"]["gate_pass"])
        with temp_project() as tmp:
            run_script("handoff.py", "--palette", "wada-122", "--strategy", "full-palette", "--mode", "persuade", "--project-dir", tmp)
            text = (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn(f'{vname}: "#FDBF68"', text)

    def test_text_on_a_region_fill_is_gated_by_the_measured_label(self):
        t = fixed("wada-122", strategy="full-palette", mode="persuade")
        for p in t["contrast"]["pairs"]:
            if p["fg"].startswith("on-voice") and p["wcag"] >= 4.5:
                self.assertEqual(p["size"], "label")
        # a mid-lightness region colour that no label can carry is advisory, never a gate failure
        mid = bt.build_tokens(hexes="Mid=#8f8f6a,Ink=#222222,Brick=#b5392e,Paper=#f4eee0", strategy="full-palette", mode="persuade")
        vd.validate_tokens(mid, do_fix=True)
        self.assertTrue(mid["contrast"]["gate_pass"])


class TestRuleRendering(unittest.TestCase):
    def test_proportion_rule_renders_cleanly_for_every_strategy(self):
        for strat in ("restrained", "committed", "full-palette", "drenched"):
            t = fixed("paint-the-great-wave-off-kanagawa", strategy=strat, mode="persuade")
            rule = next(r for r in ho.named_rules(t) if "The Proportion Rule" in r)
            self.assertNotRegex(rule, r"%\s+\d", strat)  # no "5-15% 20-45%" run-ons
            self.assertNotIn(" and tertiary", rule)
            if strat == "full-palette":
                self.assertIn("secondary 15-30%, tertiary 5-15%", rule)
            self.assertRegex(rule, r"accent \d+-\d+%")


class TestTextMinAndPointer(unittest.TestCase):
    def test_text_min_raises_the_body_and_label_gate(self):
        t = fixed("wada-229", text_min=7.0)
        self.assertEqual(t["policy"]["text_min"], 7.0)
        self.assertAlmostEqual(t["policy"]["large_text_min"], 4.67, places=2)
        self.assertTrue(t["contrast"]["gate_pass"])
        seen = 0
        for p in t["contrast"]["pairs"]:
            if p["size"] in ("body", "label") and p["gate"]:
                self.assertEqual(p["wcag_min"], 7.0)
                self.assertGreaterEqual(p["wcag"], 7.0, (p["mode"], p["fg"], p["bg"]))
                seen += 1
        self.assertGreater(seen, 30)
        default = fixed("wada-229")
        self.assertEqual(default["policy"]["text_min"], 4.5)
        self.assertEqual(default["policy"]["large_text_min"], 3.0)
        with self.assertRaises(SystemExit):
            bt.build_tokens(palette="wada-1", text_min=1.0)

    def test_text_min_is_recorded_and_stated(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--text-min", "7")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            pj = json.loads((Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["policy"]["text_min"], 7.0)
            self.assertIn("Body and label text 7:1", (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8"))
        self.assertIn("--text-min", run_script("build_tokens.py", "--help").stdout_text)

    def test_claude_md_is_not_asked_unless_the_flag_is_given(self):
        with temp_project() as tmp:
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)

            def state():
                return json.loads((Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8"))["handoff"]["claude_md"]

            self.assertEqual(state(), "not_asked")
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--claude-md", "declined")
            self.assertEqual(state(), "declined")
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            self.assertEqual(state(), "declined")  # an earlier answer is kept


if __name__ == "__main__":
    unittest.main()

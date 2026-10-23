"""Orchestrator amendments v2 (notes/2-shared-constants.md section 7)."""
import unittest

from common import run_script  # noqa: F401
import colorlib as cl
import build_tokens as bt
import validate as vd


class TestAmendments(unittest.TestCase):
    def test_border_strong_is_neutral_500_and_gated(self):
        t = bt.build_tokens(palette="wada-1")
        self.assertEqual(t["roles"]["light"]["border-strong"]["ref"], "neutral:500")
        self.assertEqual(t["roles"]["dark"]["border-strong"]["ref"], "neutral:500")
        gated = {(p["fg"], p["gate"]) for p in vd.measure_all(t)}
        self.assertIn(("border-strong", True), gated)
        self.assertIn(("border", False), gated)
        self.assertIn(("border-subtle", False), gated)

    def test_dark_accent_text_and_muted(self):
        t = bt.build_tokens(palette="wada-1", pin="none")
        self.assertEqual(t["roles"]["dark"]["accent-text"]["ref"], "accent:200")
        self.assertEqual(t["roles"]["dark"]["text-muted"]["ref"], "neutral:200")

    def test_hover_moves_toward_more_contrast_with_the_label(self):
        for pid in ("wada-1", "wada-229", "kasane-fuji", "paint-the-kiss", "ed-kurenai-kon"):
            t = bt.build_tokens(palette=pid, pin="none")
            for mode in ("light", "dark"):
                roles = t["roles"][mode]
                fill_idx = bt.STEPS.index(roles["accent"]["ref"].split(":")[1])
                hov_idx = bt.STEPS.index(roles["accent-hover"]["ref"].split(":")[1])
                label_light = roles["on-accent"]["hex"] == "#ffffff"
                if 0 < fill_idx < 10:
                    self.assertEqual(hov_idx - fill_idx, 1 if label_light else -1, (pid, mode))
                self.assertGreaterEqual(cl.wcag_contrast(roles["on-accent"]["hex"], roles["accent-hover"]["hex"]),
                                        cl.wcag_contrast(roles["on-accent"]["hex"], roles["accent"]["hex"]) - 1e-9)

    def test_dark_label_gives_a_lighter_hover(self):
        # a pale, pinned accent in dark mode takes a dark label; hover must then be the lighter neighbour
        t = bt.build_tokens(hexes="#f3e58a,#222222", pin="accent")
        d = t["roles"]["dark"]
        if d["on-accent"]["hex"] != "#ffffff":
            self.assertLess(bt.STEPS.index(d["accent-hover"]["ref"].split(":")[1]), bt.STEPS.index(d["accent"]["ref"].split(":")[1]))

    def test_pin_role_window_one_step(self):
        t = bt.build_tokens(hexes="#9a2a2a,#f4eee0", pin="accent")  # seed pins at 700 (light)
        light = t["roles"]["light"]
        self.assertEqual(light["accent-text"]["hex"], "#9a2a2a")  # default 700: the real plate colour
        self.assertEqual(light["accent"]["ref"], "accent:700")  # 600 default is one step away and the seed passes
        self.assertEqual(light["focus"]["ref"], "accent:500")  # two steps away: default kept
        self.assertTrue(any("was not used for" in n and "focus" in n for n in t["notes"]))
        t = bt.build_tokens(palette="wada-229", pin="accent")  # pale seed: not near any default
        self.assertEqual(t["roles"]["light"]["accent"]["ref"], "accent:600")
        self.assertTrue(any("not used" in n for n in t["notes"]))

    def test_status_windows_and_seeds(self):
        self.assertEqual(bt.STATUS_WINDOWS, {"success": (135.0, 165.0), "warning": (65.0, 95.0), "danger": (15.0, 40.0), "info": (230.0, 270.0)})
        self.assertEqual(bt.STATUS_DEFAULTS["danger"], (0.55, 0.19, 27.0))
        self.assertEqual(bt.STATUS_DEFAULTS["warning"], (0.72, 0.15, 72.0))
        self.assertEqual(bt.STATUS_DEFAULTS["success"], (0.55, 0.14, 150.0))
        self.assertEqual(bt.STATUS_DEFAULTS["info"], (0.55, 0.13, 250.0))
        t = bt.build_tokens(hexes="Leaf=#3f8f4a,Plum=#6b2d5c,Paper=#f4eee0")
        st = t["assignment"]["status"]
        self.assertEqual(st["danger"]["source"], "default")
        self.assertEqual(st["danger"]["seed"], cl.oklch_to_hex(0.55, 0.19, 27.0))

    def test_status_within_15_degrees_of_accent_is_reseeded(self):
        accent = cl.oklch_to_hex(0.55, 0.19, 30.0)  # hue 30, inside 15 degrees of the danger default (27)
        t = bt.build_tokens(hexes=f"Brick={accent},Paper=#f4eee0")
        d = t["assignment"]["status"]["danger"]
        self.assertEqual(d["source"], "default-reseeded")
        self.assertTrue(d["non_colour_cue_needed"])
        h = cl.hex_to_oklch(d["seed"])[2]
        acc_h = cl.hex_to_oklch(t["palette"]["members"][0]["hex"])[2]
        self.assertGreaterEqual(cl.hue_diff(h, acc_h), 14)
        self.assertTrue(any("status danger" in n for n in t["notes"]))

    def test_danger_is_never_green_dominant(self):
        for pid in ("wada-1", "wada-100", "paint-the-kiss", "kasane-fuji"):
            r, g, b = cl.parse_hex(bt.build_tokens(palette=pid)["assignment"]["status"]["danger"]["seed"])
            self.assertFalse(g > 1.1 * r and g > 1.1 * b, pid)

    def test_vanishing_uses_adjacency_list_and_siblings_need_dl(self):
        t = bt.build_tokens(palette="wada-229")
        for mode in ("light", "dark"):
            t["roles"][mode]["voice-1"]["hex"] = cl.oklch_to_hex(0.55, 0.10, 62)
            t["roles"][mode]["success"]["hex"] = cl.oklch_to_hex(0.55, 0.10, 70)  # same L and hue as voice-1, not declared adjacent
        flags = vd.validate_tokens(t, adjacency=[("voice-1", "success")])["flags"]
        self.assertTrue(any(f["type"] == "vanishing" and {f["a"], f["b"]} == {"voice-1", "success"} for f in flags))
        flags = vd.validate_tokens(t, adjacency=[("bg", "bg-subtle")])["flags"]
        self.assertFalse(any(f["type"] == "vanishing" and "success" in (f["a"], f["b"]) for f in flags))
        t["roles"]["light"]["accent-hover"]["hex"] = t["roles"]["light"]["accent"]["hex"]
        flags = vd.validate_tokens(t)["flags"]
        sib = [f for f in flags if f["type"] == "state_sibling" and f["mode"] == "light"]
        self.assertTrue(sib)
        self.assertIn("non-colour cue", sib[0]["advice"])
        proc = run_script("validate.py", "--help")
        self.assertIn("--adjacency", proc.stdout_text)

    def test_pair_groups_column_is_empty_by_design(self):
        rows = cl.load_palette_rows()
        self.assertIn("pair_groups", rows[0])
        self.assertTrue(all(r["pair_groups"] == "" for r in rows))


if __name__ == "__main__":
    unittest.main()


class TestGateDecisions(unittest.TestCase):
    def test_default_pin_is_all_and_voice_solids_are_the_plate_colour(self):
        t = bt.build_tokens(palette="wada-247", strategy="drenched", mode="experience")
        self.assertEqual(t["inputs"]["pin"], "all")
        vd.validate_tokens(t, do_fix=True)
        lyons = next(m for m in t["palette"]["members"] if m["name"] == "Deep Lyons Blue")
        self.assertEqual(lyons["hex"], "#1c4286")
        light = {k: v["hex"] for k, v in t["roles"]["light"].items()}
        self.assertIn("#1c4286", light.values())  # not only a generated #3169CE
        # every voice solid equals its seed wherever the seed clears the 3:1 gate
        for i in range(1, len(t["assignment"]["voices"]) + 1):
            ramp = t["ramps"][f"voice-{i}"]
            step = ramp["pinned"]["light"]
            self.assertIsNotNone(step)
            self.assertEqual(ramp["light"][step], ramp["seed"])
        drench = t["ramps"]["drench"]
        self.assertEqual(t["roles"]["light"]["bg"]["hex"], drench["seed"])
        css_proc = run_script("handoff.py", "--palette", "wada-247", "--strategy", "drenched", "--mode", "experience", "--dry-run")
        self.assertEqual(css_proc.returncode, 0)

    def test_plain_voice_solid_is_the_exact_colour(self):
        t = bt.build_tokens(hexes="Brick=#b5392e,Lyons=#1c4286,Olive=#6b7140,Paper=#f4eee0")
        for i, key in enumerate(t["assignment"]["voices"], 1):
            seed = next(m["hex"] for m in t["palette"]["members"] if m["key"] == key)
            ramp = t["ramps"][f"voice-{i}"]
            if ramp["pinned"]["light"]:
                solid = t["roles"]["light"][f"voice-{i}"]["hex"]
                ok = all(cl.wcag_contrast(seed, t["roles"]["light"][b]["hex"]) >= 3.0 for b in ("bg", "surface"))
                if ok:
                    self.assertEqual(solid, seed, key)
            self.assertNotEqual(t["roles"]["light"][f"voice-{i}-text"]["ref"], f"voice-{i}:{ramp['pinned']['light']}")

    def test_palette_colours_are_exported_as_primitives(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory(prefix="acp pal ") as tmp:
            p = run_script("handoff.py", "--palette", "wada-247", "--project-dir", tmp)
            self.assertEqual(p.returncode, 0, p.stderr_text)
            css = (Path(tmp) / "design" / "tokens.css").read_text(encoding="utf-8")
            self.assertIn("--palette-deep-lyons-blue: #1c4286;", css)

    def test_status_step_offsets(self):
        t = bt.build_tokens(palette="wada-229", pin="none")
        want = {"light": {"warning": "400", "success": "700", "danger": "600", "info": "500"},
                "dark": {"warning": "300", "success": "600", "danger": "400", "info": "500"}}
        for mode in ("light", "dark"):
            for name, step in want[mode].items():
                self.assertEqual(t["roles"][mode][name]["ref"], f"{name}:{step}", (mode, name))
        self.assertIn("measured", t["roles"]["light"]["on-warning"])
        # statuses now differ in lightness as well as hue
        Ls = [cl.hex_to_oklch(t["roles"]["light"][n]["hex"])[0] for n in ("warning", "success", "danger", "info")]
        self.assertGreater(max(Ls) - min(Ls), 0.15)

    def test_drift_count_is_six_everywhere(self):
        import re
        from common import SKILL

        for path in list((SKILL / "scripts").glob("*.py")) + list((SKILL / "data").glob("*")) + list((SKILL / "scripts" / "tests").glob("*.py")):
            if path.name == "test_amendments.py":
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?i)\b(7|seven) (of the 25|flagged|works flagged)|prose elsewhere says 7", path.name)


class TestReviewFixes(unittest.TestCase):
    def test_new_design_md_starts_with_frontmatter(self):
        from common import temp_project
        from pathlib import Path

        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            self.assertEqual(p.returncode, 0, p.stderr_text)
            raw = (Path(tmp) / "DESIGN.md").read_bytes().decode("utf-8")
            self.assertTrue(raw.startswith("---\n"))
            lines = raw.split("\n")
            end = lines.index("---", 1)
            self.assertIn("colors:", lines[1:end])
            self.assertTrue(lines[end + 1].startswith("<!-- acp:seed palette-only"))
            self.assertNotIn("acp:seed", "\n".join(lines[:end + 1]))

    def test_provenance_override_for_hex_input(self):
        t = bt.build_tokens(hexes="#9a2a2a,#f4eee0", provenance_label="Original composition by this skill (not a plate)")
        self.assertEqual(t["palette"]["label"], "Original composition by this skill (not a plate)")
        self.assertEqual(t["palette"]["credit"], "Original composition by this skill (not a plate)")
        self.assertEqual(bt.build_tokens(hexes="#9a2a2a,#f4eee0")["palette"]["label"], "Original composition (colours supplied by the user)")
        with self.assertRaises(SystemExit):
            bt.build_tokens(palette="wada-1", provenance_label="x")
        p = run_script("build_tokens.py", "--hex", "#9a2a2a,#f4eee0", "--provenance", "Refined from Impeccable's palette")
        self.assertIn("Refined from Impeccable's palette", p.stdout_text)
        from common import temp_project
        from pathlib import Path

        with temp_project() as tmp:
            h = run_script("handoff.py", "--hex", "#9a2a2a,#f4eee0", "--provenance", "Refined from Impeccable's palette", "--project-dir", tmp)
            self.assertEqual(h.returncode, 0, h.stderr_text)
            self.assertIn("Provenance: Refined from Impeccable's palette.", (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8"))

    def test_report_never_contradicts_itself_at_the_threshold(self):
        import re

        t = bt.build_tokens(palette="wada-229")
        # a value just under the divider target that rounds to it, and a ratio just under 4.5 that rounds to 4.5
        pair = {"fg": "text-muted", "bg": "bg", "size": "divider", "kind": "text", "label": "x"}
        orig = cl.apca_lc
        try:
            cl.apca_lc = lambda a, b: 14.97
            m = vd.measure_pair(t, "light", pair)
        finally:
            cl.apca_lc = orig
        self.assertFalse(m["apca_pass"])
        self.assertLess(abs(m["apca"]), 15)
        self.assertEqual(vd.fmt_lc(abs(m["apca"])), "14.97")
        orig = cl.wcag_contrast
        try:
            cl.wcag_contrast = lambda a, b: 4.497
            m = vd.measure_pair(t, "light", {"fg": "text", "bg": "bg", "size": "body", "kind": "text", "label": "x"})
        finally:
            cl.wcag_contrast = orig
        self.assertFalse(m["wcag_pass"])
        self.assertLess(m["wcag"], 4.5)
        # no printed "Lc N < N" contradiction anywhere in real reports
        for pid in ("wada-229", "kasane-fuji", "paint-the-kiss"):
            tt = bt.build_tokens(palette=pid)
            vd.validate_tokens(tt, do_fix=True)
            for line in vd.text_report(tt, True).split("\n"):
                mm = re.search(r"Lc ([\d.]+)(?:-([\d.]+))? < ([\d.]+)", line)
                if mm:
                    self.assertLess(float(mm.group(2) or mm.group(1)), float(mm.group(3)), line)

"""build_tokens: ramps, role map, strategies, pins, status colours, proportions."""
import json
import unittest

from common import run_script  # noqa: F401
import colorlib as cl
import build_tokens as bt
import validate as vd

SAMPLES = ["wada-229", "wada-1", "wada-100", "paint-the-great-wave-off-kanagawa", "paint-the-night-watch",
           "kasane-fuji", "kasane-ume-gasane", "ed-kurenai-kon"]


def L_of(hx):
    return cl.hex_to_oklch(hx)[0]


class TestConstants(unittest.TestCase):
    def test_tables_match_shared_constants(self):
        self.assertEqual(list(bt.LIGHT_L.values()), [0.975, 0.935, 0.885, 0.810, 0.720, 0.630, 0.540, 0.460, 0.380, 0.300, 0.240])
        self.assertEqual(list(bt.DARK_L.values()), [0.960, 0.900, 0.810, 0.710, 0.610, 0.510, 0.420, 0.340, 0.270, 0.210, 0.160])
        self.assertEqual(list(bt.PROFILE.values()), [0.15, 0.25, 0.40, 0.60, 0.80, 0.95, 1.00, 0.92, 0.80, 0.65, 0.50])
        self.assertEqual(list(bt.NEUTRAL_N.values()), [0.006, 0.010, 0.014, 0.018, 0.020, 0.020, 0.020, 0.018, 0.016, 0.014, 0.012])
        steps = list(bt.LIGHT_L.values())
        for a, b in zip(steps, steps[1:]):
            self.assertGreaterEqual(a - b, 0.04 - 1e-9)
        dark = list(bt.DARK_L.values())
        for a, b in zip(dark, dark[1:]):
            self.assertGreaterEqual(a - b, 0.03)
        for a, b in zip(dark[-4:], dark[-3:]):
            self.assertGreaterEqual(a - b, 0.05 - 1e-9)  # wider separation at the dark end
        self.assertTrue(max(steps) < 1 and min(dark) > 0)

    def test_dark_ramp_is_not_the_light_ramp_reversed(self):
        light, dark = list(bt.LIGHT_L.values()), list(bt.DARK_L.values())
        self.assertNotEqual(dark, light[::-1])
        for s in bt.STEPS:
            self.assertGreater(abs(bt.LIGHT_L[s] - bt.DARK_L[s]), 0.01, s)
        # a mechanical inversion would put light 950 where dark 50 sits; ours differ by far more than rounding
        self.assertGreater(abs(bt.LIGHT_L["950"] - bt.DARK_L["50"]), 0.5)


class TestRamps(unittest.TestCase):
    def test_unpinned_ramp_L_matches_table_and_steps_are_apart(self):
        for pid in SAMPLES:
            t = bt.build_tokens(palette=pid, pin="none")
            for name, ramp in t["ramps"].items():
                if "light" not in ramp:
                    continue
                for mode, table in (("light", bt.LIGHT_L), ("dark", bt.DARK_L)):
                    Ls = []
                    for s in bt.STEPS:
                        L = L_of(ramp[mode][s])
                        Ls.append(L)
                        self.assertAlmostEqual(L, table[s], delta=0.006, msg=f"{pid} {name} {mode} {s}")
                    for a, b in zip(Ls, Ls[1:]):
                        self.assertGreaterEqual(a - b, 0.03, f"{pid} {name} {mode}")

    def test_chroma_rules(self):
        t = bt.build_tokens(palette="wada-229", pin="none")
        acc = t["ramps"]["accent"]
        seed_L, seed_C, h = cl.hex_to_oklch(acc["seed"])
        share = seed_C / cl.max_chroma(seed_L, h)
        self.assertAlmostEqual(acc["share"], min(1, share), places=3)
        for s in bt.STEPS:
            L, C, _ = cl.hex_to_oklch(acc["light"][s])
            want = share * bt.PROFILE[s] * cl.max_chroma(bt.LIGHT_L[s], h)
            self.assertAlmostEqual(C, want, delta=0.006, msg=s)
            Ld, Cd, _ = cl.hex_to_oklch(acc["dark"][s])
            wantd = share * bt.PROFILE[s] * cl.max_chroma(bt.DARK_L[s], h) * 0.85
            if s in ("800", "900", "950"):
                wantd = min(wantd, 0.045)
                self.assertLessEqual(Cd, 0.045 + 0.004)
            self.assertAlmostEqual(Cd, wantd, delta=0.006, msg=f"dark {s}")

    def test_neutral_ramp_is_tinted_and_capped(self):
        t = bt.build_tokens(palette="wada-229")
        neutral = t["ramps"]["neutral"]
        tint_h = cl.hex_to_oklch(neutral["seed"])[2]
        for mode in ("light", "dark"):
            for s in bt.STEPS:
                L, C, h = cl.hex_to_oklch(neutral[mode][s])
                self.assertLessEqual(C, 0.03 + 1e-3)
                self.assertAlmostEqual(C, bt.NEUTRAL_N[s], delta=0.004)
                if C > 0.008:
                    self.assertLess(cl.hue_diff(h, tint_h), 12, f"{mode} {s}")
        t2 = bt.build_tokens(palette="wada-229", tint=0.0)
        for s in bt.STEPS:
            self.assertLess(cl.hex_to_oklch(t2["ramps"]["neutral"]["light"][s])[1], 0.003)

    def test_pin_keeps_seed_exactly_at_nearest_step(self):
        t = bt.build_tokens(hexes="#9a2a2a,#f4eee0", pin="accent")
        acc = t["ramps"]["accent"]
        self.assertEqual(acc["seed"], "#9a2a2a")
        step = acc["pinned"]["light"]
        self.assertEqual(step, "700")
        self.assertEqual(acc["light"][step], "#9a2a2a")
        near = min(bt.STEPS, key=lambda s: abs(bt.LIGHT_L[s] - cl.hex_to_oklch("#9a2a2a")[0]))
        self.assertEqual(step, near)
        Ls = [L_of(acc["light"][s]) for s in bt.STEPS]
        for a, b in zip(Ls, Ls[1:]):
            self.assertGreaterEqual(a - b, 0.03)
        none = bt.build_tokens(hexes="#9a2a2a,#f4eee0", pin="none")
        self.assertIsNone(none["ramps"]["accent"]["pinned"]["light"])
        self.assertNotIn("#9a2a2a", none["ramps"]["accent"]["light"].values())

    def test_pinned_seed_is_never_silently_changed_by_fix(self):
        t = bt.build_tokens(palette="wada-100", strategy="drenched", mode="experience")
        vd.validate_tokens(t, do_fix=True)
        for ramp in t["ramps"].values():
            for mode in ("light", "dark"):
                step = ramp.get("pinned", {}).get(mode) if "pinned" in ramp else None
                if step:
                    self.assertEqual(ramp[mode][step], ramp["seed"])
        for mode in ("light", "dark"):
            for tok, role in t["roles"][mode].items():
                if role.get("adjusted"):
                    ref = role["adjusted"]["from_ref"]
                    if ":" in ref and not ref.startswith("literal"):
                        name, step = ref.split(":")
                        self.assertNotEqual(t["ramps"][name].get("pinned", {}).get(mode), step, f"{tok} was L-adjusted although pinned")


class TestRoles(unittest.TestCase):
    def test_role_map_refs(self):
        t = bt.build_tokens(palette="wada-1", pin="none")
        light, dark = t["roles"]["light"], t["roles"]["dark"]
        want = {"bg": ("neutral:50", "neutral:950"), "bg-subtle": ("neutral:100", "neutral:900"), "surface": ("neutral:50", "neutral:900"),
                "surface-hover": ("neutral:200", "neutral:800"), "border-subtle": ("neutral:200", "neutral:800"),
                "border": ("neutral:300", "neutral:700"), "border-strong": ("neutral:500", "neutral:500"),
                "text": ("neutral:900", "neutral:50"), "text-muted": ("neutral:700", "neutral:200"),
                "accent": ("accent:600", "accent:500"), "accent-hover": ("accent:700", "accent:600"),
                "accent-text": ("accent:700", "accent:200"), "accent-subtle": ("accent:100", "accent:900"), "focus": ("accent:500", "accent:400")}
        for tok, (lr, dr) in want.items():
            self.assertEqual(light[tok]["ref"], lr, tok)
            self.assertEqual(dark[tok]["ref"], dr, tok)
        for mode in (light, dark):
            self.assertIn(mode["on-accent"]["hex"], ("#ffffff", t["ramps"]["neutral"]["light"]["950"], t["ramps"]["neutral"]["dark"]["950"]))
            self.assertIn("measured", mode["on-accent"])
        self.assertEqual(list(light), list(dark))

    def test_on_colour_is_chosen_by_measurement(self):
        for pid in SAMPLES:
            t = bt.build_tokens(palette=pid)
            for mode in ("light", "dark"):
                roles = t["roles"][mode]
                for tok in [k for k in roles if k.startswith("on-")]:
                    fill = roles[tok[3:]]["hex"]
                    best = max(cl.wcag_contrast("#ffffff", fill), cl.wcag_contrast(t["ramps"]["neutral"][mode]["950"], fill))
                    self.assertAlmostEqual(cl.wcag_contrast(roles[tok]["hex"], fill), best, places=2, msg=f"{pid} {mode} {tok}")

    def test_status_colours_palette_or_default_and_reported(self):
        t = bt.build_tokens(hexes="Leaf=#3f8f4a,Brick=#b5392e,Paper=#f4eee0,Ink=#1b2a4e")
        st = t["assignment"]["status"]
        self.assertEqual(st["success"]["source"], "palette")
        self.assertEqual(st["success"]["member"], "leaf")
        self.assertEqual(st["warning"]["source"], "default")
        self.assertEqual(set(st), {"success", "warning", "danger", "info"})
        for name in st:
            self.assertIn(name, t["roles"]["light"])
            self.assertIn(f"{name}-subtle", t["roles"]["light"])
            self.assertIn(f"{name}-text", t["roles"]["dark"])

    def test_voices_cover_remaining_palette_colours(self):
        t = bt.build_tokens(palette="paint-the-great-wave-off-kanagawa", strategy="full-palette", mode="persuade")
        voices = t["assignment"]["voices"]
        self.assertTrue(voices)
        for i in range(1, len(voices) + 1):
            for suffix in ("", "-subtle", "-text"):
                self.assertIn(f"voice-{i}{suffix}", t["roles"]["light"])
        self.assertNotIn(t["assignment"]["accent"], voices)

    def test_hex_list_input_and_errors(self):
        t = bt.build_tokens(hexes="#abc, Navy=#1b2a4e, #AABBCC")
        self.assertEqual([m["hex"] for m in t["palette"]["members"]], ["#aabbcc", "#1b2a4e"])
        with self.assertRaises(SystemExit):
            bt.build_tokens(hexes="#zzz")
        with self.assertRaises(SystemExit):
            bt.build_tokens(palette="wada-999")
        with self.assertRaises(SystemExit):
            bt.build_tokens(palette="wada-1", hexes="#fff")


class TestStrategies(unittest.TestCase):
    def test_proportion_targets(self):
        want = {"Restrained": ([85, 95], [0, 5], [2, 8]), "Committed": ([35, 65], [30, 60], [0, 8]),
                "Full palette": ([45, 65], [20, 45], [0, 8]), "Drenched": ([5, 30], [60, 90], [0, 8])}
        for name, (n, p, a) in want.items():
            t = bt.build_tokens(palette="wada-1", strategy=name, mode="persuade")
            pr = t["proportions"]
            self.assertEqual(pr["strategy"], name)
            self.assertEqual(pr["neutrals_pct"], n)
            self.assertEqual(pr["palette_pct"], p)
            self.assertLessEqual(pr["accent_pct"][1], a[1])
            self.assertIn("own convention", pr["label"])
        full = bt.build_tokens(palette="wada-1", strategy="full-palette")["proportions"]
        self.assertEqual((full["secondary_pct"], full["tertiary_pct"]), ([15, 30], [5, 15]))

    def test_chroma_modifier_and_kasane_and_painting(self):
        vivid = bt.build_tokens(hexes="#e8221a,#f4eee0")  # chroma well above 0.15
        self.assertEqual(vivid["proportions"]["accent_pct"][1], 5)
        kas = bt.build_tokens(palette="kasane-fuji")
        self.assertEqual(kas["proportions"]["accent_pct"][0], 5)
        paint = bt.build_tokens(palette="paint-the-night-watch")["proportions"]
        self.assertAlmostEqual(sum(paint["ground_shares_pct"].values()), 90.0, delta=0.5)
        self.assertEqual(paint["accents_total_max_pct"], 8)

    def test_every_strategy_builds_validates_and_passes_gate_after_fix(self):
        for pid in SAMPLES:
            for strat in ("restrained", "committed", "full-palette", "drenched"):
                t = bt.build_tokens(palette=pid, strategy=strat, mode="persuade")
                vd.validate_tokens(t, do_fix=True)
                self.assertTrue(t["contrast"]["gate_pass"], f"{pid} {strat}: {t['contrast']['summary']}")

    def test_bold_strategy_in_operate_mode_warns(self):
        t = bt.build_tokens(palette="wada-1", strategy="drenched", mode="operate")
        self.assertTrue(t["warnings"])
        self.assertFalse(bt.build_tokens(palette="wada-1", strategy="restrained", mode="operate")["warnings"])

    def test_override_roles(self):
        t = bt.build_tokens(palette="wada-229", roles={"accent": "Deep Slate Olive"})
        self.assertEqual(t["assignment"]["accent"], "deep-slate-olive")
        t = bt.build_tokens(palette="wada-229", roles={"neutral": "3"})
        self.assertEqual(t["assignment"]["neutral_from"], "neutral-gray")

    def test_cli_writes_json_and_is_deterministic(self):
        a = run_script("build_tokens.py", "--palette", "kasane-kobai-no-nioi", "--strategy", "committed", "--mode", "persuade")
        b = run_script("build_tokens.py", "--palette", "kasane-kobai-no-nioi", "--strategy", "committed", "--mode", "persuade")
        self.assertEqual(a.returncode, 0, a.stderr_text)
        self.assertEqual(a.stdout, b.stdout)
        data = json.loads(a.stdout_text)
        self.assertEqual(data["schema"], "acp-tokens/1")
        self.assertIn("Kōbai", data["palette"]["label"])
        bad = run_script("build_tokens.py", "--palette", "wada-999")
        self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()

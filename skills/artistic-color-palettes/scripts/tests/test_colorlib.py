"""Colour maths: the shared test vectors and invariants."""
import math
import unittest

from common import run_script  # noqa: F401
import colorlib as cl


class TestVectors(unittest.TestCase):
    def test_apca(self):
        self.assertAlmostEqual(cl.apca_lc("#888888", "#ffffff"), 63.06, delta=0.1)
        self.assertAlmostEqual(cl.apca_lc("#ffffff", "#888888"), -68.54, delta=0.1)
        self.assertAlmostEqual(cl.apca_lc("#000000", "#ffffff"), 106.04, delta=0.1)
        self.assertAlmostEqual(cl.apca_lc("#ffffff", "#000000"), -107.88, delta=0.1)
        self.assertEqual(cl.apca_lc("#808080", "#808080"), 0.0)

    def test_wcag(self):
        self.assertAlmostEqual(cl.wcag_contrast("#777777", "#ffffff"), 4.48, delta=0.01)
        self.assertAlmostEqual(cl.wcag_contrast("#000000", "#ffffff"), 21.0, delta=0.001)
        self.assertAlmostEqual(cl.wcag_contrast("#ffffff", "#777777"), cl.wcag_contrast("#777777", "#ffffff"))

    def test_oklch_red(self):
        L, C, h = cl.hex_to_oklch("#ff0000")
        self.assertAlmostEqual(L, 0.628, delta=0.001)
        self.assertAlmostEqual(C, 0.2577, delta=0.001)
        self.assertAlmostEqual(h, 29.23, delta=0.1)

    def test_self_test_cli(self):
        proc = run_script("colorlib.py", "--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout_text)


class TestHexAndGamut(unittest.TestCase):
    def test_short_hex_and_case(self):
        self.assertEqual(cl.parse_hex("#fa0"), (255, 170, 0))
        self.assertEqual(cl.parse_hex("FFAA00"), (255, 170, 0))
        self.assertEqual(cl.normalize_hex("#ABC"), "#aabbcc")
        for bad in ("#12", "#12345", "red", "#gggggg", "", None):
            self.assertFalse(cl.is_hex(bad))
            with self.assertRaises(ValueError):
                cl.parse_hex(bad)

    def test_round_trip_all_grey_and_samples(self):
        for hx in ("#000000", "#ffffff", "#808080", "#f3a257", "#253122", "#2c638c", "#c91f37"):
            L, C, h = cl.hex_to_oklch(hx)
            self.assertEqual(cl.oklch_to_hex(L, C, h, refine=False), hx)
            self.assertEqual(cl.oklch_to_hex(L, C, h), hx)

    def test_max_chroma_is_the_gamut_edge(self):
        for L in (0.2, 0.5, 0.63, 0.8, 0.95):
            for h in (0, 29, 60, 100, 150, 200, 260, 320):
                m = cl.max_chroma(L, h)
                self.assertTrue(cl.in_gamut(L, m, h), (L, h))
                self.assertFalse(cl.in_gamut(L, m + 2e-4, h), (L, h))
        self.assertEqual(cl.max_chroma(0.0, 30), 0.0)
        self.assertEqual(cl.max_chroma(1.0, 30), 0.0)

    def test_out_of_gamut_keeps_lightness_and_hue(self):
        hx = cl.oklch_to_hex(0.6, 0.4, 145)
        L, C, h = cl.hex_to_oklch(hx)
        self.assertAlmostEqual(L, 0.6, delta=0.01)
        self.assertAlmostEqual(h, 145, delta=3)
        self.assertLess(C, 0.4)


class TestOtherMaths(unittest.TestCase):
    def test_cvd_matrices_preserve_white_and_grey(self):
        for kind, m in cl.CVD_MATRICES.items():
            for row in m:
                self.assertAlmostEqual(sum(row), 1.0, places=4, msg=kind)
            self.assertEqual(cl.simulate_cvd("#ffffff", kind), "#ffffff")
            self.assertEqual(cl.simulate_cvd("#808080", kind), "#808080")
        # a pure red and green become close under deuteranopia
        self.assertLess(cl.delta_e_ok(cl.simulate_cvd("#c42e2b", "deutan"), cl.simulate_cvd("#2f9e52", "deutan")),
                        cl.delta_e_ok("#c42e2b", "#2f9e52"))
        with self.assertRaises(ValueError):
            cl.simulate_cvd("#ffffff", "nope")

    def test_delta_e_ok(self):
        self.assertEqual(cl.delta_e_ok("#336699", "#336699"), 0.0)
        self.assertAlmostEqual(cl.delta_e_ok("#000000", "#ffffff"), 1.0, places=3)

    def test_composite_in_gamma_space(self):
        self.assertEqual(cl.composite("#000000", 0.5, "#ffffff"), "#808080")
        self.assertEqual(cl.composite("#ff0000", 1.0, "#00ff00"), "#ff0000")
        self.assertEqual(cl.composite("#ff0000", 0.0, "#00ff00"), "#00ff00")

    def test_greyscale_keeps_luminance(self):
        for hx in ("#f3a257", "#2c638c", "#c91f37"):
            g = cl.to_greyscale(hx)
            self.assertAlmostEqual(cl.relative_luminance(g), cl.relative_luminance(hx), delta=0.004)

    def test_best_text_color_picks_by_measurement(self):
        self.assertEqual(cl.best_text_color("#ffffff")[0], "#111314")
        self.assertEqual(cl.best_text_color("#000000")[0], "#ffffff")
        hx, ratio = cl.best_text_color("#777777")
        self.assertGreater(ratio, 4.4)

    def test_hue_diff(self):
        self.assertEqual(cl.hue_diff(10, 350), 20)
        self.assertEqual(cl.hue_diff(0, 180), 180)

    def test_stdout_handles_japanese(self):
        proc = run_script("search.py", "--id", "ed-kurenai-kon")
        self.assertEqual(proc.returncode, 0, proc.stderr_text)
        self.assertIn("紅と紺", proc.stdout_text)


if __name__ == "__main__":
    unittest.main()

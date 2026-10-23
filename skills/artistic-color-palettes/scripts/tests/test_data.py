"""Shipped data: counts, hex validity, provenance labels, no invented plates, painting structure."""
import csv
import json
import re
import unittest

from common import DATA, REPO, SKILL, run_script  # noqa: F401  (common also fixes sys.path)
import colorlib as cl


def rows():
    return cl.load_palette_rows(DATA / "palettes.csv")


class TestPalettesTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()

    def test_counts_per_source_type(self):
        counts = {}
        for r in self.rows:
            counts[r["source_type"]] = counts.get(r["source_type"], 0) + 1
        self.assertEqual(counts, {"wada_plate": 348, "editorial": 30, "painting": 25, "kasane": 33})
        self.assertEqual(len(self.rows), 436)

    def test_columns_and_unique_ids(self):
        self.assertEqual(list(self.rows[0].keys()), [
            "id", "source_type", "title", "title_ja", "colors", "color_names", "roles", "coverage", "hue", "moods", "era",
            "season", "count", "drift", "tone_family", "pair_groups", "label", "source_url", "licence", "hues", "mood_source"])
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for r in self.rows:
            self.assertRegex(r["id"], r"^(wada-\d+|ed-[a-z0-9-]+|paint-[a-z0-9-]+|kasane-[a-z0-9-]+)$")

    def test_every_hex_is_valid(self):
        for r in self.rows:
            hexes = r["colors"].split(";")
            self.assertTrue(hexes, r["id"])
            for h in hexes:
                self.assertTrue(cl.is_hex(h) and h.startswith("#") and len(h) == 7, f"{r['id']}: {h}")
            self.assertEqual(len(r["color_names"].split(";")), len(hexes), r["id"])
            self.assertEqual(int(r["count"]), len(set(hexes)), r["id"])

    def test_no_vol2_and_plates_1_to_348(self):
        plates = sorted(int(r["id"].split("-")[1]) for r in self.rows if r["source_type"] == "wada_plate")
        self.assertEqual(plates, list(range(1, 349)))
        for r in self.rows:
            blob = " ".join([r["title"], r["label"], r["source_url"]]).lower()
            self.assertNotRegex(blob, r"vol(ume|\.)?\s*\.?\s*(2|ii)\b", r["id"])
            if r["source_type"] == "wada_plate":
                self.assertEqual(r["era"], "showa")
                self.assertIn(int(r["count"]), (2, 3, 4))

    def test_wada_plates_by_colour_count(self):
        by = {2: 0, 3: 0, 4: 0}
        for r in self.rows:
            if r["source_type"] == "wada_plate":
                n = int(r["id"].split("-")[1])
                want = 2 if n <= 120 else 3 if n <= 240 else 4
                self.assertEqual(int(r["count"]), want, r["id"])
                by[want] += 1
        self.assertEqual(by, {2: 120, 3: 120, 4: 108})

    def test_provenance_labels_and_licences(self):
        for r in self.rows:
            t = r["source_type"]
            if t == "wada_plate":
                n = r["id"].split("-")[1]
                self.assertEqual(r["label"], f"Wada plate {n} (*A Dictionary of Color Combinations*, 1933)")
                self.assertEqual(r["licence"], "PD+MIT+CC-BY-4.0")
                self.assertTrue(r["source_url"].startswith("https://colorcombinations.org/palettes/wada-"))
            elif t == "editorial":
                self.assertEqual(r["label"], "Editorial palette by colorcombinations.org, inspired by Wada's method")
                self.assertEqual(r["licence"], "CC-BY-4.0")
            elif t == "painting":
                self.assertRegex(r["label"], r"^Sampled from .+, .+, .+ by colorcombinations\.org$")
                self.assertEqual(r["licence"], "CC-BY-4.0")
                self.assertTrue(r["source_url"].startswith("https://colorcombinations.org/paintings/"))
            else:
                self.assertRegex(r["label"], r"^Kasane no irome: .+ \(Heian court colour layering; hex values are interpretations\)$")
                self.assertEqual(r["licence"], "CC-BY-SA-4.0 (base hex) + own composition")
            self.assertIn(r["tone_family"], ("same", "different"))

    def test_painting_rows(self):
        paints = [r for r in self.rows if r["source_type"] == "painting"]
        self.assertEqual(len(paints), 25)
        for r in paints:
            roles = r["roles"].split(";")
            self.assertEqual(roles.count("ground"), 3, r["id"])
            self.assertEqual(roles.count("accent"), 3, r["id"])
            cov = r["coverage"].split(";")
            self.assertEqual(len(cov), 6)
            for c in cov:
                self.assertTrue(c == "<1" or c.isdigit(), f"{r['id']}: {c}")
            self.assertIn(r["drift"], ("true", "false"))
        self.assertEqual(sum(r["drift"] == "true" for r in paints), 6)
        great_wave = next(r for r in paints if r["id"] == "paint-the-great-wave-off-kanagawa")
        self.assertEqual(great_wave["drift"], "true")
        self.assertIn("<1", great_wave["coverage"])

    def test_kasane_rows(self):
        ks = [r for r in self.rows if r["source_type"] == "kasane"]
        self.assertEqual(len(ks), 33)
        for r in ks:
            roles = r["roles"].split(";")
            self.assertEqual(roles[0], "hitoe", r["id"])
            self.assertTrue(r["season"], r["id"])
            self.assertEqual(r["era"], "heian")
        fuji = next(r for r in ks if r["id"] == "kasane-fuji")
        self.assertEqual(fuji["title_ja"], "藤")
        self.assertEqual(fuji["colors"].split(";")[0], "#ffddca")


class TestColorsAndPaintingsJson(unittest.TestCase):
    def test_colors_csv(self):
        with open(DATA / "colors.csv", encoding="utf-8", newline="") as f:
            cs = list(csv.DictReader(f))
        self.assertEqual(len(cs), 210)
        self.assertEqual(sum(1 for c in cs if c["wada_no"]), 159)
        nos = sorted(int(c["wada_no"]) for c in cs if c["wada_no"])
        self.assertEqual(nos, list(range(1, 160)))
        for c in cs:
            self.assertTrue(cl.is_hex(c["hex"]))
            self.assertGreaterEqual(float(c["best_text_ratio"]), 4.3, c["name"])
            L, C, h = cl.hex_to_oklch(c["hex"])
            self.assertAlmostEqual(float(c["oklch_l"]), L, places=3)
        sulpher = next(c for c in cs if c["name"] == "Sulpher Yellow")
        self.assertIn("Sulphur Yellow", sulpher["aliases"].split(";"))
        self.assertEqual(sulpher["cmyk"], "4;4;28;0")
        black = next(c for c in cs if c["name"] == "Black")
        self.assertEqual(black["best_text"], "#ffffff")

    def test_paintings_json(self):
        data = json.loads((DATA / "paintings.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data), 25)
        self.assertEqual(sum(1 for d in data if d["drift"]), 6)
        for d in data:
            self.assertEqual(len(d["colors"]), 6)
            self.assertEqual([c["role"] for c in d["colors"]].count("ground"), 3)
            for c in d["colors"]:
                self.assertTrue(cl.is_hex(c["hex"]))
            self.assertTrue(d["page_url"].startswith("https://colorcombinations.org/paintings/"))
            if d["drift"]:
                self.assertIn("not the artist's original colours", d["drift_note"])
        self.assertEqual([d["slug"] for d in data if d["east_asian"]], ["the-great-wave-off-kanagawa"])

    def test_snapshot_note_has_built_counts(self):
        text = (DATA / "SNAPSHOT.md").read_text(encoding="utf-8")
        self.assertIn("| palettes.csv | 436 |", text)
        self.assertIn("wada_plate 348, editorial 30, painting 25, kasane 33", text)


class TestBuildDataReproducible(unittest.TestCase):
    @unittest.skipUnless((REPO / "data-raw" / "palettes.csv").exists(), "data-raw not present")
    def test_rebuild_matches_shipped_files(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory(prefix="acp build data ") as tmp:
            proc = run_script("build_data.py", "--raw", str(REPO / "data-raw"), "--out", tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr_text)
            for name in ("palettes.csv", "colors.csv", "paintings.json"):
                self.assertEqual((Path(tmp) / name).read_bytes(), (DATA / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()

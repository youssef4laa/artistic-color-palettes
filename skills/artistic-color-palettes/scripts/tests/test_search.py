"""search.py: relevant results, filters, and the no-fabrication behaviour."""
import json
import unittest

from common import run_script


def search(*args):
    return run_script("search.py", *args)


class TestSearch(unittest.TestCase):
    def test_earthy_three_colours_returns_a_wada_plate(self):
        p = search("earthy", "three", "colours", "--json")
        self.assertEqual(p.returncode, 0, p.stderr_text)
        data = json.loads(p.stdout_text)
        types = [r["source_type"] for r in data["results"]]
        self.assertIn("wada_plate", types)
        self.assertLessEqual(len(data["results"]), 5)
        for r in data["results"]:
            self.assertEqual(r["count"], 3)
            self.assertTrue(r["label"])
            self.assertTrue(r["source_url"])

    def test_wada_plate_400_is_not_in_the_data(self):
        p = search("wada", "plate", "400")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not in the data", p.stderr_text + p.stdout_text)
        self.assertNotIn("wada-", p.stdout_text)  # no row was substituted
        p = search("--id", "wada-349")
        self.assertEqual(p.returncode, 2)
        p = search("--id", "wada-0")
        self.assertEqual(p.returncode, 2)
        p = search("--id", "nonsense-id")
        self.assertEqual(p.returncode, 2)
        self.assertIn("not in the data", p.stderr_text)

    def test_plate_lookup_edges(self):
        for n in (1, 348):
            p = search("--id", f"wada-{n}", "--json")
            self.assertEqual(p.returncode, 0)
            self.assertEqual(json.loads(p.stdout_text)["results"][0]["id"], f"wada-{n}")
        p = search("plate", "229")
        self.assertEqual(p.returncode, 0)
        self.assertIn("wada-229", p.stdout_text)
        self.assertIn("Wada plate 229 (*A Dictionary of Color Combinations*, 1933)", p.stdout_text)

    def test_vol2_is_reported_missing(self):
        for q in ("wada vol. 2 plates", "Volume 2 palettes", "dictionary vol 2"):
            p = search(*q.split())
            self.assertEqual(p.returncode, 2, q)
            self.assertIn("Vol. 2", p.stderr_text)
            self.assertNotIn("1. ", p.stdout_text)

    def test_zero_results_says_so_and_does_not_pad(self):
        p = search("zzzqqqxx")
        self.assertEqual(p.returncode, 1)
        self.assertIn("No palettes in the data match", p.stdout_text)
        self.assertNotIn("1. ", p.stdout_text)
        p = search("blue", "--count", "2", "--source-type", "kasane")
        self.assertEqual(p.returncode, 1)  # kasane patterns never have exactly two... filtered to nothing
        self.assertNotIn("1. ", p.stdout_text)

    def test_japanese_painting_puts_hokusai_first(self):
        p = search("japanese", "painting", "--json")
        self.assertEqual(p.returncode, 0, p.stderr_text)
        data = json.loads(p.stdout_text)
        self.assertEqual(data["results"][0]["id"], "paint-the-great-wave-off-kanagawa")
        self.assertTrue(data["results"][0]["drift"])
        self.assertIn("only East Asian work", " ".join(data["notes"]))
        p = search("japanese", "--source-type", "painting", "blue", "--json")
        self.assertEqual(json.loads(p.stdout_text)["results"][0]["id"], "paint-the-great-wave-off-kanagawa")

    def test_output_has_label_url_and_drift_note(self):
        p = search("sunflowers")
        self.assertEqual(p.returncode, 0)
        self.assertIn("paint-sunflowers", p.stdout_text)
        self.assertIn("label: Sampled from Sunflowers, Vincent van Gogh, 1888 by colorcombinations.org", p.stdout_text)
        self.assertIn("https://colorcombinations.org/paintings/sunflowers/", p.stdout_text)
        self.assertIn("drift:", p.stdout_text)
        self.assertIn("not the artist's original colours", p.stdout_text)
        k = search("wisteria")
        self.assertIn("Kasane no irome: Fuji (Heian court colour layering; hex values are interpretations)", k.stdout_text)

    def test_filters(self):
        p = search("--count", "4", "--mood", "bold", "--source-type", "wada_plate", "--limit", "3", "--json")
        data = json.loads(p.stdout_text)
        self.assertEqual(len(data["results"]), 3)
        for r in data["results"]:
            self.assertEqual(r["count"], 4)
            self.assertIn("bold", r["moods"])
            self.assertEqual(r["source_type"], "wada_plate")
        p = search("--season", "late autumn", "--limit", "20", "--json")
        rs = json.loads(p.stdout_text)["results"]
        self.assertTrue(rs)
        self.assertTrue(all(r["source_type"] == "kasane" and "late autumn" in r["season"].lower() for r in rs))
        p = search("--era", "edo", "--hue", "brown", "--json")
        rs = json.loads(p.stdout_text)["results"]
        self.assertTrue(rs)
        for r in rs:  # --hue matches a hue the palette contains, not only its dominant hue
            self.assertEqual(r["era"], "edo")
            self.assertIn("brown", r["hues"])

    def test_misspelling_aliases_find_the_plate(self):
        p = search("sulphur", "yellow", "--json")
        self.assertEqual(p.returncode, 0)
        names = " ".join(c["name"] for r in json.loads(p.stdout_text)["results"] for c in r["colors"])
        self.assertIn("Sulpher Yellow", names)

    def test_limit_and_help(self):
        p = search("red", "--limit", "2", "--json")
        self.assertLessEqual(len(json.loads(p.stdout_text)["results"]), 2)
        self.assertEqual(search("--help").returncode, 0)
        self.assertEqual(search().returncode, 2)

    def test_japanese_text_on_a_default_windows_pipe(self):
        p = search("紅と紺")
        self.assertEqual(p.returncode, 0, p.stderr_text)
        self.assertIn("ed-kurenai-kon", p.stdout_text)


if __name__ == "__main__":
    unittest.main()

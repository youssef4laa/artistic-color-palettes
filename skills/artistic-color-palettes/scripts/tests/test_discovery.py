"""Discovery without a named source: measured hue / moods in the data, the colour vocabulary, --hue as 'contains',
--lightness / --chroma bands and --near HEX."""
import json
import unittest

from common import DATA, run_script
import colorlib as cl


def search(*args):
    return run_script("search.py", *args)


def results(*args):
    p = search(*args, "--json")
    return p, json.loads(p.stdout_text)


class TestMeasuredData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = cl.load_palette_rows(DATA / "palettes.csv")

    def test_hue_and_hues_come_from_the_hex_values(self):
        for r in self.rows:
            p = cl.palette_profile(r)
            self.assertEqual(r["hue"], p["dominant"], r["id"])
            self.assertEqual(r["hues"].split(";"), list(p["hue_shares"]), r["id"])
            self.assertIn(r["hue"], cl.HUE_BUCKETS)
        wada = [r for r in self.rows if r["source_type"] == "wada_plate"]
        for hue in ("blue", "green", "purple", "teal"):  # the site's tag had 13 blue, 5 green, 0 purple, no teal
            self.assertGreater(sum(hue in r["hues"].split(";") for r in wada), 40, hue)

    def test_teal_is_its_own_bucket(self):
        self.assertEqual(cl.hue_bucket("#008080"), "teal")
        self.assertEqual(cl.hue_bucket("#40e0d0"), "teal")
        self.assertEqual(cl.hue_bucket("#87ceeb"), "blue")
        self.assertEqual(cl.hue_bucket("#228b22"), "green")
        self.assertEqual(cl.hue_bucket("#f5f5dc"), "neutral")

    def test_kasane_and_paintings_have_measured_moods(self):
        for r in self.rows:
            if r["source_type"] in ("kasane", "painting"):
                self.assertEqual(r["mood_source"], "measured", r["id"])
                self.assertTrue(r["moods"], r["id"])
                self.assertNotIn("refined", r["moods"].split(";"), r["id"])
            else:
                self.assertEqual(r["mood_source"], "site", r["id"])

    def test_area_weights(self):
        kasane = next(r for r in self.rows if r["id"] == "kasane-matsu-gasane")
        w = cl.palette_weights(kasane)
        self.assertAlmostEqual(sum(w), 1.0)
        self.assertAlmostEqual(w[0], cl.KASANE_HITOE_SHARE)
        wave = next(r for r in self.rows if r["id"] == "paint-the-great-wave-off-kanagawa")
        w = cl.palette_weights(wave)
        self.assertGreater(w[0], 0.5)  # the 34 % paper ground dominates the six samples


class TestVocabulary(unittest.TestCase):
    def test_everyday_words_now_find_palettes(self):
        for q in ("ocean", "sunset", "teal", "pastel", "coffee", "luxury", "forest green", "moody", "earth tones", "sky blue"):
            p, data = results(q)
            self.assertEqual(p.returncode, 0, q)
            self.assertTrue(data["results"], q)
            self.assertTrue(data["read_as"], q)  # the reading is reported, so the agent can pass it on

    def test_ocean_results_hold_blue_or_teal(self):
        _, data = results("ocean", "--limit", "10")
        for r in data["results"]:
            self.assertTrue({"blue", "teal"} & set(r["hues"]), r["id"])
        self.assertIn("blue or teal", data["read_as"]["ocean"])

    def test_modifier_narrows_the_next_colour_word(self):
        _, data = results("pastel", "pink", "--limit", "10")
        self.assertIn("pastel pink", data["read_as"])
        for r in data["results"]:
            fits = [c for c in r["colors"] if cl.hue_bucket(c["hex"]) == "pink" and cl.hex_to_oklch(c["hex"])[0] >= 0.75]
            self.assertTrue(fits, r["id"])

    def test_lone_modifier_sets_a_palette_band(self):
        _, data = results("dark", "--limit", "10")
        for r in data["results"]:
            self.assertEqual(r["tone"]["lightness"], "dark", r["id"])

    def test_negated_words_are_not_searched(self):
        p, data = results("not", "too", "dark", "earthy")
        self.assertEqual(p.returncode, 0)
        self.assertNotIn("dark", " ".join(data["read_as"]))
        self.assertIn("not searched", " ".join(data["notes"]))

    def test_product_words_say_so_and_return_nothing(self):
        p = search("fintech", "dashboard")
        self.assertEqual(p.returncode, 1)
        self.assertIn("describe the colours instead", p.stdout_text)
        self.assertNotIn("1. ", p.stdout_text)
        p, data = results("coffee", "shop")
        self.assertEqual(p.returncode, 0)
        self.assertIn("shop", " ".join(data["notes"]))

    def test_every_vocabulary_word_reads_and_scores(self):
        import search
        import vocab as cv

        rows = cl.load_palette_rows(DATA / "palettes.csv")
        profiles = [cl.palette_profile(r) for r in rows]
        spec_keys = {"buckets", "arc", "L", "C"}
        for word, (_, specs) in {**cv.COLOURS, **cv.COMPOUNDS}.items():
            self.assertTrue(specs and all(isinstance(s, dict) and set(s) == spec_keys for s in specs), word)
        for word, t in cv.THEMES.items():
            self.assertTrue(t["desc"], word)
            for g in t["groups"]:
                self.assertTrue(g and all(isinstance(s, dict) and set(s) == spec_keys for s in g), word)
        no_match_in_this_data = {"magenta", "fuchsia"}  # Wada's prints hold no saturated magenta (C >= 0.15)
        for word in [*cv.COLOURS, *cv.COMPOUNDS, *cv.MODIFIERS, *cv.THEMES]:
            facets = search.read_vocab(word.split(), set())[0]
            self.assertEqual(len(facets), 1, word)
            hits = sum(1 for r, p in zip(rows, profiles) if search.facet_score(p, r, facets[0]) > 0)
            if word in no_match_in_this_data:
                self.assertEqual(hits, 0, word)
            else:
                self.assertGreater(hits, 0, word)

    def test_heat_words(self):
        _, data = results("ember", "--limit", "10")
        self.assertIn("glowing red or orange", data["read_as"]["ember"])
        for r in data["results"]:
            self.assertIn(r["tone"]["lightness"], ("dark", "mid"), r["id"])
            self.assertTrue(any(cl.hue_bucket(c["hex"]) in ("red", "orange") and cl.hex_to_oklch(c["hex"])[1] >= 0.12
                                for c in r["colors"]), r["id"])
        _, data = results("molten", "--limit", "10")
        for r in data["results"]:
            self.assertTrue(any(cl.hex_to_oklch(c["hex"])[0] <= 0.27 for c in r["colors"]), r["id"])  # the black
        _, data = results("warm", "glow", "--limit", "10")
        for r in data["results"]:
            self.assertTrue(any(cl.hue_bucket(c["hex"]) in ("orange", "yellow") and cl.hex_to_oklch(c["hex"])[0] >= 0.65
                                for c in r["colors"]), r["id"])
        for q in ("embers", "smouldering", "fiery", "forge", "roasted", "lanterns", "heat"):
            p, data = results(q)
            self.assertEqual(p.returncode, 0, q)
            self.assertTrue(data["results"] and data["read_as"], q)

    def test_heat_words_leave_colour_compounds_alone(self):
        _, data = results("hot", "pink")
        self.assertEqual(list(data["read_as"]), ["hot pink"])
        _, data = results("burnt", "orange")
        self.assertEqual(list(data["read_as"]), ["burnt orange"])
        p, data = results("not", "too", "hot")
        self.assertEqual(data["read_as"], {})
        self.assertIn("hot", p.stdout_text)

    def test_no_fabrication_rules_still_hold(self):
        self.assertEqual(search("teal", "plate", "400").returncode, 2)
        self.assertEqual(search("sakura-gasane", "pastel").returncode, 2)


class TestFilters(unittest.TestCase):
    def test_hue_means_contains_and_ranks_by_share(self):
        _, data = results("--hue", "purple", "--source-type", "wada_plate", "--limit", "60")
        self.assertGreaterEqual(len(data["results"]), 40)
        for r in data["results"]:
            self.assertIn("purple", r["hues"])
        _, data = results("--hue", "blue", "--source-type", "wada_plate", "--limit", "8")
        shares = [cl.palette_profile(dict(colors=";".join(c["hex"] for c in r["colors"]), source_type="wada_plate"))
                  ["hue_shares"]["blue"] for r in data["results"]]
        self.assertEqual(shares, sorted(shares, reverse=True))  # plates with more blue first
        self.assertEqual(shares[0], 1.0)
        p = search("--hue", "mauve")
        self.assertEqual(p.returncode, 2)
        self.assertIn("is not a hue", p.stderr_text)

    def test_lightness_and_chroma_bands_and_ranges(self):
        _, data = results("--lightness", "light", "--chroma", "muted", "--limit", "30")
        self.assertTrue(data["results"])
        for r in data["results"]:
            self.assertGreaterEqual(r["tone"]["l_mean"], 0.72)
            self.assertLess(r["tone"]["c_max"], 0.11)
        _, data = results("--lightness", "0.3-0.45", "--limit", "30")
        self.assertTrue(data["results"])
        for r in data["results"]:
            self.assertTrue(0.3 <= r["tone"]["l_mean"] <= 0.45, r["id"])
        p = search("--chroma", "loud")
        self.assertEqual(p.returncode, 2)

    def test_count_takes_a_list_or_a_range(self):
        _, data = results("--count", "3,4", "--source-type", "wada_plate", "--limit", "300")
        counts = {r["count"] for r in data["results"]}
        self.assertEqual(counts, {3, 4})
        _, data = results("--count", "2-3", "--hue", "teal", "--limit", "300")
        self.assertTrue(data["results"])
        self.assertTrue({r["count"] for r in data["results"]} <= {2, 3})
        self.assertEqual(data["filters"]["count"], [2, 3])
        p, data = results("orange", "black", "--count", "3,4", "--lightness", "dark")
        self.assertEqual(p.returncode, 0)  # the call that failed in iteration 4
        self.assertTrue(all(r["count"] in (3, 4) for r in data["results"]))
        for bad in ("9", "x", "1-3"):
            p = search("teal", "--count", bad)
            self.assertEqual(p.returncode, 2, bad)
            self.assertIn("--count", p.stderr_text)

    def test_mood_now_covers_kasane_and_paintings(self):
        p, data = results("--mood", "serene", "--source-type", "kasane")
        self.assertEqual(p.returncode, 0)
        self.assertTrue(all(r["mood_source"] == "measured" for r in data["results"]))
        p, data = results("--mood", "cool", "--source-type", "painting")
        self.assertEqual(p.returncode, 0)
        self.assertIn("paint-the-starry-night", [r["id"] for r in data["results"]])
        self.assertEqual(search("--mood", "refined", "--source-type", "kasane").returncode, 1)
        p = search("--mood", "cozy")
        self.assertEqual(p.returncode, 2)
        self.assertIn("is not a mood in the data", p.stderr_text)


class TestNear(unittest.TestCase):
    def test_near_keeps_close_palettes_nearest_first(self):
        p, data = results("--near", "#2a9d8f", "--limit", "10")
        self.assertEqual(p.returncode, 0)
        ds = [r["near"][0]["delta_e"] for r in data["results"]]
        self.assertTrue(ds)
        self.assertTrue(all(d <= 0.08 for d in ds))
        self.assertEqual(ds, sorted(ds))
        for r in data["results"]:
            hit = r["near"][0]
            self.assertIn(hit["hex"], [c["hex"] for c in r["colors"]])
            self.assertAlmostEqual(cl.delta_e_ok("#2a9d8f", hit["hex"]), hit["delta_e"], places=3)

    def test_hex_in_the_query_and_combined_filters(self):
        _, data = results("#2a9d8f", "--count", "3")
        self.assertTrue(data["results"])
        self.assertTrue(all(r["count"] == 3 and r["near"] for r in data["results"]))
        p = search("#229")  # an all-digit #rgb is still a plate number
        self.assertIn("wada-229", p.stdout_text)

    def test_nothing_close_says_how_far_the_closest_is(self):
        p = search("--near", "#6d28d9")
        self.assertEqual(p.returncode, 1)
        self.assertIn("No palette in the data has a colour within dE_OK 0.08", p.stdout_text)
        self.assertIn("Closest:", p.stdout_text)
        self.assertIn("--near-max", p.stdout_text)
        self.assertNotIn("1. ", p.stdout_text)
        p, data = results("--near", "#6d28d9", "--near-max", "0.12")
        self.assertEqual(p.returncode, 0)
        self.assertTrue(all(r["near"][0]["delta_e"] <= 0.12 for r in data["results"]))

    def test_several_targets_must_all_match(self):
        _, data = results("--near", "#2a9d8f,#e9c46a", "--near-max", "0.1")
        for r in data["results"]:
            self.assertEqual(len(r["near"]), 2)
            self.assertTrue(all(h["delta_e"] <= 0.1 for h in r["near"]))
        self.assertEqual(search("--near", "#12345").returncode, 2)


if __name__ == "__main__":
    unittest.main()

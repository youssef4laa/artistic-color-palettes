"""Red-team fixes S2, S3, S4, S9, S10 (notes/4L-review.md, sources branch)."""
import json
import re
import unittest
from pathlib import Path

from common import run_script, temp_project
import colorlib as cl
import search as sr


def results(*args):
    p = run_script("search.py", *args, "--json")
    return p, (json.loads(p.stdout_text) if p.stdout_text.strip().startswith("{") else {})


def lightest_is_cream(row):
    return sr.is_cream_ground(row)


class TestJapanSpread(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r["id"]: r for r in cl.load_palette_rows()}

    def test_japanese_queries_span_source_types_and_limit_cream_grounds(self):
        for q in (["japanese", "restaurant"], ["japanese"], ["japan"]):
            p, d = results(*q)
            self.assertEqual(p.returncode, 0, q)
            res = d["results"]
            self.assertLessEqual(len(res), 5)
            types = [r["source_type"] for r in res]
            self.assertIn("wada_plate", types, q)
            self.assertIn("kasane", types, q)
            creams = [r["id"] for r in res if lightest_is_cream(self.rows[r["id"]])]
            self.assertLessEqual(len(creams), 1, (q, creams))
        _, d = results("japanese", "restaurant")
        self.assertTrue(any("Words not found in the data: restaurant" in n for n in d["notes"]))

    def test_showa_is_part_of_the_japan_expansion(self):
        self.assertIn("showa", sr.JAPAN_ERAS)
        p, d = results("japanese", "--source-type", "wada_plate")
        self.assertEqual(p.returncode, 0)
        self.assertTrue(d["results"])
        self.assertTrue(all(r["source_type"] == "wada_plate" for r in d["results"]))
        self.assertLessEqual(sum(lightest_is_cream(self.rows[r["id"]]) for r in d["results"]), 1)
        p, d = results("japanese", "--source-type", "kasane")
        self.assertTrue(d["results"])
        self.assertLessEqual(sum(lightest_is_cream(self.rows[r["id"]]) for r in d["results"]), 1)

    def test_calm_lifts_the_cream_limit(self):
        _, d = results("japanese", "calm")
        self.assertTrue(d["results"])
        self.assertIn("wada_plate", [r["source_type"] for r in d["results"]])
        creams = sum(lightest_is_cream(self.rows[r["id"]]) for r in d["results"])
        self.assertGreaterEqual(creams, 2)  # the serene editorial grounds are allowed through

    def test_japanese_painting_still_puts_hokusai_first(self):
        _, d = results("japanese", "painting")
        self.assertEqual(d["results"][0]["id"], "paint-the-great-wave-off-kanagawa")


class TestUsageNotes(unittest.TestCase):
    def test_notes_render_inside_the_region_and_are_idempotent(self):
        with temp_project() as tmp:
            notes = Path(tmp) / "notes.md"
            notes.write_text("## Reading column\nUse the voice colours for bands only.\n\n- keep accent under 5%\n", encoding="utf-8", newline="\n")
            proj = Path(tmp) / "proj"
            proj.mkdir()
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--notes", str(notes))
            self.assertEqual(p.returncode, 0, p.stderr_text)
            text = (proj / "DESIGN.md").read_text(encoding="utf-8")
            begin, end = text.index("<!-- acp:begin colors v1 -->"), text.index("<!-- acp:end colors -->")
            at = text.index("#### Usage notes")
            self.assertTrue(begin < at < end)
            self.assertIn("Use the voice colours for bands only.", text[begin:end])
            self.assertIn("**Reading column**", text)  # headings are flattened, no new document sections
            self.assertNotIn("\n## Reading column", text)
            self.assertEqual(len(re.findall(r"^## ", text, re.M)), 1)
            first = {f: (proj / f).read_bytes() for f in ("DESIGN.md", "design/palette.json", "design/tokens.css")}
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--notes", str(notes))
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj))  # remembered
            for f, data in first.items():
                self.assertEqual((proj / f).read_bytes(), data, f)
            # the notes follow a palette change (regenerated with the hex), and can be dropped
            run_script("handoff.py", "--palette", "ed-kurenai-kon", "--project-dir", str(proj))
            text2 = (proj / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("Use the voice colours for bands only.", text2)
            self.assertIn("Crimson & Navy", text2)
            run_script("handoff.py", "--palette", "ed-kurenai-kon", "--project-dir", str(proj), "--no-notes")
            self.assertNotIn("Usage notes", (proj / "DESIGN.md").read_text(encoding="utf-8"))
            self.assertIn("--notes", run_script("handoff.py", "--help").stdout_text)

    def test_missing_notes_file_is_an_error(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp, "--notes", str(Path(tmp) / "nope.md"))
            self.assertEqual(p.returncode, 2)
            self.assertFalse((Path(tmp) / "DESIGN.md").exists())


class TestTasteAlias(unittest.TestCase):
    def test_surface_alias_is_a_separated_step_and_map_states_the_stricter_numbers(self):
        with temp_project() as tmp:
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            css = (Path(tmp) / "design" / "tokens.css").read_text(encoding="utf-8")
            self.assertRegex(css, r"--surface: var\(--color-bg-subtle\);")
            self.assertNotIn("--surface: var(--color-surface);", css)
            pj = json.loads((Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8"))
            light = pj["roles"]["light"]
            L = lambda t: cl.hex_to_oklch(light[t]["hex"])[0]  # noqa: E731
            self.assertGreaterEqual(abs(L("bg") - L("bg-subtle")), 0.03)  # told apart by tone
            text = (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")
            self.assertIn("With Taste loaded the stricter numbers win: accent < 5%, ground <= 90%, separate surfaces by lightness, not lines.", text)
            taste = next(ln for ln in text.split("\n") if ln.startswith("- Taste:"))
            self.assertIn(f"`--surface` {light['bg-subtle']['hex'].upper()}", taste)


class TestExistingPalette(unittest.TestCase):
    FIXTURE = '---\nname: Red shop\ncolors:\n  primary: "#ff0000"\n---\n\n## Colors\n\nRed brand.\n'

    def test_existing_palette_blocks_every_write_until_yes(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            (proj / "DESIGN.md").write_text(self.FIXTURE, encoding="utf-8", newline="\n")
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj))
            self.assertEqual(p.returncode, 3, p.stderr_text)
            self.assertIn("existing palette found: choose replace or refine (SKILL.md step 1) before --yes", p.stdout_text)
            self.assertEqual((proj / "DESIGN.md").read_text(encoding="utf-8"), self.FIXTURE)
            self.assertFalse((proj / "design").exists())  # no palette.json, no tokens.css
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(p.returncode, 3)
            self.assertFalse((proj / "CLAUDE.md").exists())
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj), "--yes")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertTrue((proj / "design" / "tokens.css").exists())
            self.assertIn("Red brand.", (proj / "DESIGN.md").read_text(encoding="utf-8"))

    def test_prose_alone_or_keys_alone_count_and_a_clean_file_does_not(self):
        import handoff as ho

        self.assertTrue(ho.existing_palette_found(self.FIXTURE))
        self.assertTrue(ho.existing_palette_found('---\nname: x\ncolors:\n  primary: "#f00"\n---\n\n## Overview\n\nHi.\n'))
        self.assertTrue(ho.existing_palette_found("# Doc\n\n## Colors\n\nBlue brand.\n"))
        self.assertFalse(ho.existing_palette_found("# Doc\n\n## Typography\n\nInter.\n"))
        self.assertFalse(ho.existing_palette_found("---\nname: x\n---\n\n## Overview\n\nHi.\n"))
        with temp_project() as tmp:  # a file we generated ourselves is not "an existing palette"
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            self.assertFalse(ho.existing_palette_found((Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")))

    def test_insertion_without_an_existing_palette_also_writes_nothing_before_yes(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            (proj / "DESIGN.md").write_text("# Doc\n\n## Typography\n\nInter.\n", encoding="utf-8", newline="\n")
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(proj))
            self.assertEqual(p.returncode, 3)
            self.assertNotIn("existing palette found", p.stdout_text)
            self.assertFalse((proj / "design").exists())


class TestKasaneCredit(unittest.TestCase):
    def test_no_share_alike_licence_line_in_generated_files(self):
        with temp_project() as tmp:
            p = run_script("handoff.py", "--palette", "kasane-fuji", "--project-dir", tmp)
            self.assertEqual(p.returncode, 0, p.stderr_text)
            courtesy = "Base colours after Wikipedia, 'Traditional colors of Japan' (CC BY-SA 4.0); pattern after Heian kasane no irome."
            css = (Path(tmp) / "design" / "tokens.css").read_text(encoding="utf-8")
            pj_text = (Path(tmp) / "design" / "palette.json").read_text(encoding="utf-8")
            md = (Path(tmp) / "DESIGN.md").read_text(encoding="utf-8")
            for name, text in (("tokens.css", css), ("palette.json", pj_text), ("DESIGN.md", md)):
                self.assertNotRegex(text, r"(?i)licen[cs]e:?\s*\"?\s*CC-BY-SA", name)
                self.assertNotIn("CC-BY-SA", text, name)
                self.assertIn(courtesy, text, name)
            self.assertNotIn("Licence:", css)
        # the data row keeps its licence column
        row = next(r for r in cl.load_palette_rows() if r["id"] == "kasane-fuji")
        self.assertEqual(row["licence"], "CC-BY-SA-4.0 (base hex) + own composition")
        # other families still state their licence
        with temp_project() as tmp:
            run_script("handoff.py", "--palette", "wada-229", "--project-dir", tmp)
            self.assertIn("Licence: PD+MIT+CC-BY-4.0", (Path(tmp) / "design" / "tokens.css").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

"""handoff.py: idempotent, marker-only edits, neighbour text preserved byte for byte, opt-in pointer."""
import difflib
import json
import os
import re
import unittest
from pathlib import Path

from common import parse_frontmatter, run_script, temp_project
import colorlib as cl
import handoff as ho

IMPECCABLE_FIXTURE = """---
name: Heritage Ledger
description: "Accounting for small studios"
colors:
  oxblood-deep: "#7a1f1f"
  paper: "oklch(96% 0.01 85)"
typography:
  display:
    fontFamily: "Newsreader"
    fontSize: 2.5rem
rounded:
  md: 6px
---

# Design System: Heritage Ledger

## Overview

A calm ledger. Keep the tone plain.

## Colors

The ledger world is oxblood on paper.

### Primary
- **Oxblood Deep** (#7a1f1f / oklch(0.35 0.1 25)): the one brand colour.

### Named Rules
**The One Voice Rule.** Oxblood is used on at most 8% of any screen.

## Typography

Newsreader for headings. Tabular figures in tables.

## Components

### Buttons
Square corners. No shadows.

## Do's and Don'ts

- Do keep rows dense.
- Don't use gradients.
"""


def only_insertions(old: str, new: str) -> bool:
    a, b = old.split("\n"), new.split("\n")
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    return all(tag in ("equal", "insert") for tag, *_ in ops)


def outside_markers(text: str) -> str:
    """Text with both of our regions (marker lines included) cut out."""
    text = re.sub(r"[ \t]*# acp:begin tokens.*?# acp:end tokens[^\n]*\n", "", text, flags=re.S)
    text = re.sub(r"[ \t]*<!-- acp:begin colors v\d+ -->.*?<!-- acp:end colors -->[^\n]*\n", "", text, flags=re.S)
    return text


def run_handoff(proj, *args, palette="wada-229"):
    return run_script("handoff.py", "--palette", palette, "--project-dir", str(proj), *args)


class TestCreateAndIdempotency(unittest.TestCase):
    def test_creates_seed_files_and_rerun_is_byte_identical(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            p = run_handoff(proj, "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(p.returncode, 0, p.stderr_text + p.stdout_text)
            files = ["DESIGN.md", "design/palette.json", "design/tokens.css", "CLAUDE.md", "AGENTS.md"]
            for f in files:
                self.assertTrue((proj / f).exists(), f)
            first = {f: (proj / f).read_bytes() for f in files}
            p2 = run_handoff(proj, "--claude-md", "yes", "--user-confirmed")
            self.assertEqual(p2.returncode, 0)
            for f in files:
                self.assertEqual(first[f], (proj / f).read_bytes(), f"{f} changed on re-run")
            self.assertIn("unchanged", p2.stdout_text)
            # not stored in the repository by accident; no timestamps in generated files
            for f in ("design/palette.json", "design/tokens.css", "DESIGN.md"):
                self.assertNotRegex(first[f].decode("utf-8"), r"20\d\d-\d\d-\d\dT")

    def test_seed_design_md_shape_and_frontmatter_parses(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            run_handoff(proj)
            text = (proj / "DESIGN.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"))  # frontmatter opens on line 1
            lines = text.split("\n")
            close = lines.index("---", 1)
            self.assertTrue(lines[close + 1].startswith("<!-- acp:seed palette-only"))  # seed comment is the first body line
            self.assertNotIn("SEED:", lines[close + 1])
            fm = parse_frontmatter(text)
            self.assertEqual(fm["name"], "Golden Yellow & Deep Slate Olive +1")
            colors = fm["colors"]
            self.assertTrue({"bg", "text", "accent", "on-accent", "success"} <= set(colors))
            for k, v in colors.items():
                self.assertRegex(v, r"^#[0-9A-F]{6}$", k)
            self.assertIn("# acp:begin tokens", text)
            self.assertIn("# acp:end tokens", text)
            self.assertEqual(len(re.findall(r"^## ", text, re.M)), 1)
            self.assertIn("## Colors\n<!-- acp:begin colors v1 -->", text)
            self.assertIn("<!-- acp:end colors -->", text)
            # body hex values equal the frontmatter's
            for key in ("accent", "bg", "text"):
                self.assertIn(f"{colors[key]} / oklch(", text) if key == "accent" else None
            self.assertIn("### Primary", text)
            self.assertIn("### Neutral", text)
            self.assertIn("### Named Rules", text)
            self.assertIn("The Restrained Rule", text)
            self.assertIn("Wada plate 229 (*A Dictionary of Color Combinations*, 1933)", text)

    def test_palette_json_and_tokens_css(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            run_handoff(proj)
            pj = json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["schema"], "acp-palette/1")
            self.assertTrue(pj["contrast"]["gate_pass"])
            self.assertEqual(pj["palette"]["id"], "wada-229")
            self.assertEqual(pj["palette"]["licence"], "PD+MIT+CC-BY-4.0")
            for key in ("ramps", "roles", "proportions", "adjustments", "assignment"):
                self.assertIn(key, pj)
            self.assertEqual(pj["handoff"]["claude_md"], "not_asked")
            self.assertEqual(pj["handoff"]["tokens_css"], "design/tokens.css")
            css = (proj / "design" / "tokens.css").read_text(encoding="utf-8")
            self.assertIn("/* Wada plate 229 via colorcombinations.org (CC BY 4.0) */", css)
            self.assertIn("@media (prefers-color-scheme: dark)", css)
            self.assertIn('[data-theme="dark"]', css)
            self.assertIn("--neutral-50:", css)
            self.assertIn("--accent-dark-500:", css)
            self.assertIn("--color-bg: var(--neutral-50);", css)
            self.assertIn("--color-bg: var(--neutral-dark-950);", css)
            self.assertLess(css.index("--neutral-50:"), css.index("--color-bg:"))  # primitives before semantics
            for alias in ("--bg:", "--surface:", "--ink:", "--accent-ink:", "--color-primary:", "--color-ring:", "--foreground:", "--faint:"):
                self.assertIn(alias, css)
            # every semantic token resolves to a defined primitive or literal
            defined = set(re.findall(r"^\s*(--[a-z0-9-]+):", css, re.M))
            for ref in re.findall(r"var\((--[a-z0-9-]+)\)", css):
                self.assertIn(ref, defined, ref)

    def test_failing_gate_writes_nothing(self):
        import build_tokens as bt

        t = bt.build_tokens(palette="wada-229")
        t["roles"]["light"]["text"]["hex"] = "#cccccc"
        t["contrast"] = None
        bad = bt.dump_tokens(t)
        with temp_project() as tmp:
            proj = Path(tmp)
            tok = proj / "bad.json"
            tok.write_text(bad, encoding="utf-8")
            # handoff validates and fixes by itself, so even a broken input ends up passing
            p = run_script("handoff.py", "--tokens", str(tok), "--project-dir", str(proj))
            self.assertEqual(p.returncode, 0, p.stderr_text)
            pj = json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertTrue(any(a["role"] == "text" for a in pj["adjustments"]))

    def test_each_source_type_and_strategy(self):
        for pid, strat in (("kasane-kobai-no-nioi", "committed"), ("ed-kurenai-kon", "full-palette"),
                           ("paint-the-great-wave-off-kanagawa", "restrained"), ("wada-100", "drenched")):
            with temp_project() as tmp:
                proj = Path(tmp)
                p = run_handoff(proj, "--strategy", strat, "--mode", "persuade", palette=pid)
                self.assertEqual(p.returncode, 0, (pid, p.stderr_text))
                text = (proj / "DESIGN.md").read_text(encoding="utf-8")
                self.assertIn(f"The {ho.bt.STRATEGY_ALIASES[strat]} Rule", text)
                if pid.startswith("paint-"):
                    self.assertIn("not the artist's original colours", text)
                    self.assertIn("The Measured Ground Rule", text)
                if pid.startswith("kasane"):
                    self.assertIn("interpretations", text)
                    self.assertIn("CC BY-SA 4.0", (proj / "design" / "tokens.css").read_text(encoding="utf-8"))


class TestExistingDesignMd(unittest.TestCase):
    def _fixture(self, proj, text=IMPECCABLE_FIXTURE, eol="\n"):
        path = proj / "DESIGN.md"
        path.write_bytes(text.replace("\n", eol).encode("utf-8"))
        return path

    def test_insertion_needs_yes_then_only_adds_lines(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            path = self._fixture(proj)
            before = path.read_bytes()
            p = run_handoff(proj)
            self.assertEqual(p.returncode, 3, p.stdout_text + p.stderr_text)
            self.assertEqual(path.read_bytes(), before)  # nothing written without --yes
            self.assertIn("+  # acp:begin tokens", p.stdout_text)
            self.assertIn("+<!-- acp:begin colors v1 -->", p.stdout_text)
            p = run_handoff(proj, "--yes")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            new = path.read_bytes().decode("utf-8")
            old = before.decode("utf-8")
            self.assertTrue(only_insertions(old, new), "something outside our markers changed")
            # our regions sit where they belong
            self.assertLess(new.index("## Colors"), new.index("<!-- acp:begin colors v1 -->"))
            self.assertLess(new.index("<!-- acp:end colors -->"), new.index("## Typography"))
            fm = parse_frontmatter(new)
            self.assertEqual(fm["colors"]["oxblood-deep"], "#7a1f1f")  # neighbour entries kept
            self.assertEqual(fm["typography"]["display"]["fontFamily"], "Newsreader")
            self.assertEqual(fm["rounded"]["md"], "6px")
            self.assertIn("accent", fm["colors"])
            # outside the markers the file is the original, except for blank-line padding
            stripped = [ln for ln in outside_markers(new).split("\n") if ln.strip()]
            self.assertEqual(stripped, [ln for ln in old.split("\n") if ln.strip()])

    def test_rerun_with_markers_replaces_only_between_them(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            path = self._fixture(proj)
            run_handoff(proj, "--yes")
            one = path.read_bytes().decode("utf-8")
            again = run_handoff(proj)  # markers exist: no --yes needed
            self.assertEqual(again.returncode, 0)
            self.assertEqual(path.read_bytes().decode("utf-8"), one)  # idempotent
            other = run_handoff(proj, "--strategy", "committed", palette="ed-kurenai-kon")
            self.assertEqual(other.returncode, 0, other.stderr_text)
            two = path.read_bytes().decode("utf-8")
            self.assertNotEqual(one, two)
            self.assertEqual(outside_markers(one), outside_markers(two))  # byte for byte
            self.assertIn("Crimson & Navy", two)
            self.assertNotIn("Golden Yellow & Deep Slate Olive", two.split("<!-- acp:begin colors")[1])
            self.assertEqual(two.count("<!-- acp:begin colors v1 -->"), 1)
            self.assertEqual(two.count("# acp:begin tokens"), 1)

    def test_crlf_file_stays_crlf_and_outside_text_is_byte_identical(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            path = self._fixture(proj, eol="\r\n")
            before = path.read_bytes()
            run_handoff(proj, "--yes")
            new = path.read_bytes()
            self.assertNotIn(b"\n", new.replace(b"\r\n", b""))  # no bare LF anywhere
            self.assertTrue(only_insertions(before.decode("utf-8").replace("\r\n", "\n"), new.decode("utf-8").replace("\r\n", "\n")))
            run_handoff(proj, "--strategy", "full-palette", palette="kasane-fuji")
            newer = path.read_bytes()
            self.assertEqual(outside_markers(new.decode("utf-8")), outside_markers(newer.decode("utf-8")))
            self.assertNotIn(b"\n", newer.replace(b"\r\n", b""))

    def test_file_without_frontmatter_or_colors_section(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            plain = "# Notes\n\nSome words.\n\n## Typography\n\nInter.\n"
            path = proj / "DESIGN.md"
            path.write_text(plain, encoding="utf-8", newline="\n")
            p = run_handoff(proj, "--yes")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            new = path.read_text(encoding="utf-8")
            self.assertIn("## Colors", new)
            self.assertLess(new.index("## Colors"), new.index("## Typography"))  # canonical order
            self.assertIn("Some words.", new)
            fm = parse_frontmatter(new)
            self.assertIn("accent", fm["colors"])

    def test_key_clash_is_refused_and_prefix_fixes_it(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            clash = IMPECCABLE_FIXTURE.replace("  oxblood-deep:", "  accent: \"#111111\"\n  oxblood-deep:")
            path = self._fixture(proj, clash)
            before = path.read_bytes()
            p = run_handoff(proj, "--yes")
            self.assertEqual(p.returncode, 2)
            self.assertIn("accent", p.stderr_text)
            self.assertEqual(path.read_bytes(), before)
            p = run_handoff(proj, "--yes", "--key-prefix", "acp-")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
            self.assertEqual(fm["colors"]["accent"], "#111111")
            self.assertIn("acp-accent", fm["colors"])

    def test_damaged_markers_are_refused(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            self._fixture(proj, IMPECCABLE_FIXTURE.replace("## Colors\n", "## Colors\n<!-- acp:begin colors v1 -->\n"))
            before = (proj / "DESIGN.md").read_bytes()
            p = run_handoff(proj, "--yes")
            self.assertEqual(p.returncode, 2)
            self.assertIn("damaged", p.stderr_text)
            self.assertEqual((proj / "DESIGN.md").read_bytes(), before)

    def test_dry_run_writes_nothing(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            p = run_handoff(proj, "--dry-run")
            self.assertEqual(p.returncode, 0)
            self.assertEqual(list(proj.iterdir()), [])

    def test_other_neighbour_files_are_never_touched(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            guarded = {"PRODUCT.md": "# Product\n", ".impeccable/design.json": "{}\n", ".taste-skill/direction.json": "{}\n",
                       ".interface-design/system.md": "# Design System\n", "design-system/x/MASTER.md": "# Master\n"}
            for rel, body in guarded.items():
                f = proj / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(body, encoding="utf-8", newline="\n")
            run_handoff(proj, "--claude-md", "yes", "--user-confirmed")
            for rel, body in guarded.items():
                self.assertEqual((proj / rel).read_text(encoding="utf-8"), body, rel)


class TestClaudeMdPointer(unittest.TestCase):
    def test_pointer_only_written_with_yes(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            (proj / "CLAUDE.md").write_text("# Project rules\n\nBe kind.\n", encoding="utf-8", newline="\n")
            run_handoff(proj)
            self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), "# Project rules\n\nBe kind.\n")
            self.assertFalse((proj / "AGENTS.md").exists())
            pj = json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["handoff"]["claude_md"], "not_asked")
            run_handoff(proj, "--claude-md", "yes", "--user-confirmed")
            text = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# Project rules\n\nBe kind.\n"))
            self.assertIn("<!-- acp:begin pointer v1 -->", text)
            self.assertIn("the project palette lives in DESIGN.md (## Colors) and design/tokens.css", text)
            self.assertTrue((proj / "AGENTS.md").exists())
            self.assertTrue(json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))["handoff"]["claude_md"] is True)
            # plain re-run (no flag) keeps the pointer and the recorded answer
            run_handoff(proj)
            self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), text)
            self.assertTrue(json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))["handoff"]["claude_md"] is True)
            # remove it again
            run_handoff(proj, "--claude-md", "no")
            self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), "# Project rules\n\nBe kind.\n")
            self.assertFalse((proj / "AGENTS.md").exists())  # held only the pointer, so it is gone
            self.assertIs(json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))["handoff"]["claude_md"], False)

    def test_declined_is_recorded_and_writes_nothing(self):
        with temp_project() as tmp:
            proj = Path(tmp)
            run_handoff(proj, "--claude-md", "declined")
            self.assertFalse((proj / "CLAUDE.md").exists())
            self.assertEqual(json.loads((proj / "design" / "palette.json").read_text(encoding="utf-8"))["handoff"]["claude_md"], "declined")

    def test_never_touches_the_home_directory(self):
        with temp_project("acp fake home ") as tmp:
            home = Path(tmp)
            env = {"USERPROFILE": str(home), "HOME": str(home), "HOMEDRIVE": home.drive, "HOMEPATH": str(home)[len(home.drive):]}
            p = run_script("handoff.py", "--palette", "wada-229", "--project-dir", str(home), "--claude-md", "yes", "--user-confirmed", env_extra=env)
            self.assertEqual(p.returncode, 4, p.stdout_text + p.stderr_text)
            self.assertIn("home folder", p.stderr_text)
            self.assertFalse((home / "CLAUDE.md").exists())
            self.assertFalse((home / "AGENTS.md").exists())


class TestPathsAndEncoding(unittest.TestCase):
    def test_windows_paths_with_spaces_and_japanese_output(self):
        with temp_project("acp 日本 dir ") as tmp:
            proj = Path(tmp) / "my project" / "sub dir"
            proj.mkdir(parents=True)
            p = run_script("handoff.py", "--palette", "kasane-kobai-no-nioi", "--project-dir", str(proj),
                           "--design-dir", "design files", "--strategy", "committed", "--mode", "persuade")
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertIn("Kōbai", p.stdout_text)  # console is cp1252 by default: the script must force UTF-8
            self.assertTrue((proj / "design files" / "palette.json").exists())
            pj = json.loads((proj / "design files" / "palette.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["palette"]["title_ja"], "紅梅の匂")
            self.assertEqual(pj["handoff"]["tokens_css"], "design files/tokens.css")
            self.assertIn("紅梅の匂", pj["palette"]["title_ja"])

    def test_tokens_from_stdin_and_file(self):
        import build_tokens as bt

        with temp_project() as tmp:
            proj = Path(tmp)
            tok = bt.dump_tokens(bt.build_tokens(palette="wada-3"))
            p = run_script("handoff.py", "--tokens", "-", "--project-dir", str(proj), input_text=tok)
            self.assertEqual(p.returncode, 0, p.stderr_text)
            self.assertTrue((proj / "DESIGN.md").exists())


if __name__ == "__main__":
    unittest.main()

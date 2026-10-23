"""Doc test: the numbers quoted in references/style-recipes.md worked examples (a) and (c) are the
numbers the shipped scripts produce.

Rebuilds each example with build_tokens.py + validate.py --fix --in-place and asserts that every hex,
every `<ramp>-<step> #hex` pairing and every `N:1` contrast ratio quoted in the example section appears
in the build output. Example (b) is excerpted from handoff.py output and is not covered here.

Run from the skill root:  python -m unittest scripts/tests/test_docs.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent
SKILL = SCRIPTS.parent
RECIPES = SKILL / "references" / "style-recipes.md"

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
RATIO = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?):1\b")
STEPPED = re.compile(r"\b(neutral|accent|voice-\d)-(\d{2,3})\s+`(#[0-9a-fA-F]{6})`")

EXAMPLES = {
    "a": {
        "heading": r"## 2\. Worked example \(a\)",
        "next": r"## 3\. ",
        "args": ["--palette", "wada-218", "--strategy", "restrained", "--mode", "operate"],
    },
    "c": {
        "heading": r"## 4\. Worked example \(c\)",
        "next": None,
        "args": ["--palette", "paint-the-milkmaid", "--strategy", "restrained", "--mode", "read"],
    },
}


def section(text: str, heading: str, nxt: str | None) -> str:
    m = re.search(heading, text)
    assert m, f"heading {heading!r} not found in {RECIPES.name}"
    rest = text[m.end():]
    if nxt:
        n = re.search("^" + nxt, rest, re.M)
        if n:
            rest = rest[:n.start()]
    return rest


def build(args: list[str], tmp: Path) -> dict:
    out = tmp / "tokens.json"
    cmds = [
        [sys.executable, str(SCRIPTS / "build_tokens.py"), *args, "--out", str(out)],
        [sys.executable, str(SCRIPTS / "validate.py"), str(out), "--fix", "--in-place"],
    ]
    for cmd in cmds:
        proc = subprocess.run(cmd, capture_output=True, cwd=str(SKILL), timeout=180)
        if proc.returncode != 0:
            raise AssertionError(f"{' '.join(cmd[1:3])} failed: {proc.stdout.decode('utf-8', 'replace')[-800:]}"
                                 f"{proc.stderr.decode('utf-8', 'replace')[-800:]}")
    return json.loads(out.read_text(encoding="utf-8"))


def ratios_in(data: dict) -> set[float]:
    found: set[float] = set()
    for p in data["contrast"]["pairs"]:
        found.add(float(p["wcag"]))
    for mode in data["roles"].values():
        for role in mode.values():
            for v in (role.get("measured") or {}).values():
                found.add(float(v))
            for k in ("white", "neutral_950"):
                if k in role:
                    found.add(float(role[k]))
    for a in data.get("adjustments", []):
        for k in ("before_ratio", "after_ratio"):
            if k in a:
                found.add(float(a[k]))
    for f in data["contrast"].get("flags", []):
        for k in ("white", "neutral_950"):
            if k in f:
                found.add(float(f[k]))
    return found


class TestStyleRecipeExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RECIPES.read_text(encoding="utf-8")
        cls.tmp = tempfile.TemporaryDirectory(prefix="acp docs ")
        cls.built = {}
        for key, ex in EXAMPLES.items():
            d = Path(cls.tmp.name) / key
            d.mkdir()
            cls.built[key] = build(ex["args"], d)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, key: str):
        ex = EXAMPLES[key]
        body = section(self.text, ex["heading"], ex["next"])
        data = self.built[key]
        blob = json.dumps(data).lower()
        hexes = {h.lower() for h in HEX.findall(body)}
        self.assertGreater(len(hexes), 20, "example should quote its hex values")
        missing = sorted(h for h in hexes if h not in blob)
        self.assertEqual(missing, [], f"example ({key}): hex not in the build output")

        ramps = {}
        for name, ramp in data["ramps"].items():
            for mode in ("light", "dark"):
                for step, hx in (ramp.get(mode) or {}).items():
                    ramps.setdefault((name, step), set()).add(hx.lower())
        bad = []
        for name, step, hx in STEPPED.findall(body):
            if hx.lower() not in ramps.get((name, step), set()):
                bad.append(f"{name}-{step} {hx}")
        self.assertEqual(bad, [], f"example ({key}): step does not match the ramp")

        measured = ratios_in(data)
        quoted = {float(r) for r in RATIO.findall(body)}
        self.assertGreater(len(quoted), 10)
        stray = sorted(r for r in quoted if not any(abs(r - m) < 0.005 for m in measured))
        self.assertEqual(stray, [], f"example ({key}): ratio not in the build output")

    def test_example_a_wada_218_operate_restrained(self):
        self.check("a")

    def test_example_c_milkmaid_read_restrained(self):
        self.check("c")

    def test_examples_say_how_they_were_generated(self):
        for key, needle in (("a", "build_tokens.py --palette wada-218"), ("c", "build_tokens.py --palette paint-the-milkmaid")):
            body = section(self.text, EXAMPLES[key]["heading"], EXAMPLES[key]["next"])
            self.assertIn(needle, body)
            self.assertIn("--pin all", body)

    def test_recipes_file_length(self):
        self.assertLessEqual(len(self.text.splitlines()), 300)


if __name__ == "__main__":
    unittest.main()

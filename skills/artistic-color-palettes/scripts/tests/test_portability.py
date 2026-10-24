"""Portability across agents and platforms: the skill is installed by `npx skills` as a copy under
.agents/skills/ with symlinks from other agents' folders (.claude/skills/ and others), and agents on
macOS and Linux often have no `python` on PATH.

Run from the skill root:  python3 -m unittest scripts/tests/test_portability.py
"""
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

from common import SCRIPTS, SKILL, temp_project

BARE_PYTHON = re.compile(r"(?:^|[\s`|])python (?:<skill>|scripts/)")


class TestCommandsUsePython3(unittest.TestCase):
    def test_skill_md_commands_use_python3(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual([ln for ln in text.splitlines() if BARE_PYTHON.search(ln)], [])
        self.assertIn("python3 <skill>/scripts/search.py", text)

    def test_script_usage_lines_use_python3(self):
        for path in sorted(SCRIPTS.glob("*.py")):
            bad = [ln for ln in path.read_text(encoding="utf-8").splitlines() if BARE_PYTHON.search(ln)]
            self.assertEqual(bad, [], path.name)


class TestThroughSymlink(unittest.TestCase):
    """The layout `npx skills add` makes: <project>/.claude/skills/<name> -> ../../.agents/skills/<name>."""

    def test_scripts_find_their_data_through_a_relative_symlink(self):
        with temp_project() as tmp:
            agent_dir = Path(tmp).resolve() / ".claude" / "skills"
            agent_dir.mkdir(parents=True)
            link = agent_dir / SKILL.name
            try:
                os.symlink(os.path.relpath(SKILL, agent_dir), link, target_is_directory=True)
            except (OSError, NotImplementedError) as e:  # Windows without developer mode
                self.skipTest(f"symlinks unavailable: {e}")
            p = subprocess.run([sys.executable, str(link / "scripts" / "search.py"), "--id", "wada-218"],
                               capture_output=True, cwd=tmp, timeout=180)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8"))
            self.assertIn("Wada plate 218", p.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()

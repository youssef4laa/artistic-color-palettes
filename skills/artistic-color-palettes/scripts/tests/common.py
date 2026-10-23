"""Shared helpers for the test suite (stdlib unittest only)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent
SKILL = SCRIPTS.parent
REPO = SKILL.parent.parent
DATA = SKILL / "data"
sys.path.insert(0, str(SCRIPTS))


def run_script(name: str, *args: str, input_text: str | None = None, env_extra: dict | None = None, cwd: Path | None = None):
    """Run scripts/<name> in a fresh interpreter. stdout/stderr are decoded as UTF-8 (the scripts must
    force UTF-8 themselves: we deliberately do not set PYTHONUTF8 / PYTHONIOENCODING)."""
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env.pop("PYTHONIOENCODING", None)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args], capture_output=True, input=input_text.encode("utf-8") if input_text else None,
        env=env, cwd=str(cwd) if cwd else None, timeout=180,
    )
    proc.stdout_text = proc.stdout.decode("utf-8")
    proc.stderr_text = proc.stderr.decode("utf-8")
    return proc


def temp_project(prefix: str = "acp test ") -> tempfile.TemporaryDirectory:
    """A temporary directory whose name contains a space (Windows path check)."""
    return tempfile.TemporaryDirectory(prefix=prefix)


def parse_frontmatter(text: str) -> dict:
    """Tiny stdlib YAML subset: nested `key: value` maps by indentation, `#` comment lines ignored."""
    lines = text.replace("\r\n", "\n").split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "---")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "---")
    root: dict = {}
    stack = [(-1, root)]
    for raw in lines[start + 1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, _, val = raw.strip().partition(":")
        key = key.strip().strip("\"'")
        val = val.strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            if val[0] in "\"'" and val[-1] == val[0]:
                val = val[1:-1]
            parent[key] = val
    return root

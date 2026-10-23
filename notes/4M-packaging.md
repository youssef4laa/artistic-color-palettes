# 4M - Packaging (2026-10-23)

## Files created / changed
- `.claude-plugin/plugin.json` (name, version 0.1.0, description, author, homepage, repository, license MIT, keywords)
- `.claude-plugin/marketplace.json` (name artistic-color-palettes, owner youssef4laa, one plugin, source "./", version 0.1.0)
- `skills/artistic-color-palettes/SKILL.md`: added `metadata: {version: "0.1.0"}` (block form); nothing else changed
- `README.md`: install section (both channels, GitHub + local forms), Publishing checklist; Works with table was already present
- Schema sources: https://code.claude.com/docs/en/plugins-reference and https://code.claude.com/docs/en/plugin-marketplaces
- Versions: 0.1.0 in all three files.

## Package
`dist/artistic-color-palettes.skill` (git-ignored), 194,565 bytes, 31 files. evals/ and __pycache__ excluded (verified in the archive).
Included: SKILL.md, NOTICE.md, assets/, data/ (colors.csv, paintings.json, palettes.csv, SNAPSHOT.md), references/ (6), scripts/ (+ scripts/tests).
Run needed `PYTHONIOENCODING=utf-8` (package_skill prints an emoji; cp1252 console crashed otherwise).

## Validation
- `npx --yes skills-ref validate skills/artistic-color-palettes` -> "Valid skill".
- `claude plugin validate .` -> "Validation passed" (marketplace manifest).

## Install tests (isolated CLAUDE_CONFIG_DIR = scratchpad\4M\claude-config; real ~/.claude untouched)
- `claude plugin marketplace add D:\Code\Skill\artistic-color-palettes` -> added.
- `claude plugin install artistic-color-palettes@artistic-color-palettes` -> installed (scope user, v0.1.0, enabled; 1 skill, always-on ~258 tok, on-invoke ~4.8k).
- `npx --yes skills add D:\Code\Skill\artistic-color-palettes --skill artistic-color-palettes --copy -y` run in scratchpad\4M\scratch-project -> project-level install to .claude/skills and .agents/skills (not global; ~/.agents has no copy).

## Not tested / caveats
- GitHub forms (`youssef4laa/...`) untestable until the repo is pushed.
- skills.sh indexing/listing is server-side; not testable locally.
- Plugin and skills-CLI installs from the repo include `skills/.../evals/` (277K) because it is in the tree; only the .skill archive excludes it. Consider git-ignoring or relocating evals if that matters.
- Marketplace added from a local path reads in place, so it does not exercise the plugin cache copy.

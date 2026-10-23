# Gate 0 — Setup (2026-10-22)

Produced
- Repo scaffold at `D:\Code\Skill\artistic-color-palettes\` (git init; parent folder untouched),
  with `.claude-plugin/`, `skills/artistic-color-palettes/{references,assets,data,scripts/tests,evals}`,
  `notes/`, `data-raw/` (intermediate data, not shipped).
- `.gitignore` keeps book renders/text (`notes/_private/`, `notes/wada-pages/`) and third-party
  clones (`notes/reference-skills/`, `notes/neighbour-skills/`) out of git, so a public push never
  carries copyrighted material.
- `notes/skills-reference.md`, `notes/fetch-reference-skills.sh` copied from `Code References/`.
- Four reference skills fetched at pinned commits, each with licence: better-colors (MIT),
  ui-ux-pro-max (MIT), theme-factory (Apache-2.0, `LICENSE.txt` in skill folder), impeccable
  (Apache-2.0 + `NOTICE.md`).
- `pypdfium2` render confirmed: Wada PDF has 356 pages; PDF p. 20 renders at 859×1281 and shows
  printed p. 18 (heading 配色の構成). PDF pp. 10–30 pre-rendered to `notes/wada-pages/` for 1C.
- Albers text extracted with `pdftotext -layout` → `notes/_private/albers.txt` (≈180k chars).
- `notes/00-brief.md` written.

Fixed / rejected
- First fetch run produced empty sparse checkouts: Git Bash converted the leading-slash sparse
  paths into `C:/Program Files/Git/...`. Fixed by adding `export MSYS_NO_PATHCONV=1` to
  `notes/fetch-reference-skills.sh` (the original in `Code References/` is unchanged) and
  re-fetching.
- Decision: plan's `data/raw/` moved to repo-level `data-raw/` so raw snapshots never ship
  inside the skill; `data/SNAPSHOT.md` stays in the skill.

Gate: passed (4 folders with licences; rendered page opens).

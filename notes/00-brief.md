# 00 — Brief for every agent

## What the skill is

`artistic-color-palettes` is an Agent Skill (skills.sh / agentskills.io format, also shipped as a
Claude Code plugin marketplace) that helps users choose artistic colour palettes and apply them to
real UI. Its palette families are Sanzo Wada's *A Dictionary of Color Combinations* (1933–34; 348
plates, data from colorcombinations.org), Heian *kasane no irome* layered colour patterns, palettes
sampled from public-domain paintings (colorcombinations.org), and the perceptual principles of Josef
Albers' *Interaction of Color*. It turns a chosen palette into OKLCH ramps, two-tier design tokens,
proportion rules, measured contrast (WCAG 2 and APCA) and a composed (never inverted) dark mode, and
hands the result to neighbour design skills (Impeccable, Taste, Design Principles, UI/UX Pro Max,
Theme Factory) through a shared file. It does not do typography, layout, spacing, motion or copy.
Bundled scripts are Python 3.10+ standard library only and must run on Windows paths. It never
invents a plate number, painting or palette; if the data has no match it says so.

## Paths

- Repo root: `D:\Code\Skill\artistic-color-palettes\` (git repo; do not commit — the orchestrator does)
- Skill root: `D:\Code\Skill\artistic-color-palettes\skills\artistic-color-palettes\`
- Raw downloads and intermediate data (not shipped): `D:\Code\Skill\artistic-color-palettes\data-raw\`
- Agent hand-off notes: `D:\Code\Skill\artistic-color-palettes\notes\`
- Copyrighted working material, git-ignored, never copied into the skill:
  `notes\_private\` (e.g. `albers.txt`), `notes\wada-pages\` (page renders)
- Source books and notes: `D:\Code\Skill\Art References\` (read only; do not modify that folder or
  anything else under `D:\Code\Skill` outside the repo)
- Reference skills at pinned commits: `notes\reference-skills\{better-colors,ui-ux-pro-max,theme-factory,impeccable}\`

## Tooling notes

- Python 3.14 on PATH; no colour libraries. `pypdfium2` and Pillow are in the *user* site-packages,
  so run Python **without** `-I` for anything that imports them.
- Render a page of the Wada scan (356 pages, image-only):
  `python <script>` using `pypdfium2.PdfDocument(path)[page_index].render(scale=3.2).to_pil().save(...)`.
  PDF page numbers differ from printed page numbers (PDF p. 20 = printed p. 18); always cite both.
- `pdftotext` is available in Git Bash; `pdftoppm` is not.
- In Git Bash, set `MSYS_NO_PATHCONV=1` before passing arguments that start with `/` to git.

## Model and effort rules (from PLAN.md §1)

- Haiku, low: mechanical work with a checkable result (downloads, counts, file moves).
- Sonnet, medium: transcription, data engineering, scripted checks, eval runs.
- Sonnet, high: code that has to be correct first time (OKLCH maths, validator).
- Opus, high: reading Japanese scans, distilling art theory, writing SKILL.md, reviews.
- Opus, xhigh: the one creative synthesis step (style recipes).

## Copyright line (applies to every agent that touches a book)

Paraphrase only, in our own words. No quotation from either book (Wada's *配色事典* /
*A Dictionary of Color Combinations*, or Albers' *Interaction of Color*) longer than 15 words, and
keep even short quotes rare and attributed. Do not reproduce plates, diagrams, exercise layouts or
figure descriptions; do not transcribe page text. Ideas, rules and numbers restated in our words are
fine, with page or chapter citations. Third-party skill text and code: restate in our words; copy
code only where it saves real effort, and record file, pinned commit and licence for every copied
block so it can go in `NOTICE.md`.

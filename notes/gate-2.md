# Gate 2 — Synthesis and build (2026-10-22)

Agents: 2G on **Fable, xhigh** (PLAN: "Opus xhigh, Fable if available"), 2H on Sonnet high.

## Produced and accepted
- 2G: `references/application-rules.md` (≈ 240 lines), `references/style-recipes.md` (300),
  `references/interop.md` (≈ 170), `notes/2G-notes.md` (traceability table, objections),
  measurement scripts in `data-raw/2G/`. Three worked examples on real data with measured numbers:
  Wada 218 (Operate/Restrained dashboard), Wada 247 with Impeccable loaded (Persuade/Drenched
  landing, full DESIGN.md region), Vermeer *The Milkmaid* (Read/Restrained + coverage).
- 2H: `data/palettes.csv` (436 rows = 348 wada_plate / 30 editorial / 25 painting / 33 kasane),
  `data/colors.csv` (210, 159 with the printed Wada CMYK index merged), `data/paintings.json`,
  scripts `colorlib, build_data, search, build_tokens, validate, preview, handoff`,
  `assets/palette-handoff.template.md`, `NOTICE.md`, `scripts/tests/` (103 tests).

## Orchestrator checks
- `python -m unittest discover -s scripts/tests`: **103 tests OK** (≈ 14 s).
- `search.py --id wada-400` and `search.py "vol 2 plate"`: refuse, exit 2, nothing substituted.
- `handoff.py` run twice on a project with a neighbour DESIGN.md (Overview / Colors /
  Typography): byte-identical; neighbour text outside markers preserved. Re-checked after the
  2H follow-up on wada-218: identical; pinned Helvetia Blue `#005b8d` present in tokens.css.
- `preview.py` with 4 candidates (wada-218, wada-247, The Milkmaid, kasane fuji) opened in the
  browser pane: provenance, swatches with OKLCH, proportion bar, light / composed dark / greyscale
  mini-layouts render correctly.
- Quote scan over all six references: clean.

## Decisions (amendments v2, `2-shared-constants.md` §7)
Accepted from 2G: `--color-border-strong`; dark links accent-200 and muted neutral-200; hover
polarity by measurement; vanishing flag scoped to region fills; role may take the pinned step;
2G's status seeds. Rejected: normalising chroma by the pin step (makes pale seeds more vivid).
From 2H: default `--pin all` so voice/brand/drench solids are the exact plate colour (first run
showed Deep Lyons Blue `#1c4286` replaced by a generated `#3169CE`); status step offsets
(warning 400/300, success 700/600, danger 600/400, info 500/500).

## Fixed by the orchestrator in existing files
- Albers 7 (interval rule exempts text/bg), Albers 9 (points to strategy table, accent ≤ 8%),
  Albers 13 (WCAG gate, APCA target).
- Kasane: dark-surface chroma cap in step 6; shade vs ramp note; example page background labelled
  as Persuade/Drenched with the reading-surface alternative.
- `interop.md` precedence gains rank 5 (neighbour-generated colours).
- Drift-flagged paintings: **6**, not 7 (data count; the source note's prose was wrong).

## Known issues carried forward (for 4L)
- style-recipes examples (a) and (c) describe dark muted/link text starting from the old 300
  steps before adjustment; coherent, but predates amendment 2.
- Light warning at step 400 fails 3:1 on the page and is lifted toward L 0.55 by `--fix`, partly
  undoing the status lightness cue; collisions are reported, not hidden.
- `pair_groups` (quad positions) is empty: CSV order ≠ plate position; style-recipes tells the
  agent to read pairs from the preview. Possible v0.2 data job.
- 2H could not delete its scratch files in the system temp folder (blocked); harmless.

Gate: **passed**.

# Gate 3 — SKILL.md and first evals (2026-10-22)

## Produced
- 3I (Opus high): `SKILL.md` (276 lines; description 985 chars, names all four sources;
  frontmatter `license`, `compatibility`), repo `README.md` (install for skills.sh and the Claude
  Code marketplace under `youssef4laa/artistic-color-palettes`, "Works with" table, licences,
  not-affiliated line). `quick_validate.py`: **Skill is valid!** One SKILL.md in the tree.
- 3J (Sonnet medium): 10 eval cases in `skills/artistic-color-palettes/evals/` (5 solo, 5
  combination; Design Principles tested in both variants as the user asked). Combination cases
  fetch neighbours at pinned SHAs in `place-files.sh`; no third-party files in the repo.
- Orchestrator: 49 assertions (graders/ + eval_metadata.json); iteration-1 runs, grading,
  benchmark, analyst notes, static viewer.

## Fixes made before the runs (from 3I's review)
- `handoff.py`: seed comment now after the frontmatter (a new DESIGN.md starts with `---`, so
  Impeccable's parser sees the colours); `--provenance` for `--hex` input; validator no longer
  prints "Lc 15 < 15". 106 tests pass.
- Docs aligned with scripts: frontmatter keys are role names with hex (`--key-prefix` on
  clash); `source_type` names; C ≤ 0.04 for text-bearing surfaces, Drenched as the exception.

## Iteration 1 (Sonnet 5.5, medium; 20 runs; baseline for combos = neighbours only)
| | With skill | Without | Delta |
|---|---|---|---|
| Pass rate | 98% ± 6% | 72% ± 23% | +0.26 |
| Time | 64 s | 68 s | −4 s |
| Tokens | 87.5k | 71.0k | +16.5k |

Per case (with / without): dashboard 5/5 vs 2/5; kasane landing 7/7 vs 3/7; Milkmaid 6/6 vs
4/6; pinned plate 5/5 vs 5/5; no-match 5/5 vs 4/5; combo Impeccable 6/6 vs 4/6; combo Taste 4/4
vs 3/4; combo DP owl 4/5 vs 5/5; combo DP libreuiux 4/4 vs 2/4; combo all-neighbours hand-off
4/4 vs 4/4 (interop regression check: neighbours consume our files unchanged).

## Defects found (to fix in iteration 2 after the user's review) — `notes/3-iteration1-observations.md`
1. No flag for a required on-accent colour ("white button text") → `--on-accent light|dark|auto`.
2. No tinted/outline action style for principles like "no saturated colour behind text" →
   `--action-style solid|tinted|outline`, generated region must match.
3. A pinned accent that already passed was moved by the generator (kasane ki).
4. Voice colours used as region bands are lifted to 3:1 vs page (Cream Yellow became #94630E):
   split region fill (exact plate colour) from mark (gated).
5. Full-palette Proportion Named Rule prints a stray range ("tertiary 5-15% 20-45%").
6. Runs record the CLAUDE.md pointer as `declined` when nobody was asked → leave unset, ask in
   the final message.
7. Optional `--text-min` for principles that ask for more than 4.5:1.
8. Weak assertions (graders' feedback): tighten dashboard, no-match, kasane, Milkmaid, pinned
   plate (add dark mode, plate colour stays visible).

## Not done yet
- User review of the viewer (`artistic-color-palettes-workspace/iteration-1/review.html`).
- Iteration 2, the Opus confirmation iteration, Phase 4 (red-team 4L, description optimiser 4K
  with the user's review of trigger queries, packaging 4M incl. pushing to GitHub — user actions).

Gate: **iteration 1 ready for user review.**

# Gate 3b — Iteration 2 (2026-10-23)

User instruction: skip the iteration-1 review, apply the iteration-2 fixes from `gate-3.md`, run
iteration 2. No `feedback.json` was produced for iteration 1.

## Fixes applied before the runs
- 2H (scripts; 121 tests pass, `quick_validate` passes, hand-off still byte-identical on re-run):
  `--on-accent light|dark|auto`, `--action-style solid|tinted|outline` (+ `--color-action*`
  tokens, region text matches the style), `--text-min N`, pinned colours never moved when they
  pass (role moves or gets an adjusted copy instead), voice split into exact region fill
  `--color-voice-n` + gated `--color-voice-n-mark`, proportion Named Rule rendering fixed for all
  four strategies, `handoff.claude_md: "not_asked"` when the flag is omitted.
- SKILL.md (orchestrator): when to use the new flags, voice region vs mark, unasked ≠ declined.
- Assertions tightened (49 → 56) where graders flagged them: dashboard (computed risk per
  candidate), no-match (absence stated; real-source next step), kasane (layer order + proportion),
  Milkmaid (sampled hex in tokens; dark-mode glare), pinned plate (+ dark theme, plate colour
  visible), DP owl (+ hover/dark chroma), Impeccable (plate hex in frontmatter; coherent ranges).

## Results (Sonnet 5.5 medium; baseline = no skill / neighbours only)
| | With skill | Without | Delta |
|---|---|---|---|
| Pass rate | 99% ± 4% | 62% ± 23% | +0.37 (iteration 1: +0.26) |
| Time | 68 s | 81 s | −13 s |
| Tokens | 86.3k | 67.3k | +19.0k |

Per case (with / without): dashboard 5/5 vs 1/5; kasane 6/7 vs 3/7; Milkmaid 7/7 vs 5/7;
pinned plate 7/7 vs 5/7; no-match 5/5 vs 2/5; Impeccable 7/7 vs 3/7; Taste 4/4 vs 3/4; DP owl
6/6 vs 5/6 (was 4/5 with skill); DP libreuiux 4/4 vs 2/4; all-neighbours hand-off 4/4 vs 4/4
(interop regression check).

Verified fixes in the outputs: plate 122 Cream Yellow #FDBF68 and Benzol Green stay exact as
bands; kasane ki #F3C13A kept; tinted action style keeps label backgrounds at C ≤ 0.04; runs ask
about the pointer instead of recording "declined" — except one (below).

## Open defects found in iteration 2
1. kasane with_skill wrote the CLAUDE.md/AGENTS.md pointer without a yes ("on the assumption
   that you want it"). SKILL.md tightened after the run; `handoff.py` should refuse
   `--claude-md yes` without an explicit `--user-confirmed` flag (not yet done).
2. Kasane patterns whose hitoe equals a layer (Kurenai momiji: hitoe = layer 5 = kurenai): the run
   mislabelled ki as the hitoe accent. Needs a recipe rule + build_tokens kasane mapping note.
3. Two assertions remain easy for the baseline (libreuiux 3–4; DP owl 1–5 except dark mode).

## Not done
- Opus confirmation iteration (PLAN §2 Phase 3), Phase 4 (4L red-team, 4K description
  optimisation with the user's review of trigger queries, 4M packaging; push to GitHub is a user
  action). Nothing committed.

Viewer: `skills/artistic-color-palettes-workspace/iteration-2/review.html` (with iteration-1 as
previous outputs).

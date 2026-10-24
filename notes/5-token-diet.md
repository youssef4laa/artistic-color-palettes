# 5 — Token diet (v0.1.1, 2026-10-23)

Approximate tokens = UTF-8 characters / 4. 'Before' is the v0.1.0 tree snapshotted at
`skills/artistic-color-palettes-workspace/skill-snapshot/`; 'after' is the shipped tree.

## Files an agent reads

| File | Before | After | Note |
|---|---|---|---|
| SKILL.md | 5571 | 4142 | duplicated sections removed; one 'which reference to read' list |
| references/style-recipes.md | 5246 | 2320 | worked examples moved to worked-examples.md |
| references/worked-examples.md | - | 3063 | new; read only when building tokens the first time |
| references/kasane-no-irome.md | 5193 | 3587 | 33 pattern blocks replaced by an index table (hex via search.py --id); full source now data-raw/kasane-no-irome.md |
| references/wada-method.md | 3278 | 2474 | editorial framing condensed |
| references/application-rules.md | 4711 | 4595 | §11 removed; chroma profiles point at build_tokens.py |
| references/albers-principles.md | 4591 | 4978 | index by validator flag added (read one section) |
| references/interop.md | 3211 | 2967 | §1 one-liner, §7 removed |
| data/paintings.json | 10538 | - | moved to data-raw (only build_data.py reads it) |

Description: 985 chars before, 818 chars after (hand-written). The skill-creator description optimiser (`scripts.run_loop`, 24 queries in
`skills/artistic-color-palettes-workspace/trigger-eval/trigger-eval.json`) could not run on 2026-10-23: `claude -p` reported
"OAuth session expired and could not be refreshed" (log: `trigger-eval/run-5/run_loop.log`). Re-run after `claude login`.

Discovery read set (SKILL + recipes + wada + kasane): 19288 → 12523 tokens.
Build read set (SKILL + recipes + application-rules + interop): 18739 → 14024 tokens (plus worked-examples.md 3063 the first time).

## Script output on the common path (chars)

| Command | Before | After |
|---|---|---|
| `search.py "slate blue"` (5 results) | 2215 | 1578 (`--full` restores source, licence, score) |
| `validate.py tokens.json` (wada-218 restrained) | 3996 | 3171 (APCA shortfalls grouped by role family; flag advice printed once per type; `--all` unchanged) |
| `handoff.py --dry-run` on a new project | 11255 | 452 (summary; `--diff` prints the full text) |
| `search.py --json --limit 3` | 3763 | 2513 (compact JSON, every field kept) |

## Eval re-run (iteration-5, Sonnet, new skill vs the v0.1.0 snapshot, one run each)

Workspace: `skills/artistic-color-palettes-workspace/iteration-5/` (`review.html`, `benchmark.md`, `grade_it5.py`, `check_it5.py`).
Every assertion passed in both configurations (24/24 each), so the diet lost nothing the evals measure.

| Case | New skill tokens | Snapshot tokens | Change | References read (new / old) |
|---|---|---|---|---|
| dashboard-restrained-wada (discovery, waits for choice) | 88,792 | 100,846 | -12% | 3 / 3 |
| discovery-coffee-roastery (discovery, kasane + Wada) | 92,843 | 96,433 | -4% | 4 / 2 |
| combo-impeccable-landing (build + hand-off, Impeccable loaded) | 117,197 | 122,252 | -4% | 6 / 5 |
| landing-drenched-kasane-autumn (pinned kasane, full build) | 141,722 | 130,348 | +9% | 8 / 6 |
| mean | 110,138 | 112,470 | -2% | |

Reading: the docs are a minority of a run's tokens. Most of each run is the agent's own work (searches, previews it
hand-writes, re-runs), which the diet does not touch, so the -25% target for whole-run tokens was not met; the measured
savings are in what the agent reads (discovery read set 19.3k -> 13.1k tokens) and in script output. The kasane run went
up for three reasons visible in its trace: the agent took the new "which reference to read" list as a reading list and
opened all eight files (SKILL.md now says a run never needs all of them; not re-tested), both kasane runs collided in the
shared scratchpad and rebuilt their tokens, and the new run hand-wrote a landing mock and tried a browser check.

Previous with-skill runs of the same cases on Sonnet (iteration 2): dashboard 76.6k-114k, kasane 118k-177k, Impeccable
99.6k-159k; the spread between runs of one case is larger than the diet's effect, so the per-case numbers above are
indicative, not a measurement.

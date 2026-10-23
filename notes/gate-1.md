# Gate 1 — Extraction (2026-10-22)

All eight Phase 1 agents ran with the model/effort from PLAN.md §2 (1A Sonnet medium, 1B Sonnet
low, 1C Opus high, 1D Sonnet medium, 1E Opus high, 1F Sonnet medium, 1G Sonnet high, 1H Sonnet
medium).

## Produced and accepted

| ID | Output | Gate check |
|---|---|---|
| 1A | `notes/1A-reference-digest.md` (318 lines) | File:line citations at pinned commits. Recommends stdlib rewrites in our words, copying no code, so `NOTICE.md` needs no code entries. APCA is in none of the four repos: 2H writes it. |
| 1B | `data-raw/{palettes,colors,collections}.csv`, `data-raw/studies/*.csv` (2), `data-raw/paintings/*.json` (25), `skills/.../data/SNAPSHOT.md`, `notes/1B-snapshot-report.md` | Re-counted by orchestrator: 378 palettes (348 `wada-*`, 30 editorial), 210 colours, 71 collections, 25 paintings; plates 1–348 gap-free; `wada-` ⇔ era `showa`. Painting JSON has no URL endpoint: the page's Download JSON builds it from an inline payload holding only hex; 1B stored that verbatim plus roles/coverage parsed from page HTML. |
| 1C | `references/wada-method.md` (187 lines, 27 rules), `notes/1C-readings.md` | Read cold. Page-cited (printed + PDF), paraphrased, a "How the skill uses this" line per rule. 3 `[uncertain]` marks, each a stated interpretation (色度 = chroma; different-tone sub-types by analogy; cut-card placement), none a missing reading: accepted. |
| 1D | `data-raw/wada-index.csv` (159 rows, 21 with reading notes), `data-raw/1D/compare.py`, `notes/1D-hex-drift.md` | Site hex = mattdesl hex for all 159 (scan-sampled). Naive CMYK drifts > 0.05 ΔE_OK on 98/159; GCR-aware on 8/159. Ship website hex as the value; CMYK index is supporting data. Six site misspellings (Sulpher, Pomegranite, …) kept for search, with print spellings as aliases. |
| 1E | `references/albers-principles.md` (13 principles, ≤ 250 lines) | Read cold. Chapter-cited; one 7-word attributed quote. **Amended** by orchestrator: principle 10 said "evenly spaced L"; changed to follow the ramp table in `application-rules.md` (finer light-end steps, better-colors), so the two files cannot contradict. |
| 1F | `references/kasane-no-irome.md`, `data-raw/1F/check_kasane.py`, `notes/1F-changes.md` | Checker PASS. **Source has 33 patterns, not 35** (orchestrator confirmed: 33 `####` headings in the original). Dark mode rewritten as composed; shade chroma as share of the hue's in-gamut max. Listed shade hexes kept as published and labelled. Orchestrator fixed the stale "Sanzo Wada palette skill" line. |
| 1G | `data-raw/wada-proportions.csv`, `data-raw/1G/mine.py`, `notes/1G-report.md` | Clean measurement, **no information**: all 108 four-colour plates are four equal rectangles (shares 0.232–0.265, sd 0.005). Quads are on PDF pp. 152–259 (page = plate − 89). |
| 1H | `notes/1H-neighbour-skills.md`, neighbour clones in `notes/neighbour-skills/` (git-ignored), fetch script extended | Every path quoted with file:line. Contract accepted with amendments: `notes/1H-contract-accepted.md`. |

Copyright scan (`data-raw/gate_quotes.py`): no quote over 15 words, no `??`, in all three
reference files and the 1A digest.

## Rejected / not shipped
- 1G proportion data: kept in `data-raw/` only (PLAN §4.1 resolves itself: there is nothing to
  ship). The skill states only the fact that Wada's swatches are equal-area for convenience
  (1C §5.1) and that UI proportion targets are our own convention, labelled as such.
- 1H's "no hex in the DESIGN.md prose" rule: replaced (Impeccable's own template writes hex in
  prose; only a *different* value is forbidden).

## Corrections to PLAN.md facts (for downstream briefs)
- Kasane: 33 patterns, not 35 → 2H test expects `kasane` = 33.
- Painting data: roles/coverage come from page HTML, coverage as integers or "<1".
- Windows: Python's default console encoding is cp1252, so printing Japanese names crashes. All
  scripts must call `sys.stdout.reconfigure(encoding="utf-8")` (or equivalent) and open files with
  `encoding="utf-8"`.

## Open choices for the user (PLAN §4) — asked at this gate
- §4.4 CLAUDE.md pointer for neighbours without a file convention (triggered: Taste, both Design
  Principles candidates and Theme Factory read no shared file).
- Which "Design Principles" skill is meant (owl-listener vs libreuiux).
- §4.2 licence, including how to license the kasane file whose base hexes come from Wikipedia
  (CC BY-SA 4.0).
- §4.3 GitHub owner/repo (needed only in Phase 4).
Answers recorded below when given.

## Answers (user, 2026-10-22)
- §4.4: **opt-in pointer**. The skill asks once per project; on yes, writes the marker-delimited
  pointer (1H §7.6 text) into the project's `CLAUDE.md` and `AGENTS.md`; records
  `handoff.claude_md: true|false|declined` in `palette.json`; never touches `~/.claude/CLAUDE.md`.
- Design Principles: **test against both** owl-listener `design-principles` and libreuiux
  `design-principles` (two combination variants / neighbour sets).
- §4.2: **MIT** for our code and text; `references/kasane-no-irome.md` explicitly **CC BY-SA 4.0**
  with Wikipedia credit; NOTICE carries CC BY 4.0 (colorcombinations.org), MIT (mattdesl) and
  Apache-2.0 attributions.
- §4.3: GitHub owner **youssef4laa** → `youssef4laa/artistic-color-palettes`.
- §4.1: resolved by data (1G): not shipped.

Gate: **passed**. Phase 2 (2G, 2H) starts.

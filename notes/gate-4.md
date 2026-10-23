# Gate 4 — Opus confirmation, review, packaging (2026-10-23)

## Fixes before this phase (2H; 130 tests pass)
- `handoff.py --claude-md yes` refuses (exit 4, nothing written) without `--user-confirmed`.
- Kasane: when the hitoe equals a layer colour that becomes the ground, the accent is the
  best-separating layer named by its own layer ("ki (layer 3)") and a `kasane_note` is recorded.
  SKILL.md and style-recipes §1.8 updated.

## Opus confirmation iteration (iteration 3; Opus 5.5 high; with skill only)
95.5% (47/49) vs iteration 2 on Sonnet 99%: the skill is not Sonnet-specific. Misses are strict
readings (no-match "not in my data, plates 1–348" vs "does not exist"; libreuiux names a sixth
real plate). No run wrote CLAUDE.md/AGENTS.md; all asked first. Kasane rule confirmed. Opus runs
≈ 4× slower and 1.6× tokens. Viewer: `skills/artistic-color-palettes-workspace/iteration-3/review.html`.

## 4L red-team (Opus high) — `notes/4L-review.md`: 1 blocker, 10 should-fix, 14 nits
- **B1 (blocker, reproduced by orchestrator):** `handoff.py --hex … --provenance "Wada plate 400 …"`
  writes the invented plate into DESIGN.md and tokens.css, exit 0.
- Before tagging (4L): **S1** missing kasane name returns other patterns with exit 0 (reproduced);
  **S5** a recorded pointer "no" reverts to `not_asked` on re-run; **S6** global-CLAUDE.md guard
  checks the home folder, not `~/.claude`.
- Other should-fix: S2 "japanese" query never surfaces a Wada plate (Showa not in era words) and
  leans to cream/red-black-gold editorials; S3 runs write hex outside our DESIGN.md markers; S4
  Taste: light surface = bg and our 2–8% accent vs Taste's < 5%; S7 recipe examples (a)/(c) stale;
  S8 new tokens/flags missing from application-rules/interop; S9 existing DESIGN.md palette kept
  beside ours without warning; S10 mattdesl MIT notice missing, generated kasane CSS licence line.
- Passes: copyright (no quotes > 15 words), attribution, no network, stdlib only, Windows paths
  with spaces, one SKILL.md, reference links, idempotent hand-off, 130 tests.
- Verdict: **don't ship v0.1.0 until B1 is fixed**; land S1, S5, S6 before tagging.

## 4M packaging — `notes/4M-packaging.md`
`.claude-plugin/plugin.json` + `marketplace.json` (schema from code.claude.com plugin docs),
version 0.1.0 in both and in SKILL.md `metadata.version`; `dist/artistic-color-palettes.skill`
(194,565 bytes, 31 files, evals and __pycache__ excluded); `npx skills-ref validate` valid;
`claude plugin validate .` passed; local install tests passed for both channels with an isolated
`CLAUDE_CONFIG_DIR` and a scratch project (user's `~/.claude` untouched). README has both install
channels and a publishing checklist. Repo installs also ship `evals/` (277 KB); the `.skill`
archive excludes it.

## Orchestrator catch
1G had written Wada scan debug renders into `data-raw/notes/wada-pages/1G/`; now git-ignored
(`**/wada-pages/`, `data-raw/**/*.png|jpg`). No image file remains for git to track.

## Red-team fixes landed (2026-10-23, user instruction: fix B1, S1, S5, S6)
- B1: `--provenance` naming a data source (Wada plate, plate N, editorial palette, sampled from,
  kasane no irome, kasane:, colorcombinations.org) refused, exit 2, nothing written — also for a
  forged label inside a `--tokens` file; honest labels pass. SKILL.md §Provenance states the rule.
- S1: `search.py` lists unknown words always; an absent kasane/title name exits 2 with no rows
  ("yanagi-gasane", "Kōri-gasane"); real names still resolve.
- S5: a stored pointer "no"/"declined" persists across re-runs; only a missing value is `not_asked`.
- S6: `handoff.py` exits 4, writing nothing, for the home folder, its ancestors, or anything in
  `~/.claude`, `~/.codex`, `~/.agents`.
- Orchestrator re-ran every repro: B1 exit 2 / 0 files; honest label exit 0; S1 exit 2; S5 stays
  False; S6 exit 4. Suite: 144 tests OK, 1 skipped (symlink creation unavailable on this machine).
- Repackaged: `dist/artistic-color-palettes.skill` 199,040 bytes, 32 files, no evals/__pycache__;
  `quick_validate` valid, `skills-ref validate` valid, `claude plugin validate .` passed;
  version 0.1.0 unchanged in plugin.json, marketplace.json, SKILL.md.
- Remaining should-fix (not requested at that point): S2, S3, S4, S7, S8, S9, S10 and 14 nits.

## Remaining should-fix landed (2026-10-23, user instruction: fix S2, S3, S4, S7, S8, S9, S10)
- Scripts (2H): S2 Japan queries include `showa` and always surface the best Wada plate and kasane,
  max one cream/kinari/gofun-ground candidate unless calm is asked; S3 `handoff.py --notes FILE`
  renders `#### Usage notes` inside our region (remembered; `--no-notes` drops it); S4 Taste alias
  `--surface: var(--color-bg-subtle)` + "stricter numbers win" neighbour-map line; S9 existing
  palette in DESIGN.md → exit 3 with "existing palette found: choose replace or refine", nothing
  written until `--yes`; S10 kasane outputs carry a courtesy credit, not a "Licence:" line.
- Docs: S7 style-recipes examples (a), (c) regenerated from the scripts, (b) uses real role keys
  with hex; new `scripts/tests/test_docs.py` checks every quoted hex, step pairing and ratio
  against a fresh build. S8 role table + flags in application-rules §2; interop §5 pointer
  values. S2 recipes §1.6 refusals (red+black+gold lacquer default; ≤ 1 cream ground). S3 SKILL.md
  step 8 "write nothing outside our markers" + `--notes`. S4 interop Taste wording. S10 NOTICE.md
  carries mattdesl's copyright line and MIT text from upstream LICENSE.md; kasane CC BY-SA scoped
  to the reference file and data rows.
- Orchestrator checks: 159 tests OK (1 skipped: symlinks unavailable); quote scan clean on all
  references; each reference linked once from SKILL.md (kasane also named in `license:`); SKILL.md
  304 lines; fabrication still refused; S9 repro warns and writes nothing; no image files left for git.
- Residual: for "japanese restaurant" two red-black-gold editorials still rank 2nd and 3rd (a Wada
  plate and a kasane are now in the top 5); the recipes tell the agent to refuse that default.
- Repackaged: `dist/artistic-color-palettes.skill` 207,461 bytes, 34 files, no evals/__pycache__;
  quick_validate, skills-ref validate and `claude plugin validate .` pass; version 0.1.0.

## Open
- 4K description tuning waits for the user's export of `trigger-eval/eval_review.html`
  (24 queries: 11 should-trigger, 13 should-not incl. 4 neighbour-competition queries).
- Fix B1, S1, S5, S6 (and ideally S2, S3, S7–S10) before tagging v0.1.0.
- v0.2 list in `notes/3-iteration1-observations.md` (`--nontext-min`, voice-as-mark, painting
  colour names, season claims, quad pair positions).
- Nothing committed, tagged or pushed.

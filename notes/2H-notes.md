# 2H notes (data + scripts engineer)

Skill root: `skills/artistic-color-palettes/`. Python stdlib only, UTF-8 forced on stdout/stderr, `pathlib`, no network.
Nothing committed.

## Test result (this machine, Windows 11, Python 3.14)

```
python -m unittest discover -s scripts/tests      (from the skill root)
Ran 103 tests in ~14s (98 + 5 gate-decision tests; the count was 98 before the gate decisions below)
OK
```
Covers: row counts 348/30/25/33 (+436 total), valid hex everywhere, plates 1-348 gap-free and no Vol. 2, painting 3 ground + 3 accent,
exact provenance labels, shared test vectors (APCA, WCAG, OKLCH), ramp L = table (+-0.006) and dL >= 0.03, dark ramp not the light reversed,
chroma profile, pin, role map, strategies/proportions, search behaviour (earthy three colours returns a Wada plate; "wada plate 400",
Vol. 2 and unknown ids give a message and non-zero exit; zero results pad nothing; Hokusai first), validator (known failing pair, `--fix`
report names exactly what moved, lightness only), handoff (create, idempotent byte-for-byte, markers only, CRLF, key clash, damaged markers,
neighbour files untouched, pointer only with `--claude-md yes`, home directory refused, spaces + Japanese in paths), preview (self-contained
HTML, 3 candidates x light/dark/grey), `--help` on every script, amendments v2.

## What exists

| File | Notes |
|---|---|
| `scripts/colorlib.py` | colour maths, hex, gamut/`max_chroma`, WCAG, APCA, CVD, composite, data-loading helpers; `--self-test` |
| `scripts/build_data.py` | raw -> `data/palettes.csv` (436 rows), `colors.csv` (210), `paintings.json` (25); updates `SNAPSHOT.md` between `build_data` markers; rebuild is byte-identical (tested) |
| `scripts/search.py` | BM25-lite k1 1.5 b 0.75; exit 0 results / 1 no match / 2 not in data |
| `scripts/build_tokens.py` | ramps, roles, voices, status, proportions -> JSON `acp-tokens/1` |
| `scripts/validate.py` | gate, APCA, flags, ramp checks, `--fix`, `--adjacency`, `--out/--in-place/--json` |
| `scripts/preview.py` | 3-5 candidates (`--any-count` overrides), light/dark/greyscale, no network |
| `scripts/handoff.py` | DESIGN.md (markers only), `design/palette.json`, `design/tokens.css`, opt-in CLAUDE.md/AGENTS.md pointer |
| `assets/palette-handoff.template.md` | fixed shape of the `## Colors` region, rendered by handoff.py |
| `NOTICE.md` | attribution block, kasane CC BY-SA, ideas-only list; states no third-party code is copied |

Typical pipeline: `build_tokens.py --palette wada-229 | validate.py - --fix --json > t.json` then `handoff.py --tokens t.json --project-dir .`
(or `handoff.py --palette wada-229 --strategy restrained`, which builds and fixes by itself).

## Decisions and derived columns

- **tone_family**: chromatic colours = OKLCH C >= 0.04. Arc = 360 deg minus the largest gap between neighbouring hues. `same` when the
  arc <= 70 deg (`TONE_SPREAD_DEG`), else `different`; fewer than two chromatic colours -> `same`. Distribution over the 348 plates has no
  natural valley (spreads are spread evenly), so 70 deg is the skill's own cut: about two neighbouring 30-deg hue families. 134 same / 302 different overall.
- **count** = distinct colours (kasane stacks repeat colours: Futatsu-iro has 7 entries, 4 distinct). `colors`/`roles` keep the full ordered stack.
- **hue** for paintings and kasane = bucket with the largest summed OKLCH chroma (`dominant_hue`); Wada/editorial keep the site's value.
- **era** is empty for paintings (the export's "edo" is meaningless, per 1B); kasane era = heian; `season` = the heading of the section in the kasane file.
- **Painting drift flags: 6, not 7.** The table in `colorcombinations-data.md` marks 6 (Sunflowers, La Grande Jatte, Great Wave, The Kiss,
  The Scream, Girl with a Pearl Earring) and I fetched all 25 live pages (2026-10-22): exactly those 6 carry the "Has the colour changed?" panel.
  The prose "7 of the 25" (and shared constants section 6) is therefore not supported by the data; I flagged 6 and invented no 7th. Drift note is a separate
  `drift` column + `drift_note` in JSON; the label stays the plain "Sampled from ..." line.
- **colors.csv** keeps 210 rows (all 159 printed index entries match a site colour: 147 exact, 8 spelling, 4 duplicate-name by number); `aliases` holds the print
  spelling (Sulphur Yellow, Ocher Red, Pomegranate Purple, Kronbergs->Kronbergs, Artemisia, Vernonia, Eugenia Red, Grayish Lavender). search.py expands them.
- **Search extras** (own choices): `earthy` has no Wada plate with that mood in the data (only editorial rows carry it), so "earthy" soft-expands to earth-tone words
  at half weight, and when no source filter is active and limit >= 3 the best-scoring Wada plate is guaranteed a slot ("Wada first-class"). Natural-language count
  words ("three colours") become a hard `--count`; words wada/painting/kasane/editorial become a source filter; calm/quiet -> serene.
- **pair_groups** (amendment 8): column exists, always empty. `wada-proportions.csv` / `1G/diagnostics.csv` hold area shares per colour in website order and no positions
  (`color_index` is the website order), so which colours face each other on a four-colour plate cannot be derived without rendering; not done.
- **Chroma floor for palette-sourced status colours** `STATUS_MIN_CHROMA = 0.09` is mine (application-rules.md prints windows and seeds, not a floor).

## Amendments v2 implemented (build_tokens.py / validate.py / tests/test_amendments.py)

1. `--color-border-strong` = neutral-500 in both modes; the 3.0 gate applies to it only (border/border-subtle are ungated dividers, APCA 15 reported).
2. Dark `accent-text` = accent-200, dark `text-muted` = neutral-200 (also in the drenched dark/light-text branches).
3. Hover polarity: `accent-hover` = adjacent step in the direction that raises contrast with `on-accent` (light label -> darker step, in both modes). `surface-hover`
   follows the same rule vs `text` only when a distinct step exists; with the default neutrals the contrast-increasing step coincides with the page colour or runs off the ramp,
   so the table default stays and a note says so.
4. Vanishing: only declared pairs (`default_adjacency`: bg/surface, surface/accent-subtle, voice pairs, accent/voice chart series; `--adjacency a:b,...` overrides).
   State siblings (accent/accent-hover, surface/surface-hover) need dL >= 0.06 else a `state_sibling` flag requiring a non-colour cue. Note: light-mode bg and surface are the same
   value by the role table, so bg/surface is always flagged as vanishing (true to the table; the separation is the border).
5. Pinned seed step is used for `accent`, `accent-text` and `focus` only when within one step of that role's default and the role's gate passes; otherwise defaults stay and
   the report (`notes`) lists the roles the seed was not used for. A pinned fill that fails moves to another step (never L-changed; `--fix` also moves the step, not the L).
6. Status colours per application-rules section 2: windows success 135-165, warning 65-95, danger 15-40, info 230-270; seeds as printed; member must be >= 15 deg from the accent;
   a default within 15 deg of the accent is re-seeded 16 deg away (`default-reseeded`, `non_colour_cue_needed`, note in the report); danger never green-dominant.
7. Chroma profile left anchored at 600.
8. Amendment 8 (Albers 7 +-0.05 tolerance): not requested in the message, not implemented.

## Objections / observations on the shared constants (numbers kept)

- With the fixed L tables every light fill is L 0.54 and every dark fill L 0.51, so equal-lightness hues are the rule: the validator reports many
  `vibrating`/`cvd` flags for accent vs status fills (red/green/amber differ only in hue under deutan/protan). That is true to Albers 12 but noisy; a per-status step
  offset (e.g. danger 700, warning 400) would give a lightness cue for free. Needs an orchestrator decision.
- Dark mode APCA targets are missed on many pairs (muted/accent text about Lc 50 against 60-75; fills against the page about Lc 22 against 30) because the dark L table tops out
  at 0.96/0.71/0.51. The WCAG gate passes everywhere; the report lists APCA shortfalls and `--fix` only nudges text roles within 0.04 L.
- Dark `border-strong` = neutral-500 (L 0.51) on neutral-900 surface sits at about 3.0:1; `--fix` lifts it by a few thousandths when needed.
- Drenched strategy: the dark-ramp chroma cap (0.045 on 800/900/950) makes the dark drenched surface nearly neutral; a mid-lightness drench colour forces text and fills to
  extreme steps in light mode (many `--fix` adjustments). Surfaces/text/fill polarity for Drenched is my own construction (`_drench_light`).
- Kasane `hitoe` accents that are dark (e.g. koki murasaki, L 0.26) give vivid mid-tone ramps because chroma is a share of the *seed's* gamut ceiling (at L 0.26 the ceiling is small, share high).
  Per spec; noted for the style recipes.
- Impeccable merge: when DESIGN.md already has its own `### Primary/### Named Rules` under `## Colors`, our region repeats those h3 headings inside the markers (spec-mandated shape).
- The prose in `1H` said markers "no hex in prose"; amendment 1 changed that and the region follows amendment 1 (hex identical to the frontmatter).

## Design choices worth knowing

- Frontmatter holds light values only (`bg`, `text`, `accent`, voices, statuses, ...), uppercase hex in double quotes; dark values live in the body table and `tokens.css`.
  Key collisions with an existing `colors:` map abort with exit 2 (`--key-prefix` fixes). Inline/flow `colors: {...}` is left alone (body region still lands).
- `handoff.py` re-validates with `--fix` when the tokens JSON has no contrast block, refuses to write when the gate still fails (`--allow-failing` overrides, exit 1).
- Companion files are always written; DESIGN.md insertion without markers needs `--yes` (exit 3 prints the diff). `--dry-run` writes nothing.
- CSS: semantic dark values are written three times (media query, `[data-theme="dark"]`, and the light default scope re-declared for `[data-theme="light"]`); aliases sit on `:root, [data-theme]`.
  `--muted`/`--accent` are shared by Taste and interface-design; `--secondary` and `--muted` both map to muted text (only two text tiers exist).
- Pointer text is exactly 1H section 7.6; `--claude-md no` deletes CLAUDE.md/AGENTS.md only if they contained nothing but the pointer.
- Line endings: files are written as LF; an existing CRLF DESIGN.md/CLAUDE.md keeps CRLF (tested).
- Not done / limitations: no visual check of preview.html in a browser (the pane cannot screenshot local files); markup balance was checked with html.parser.
  Temp files from my scratch work remain in the system temp folder (deletion was blocked by a safety check).

## Gate decisions implemented (after the first report)

1. **Plate colours stay visible.** `--pin` now defaults to `all` (build_tokens, handoff; preview inherits it). Brand and voice solids are non-text fills, so
   `--color-voice-n` / `--color-brand` are the exact pinned seed value in each mode where the seed clears the 3:1 non-text gate against bg and surface (otherwise the default
   step is used and the report says the seed stays a primitive); `-text` and `-subtle` stay generated steps chosen by measurement. Accent: amendment 5 unchanged. Drenched surface =
   exact pinned colour. Palette-sourced status colours are pinned too and used when within one step of the status default. `tokens.css` also exports every palette colour as
   `--palette-<key>: #hex`. Check: wada-247 drenched, Deep Lyons Blue `#1c4286` is the light `--color-voice-1` (pinned at voice-1-800) and `--palette-deep-lyons-blue`.
2. **Status step offsets** (light: warning 400, success 700, danger 600, info 500; dark: warning 300, success 600, danger 400, info 500); on-colour by measurement.
   Observation: the 3:1 non-text gate for fills against the page lifts light warning 400 (L 0.72, about 2.3:1) back toward L 0.55 (validate `--fix` darkens it), so the lightness
   cue is partly undone for warning; danger/success/info keep theirs. Remaining accent-vs-status and status-vs-status collisions are still reported (cvd/vibrating flags), as asked.
   A status taken from a palette member that is also a voice (wada-247: Deep Lyons Blue is both voice-1 and info) is the same colour twice; left as specified.
3. **Drift: 6.** No script, data file or test says 7 (`test_drift_count_is_six_everywhere` greps for it; the earlier code comment that quoted "7" was reworded).
4. **Documented in `--help`/docstrings:** tone_family 70-degree arc (build_data docstring), Drenched polarity construction and pin/status rules (build_tokens `--help`),
   earthy soft-expansion with a guaranteed Wada slot and count/source word parsing (search `--help`).
5. Scratch files in the system temp folder left alone.

## Review fixes (3I)

1. New DESIGN.md now opens with `---` on line 1; the `<!-- acp:seed palette-only ... -->` comment is the first line after the closing `---` (test: created file starts with `---\n`).
   Insertion into existing files still tolerates a leading comment before the frontmatter.
2. `--provenance "<text>"` on build_tokens.py and handoff.py overrides the label (and credit) for `--hex` input; default unchanged; an error for palette ids.
3. validate.py never prints "Lc 15 < 15" or "4.5:1 < 4.5:1": failing values that round up to their threshold keep extra digits (`fmt_lc`, floor to 2-3 decimals).
Tests now 106 (3 added to `tests/test_amendments.py`, 1 fixture assertion changed in `test_handoff.py`). Frontmatter keys remain role names with hex values.

## Iteration-2 fixes (from 3-iteration1-observations.md)

1. `--on-accent light|dark|auto` (build_tokens, handoff). Forced polarity sets `--color-on-accent`; the accent fill moves to the nearest step passing text-min (light label: darker; dark label: lighter) and the move is in `notes`. `validate --fix` re-measures other labels but never flips a forced one (it moves the fill).
2. `--action-style solid|tinted|outline`. `--color-action`, `-action-hover`, `-on-action`, `-action-border` exist in every style (solid = aliases emitted as `var(--color-accent)` etc.; aliases are re-synced after `--fix`). tinted: fill = accent-subtle, border = accent (3:1 gated), on-accent/on-action = text colour; hover is a low-chroma literal (C <= 0.038, one clear lightness step). outline: transparent fill (`--color-action: transparent`), accent border, accent-text label. Validator pairs switch from on-accent/accent to on-action/action, action-hover, action-border. DESIGN.md gets an "Action Style Rule" and the Primary entries never say "the one solid action colour" unless solid.
3. Pinned colours: the accent fill takes the pinned plate colour whenever it passes the fill gate, wherever it sits on the ramp (this supersedes the one-step window for the fill only; accent-text and focus keep it). `--fix` never alters a ramp value; a failing role moves step, and only when no step passes (e.g. a forced white label in dark mode) it gets an L-adjusted copy and the pinned value stays in its ramp and in `--<ramp>-seed`. Regression: kasane-kurenai-momiji drenched/persuade keeps `#f3c13a` as the light accent.
4. Voice split: `voice-n` / `brand` are region fills = exact plate colour, not gated against the page; `on-voice-n` is measured and gated (text-min, then the large-text floor; advisory when no polarity reaches 3:1, per application-rules section 4); `voice-n-mark` / `brand-mark` = nearest step passing 3:1 against bg and surface. Statuses keep their fixed steps and the fill gate. Regression: wada-122 full-palette persuade keeps Cream Yellow `#FDBF68` (also in the frontmatter).
5. Proportion Named Rule renders "secondary 15-30%, tertiary 5-15%" for Full palette and a single band for the others (tested for all four strategies).
6. `--text-min N` (default 4.5): body and label gate; large-text floor = max(3, N/1.5) (my reading of "unless higher"); recorded in `tokens["policy"]`, `palette.json` and the Contrast Floor rule.
7. `handoff.claude_md` is `"not_asked"` when `--claude-md` was never given (previous answers are kept; `null` no longer written).
Tests: 121 (15 new in `tests/test_iteration2.py`; two fixtures updated for `not_asked`).

## Gate 3b fixes

1. `handoff.py --claude-md yes` now needs `--user-confirmed` (records that the user explicitly said yes in this conversation); without it: exit 4, clear error, nothing written (not even DESIGN.md or design/). `no` and `declined` need nothing; `--user-confirmed` alone only prints a note.
2. Kasane: when the hitoe hex equals a layer colour (merged into one member) and the page (drench, brand or ground) uses it, no other colour is called hitoe; the edge accent is the layer with the largest dL from the page colour among those clearing 3:1 (`kasane_edge_accent`), renamed e.g. `ki (layer 3)`; JSON `kasane_note` ("hitoe equals layer 5; accent taken from layer 3", also in `palette.kasane_note`) and the DESIGN.md provenance line carry it. An explicit `--accent`/`--roles accent=` wins and suppresses it. Note: kasane-fuji also triggers it in Drenched (its hitoe shiro equals layers 1-2).
Tests: 130.

## Red-team fixes (4L-review B1, S1, S5, S6)

- B1: `--provenance` naming a data source (^wada plate | plate N | editorial palette | sampled from | kasane no irome | kasane: , or containing colorcombinations.org; case-insensitive) is refused by build_tokens.py and handoff.py with exit 2 and nothing written; a forged label inside a `--tokens` file is refused too.
- S1: search.py always lists unknown query words; a named kasane pattern not in the 33 (x-gasane, x no nioi, x no usuyo, macrons folded) or a quoted title without a match exits 2 with no rows.
- S5: a stored claude_md of false / "declined" is kept on re-runs; only a missing value becomes "not_asked".
- S6: handoff.py exits 4 (nothing written) when --project-dir is the home folder, an ancestor, or inside ~/.claude, ~/.codex, ~/.agents, and refuses a CLAUDE.md/AGENTS.md that resolves into them (tested with Path.home patched; the symlink test skips where symlinks are unavailable).
Tests: 144 (1 skipped on this machine: symlink creation).

## Red-team fixes S2, S3, S4, S9, S10

- S2: `showa` added to the Japan expansion; Japan-word queries (not paintings) spread results: best Wada plate and best kasane always in when any match, at most one cream/kinari/gofun-ground candidate (L >= 0.90, C <= 0.06, hue 60-100) unless the query asks calm/serene/quiet. Works with and without `--source-type`.
- S3: `handoff.py --notes FILE` renders `#### Usage notes` inside the `## Colors` region (headings flattened to bold lines), remembered in `palette.json` (`handoff.usage_notes`) so re-runs keep it; `--no-notes` drops it. Template gained `{{USAGE_NOTES}}`.
- S4: Taste alias `--surface: var(--color-bg-subtle)`; neighbour map line shows the bg-subtle hex and says "With Taste loaded the stricter numbers win: accent < 5%, ground <= 90%, separate surfaces by lightness, not lines."
- S9: inserting into a DESIGN.md without our markers now writes NOTHING before `--yes` (no palette.json, tokens.css or pointer files); exit 3 adds "existing palette found: choose replace or refine (SKILL.md step 1) before --yes" when non-acp colour keys or prose under `## Colors` exist.
- S10: kasane generated files carry the courtesy credit instead of a `Licence: CC-BY-SA` line (palette.json `licence` and `credit` hold the courtesy sentence); the data CSV licence column is unchanged.
Tests: 155 (1 skipped: symlink creation).

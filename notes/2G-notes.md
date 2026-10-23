# 2G notes — style synthesis (application-rules, style-recipes, interop)

Agent 2G (Opus, xhigh). Files written: `skills/artistic-color-palettes/references/application-rules.md`
(226 lines), `references/style-recipes.md` (300), `references/interop.md` (169); build-time scripts
`data-raw/2G/colour.py` (OKLab/OKLCH, Cmax search, ramps per shared constants, WCAG 2, APCA-W3
0.0.98G-4g; `python -I colour.py` reproduces all six test vectors), `data-raw/2G/examples.py` and
`extra.py` (every number quoted in the three worked examples; outputs in `examples-output.txt`,
`extra-output.txt`). Quote gate (`data-raw/gate_quotes.py`): no quote over 15 words in the three files.
Every hex cited in style-recipes.md was checked by script: 20 are plate / painting / kasane values
present verbatim in `data-raw/palettes.csv`, `data-raw/paintings/*.json` or `kasane-no-irome.md`;
the other 59 are generated tokens that appear in the measurement outputs. All ten cited plates and
the five cited paintings exist in the data. Plate 247's swatch positions were read from the scan
(PDF p. 158, rendered to the scratchpad only, not shipped).

## 1. Traceability: rule → source

Abbreviations: SC = `notes/2-shared-constants.md`; 1A = `notes/1A-reference-digest.md`; 1H =
`notes/1H-neighbour-skills.md`; 1Hacc = `notes/1H-contract-accepted.md`; WM = `references/wada-method.md`;
AP = `references/albers-principles.md`; KI = `references/kasane-no-irome.md`; CCD =
`Art References/colorcombinations-data.md`; IM = Impeccable reference files; G1 = `notes/gate-1.md`.

### application-rules.md

| Section / rule | Source |
|---|---|
| §1 ramp L tables, ΔL ≥ 0.03, ends never 0/1, light-end finer, dark-end wider | SC §1; 1A §1.2 (BC rules 1–6); AP 10 |
| §1 Cmax binary search, seed share, profile, dark × 0.85, dark-surface cap 0.045 | SC §2 |
| §1 neutral ramp n[step], tint, cap 0.03, one temperature | SC §2; 1A §1.5 (BC 0.005–0.02 band); AP 11 |
| §1 proportional vividness across hues | 1A §1.4 (BC multi-hue matching); KI "Shade wording" step 4 |
| §1 pinned seed kept, placed at nearest L, never darkened silently | SC §2; 1A §1.3 (BC brand placement) |
| §1 P3 as enhancement over sRGB | 1A §1.4 (BC color-formats) |
| §2 two tiers, `--color-*` prefix, one word per concept, `primary` reserved | 1A §1.7 (BC token grammar); 1Hacc "Companions" (`--color-*` for Impeccable's scan) |
| §2 role table | SC §4 verbatim |
| §2 voices, 15° same-colour rule, never sole signal | SC §4; 1A §1.11 (BC one colour one meaning) |
| §2 `--color-border-strong` addition | 2G measurement (neutral-300 on neutral-50 = 1.68:1 light / 1.64:1 dark); gate in SC §3 |
| §2 status hue windows and default seeds; ≥ 15° from accent; danger never green | SC §4 ("hue window … else neutral default set" — numbers are 2G's); 1A §1.5 (BC 15° rule), 1A §3.4 (Pro Max green-destructive check) |
| §2 browser surfaces themed | 1A §5.4 (IM craft-floor) |
| §3 WCAG gate values, APCA targets, adjustment procedure, test vectors | SC §3 verbatim; 1A §1.8 (BC thresholds), §8 conflicts 1 and 8 |
| §3 sits-on lists, measure the painted surface, both modes | AP 1; 1A §1.8 measurement rules |
| §3 both polarities by measurement | SC §3 text-bearing warning; 1A §8 conflict 9; AP 13 |
| §4 mid-lightness numbers | AP 13 (computed there); 1A §1.9 (BC L 0.75 cap); skills-reference §1 item 6 |
| §4 fill moves to 600/700, measure 600 | SC §2 pin rule; 2G measurements (Helvetia 600 4.65:1, Benzol 600 4.49:1) |
| §5 vibrating flag | SC §3; AP 12 |
| §5 vanishing flag, ΔL ≥ 0.10 or stroke; scope to region fills; siblings under Albers 3 | SC §3; AP 13; AP 3 (ΔL ≥ 0.06 + cue) — scoping is 2G's (see §2 objection 4) |
| §5 accent within 30° of surface → ΔL ≥ 0.25 | AP 3 |
| §6 composed dark mode steps | SC §1–§2 dark tables; AP 7; KI "How to apply" step 6; WM §4.3; 1A §1.10 and §8 conflict 2; IM colorize ("do not invert") |
| §6 switching mechanism | 1A §1.10 (BC) |
| §7 CVD simulation, non-colour cue, greyscale render | 1A §5.4 (IM colorize verify list); AP 2; AP 13 |
| §8 pinned colour: role may take the pin within one step | SC §2 (fill role moves) extended by 2G (see §2 observation 5) |
| §9 translucency | AP 5; 1A §1.8 (alpha measured as rendered); WM §4.2; IM colorize |
| §10 cultural meaning (red gains, white mourning, per-locale tokens) | 1A §1.11 (BC color-usage); skills-reference §1 item 8; 1A §8 conflict 12 |
| §11 report contents | 1Hacc amendment 3 (region contents) |

### style-recipes.md

| Section / rule | Source |
|---|---|
| §1.1 read first, pinned palette honoured, adjust only for contrast and say so | 1H §7.3; 1A §5.1 (IM "the brief wins"); skills-reference §4 item 6 |
| §1.2 modes, colour's job per mode, inferred from the surface | IM SKILL.md Modes; IM mode-operate/read/persuade; 1A §5.2; 1A §8 conflict 11 |
| §1.2 "grey + one accent is the category default" | IM mode-operate; 1A §8 conflict 5 |
| §1.3 four strategies, 30–60% descriptive not quota, scene sentence | IM new-work §4; IM colorize "Choose a strategy"; 1A §5.3, §8 conflict 6 |
| §1.4 duo/trio/quad ranges, same- vs different-tone, quad pairs | WM §1.1, §1.6, §3.5, §3.8 |
| §1.4 CSV order ≠ plate position | `notes/1G-report.md` ("hex_1..hex_4 order is not the position order") |
| §1.4 kasane layer roles, hitoe 5–10% | KI "Garment layers"; SC §5 modifier |
| §1.4 painting ground/accent proportions, Hokusai first | CCD "Collection 2", "Two notes for an eastern-palette skill" |
| §1.4 editorial labelled, never a Wada plate | CCD "Wada plates vs editorial palettes" |
| §1.5 filters then free text | CCD "Filters available", "How the skill should use this data" item 3; 1A §3.3 (Pro Max query contract) |
| §1.5 3–5 candidates as mini-layouts, wait for explicit choice | skills-reference §3 (Theme Factory flow, "never silently pick"); 1A §4.1; AP "Why the skill previews"; WM §1.7, §5.4 |
| §1.5 no match → say so, retry once, original composition shown for review | 1A §3.3 zero-result rule; 1A §4.3 (TF custom fallback); CCD item 4 |
| §1.6 cream/red-circle/cherry-blossom | skills-reference §4 item 8; 1A §5.5 |
| §1.6 Rising Sun rays, militarist emblems | IM SKILL.md "Loaded symbols"; 1A §5.5; §8 conflict 12 |
| §1.6 no Zen beige; plates mostly saturated | `data-raw/studies/sanzo-wada-color-analysis.csv` (red 46.8%, yellow 25%); IM new-work calibration ("cream is the smallest corner") |
| §1.6 no European painting as eastern | CCD "Two notes" |
| §1.6 generic AI looks | IM new-work calibration; 1A §5.5 |
| §1.7 provenance labels | SC §6 verbatim; CCD "How the skill should label them" |
| §1.7 no fabrication, Vol. 2 absent, 1–348 only, 25 / 33 / 30 | CCD "Not in this dataset"; WM §1.1; G1 (33 kasane); 1B counts in G1 |
| §1.8 role-mapping order and per-family rules | 1A §8 conflict 3; WM §5.3 (collar / robe / sash ladder); KI layer table; CCD ground/accent mapping |
| §1.9 proportion table and modifiers, labelled ours | SC §5 verbatim; WM §5.1–5.2; AP 9; G1 (1G: equal areas) |
| §1.10 order of build steps | skills-reference "How the pieces fit" workflow |
| Example (a) numbers | `data-raw/2G/examples-output.txt` (EXAMPLE (a)), `extra-output.txt` |
| Example (b) numbers, plate positions | `examples-output.txt` (EXAMPLE (b)), `extra-output.txt`; scan PDF p. 158 |
| Example (b) PRODUCT.md sections read, DESIGN.md timing, merge hazard | IM init.md template; 1H §1 "Overlaps" conflict window; 1Hacc "Impeccable merge hazard" |
| Example (b) DESIGN.md region shape | 1Hacc amendments 1–3; IM document.md `## Colors` template |
| Example (c) numbers | `examples-output.txt` (EXAMPLE (c)), `extra-output.txt` |

### interop.md

| Section / rule | Source |
|---|---|
| §1 owns / does not own, defer by name | `00-brief.md`; 1H §7.4 last sentence; IM command names |
| §2 Impeccable names verbatim; alias crosswalk | 1Hacc amendment 2; 1H §2 (Taste roles), §4 (Pro Max roles), §3c (interface-design `system-template.md:19-23`, `--faint` = border), §5 (Theme Factory bullets); 1A §8 conflict 7 |
| §3 files, markers, creation rule, existing-file rule, never touch list | 1Hacc "Accepted as proposed"; 1H §7.1–7.2 |
| §3 region contents fixed order; hex allowed, never different | 1Hacc amendments 1 and 3 |
| §3 read-before-write order | 1H §7.3 |
| §3 precedence; contrast fix the one override, reported | 1H §7.4; 1Hacc; task brief |
| §4 Impeccable automatic, timing, merge hazard, no sidecar write | 1H §1, §7.5; 1Hacc |
| §4 Taste flags, one accent, cream+terracotta ban, 70–90 / < 5 | 1H §2, §7.5; 1Hacc "Taste note"; Taste `references/colour.md` §3 and §9 (read directly) |
| §4 Design Principles owl (process) and libreuiux (60-30-10, wheel, config enums) | 1H §3a, §3b, §7.5; libreuiux `color-theory.md` 60-30-10 (read directly) |
| §4 Pro Max: MASTER.md with consent, never `--force`, pointer line, slug search | 1H §4, §7.5, §7.7; 1A §3.3 |
| §4 Theme Factory custom-theme bullets from palette.json | 1H §5, §7.5; 1A §4.2–4.3 |
| §4 interface-design | 1H §3c, §7.5 |
| §5 opt-in pointer text, ask once, `handoff.claude_md`, never global | G1 answer §4.4; 1H §7.6 (text verbatim) |
| §6 non-duplication (replace or refine, never a second palette silently) | task brief; 1H §7.3 (direction.json), §4 (Pro Max competitor) |
| §7 template sections by name | 1Hacc amendment 3 (contents list), extended with Flags / Switching mechanism / Pointer status |

## 2. Objections and observations on the shared constants (numbers kept as fixed)

1. **`--color-border` cannot carry meaning.** SC §4 border = neutral-300 measures 1.68:1 on
   neutral-50 (light) and neutral-700 on neutral-950 = 1.64:1 (dark), far below the SC §3 non-text
   gate of 3.0 for "borders that carry meaning". Not a contradiction if `--color-border` is
   structural, but the role map has no step for a meaning-bearing edge. 2G added
   `--color-border-strong` = neutral-500 (3.26:1 light, 3.36:1 dark; on a neutral-200 surface use
   neutral-600, 3.57:1). Proposed: adopt it into SC §4 so 2H emits it.
2. **Dark-mode links (accent-300) and muted text (neutral-300) miss the APCA target.** Across all
   three examples accent-300 on neutral-950 gives Lc −51 to −52 (WCAG 7.5–7.6:1), neutral-300 gives
   −51. The gate passes; the body target (75) and label target (60) do not. The adjustment
   procedure reaches them by raising L to about 0.84 (links) and 0.77 (muted). Proposed: either
   accept as "target missed, reported" or set dark links at accent-200 and dark muted at a value
   between 300 and 200. 2G documents the adjustment in every example and in application-rules §6.
3. **Dark accent-hover (accent-400) fails with light text.** In examples (a) and (c) the dark
   role-map hover step (accent-400, L 0.61) measures 3.3:1 with neutral-50 while the rest fill
   (accent-500) passes at 5.0–5.1:1. A hover that flips label polarity is unacceptable, so 2G
   moved hover to accent-600 (darker on hover) in both examples and documents the move.
   Proposed: SC §4 dark hover = accent-600, or state that hover polarity is measured separately.
4. **Vanishing flag triggers on designed siblings.** SC §3 "adjacent fills with ΔL < 0.10 and hue
   difference < 40°" fires on surface/surface-hover (ΔL 0.09 by table), rest/hover (0.08–0.09) and
   dark 950/900 (0.05). 2G scoped the flag in application-rules §5 to fills that must read as
   distinct regions and left state siblings to Albers 3 (ΔL ≥ 0.06 + non-colour cue). 2H's
   validator needs an adjacency list to apply the same scoping.
5. **Role may take the pinned step.** SC §2 says the fill role moves off a failing pinned step; 2G
   added the symmetric rule (application-rules §8.2): a role may take the pinned step when it is
   within one step of the default and passes the gate, so the real plate colour is actually seen
   (Vermeer blue pins at 700 = link step; Helvetia Blue pins at 700, so links and hover are the
   real colour). Proposed for SC §4.
6. **Profile anchored at 600, not at the seed's step.** A pale seed pinned at 300 (profile 0.60)
   yields a 600 step at share s × 1.00, i.e. visibly more vivid than the seed: Grayish Lavender A
   (`#b5b1d8`, C 0.055) produces voice-1-600 `#6e60b2` (C 0.125). It is inside gamut and
   consistent, but the voice "solid" is a different character from the plate chip. Observation
   only; an alternative is to normalise by `profile[pin_step]`.
7. **Albers 7's ±0.05 interval rule vs the two tables.** The light table spans 0.24–0.975 and the
   dark 0.16–0.96, so the text/bg interval necessarily widens from about 0.68 to 0.80. The ±0.05
   rule can hold for accent/surface and surface/surface pairs but not for text/bg. Proposed fix in
   albers-principles.md principle 7: exempt text/bg (or widen its tolerance to 0.15) and keep
   ±0.05 for the other pairs. 2G reports intervals rather than failing them.
8. **Status seeds are not in SC.** SC §4 says status comes from "a neutral default set" without
   values. 2G printed hue windows and OKLCH seeds in application-rules §2; 2H must hold the same
   numbers or the orchestrator must pick others. The default info hue (250°) collides with any blue
   accent (example (a): 7° apart), so the re-seeding rule matters in practice.
9. **Kasane hitoe 5–10% vs accent ≤ 8%.** SC §5 modifier allows a kasane edge accent up to 10%
   while the table caps accents at 8%. Harmless if read as "the kasane exception"; the file says so.

## 3. Contradictions found between existing reference files (not edited by 2G)

1. **albers-principles.md principle 9 vs shared §5.** Albers 9's rule gives one range (ground and
   neutrals 60–85%, supporting 10–30%, accent ≤ 10%, ≤ 5% when C ≥ 0.15) while SC §5 (printed in
   style-recipes §1.9) gives per-strategy tiers and caps accents at 8%. Proposed fix: Albers 9 rule
   text → "every role gets an area target from the strategy table in style-recipes.md; accent
   ≤ 8%, ≤ 5% when C ≥ 0.15; the lightest or most saturated colour gets the smallest area".
2. **kasane-no-irome.md example CSS vs Albers 4.** The example sets the page background to usuki
   kōbai `#FECBCD` (measured oklch(0.887 0.058 15.7)); Albers 4 says body-text surfaces stay at
   C ≤ 0.04. Contrast itself passes (ink `#640A25` on it 9.08:1, Lc +74.7; hitoe `#391336`
   11.09:1). Proposed fix: label the example as a Persuade / Drenched usage, or make `--kasane-bg`
   a neutral-50 tinted from kōbai's hue and move `#FECBCD` to a band or hero token.
3. **kasane-no-irome.md dark-mode step 6 vs shared §2 cap.** "Build the surfaces from the
   pattern's darkest layer" can put a surface above the dark-surface chroma cap (C ≤ 0.045):
   murasaki `#4F284B` C 0.078, koki suō `#640A25` C 0.121, koki ao `#114A26` C 0.085 all exceed it.
   application-rules §6.3 resolves it (the darkest layer becomes a band on a capped ground of the
   same hue). Proposed fix in the kasane file: add "unless its chroma exceeds the dark-surface
   cap, in which case it is a band on a deeper neutral of its hue".
4. **kasane-no-irome.md shade rule L range vs ramp ends.** The shade table keeps derived L between
   0.12 and 0.96; the ramp tables end at 0.16 / 0.24 (dark) and 0.975 (light). Shades are
   one-off derivations, not ramp steps, so no conflict in practice; a one-line note in the kasane
   file ("ramp steps follow application-rules.md") would remove the ambiguity.
5. **albers-principles.md principle 10 references "the ramp table in application-rules.md".**
   Now resolved: application-rules §1 prints it. No action.
6. **1A §8 conflict 10 (Radix numbering internally) vs SC §4 (Tailwind names, Radix alias).** SC
   wins; application-rules follows SC. No action beyond noting that 1A's recommendation was not
   adopted.
7. **wada-method §3.5 UI meanings vs mid-lightness rule.** "Bright different-tone → tags, category
   fills on light ground" is fine, but several such plates have members at L 0.50–0.70; the table
   does not say they need the trap check. Not a contradiction; style-recipes §1.8 adds it.

## 4. Data notes for 2H and the orchestrator

- **Quad positions are not in the CSV.** 1G confirmed `hex_1..hex_4` is site order, not plate
  position, so wada-method §1.6 (keep internal pairs together) cannot be applied from `palettes.csv`
  alone. For plate 247 the positions were read from the scan (top Raw Sienna, middle-left Benzol
  Green, middle-right Deep Lyons Blue, bottom Apricot Yellow; pairs sienna+apricot, benzol+lyons).
  1G's `mine.py` already matches each region to a hex by colour, so it can emit a `position`
  column (top / left / right / bottom) for all 108 quads at build time. Recommended: add
  `pair_a`/`pair_b` to the shipped quad rows; until then style-recipes tells the agent to read the
  plate preview before pairing.
- The Milkmaid JSON's `role` field marks `#0F1317` (8%) as a ground; it is the painting's dark
  mass and works as text only because its L is 0.184. The role-mapping rule in style-recipes §1.8
  ("darkest ground is text when dark enough") depends on that measurement, not on the role label.
- Painting coverage strings include "<1"; examples treat it as 0.5% for proportion maths and say
  "under 1%" in prose.
- All example tokens were generated with `pin=True` for palette colours and `pin=False` for status
  seeds, exactly as SC §2 describes; 2H's `build_tokens.py` should reproduce the hexes in
  `examples-output.txt` from the same seeds (a useful regression test: Helvetia Blue light 600
  `#0075b3`, Vermeer blue light 600 `#386fb9`, Lyons dark 900 `#0f1829`).

## 5. Open items passed to the orchestrator

1. Decide objections 1, 2, 3, 5 and 8 (role-map additions / changes) before 2H freezes constants.
2. Approve or amend the proposed edits to `albers-principles.md` (9, 7) and `kasane-no-irome.md`
   (example CSS, dark-mode step 6).
3. `assets/palette-handoff.template.md` (2H) should carry the section names listed in interop §7.

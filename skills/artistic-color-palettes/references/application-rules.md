# Application rules: ramps, roles, tokens, contrast, dark mode

How a chosen palette becomes a usable colour system. `L`, `C`, `h` are OKLCH lightness (0–1),
chroma and hue (degrees); `ΔL` is an absolute difference in L. The numbers in §1–§3 are the
skill's fixed constants (also held by `scripts/build_tokens.py` and `scripts/validate.py`); the
others are the skill's working conventions. Perceptual reasons live in `albers-principles.md`
(cited as "Albers N"); the palette families in `wada-method.md` and `kasane-no-irome.md`.
Nothing here is measured by eye: every value is computed and every contrast figure is measured.

## 1. Ramps in OKLCH

Each palette colour that plays a role seeds an eleven-step ramp. Steps are named Tailwind-style
(50 … 950); Radix 1–12 is a role alias (§2). Light mode and dark mode use two separately composed
tables: the dark one is not the light one mirrored (Albers 7, 10).

| Step | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Light ramp L | 0.975 | 0.935 | 0.885 | 0.810 | 0.720 | 0.630 | 0.540 | 0.460 | 0.380 | 0.300 | 0.240 |
| Dark ramp L | 0.960 | 0.900 | 0.810 | 0.710 | 0.610 | 0.510 | 0.420 | 0.340 | 0.270 | 0.210 | 0.160 |

- Light ramp: finer at the light end (0.04–0.05 apart), 0.075–0.09 mid-ramp, because surfaces,
  hovers and borders live there. Dark ramp: wider separation at the dark end (≥ 0.05), because
  dark surfaces collapse together more easily (Albers 10). Neither end reaches 0 or 1.
- Consecutive steps are at least ΔL 0.03 apart. Hue is constant across a ramp (= the seed's h).
- Chroma is a share of the gamut, never a copied number (several hues side by side look equally
  vivid only when they use the same *share*; yellow and cyan top out far lower than red or blue):
  - `Cmax(L, h)` = the largest chroma inside sRGB at that L and h (binary search, tolerance 1e-4).
  - Seed share `s = C_seed / Cmax(L_seed, h)`.
  - Step chroma `C_step = s × profile[step] × Cmax(L_step, h)`; the light profile rises from 0.15 at step 50
    to 1.00 at 600 and falls to 0.50 at 950 (exact values: the constants at the top of `scripts/build_tokens.py`),
    so chroma peaks mid-ramp and both ends are nearly neutral.
  - Surfaces that carry body text stay at C ≤ 0.04 in light mode (Albers 4); this is why the
    neutral ramp is capped at 0.03 and a vivid palette colour becomes a band, not the reading ground.
    The exception is a Drenched surface, where the colour *is* the ground by choice: short copy
    only, measured, and long reading moves to a calmer panel.
  - Dark ramp: same profile × 0.85; steps 950/900/800 (dark surfaces) are also capped at C ≤ 0.045,
    so saturated colour never sits behind text as a page ground in dark mode.
  - Neutral ramp: h = the hue of the palette colour chosen to tint it, C from a small per-step profile
    (0.006 at the ends to 0.020 mid-ramp; constants in `build_tokens.py`) times `tint` (default 1.0), hard
    cap C ≤ 0.03. One temperature, held across the whole ramp (Albers 11). Pure grey only on request.
- **Pinned seed.** The plate, pattern or painting colour is kept exactly, exported as
  `--<name>-seed`, and placed at the step whose table L is nearest its own L; that step holds the
  seed value unchanged and the other steps are generated around it (so one interval may be
  slightly uneven; that is the price of keeping the real colour). A pinned colour is never
  darkened or desaturated silently. If it fails the gate in the role its step would normally
  play, the role moves to another step and the report says so (§8).
- P3: generate against sRGB; a `@media (color-gamut: p3)` override may raise chroma later, never
  the base value.

## 2. Roles and two-tier tokens

Primitives name a value by ramp and step (`--accent-600`, `--neutral-100`, `--voice-1-300`) and
never appear in a component. Semantic tokens name a job, point at a primitive, and are the only
tier components use; theming (dark, high contrast, white label) repoints only the semantic tier.
Semantic names use the `--color-*` prefix so Impeccable's document scan finds them. One word per
concept: `text` (never ink, fg), `bg` (never background), `border` (never stroke), `accent`
(never primary, which is reserved for "most prominent of its group").

| Semantic token | Light | Dark | Radix alias |
|---|---|---|---|
| `--color-bg` (page) | neutral-50 | neutral-950 | 1 |
| `--color-bg-subtle` | neutral-100 | neutral-900 | 2 |
| `--color-surface` (cards, panels) | white-ish neutral-50 or palette ground | neutral-900 | 2–3 |
| `--color-surface-hover` | neutral-200 | neutral-800 | 4 |
| `--color-border-subtle` | neutral-200 | neutral-800 | 6 |
| `--color-border` (structural) | neutral-300 | neutral-700 | 7 |
| `--color-border-strong` (carries meaning) | neutral-500 | neutral-500 | 8 |
| `--color-text` | neutral-900 | neutral-50 | 12 |
| `--color-text-muted` | neutral-700 | neutral-200 | 11 |
| `--color-accent` (fill for the primary action) | accent-600 | accent-500 | 9 |
| `--color-accent-hover` | accent-700 ¹ | accent-600 ¹ | 10 |
| `--color-on-accent` | chosen by measurement (white or neutral-950) | chosen by measurement | — |
| `--color-accent-text` (links) | accent-700 | accent-200 | 11 |
| `--color-accent-subtle` | accent-100 | accent-900 | 3 |
| `--color-focus` | accent-500 | accent-400 | 8 |
| `--color-voice-n` (region fill) | the exact plate colour at its pinned step (600 if unpinned) | same in the dark ramp (500 if unpinned) | — |
| `--color-voice-n-mark` (marks, icons, edges) | nearest step of the voice ramp that reaches 3:1 on the page; equals the region when it already does | same rule on the dark page | — |
| `--color-on-voice-n` (label on the region) | chosen by measurement (neutral-950 or white) | chosen by measurement | — |
| `--color-action` | solid: alias of `--color-accent`; tinted: accent-subtle; outline: transparent | same | — |
| `--color-action-hover` | solid: alias of `--color-accent-hover`; tinted, outline: a low-chroma tint one step from the rest tint | same | — |
| `--color-on-action` | solid: alias of `--color-on-accent`; tinted: `--color-text`; outline: `--color-accent-text` | same | — |
| `--color-action-border` | alias of `--color-accent` (the accent edge on every style) | same | — |

¹ Hover is the step next to the rest fill in the direction that *increases* contrast with
`--color-on-accent` (light label → darker step, dark label → lighter step); the values shown
assume a light label. `--color-surface-hover` follows the same rule relative to `--color-text`.
A role may take the pinned seed's step instead of its default when that step is within one step
and passes the gate, so the real plate colour is seen (§8).

Remaining palette colours become `--color-voice-1..n`, `-subtle` (100 / 900) and `-text`
(700 / 300) for regions, categories, chart series and illustration. A voice has two forms because a
region and a mark have different jobs: `--color-voice-n` is a region fill (band, section, card) and
keeps the exact plate colour, with its own measured label colour `--color-on-voice-n`; a mid-lightness
plate colour is therefore never darkened for a region. `--color-voice-n-mark` is the step that passes
3:1 for chart marks, icons and meaningful edges; it may equal the region (the build reports
`same_as_region`). Each voice keeps one meaning (anything within 15° of hue counts as the same colour)
and is never the only signal (§7).

Three build options change the action roles and the text floor; turn the user's constraint into the
option rather than editing tokens by hand:
- `--action-style solid|tinted|outline`: solid is an accent fill with a measured label (default);
  tinted is a pale accent tint, accent border and body-text label (for "no saturated colour behind
  text"); outline is transparent with an accent border and accent-text label. The `--color-action*`
  tokens are always emitted, so components use them whichever style is chosen.
- `--on-accent light|dark|auto`: auto measures both labels; `light` or `dark` fixes the label (a
  brand rule such as white button text) and the fill moves to the nearest step that passes.
- `--text-min N`: WCAG floor for body and label text (default 4.5; 7 for "comfortably above the
  minimum"); the large-text floor becomes N / 1.5 when N is above 4.5.

Additions this file makes to that map (the skill's convention):
- `--color-border-strong` (in the table above): the boundary that *carries
  meaning* (form-field outline, required or invalid edge, table rule a reader relies on). The
  role-map `--color-border` (neutral-300) measures about 1.7:1 on `--color-bg` in both modes, so it
  is structural only and never asked to pass the non-text gate. On a neutral-200 surface use
  neutral-600 (neutral-500 measures 2.5:1 there).
- Status roles `--color-{success,warning,danger,info}` with `-subtle`, `-text`, `-on`: taken from
  the palette when a member's hue falls in the window success 135–165°, warning 65–95°, danger
  15–40°, info 230–270° and is ≥ 15° from the accent's hue; otherwise from the default seeds
  danger `oklch(0.55 0.19 27)`, warning `oklch(0.72 0.15 72)`, success `oklch(0.55 0.14 150)`,
  info `oklch(0.55 0.13 250)`, built into ramps like any seed. A status within 15° of the accent
  is re-seeded on another palette hue or given a non-colour treatment (outlined control + icon),
  and the report says which status came from where. Danger is never green-dominant.
- Browser surfaces (selection, caret, scrollbar, focus ring) take semantic tokens too.

## 3. Contrast: gate, target, procedure

**Gate (must pass; adjust until it does).** WCAG 2 ratio against the surface actually painted
behind the element: body text ≥ 4.5; large text (≥ 24px, or ≥ 18.66px bold) ≥ 3.0; non-text UI
that carries meaning (meaningful borders, focus ring, icons, chart marks) ≥ 3.0.

**Target (reported beside the gate; adjusted toward when that does not break the palette, else
warned).** APCA Lc (APCA-W3 0.0.98G-4g, absolute value; sign shows polarity): body 75,
labels and headings 60, large text 45, non-text fine detail 45, solid icons and UI 30, dividers 15.
Where WCAG and APCA favour different text colours on a fill, the gate decides and both are shown.

**Procedure.** Measure every (role, surface) pair in the role's sits-on list, in both modes
(Albers 1). For a failing pair: change L only (keep C and h; reduce C only when the L change
leaves the gamut), re-measure, and record before/after hex, L and ratio for every change. Prefer
moving the *token* (a neutral or a generated step) over moving a pinned palette colour; if the
pinned colour itself must move, the role moves to a neighbouring step instead (§8). Alpha, `color-mix`
and translucent tokens are measured as rendered (§9). Text over images: worst region or scrim.

**Text-bearing fill rule.** For every fill that carries text (button, chip, banner, rail), measure
both polarities (`--color-text` and `--color-bg`, or neutral-950 and neutral-50) and let the gate
choose `--color-on-*`; never assume "dark fill, white text".

**Self-test vectors** (`validate.py` must reproduce them to 0.1): APCA text `#888888` on
`#ffffff` → Lc 63.06; `#ffffff` on `#888888` → −68.54; `#000000` on `#ffffff` → 106.04;
`#ffffff` on `#000000` → −107.88. WCAG `#777777` on `#ffffff` → 4.48. OKLCH of `#ff0000` →
L 0.628, C 0.2577, h 29.23.

## 4. The mid-lightness trap

A fill with L in 0.50–0.70 cannot carry body text reliably in either polarity: near L 0.56 no
neutral text exceeds about 4.6:1, and across roughly L 0.54–0.83 no text reaches Lc 75 (Albers
13). Many Wada chips, kasane mid-layers and painting accents sit exactly there. So:

- A mid-lightness palette colour becomes a region fill, a border, a chart mark, a large-type
  ground or a decorative band; never a body-text ground. Large text may sit on it only when the
  measured pair passes the 3.0 gate (and ideally Lc 45).
- When the role needs body text (a button label, a banner), the fill moves to the generated 600
  or 700 step of the same ramp and the pinned colour keeps the graphic band (§8). The generated
  600 step is often still in the trap (Helvetia Blue 600 measures 4.65:1 with light text, Benzol
  Green 600 only 4.49:1), so measure; do not assume 600 is safe.
- The validator flags every text-bearing fill in L 0.50–0.70 and prints both polarities.

## 5. Vibrating and vanishing pairs

Checked on every adjacent pair in the layout's adjacency list (text/surface and fill/fill), and
reported separately from the contrast result because WCAG does not see them:

- **Vibrating (Albers 12):** hue difference ≥ 100°, both C ≥ 0.10, ΔL < 0.15. Never for text on
  a fill, never for two touching fills. A poster may keep a vibrating pair as decoration, away
  from reading areas and separated by a ground or neutral gap; the report still lists it.
- **Vanishing (Albers 13):** two adjacent fills with ΔL < 0.10 and hue difference < 40° lose
  their edge, in greyscale, under colour-vision deficiency and at a glance. Fix with ΔL ≥ 0.10
  (next-but-one step) or a stroke that passes 3.0 against the lighter fill. Scope: fills that must
  read as distinct regions (card on page, rail selection on rail, two chart segments). State
  siblings (rest/hover/pressed) are governed by Albers 3 instead: ΔL ≥ 0.06 plus a non-colour cue.
- Related: when an accent's hue is within 30° of its surface's hue, separation comes from
  lightness (ΔL ≥ 0.25 for text-bearing accents), not more chroma (Albers 3).

## 6. Composed dark mode (never inverted)

Dark mode is a new ground, so it is recomposed (wada-method §3; kasane-no-irome "How to apply"
step 6; Albers 7). The light ramp reversed is a defect, not a starting point.

1. Build the dark ramps from the same seeds with the dark table (§1): lower chroma (× 0.85), dark
   surfaces capped at C ≤ 0.045, wider steps at the dark end.
2. Remap the semantic tier with the Dark column of §2. The pinned seed lands on its nearest *dark*
   step, which is usually one step higher than in light mode (Helvetia Blue: 700 light, 600 dark).
3. Choose the ground from the use scene, not the category: a drenched or kasane page may keep its
   plate colour as a band on a deeper ground of the same hue; the page ground itself obeys the
   dark-surface chroma cap, so a saturated plate colour is a band, not the background.
4. Keep intervals: for accent/surface and surface/surface-hover pairs, ΔL in dark mode stays
   within ±0.05 of its light value where gamut allows; text/surface pairs keep their order and
   pass the gate (their interval necessarily widens with the dark table). Order by L never flips; lower chroma rather than distort an interval.
5. Re-measure every pair (§3); contrast does not carry over. Dark links (accent-200) and muted
   text (neutral-200) sit one step lighter than a mirror would put them, because the 300 steps pass
   the gate but miss the Lc target; any remaining shortfall is raised in L (§3) and reported.
6. Pick one switching mechanism and state it: `prefers-color-scheme` only (no toggle), a `.dark`
   class (user override; the media query only sets the initial value), or `light-dark()` with
   `color-scheme: light dark`. Mixing mechanisms half-themes the UI after a user override.

## 7. Colour-vision deficiency and colour as a signal

- Simulate protanopia, deuteranopia and tritanopia on the final token set (linear-sRGB matrix
  simulation in `validate.py`, stdlib) and re-check: every status pair, every chart-series pair and
  every voice pair must still differ by ΔL ≥ 0.10 or carry a non-colour cue; red/green status pairs
  are the usual failure, amber/blue the usual fix.
- Colour is never the sole signal: a state, category or gain/loss also gets text, an icon, a shape,
  a pattern or a position. The report lists every token whose meaning would otherwise be colour-only.
- Greyscale render of the preview (C = 0, L kept) is part of the hand-off (Albers 2).

## 8. Keeping a pinned palette colour

The plate colour is the point of the palette, so it is never "fixed" into something else:

1. Place it at its nearest step (§1) and export it as `--<name>-seed` and as that primitive.
2. Role steps in §2 are defaults. A role may take the pinned step instead when it is within one
   step of the default and passes the gate (Vermeer blue pins at 700, so links use the real
   painting colour, not a generated 700).
3. When the pinned colour fails as a text-bearing fill, the fill role moves to a generated
   neighbouring step (600 → 700, or the dark-mode equivalent) and the pinned colour keeps a
   non-text role: band, rail, chart mark, large-type ground. The report states the move, the
   measured before/after pair and the step now used.
4. The pinned value is written unchanged into `palette.json`, `tokens.css` and the DESIGN.md region;
   the frontmatter and the prose carry the same value.

## 9. Translucency

Text-bearing roles are opaque. Translucency is for scrims, hover and press tints and decorative
glass only, with at most one translucent layer under any text (Albers 5). The validator flattens
each translucent token over every surface in its sits-on list (gamma-encoded sRGB, as browsers
do), measures the result, and reports the worst case; text over two or more translucent layers is
flagged. Elevation prefers opaque surfaces stepped by ΔL 0.02–0.05 (within the §5 scoping) over
alpha. A tint mixed toward white and a tint made by alpha are different colours (wada-method §3):
tokens use the solid mixed value.

## 10. Cultural meaning

Colour meanings are per locale, not universal, so meaning-bearing tokens are named by meaning and
remapped per market, never hard-wired to a hue:

- Finance: Chinese, and often Japanese and Korean, market UIs show gains in red and losses in
  green, the reverse of English-language convention. Ship `--color-gain` / `--color-loss` tokens
  and remap them per locale instead of reusing `success` / `danger`.
- White carries mourning associations in several East Asian contexts; red carries celebration
  and luck in Chinese contexts; a palette chosen for a Japanese subject is not a licence to add
  symbols (see the anti-cliché list in `style-recipes.md`).
- Status conventions (red danger, amber warning, green success) are respected by default but the
  report names them so a locale can override them.

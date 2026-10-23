# Shared constants for Phase 2 (fixed by the orchestrator; 2G and 2H must both use these)

`references/application-rules.md` (2G) prints these tables; `scripts/build_tokens.py` and
`scripts/validate.py` (2H) hold them as module constants. If either agent believes a number is
wrong, it keeps the number and writes the objection in its notes file; the orchestrator decides.
Sources: better-colors via `notes/1A-reference-digest.md` §1, Albers principles 7, 9, 10, 13.

## 1. Ramp lightness (OKLCH L), step names Tailwind-style; Radix 1–12 is a role alias (§4)

| Step | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Light ramp L | 0.975 | 0.935 | 0.885 | 0.810 | 0.720 | 0.630 | 0.540 | 0.460 | 0.380 | 0.300 | 0.240 |
| Dark ramp L  | 0.960 | 0.900 | 0.810 | 0.710 | 0.610 | 0.510 | 0.420 | 0.340 | 0.270 | 0.210 | 0.160 |

Light ramp: finer at the light end (0.04–0.05), 0.075–0.09 mid. Dark ramp: a separately composed
ramp (not the light ramp mirrored), with wider separation at the dark end (≥ 0.05). Minimum
ΔL between neighbours: 0.03. Neither end reaches 0 or 1.

## 2. Chroma

- Seed share `s = C_seed / Cmax(L_seed, h)`, where `Cmax(L, h)` is the largest in-sRGB-gamut
  chroma at that L and h (binary search, tolerance 1e-4).
- Step chroma `C_step = s × profile[step] × Cmax(L_step, h)`; hue constant (= seed h).
- Profile (light): 50 0.15 · 100 0.25 · 200 0.40 · 300 0.60 · 400 0.80 · 500 0.95 · 600 1.00 ·
  700 0.92 · 800 0.80 · 900 0.65 · 950 0.50.
- Dark ramp: same profile × 0.85; additionally steps 950/900/800 (dark surfaces) are capped at
  C ≤ 0.045.
- Neutral ramp: hue = hue of the palette colour chosen to tint it, C = tint × n[step] with
  n = 50 0.006 · 100 0.010 · 200 0.014 · 300 0.018 · 400 0.020 · 500 0.020 · 600 0.020 ·
  700 0.018 · 800 0.016 · 900 0.014 · 950 0.012, `tint` default 1.0, hard cap C ≤ 0.03.
- Pinned seed: the plate/pattern colour is kept exactly as `--<name>-seed` and placed at the step
  with nearest L; that step uses the seed value exactly (pin) and neighbours are generated
  around it. A pinned colour is never darkened silently; if it fails as a fill, the fill role
  moves to another step and the report says so.

## 3. Contrast gates

- **Gate (must pass, adjust until it does):** WCAG 2 contrast ratio — body text ≥ 4.5,
  large text (≥ 24px, or ≥ 18.66px bold) ≥ 3.0, non-text UI (borders that carry meaning, focus
  ring, icons, chart marks) ≥ 3.0 against their surface.
- **Target (reported, adjusted toward when it does not break the palette, else warned):** APCA
  Lc (APCA-W3 0.0.98G-4g, absolute value) — body 75, labels/headings 60, large text 45, non-text
  fine detail 45, solid icons/UI 30, dividers 15.
- Adjustment procedure: change L only (keep C and h; reduce C only if L change leaves gamut),
  re-measure, record before/after hex, L and ratio for every change.
- Vibrating pair flag (Albers 12): hue difference ≥ 100°, both C ≥ 0.10, ΔL < 0.15.
- Vanishing pair flag (Albers 13): adjacent fills with ΔL < 0.10 and hue difference < 40°.
- Text-bearing fill warning: fill L in 0.50–0.70 (mid-lightness trap) → measure both text
  polarities and choose by the gate.

Test vectors (must be reproduced to 0.1): APCA text `#888888` on bg `#ffffff` → Lc 63.06;
text `#ffffff` on bg `#888888` → Lc −68.54; `#000000` on `#ffffff` → 106.04;
`#ffffff` on `#000000` → −107.88. WCAG `#777777` on `#ffffff` → 4.48. OKLCH of `#ff0000` →
L 0.628, C 0.2577, h 29.23.

## 4. Role map (semantic tier; `--color-*` names so Impeccable's document scan finds them)

| Semantic token | Light | Dark | Radix alias |
|---|---|---|---|
| `--color-bg` (page) | neutral-50 | neutral-950 | 1 |
| `--color-bg-subtle` | neutral-100 | neutral-900 | 2 |
| `--color-surface` (cards, panels) | white-ish neutral-50 or palette ground | neutral-900 | 2–3 |
| `--color-surface-hover` | neutral-200 | neutral-800 | 4 |
| `--color-border-subtle` | neutral-200 | neutral-800 | 6 |
| `--color-border` | neutral-300 | neutral-700 | 7 |
| `--color-text` | neutral-900 | neutral-50 | 12 |
| `--color-text-muted` | neutral-700 | neutral-300 | 11 |
| `--color-accent` (solid fill) | accent-600 | accent-500 | 9 |
| `--color-accent-hover` | accent-700 | accent-400 | 10 |
| `--color-on-accent` | chosen by measurement (white or neutral-950) | chosen by measurement | — |
| `--color-accent-text` (links) | accent-700 | accent-300 | 11 |
| `--color-accent-subtle` | accent-100 | accent-900 | 3 |
| `--color-focus` | accent-500 | accent-400 | 8 |

Remaining palette colours become `--color-voice-1..n` (+ `-subtle`, `-text`) for regions,
categories and illustration; status colours (`success`, `warning`, `danger`, `info`) are taken
from the palette when a member fits the meaning (hue window), else from a neutral default set,
and the report says which.

## 5. Proportion targets by strategy (Impeccable names, verbatim)

| Strategy | Ground + neutrals | Palette colours | Accent |
|---|---|---|---|
| Restrained | 85–95% | voice colours 0–5% | 2–8% |
| Committed | 35–65% | one palette colour 30–60% | ≤ 8% |
| Full palette | 45–65% (ground) | secondary 15–30%, tertiary 5–15% | ≤ 8% |
| Drenched | 5–30% (text and neutrals) | palette surface 60–90% | ≤ 8% |

Modifiers: an accent with C ≥ 0.15 targets ≤ 5% (Albers 9; also Taste's < 5%). Kasane: the
innermost/edge layer (*hitoe* or the last visible layer) 5–10%. Painting palettes: ground colours
take shares proportional to their measured coverage, accents ≤ 8% total. Wada's plates show equal
swatch areas for convenience only (1C §5.1, 1G): these targets are the skill's own convention and
must be labelled so.

## 6. Output conventions

- Scripts: Python ≥ 3.10, stdlib only, `encoding="utf-8"` on every file open, and
  `sys.stdout.reconfigure(encoding="utf-8")` at start (Windows cp1252 console crashes on Japanese
  names). Paths via `pathlib`; no network at run time.
- Hand-off files: `DESIGN.md` (project root, our marker regions only), `design/palette.json`
  (source of truth), `design/tokens.css`; contract in `notes/1H-contract-accepted.md`.
- Provenance labels exactly as `Art References/colorcombinations-data.md` "How the skill should
  label them": "Wada plate 229 (*A Dictionary of Color Combinations*, 1933)"; "Editorial palette by
  colorcombinations.org, inspired by Wada's method"; painting: "Sampled from <title>, <artist>,
  <date> by colorcombinations.org" plus the drift note for the 6 flagged works (data count; the source note's prose said 7); kasane:
  "Kasane no irome: <name> (Heian court colour layering; hex values are interpretations)".

## 7. Amendments v2 (orchestrator, after 2G's objections in `notes/2G-notes.md` §2)

1. New role `--color-border-strong` = neutral-500 in light and dark. The non-text 3.0 gate applies
   to it (meaning-bearing edges); `--color-border` and `--color-border-subtle` are structural.
2. Dark `--color-accent-text` = accent-200; dark `--color-text-muted` = neutral-200.
3. Hover polarity: `--color-accent-hover` is the step next to the rest fill in the direction that
   increases contrast with `--color-on-accent`; `--color-surface-hover` likewise relative to
   `--color-text`. Applies in both modes (table values in §4 are the defaults when on-accent is
   light in light mode).
4. Vanishing flag only for fill pairs declared as distinct regions (validator adjacency list);
   state siblings need ΔL ≥ 0.06 plus a non-colour cue.
5. A role may take the pinned seed's step when it is within one step of the role's default and
   passes the gate; otherwise the default step stays and the report says so.
6. Status colours: hue windows and OKLCH seeds as printed in `references/application-rules.md` §2.
7. Chroma profile stays anchored at 600 (observation 6 noted, no change).
8. Albers 7's ±0.05 interval tolerance applies to accent/surface and surface/surface pairs only;
   text/background pairs must keep their order and pass the gate.

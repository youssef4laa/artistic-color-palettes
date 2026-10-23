---
name: "Fieldbook"
description: "Farm record-keeping app: calm, field-notebook feel, Wada plate 229 palette."
colors:
  # acp:begin tokens (artistic-color-palettes; do not edit between markers)
  bg: "#FAF6F3"
  bg-subtle: "#EFE8E3"
  surface: "#FAF6F3"
  border: "#CABFB6"
  border-strong: "#92877D"
  text: "#332C27"
  text-muted: "#60564E"
  accent: "#995F27"
  accent-hover: "#784D25"
  on-accent: "#FFFFFF"
  accent-text: "#784D25"
  accent-subtle: "#EEE8E4"
  focus: "#BA783A"
  voice-1: "#253122"
  success: "#1F6836"
  warning: "#B9862C"
  danger: "#C42E2B"
  info: "#3A8DDB"
  # acp:end tokens
typography:
  display:
    fontFamily: "Fraunces"
    fontSize: "2rem"
    fontWeight: 600
  body:
    fontFamily: "Public Sans"
    fontSize: "1rem"
    fontWeight: 400
rounded:
  sm: "4px"
  md: "8px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "32px"
---

# Design System: Fieldbook

## Overview

**Creative North Star:** "The field notebook"

Fieldbook is a record-keeping tool for small farms: fields, spray logs, harvest tallies. It is
used in a farm office and on a phone in the yard, in daylight. Mode: Operate. The interface is
quiet, dense where it must be, and the palette is the one in the Colors section below, chosen
from Wada plate 229 and unchanged since the first design pass.

## Colors
<!-- acp:begin colors v1 -->
Golden Yellow & Deep Slate Olive +1: 3 colours (Golden Yellow, Deep Slate Olive, Neutral Gray), composed as a Restrained palette for an Operate surface, with a separately composed dark mode.

Provenance: Wada plate 229 (*A Dictionary of Color Combinations*, 1933). Credit: Wada plate 229 via colorcombinations.org (CC BY 4.0). Licence: PD+MIT+CC-BY-4.0.

### Primary

- **Golden Yellow Accent** (#995F27 / oklch(0.539 0.103 61.3)): the one solid action colour (light mode); text on it is white.
- **Golden Yellow Accent Text** (#784D25 / oklch(0.460 0.080 61.5)): links and accent-coloured text on the page.
- **Golden Yellow Accent Tint** (#EEE8E4 / oklch(0.935 0.008 56.3)): selected and hover backgrounds, quiet badges.

### Secondary

- **Deep Slate Olive Voice** (#253122 / oklch(0.297 0.031 139.4)): voice colour 1: regions, categories, illustration; never the call to action.

### Tertiary

- **Success** (#1F6836 / oklch(0.459 0.107 150.2)): status colour, from the default seeds (no palette colour fits this meaning).
- **Warning** (#B9862C / oklch(0.655 0.120 77.4)): status colour, from the default seed, re-seeded away from the accent hue (pair it with an icon and a label).
- **Danger** (#C42E2B / oklch(0.540 0.187 27.0)): status colour, from the default seeds (no palette colour fits this meaning).
- **Info** (#3A8DDB / oklch(0.630 0.142 250.0)): status colour, from the default seeds (no palette colour fits this meaning).

### Neutral

The neutral ramp is tinted with Golden Yellow (chroma capped at 0.03), never plain grey.

- **Page** (#FAF6F3 / oklch(0.975 0.006 59.7)): the page background
- **Surface** (#FAF6F3 / oklch(0.975 0.006 59.7)): cards and panels
- **Subtle Surface** (#EFE8E3 / oklch(0.935 0.010 58.2)): wells, table stripes
- **Divider** (#CABFB6 / oklch(0.811 0.018 61.9)): dividers and quiet borders
- **Control Border** (#92877D / oklch(0.630 0.020 64.8)): borders that carry meaning (inputs, 3:1 against the page)
- **Text** (#332C27 / oklch(0.299 0.014 57.7)): body text
- **Muted Text** (#60564E / oklch(0.460 0.018 61.0)): secondary text

### Named Rules

- **The Restrained Rule.** Colour strategy Restrained, mode Operate. Do not mix strategies on one surface.
- **The Proportion Rule.** Screen share: ground and neutrals 85-95%; voice colours 0-5%; accent 2-8%. Proportion targets are this skill's own convention (Impeccable's strategy names, numbers from the skill's shared constants); Wada's plates show equal-area swatches for convenience only.
- **The Contrast Floor Rule.** Body text 4.5:1, large text and non-text UI (focus ring, control borders, icons, chart marks) 3:1, measured with WCAG 2 for every pair in both modes; APCA Lc is reported against 75 body, 60 labels, 45 large text and fine detail, 30 solid UI.
- **The Composed Dark Rule.** Dark mode is a separately composed ramp (lower chroma, wider dark-end steps), never the light ramp inverted; every pair is re-measured.

#### Token tables

| Token | Light | Dark | Light source | Dark source |
|---|---|---|---|---|
| `--color-bg` | #FAF6F3 | #110C08 | neutral-50 | neutral-950 |
| `--color-bg-subtle` | #EFE8E3 | #1D1712 | neutral-100 | neutral-900 |
| `--color-surface` | #FAF6F3 | #1D1712 | neutral-50 | neutral-900 |
| `--color-surface-hover` | #E0D7D0 | #2C251F | neutral-200 | neutral-800 |
| `--color-border-subtle` | #E0D7D0 | #2C251F | neutral-200 | neutral-800 |
| `--color-border` | #CABFB6 | #3F362F | neutral-300 | neutral-700 |
| `--color-border-strong` | #92877D | #6F645B | neutral-500 | neutral-500 |
| `--color-text` | #332C27 | #F5F1EE | neutral-900 | neutral-50 |
| `--color-text-muted` | #60564E | #C8BFB8 | neutral-700 | neutral-200 |
| `--color-accent` | #995F27 | #865B35 | accent-600 | accent-500 |
| `--color-on-accent` | #FFFFFF | #FFFFFF | white | white |
| `--color-accent-hover` | #784D25 | #674424 | accent-700 | accent-600 |
| `--color-accent-text` | #784D25 | #F3A257 | accent-700 | accent-200 |
| `--color-accent-subtle` | #EEE8E4 | #20160E | accent-100 | accent-900 |
| `--color-focus` | #BA783A | #A67851 | accent-500 | accent-400 |
| `--color-voice-1` | #253122 | #5A6C54 | voice-1-900 | voice-1-500 |
| `--color-voice-1-subtle` | #E6EBE4 | #151A15 | voice-1-100 | voice-1-900 |
| `--color-voice-1-text` | #4B5E46 | #96A891 | voice-1-700 | voice-1-300 |
| `--color-on-voice-1` | #FFFFFF | #FFFFFF | white | white |
| `--color-success` | #1F6836 | #367147 | success-700 | adjusted from success-600 |
| `--color-success-subtle` | #DEEFE1 | #0E1C11 | success-100 | success-900 |
| `--color-success-text` | #1F6836 | #77B283 | success-700 | success-300 |
| `--color-on-success` | #FFFFFF | #FFFFFF | white | white |
| `--color-warning` | #B9862C | #BC9C6B | adjusted from warning-400 | warning-300 |
| `--color-warning-subtle` | #EFE8DF | #1F170B | warning-100 | warning-900 |
| `--color-warning-text` | #735112 | #BC9C6B | warning-700 | warning-300 |
| `--color-on-warning` | #241E19 | #110C08 | neutral-950 | neutral-950 |
| `--color-danger` | #C42E2B | #CB5C53 | danger-600 | danger-400 |
| `--color-danger-subtle` | #EEE8E7 | #28100E | danger-100 | danger-900 |
| `--color-danger-text` | #992B27 | #CE8F87 | danger-700 | danger-300 |
| `--color-on-danger` | #FFFFFF | #110C08 | white | neutral-950 |
| `--color-info` | #3A8DDB | #36699B | info-500 | info-500 |
| `--color-info-subtle` | #E6EAEE | #0E1924 | info-100 | info-900 |
| `--color-info-text` | #255B8D | #82A5CA | info-700 | info-300 |
| `--color-on-info` | #241E19 | #FFFFFF | neutral-950 | white |

#### Measured contrast

104 pairs measured in light and dark; 100 are gated and all pass (tightest: warning on bg, light, 3.0:1 against 3.0:1). APCA Lc is below its target on 30 pairs; WCAG 2 is the gate.

| Pair | Mode | WCAG 2 | APCA Lc |
|---|---|---|---|
| `text` on `bg` | light | 12.77:1 | 95 |
| `text` on `bg` | dark | 17.32:1 | 99 |
| `text` on `surface` | light | 12.77:1 | 95 |
| `text` on `surface` | dark | 15.8:1 | 98 |
| `text-muted` on `bg` | light | 6.65:1 | 80 |
| `text-muted` on `bg` | dark | 10.74:1 | 69 |
| `text-muted` on `surface` | light | 6.65:1 | 80 |
| `text-muted` on `surface` | dark | 9.8:1 | 68 |
| `accent-text` on `bg` | light | 6.77:1 | 80 |
| `accent-text` on `bg` | dark | 9.37:1 | 62 |
| `on-accent` on `accent` | light | 5.22:1 | 81 |
| `on-accent` on `accent` | dark | 5.9:1 | 85 |
| `accent` on `bg` | light | 4.86:1 | 71 |
| `accent` on `bg` | dark | 3.3:1 | 22 |
| `focus` on `bg` | light | 3.35:1 | 58 |
| `focus` on `bg` | dark | 5.03:1 | 35 |
| `border-strong` on `bg` | light | 3.27:1 | 58 |
| `border-strong` on `bg` | dark | 3.38:1 | 23 |

Flags to design around (see design/palette.json): cvd, vanishing, vibrating (11 findings). Do not rely on colour alone to tell the accent from status colours.

#### Adjustments

Lightness-only changes made to pass the gate (hue kept):

- `warning` (light): #CE9A43 to #B9862C, L 0.7195 to 0.6548, ratio 2.35:1 to 3.0:1 against `bg`; reason: WCAG gate.
- `success` (dark): #205B32 to #367147, L 0.4212 to 0.497, ratio 2.41:1 to 3.34:1 against `bg`; reason: WCAG gate.

#### Keep in sync

Do not change a colour here without re-validating: edit nothing between the acp markers by hand. Change the palette or strategy, then re-run `scripts/handoff.py` (idempotent). If Impeccable's document step asks refresh, overwrite or merge, choose merge and re-run it.

#### Hand-off files

- Tokens: `design/tokens.css` (primitives, then semantic `--color-*`, light, dark and `[data-theme=dark]`).
- Source of truth: `design/palette.json` (provenance, ramps, contrast, adjustments).

#### Neighbour map

- Taste: `--bg` #FAF6F3, `--surface` #FAF6F3, `--ink` #332C27, `--muted` #60564E, `--accent` #995F27 (the one accent), `--accent-ink` #FFFFFF. Run Taste with `--keep palette`; pass `--allow palette-purple` if the palette has violet or indigo, and expect its inspector to question a cream plus terracotta ground.
- UI/UX Pro Max: `--color-primary` and `--color-accent` #995F27, `--color-background` #FAF6F3, `--color-foreground` #332C27, `--color-card` #FAF6F3, `--color-muted-foreground` #60564E, `--color-border` #CABFB6, `--color-destructive` #C42E2B, `--color-ring` #BA783A. Keep its pattern and type output, take colours from `design/tokens.css`; never edit its MASTER.md without consent.
- interface-design: `--foreground`, `--secondary`, `--muted`, `--faint`, `--accent` resolve to the semantic tokens in the alias block of the CSS file.
- Theme Factory custom theme, colour bullets: Golden Yellow #995F27 (accent); Deep Slate Olive #253122 (voice); Golden Yellow-tinted neutrals #FAF6F3 to #332C27.
<!-- acp:end colors -->

## Typography

Display in Fraunces, body in Public Sans. Sizes follow a 1.25 scale from 16px. Numbers in tables use tabular figures.

## Components

- **Buttons:** 8px radius, 44px minimum height; primary uses the accent token with its on-accent text.
- **Forms:** labels above fields, 16px text, one column.
- **Toggles:** track plus a visible on/off word, never colour alone.

## Do's and Don'ts

- Do keep one primary action per section.
- Do not introduce new colours; every colour comes from the Colors section.
- Don't use shadows heavier than 1px borders for elevation.

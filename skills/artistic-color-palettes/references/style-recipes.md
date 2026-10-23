# Style recipes: from a brief to a distinctive colour system

A "unique art style" here is not a stereotype applied to a page; it is a real palette with a
provenance (Wada plate, kasane stack, sampled painting, editorial composition), placed into roles
and proportions that fit the surface, measured, and handed over. The brief and the palette lead;
the agent's habits do not. Numbers: `application-rules.md`; families: `wada-method.md`,
`kasane-no-irome.md`; neighbours: `interop.md`.

## 1. The chain

Every run records a decision at each step: brief → surface mode → colour strategy → palette family →
search and candidates → user's choice → role mapping → proportion → ramps → tokens → verify → preview → hand-off.

### 1.1 Brief

Read what exists first (interop.md §3). Note pinned colours, brand commitments, the accessibility
standard, the markets served, and what the user said about mood, era, season, subject or a named
plate or painting. A pinned palette is honoured as given; the skill adjusts only for contrast and says so.

### 1.2 Surface mode (Impeccable's names, chosen from the surface, not the product)

| Mode | The visitor… | Colour's job | Default strategy |
|---|---|---|---|
| Persuade | decides and acts (landing, marketing, pricing) | may carry the voice and own regions | Committed, Full palette or Drenched |
| Operate | completes a task (apps, dashboards, admin, tools) | action, selection, status, series, one committed shell element | Restrained |
| Read | understands (docs, articles, help) | frame owns the world; the column stays calm | Restrained |
| Experience | is inside the work (portfolios, galleries) | the artifact leads, the interface recedes | Committed, Drenched or Full palette |

Infer the mode from the requested surface; ask only when it is ambiguous. A grey screen with one
accent is not Restrained but the category default: on Operate and Read, Restrained still means tinted
neutrals, one accent, palette-derived state colours and one committed shell element (rail, masthead).

### 1.3 Colour strategy (Impeccable's names, verbatim)

**Restrained**: neutrals tinted from the palette plus one accent; any family. **Committed**: one
saturated colour carries roughly 30–60% of the surface (a description, not a quota); a Wada duo, a
kasane *nioi*, a painting's largest ground. **Full palette**: 3–4 named roles; trios, quads,
kasane stacks. **Drenched**: the surface *is* the colour; posters, campaigns, galleries. Pick the
strategy before the colours. Light or dark is never chosen by category: write one sentence of the
physical scene (who, where, under what light) and let it decide.

### 1.4 Palette family

| Family | Shape | Fits | Rule of thumb |
|---|---|---|---|
| Wada duo (plates 1–120) | 2 colours | Committed, Restrained | one is ground or accent, the other the counter-voice; the neutral ramp is tinted from one of them |
| Wada trio (121–240) | 3 colours | Restrained, Full palette | classify as same-tone or different-tone (wada-method §3.5); same-tone → Restrained (accent, voice, tint seed); different-tone → Full palette |
| Wada quad (241–348) | 4 colours in two internal pairs | Full palette, Drenched | keep the plate's pairs together (wada-method §1.6): one pair ground + surface, the other accent + voice. The CSV lists colours in site order, not plate position, so read the pairs from the plate preview |
| Kasane stack | hitoe accent + 4–6 ordered layers | Full palette, Drenched, Restrained (usuyō) | layers → surface ramp in order, hitoe → edge accent at 5–10% (kasane file, "Garment layers") |
| Painting ground/accent | 3 grounds with coverage + 3 accents | Restrained, Committed | grounds take shares in proportion to coverage; accents stay rare; Hokusai first when the user asks for Japanese paintings |
| Editorial (colorcombinations.org) | 3–4 colours, era-tagged | as a trio/quad | always labelled editorial, never "a Wada plate" |

Same-tone rows (wada-method §3.5) suit restrained palettes; different-tone rows suit full-palette work
and get the stricter checks (every adjacent pair, proportion preview). A plate is never judged by wheel geometry.

### 1.5 Search and candidates

1. Filters first: colour count (2/3/4), mood (austere, bold, cool, earthy, playful, refined,
   serene, solemn, warm), dominant hue, era, source type (`wada_plate` / `editorial` / `painting` / `kasane`);
   then free text over names, summary and tags.
2. Return three to five candidates, each with provenance label, hex and OKLCH per colour, tone
   pattern, suited strategy, one line on fit, and the known trap (mid-lightness members, vibrating
   pairs, drift). Show them as applied mini-layouts in light and dark, never as bare swatches.
3. **Wait for the user's explicit choice.** The skill never picks one of 348 plates silently and
   never proceeds on "any of these".
4. Zero or weak matches: say "no match" with the filters used; retry once narrower; then offer an
   *original composition*, clearly labelled as such, shown for review before any use.

### 1.6 Anti-cliché list (what the skill refuses by reflex)

- No cream paper + red circle + cherry blossom as the default rendering of "Japanese"; the chosen
  plate's actual colours (mostly warm, deep, unexpected) carry the subject.
- No Rising Sun rays, no imperial, militarist or nationalist emblems or their stylised variants as
  motif, badge or ornament, whatever the subject; use the world's neutral forms.
- No "Zen" beige minimalism by reflex; no stone-and-bone ground unless the brief asks for calm.
  Wada's plates are mostly saturated (red, yellow and orange dominate); the muted rendition is spent.
- No red + black + gold lacquer as the default for food or restaurant briefs.
- For a Japanese brief, at most one candidate on a cream, kinari or gofun ground unless the brief
  asks for calm; even then include one non-beige candidate (a Wada plate or a kasane stack).
- Never pass a European or American painting's palette off as eastern; the set has one East Asian
  work (Hokusai's *Great Wave*), offered first when the user asks for Japanese paintings.
- When the brief is free, do not land in the generic AI looks: cream + serif + terracotta,
  near-black + neon, broadsheet hairlines + italic serif, flat ink + hard offset shadows. And
  decoration unrelated to hierarchy, state or content is not a colour strategy.

### 1.7 Provenance and the no-fabrication rule

Every suggestion carries one of these labels exactly: "Wada plate N (*A Dictionary of Color
Combinations*, 1933)"; "Editorial palette by colorcombinations.org, inspired by Wada's method";
"Sampled from <title>, <artist>, <date> by colorcombinations.org" plus the drift note for the six
flagged works (values are the painting as it looks today); "Kasane no irome: <name> (Heian court
colour layering; hex values are interpretations)"; or "Original composition by this skill (not a
plate)". Plates exist only in 1–348 (Vol. 2 is not in the data); 25 paintings, 33 kasane, 30
editorial. Not in `data/` means it does not exist. Every hex approximates a print, never "Wada's exact colour".

### 1.8 Role mapping

Decide, in order, which member seeds (a) the neutral tint, (b) the accent, (c) the shell or ground,
(d) the voices; then status (application-rules §2). Same-tone trio → most saturated member is the
accent, most neutral the tint seed, the third a voice. Quad → pairs stay together. Kasane → hitoe
is the accent, layers the surface ramp in order, palest layer the ground. When the hitoe repeats a
layer's colour (Kurenai momiji: hitoe and layer 5 are both kurenai) and that colour becomes the ground,
the edge accent is the best-separating other layer, named by its layer ("ki, layer 3"), never "the hitoe". Painting → largest ground
seeds the tint and the frame, darkest ground is text when dark enough, most saturated accent is the
accent. Mid-lightness members get non-text roles (application-rules §4). Every role gets a sits-on list.

### 1.9 Proportion (the skill's own convention; Wada's plates show equal areas only for convenience)

| Strategy | Ground + neutrals | Palette colours | Accent |
|---|---|---|---|
| Restrained | 85–95% | voice colours 0–5% | 2–8% |
| Committed | 35–65% | one palette colour 30–60% | ≤ 8% |
| Full palette | 45–65% (ground) | secondary 15–30%, tertiary 5–15% | ≤ 8% |
| Drenched | 5–30% (text and neutrals) | palette surface 60–90% | ≤ 8% |

Modifiers: an accent with C ≥ 0.15 targets ≤ 5%; kasane hitoe 5–10%; painting grounds in
proportion to measured coverage, accents ≤ 8% in total. The lightest or most saturated colour gets
the smallest area; the accent marks one action or idea per view (Albers 9). Written into DESIGN.md
as Named Rules so neighbours read them as the world's invariant.

### 1.10 Ramps, tokens, verify, preview, hand-off

Build ramps and two-tier tokens (application-rules §1–§2); run gate and target on every sits-on
pair in both modes, adjust, flag vibrating and vanishing pairs, simulate CVD (§3–§7); render the
preview (light, dark, greyscale, at target areas); only then write `design/palette.json`,
`design/tokens.css` and the DESIGN.md region (interop §3).

## 2. Worked example (a): SaaS analytics dashboard

**Brief.** "Analytics dashboard for a logistics SaaS; data-dense tables and charts; light and dark;
cool and serious but not generic." Mode **Operate**. Scene: a dispatcher at a desk monitor in
daylight all day → light default, dark available. Strategy **Restrained** with one committed shell
element. Search: count 3, moods refined + cool, hue blue / green / neutral, source wada. Candidates
as mini-layouts: plates 139 (Salvia Blue, Deep Indigo, Neutral Gray), 143 (Blue, Lilac, Warm Gray),
187 (Helvetia Blue, Grayish Lavender B, Aconite Violet), 202 (Turquoise Green, Cobalt Green,
Slate Color) and 218. **User chooses 218.**

*Generated with* `build_tokens.py --palette wada-218 --strategy restrained --mode operate` (default
`--pin all`), then `validate.py --fix --in-place`. Every hex, step and ratio below is read from that
JSON; `scripts/tests/test_docs.py` rebuilds it and fails if the text drifts.

**Palette and roles.** Wada plate 218 (*A Dictionary of Color Combinations*, 1933): Helvetia Blue
`#005b8d` oklch(0.452 0.109 242.8), Grayish Lavender A `#b5b1d8` oklch(0.777 0.055 289.8), Deep
Violet / Plumbeous `#70727c` oklch(0.554 0.016 276.9). Related hues across dark, light and mid
lightness: *same-tone* (wada-method §3.5), so Restrained fits. The script maps: accent = Helvetia
Blue, pinned at light 700 / dark 600; neutral tint seed = Grayish Lavender A (hue 290°); voice-1 =
Grayish Lavender A, pinned at light 300 / dark 200; Plumbeous is left unused (mid-lightness, so it
never carries text). Shell = a rail in the pinned Helvetia Blue.

**Light tokens (measured).** bg neutral-50 `#f6f6fb`; text neutral-900 `#2d2d35` 12.67:1, Lc +95.0;
text-muted neutral-700 `#575762` 6.62:1, +79.6; surface-hover neutral-200 `#d8d8e2` (text on it
9.65:1); border neutral-300 `#c0bfcc` 1.69:1 (structural, below the non-text bar of three to one, by design);
border-strong neutral-500 `#898795` 3.27:1. `surface` equals `bg` in light (dL 0.00, flagged
vanishing), so cards separate with bg-subtle neutral-100 `#e9e8f0` (text 11.22:1) or border-strong.
Accent fill = the pinned accent-700 `#005b8d`; on-accent white 7.29:1, Lc −89.6 (neutral-950 2.27:1
loses); accent-hover accent-800 `#194666` (white 9.96:1); links = accent-text `#005b8d` 6.77:1;
accent-subtle accent-100 `#e5eaef` (accent-text on it 6.02:1); focus accent-500 `#1a91d9` 3.20:1.
Rail `#005b8d`: white text 7.29:1. Voice-1 is a region fill: pinned `#b5b1d8` with on-voice-1
neutral-950 `#1f1e24` 8.07:1; as a chart mark it steps to voice-1-mark voice-1-500 `#887fbd`
3.35:1; voice-1-text `#584b90` 6.90:1. Status: no plate hue falls in a status window, so the
default seeds are used and info is re-seeded because its default hue is within 15° of the accent
(give info an icon and a label); danger-text `#992b27` 7.14:1, warning-text `#764f15` 6.72:1,
success-text `#1f6836` 6.31:1, info-text `#33588f` 6.65:1. Flags to design around: accent vs
danger vibrate (hue difference 144°), and surface vs accent-subtle merge (dL 0.04).

**Dark tokens (composed).** bg neutral-950 `#0d0c12`; surface neutral-900 `#18171e`; text
neutral-50 `#f1f1f6` 17.30:1, Lc −98.7; text-muted neutral-200 `#c0c0ca` 10.79:1, −68.8;
border-strong neutral-500 `#666471` 3.36:1; accent fill accent-500 `#296c9a` with white 5.67:1,
−83.3 (mid-lightness fill; neutral-950 3.44:1 loses); accent-hover = the pinned blue accent-600
`#005b8d` (white 7.29:1), only dL 0.058 from the fill, so hover also needs a non-colour cue;
focus accent-400 `#488aba` 5.21:1. Links start at accent-text accent-200 `#aec4d6` and
`validate.py --fix` lifts them to `#bbd1e3` for the APCA target: 12.37:1 on bg, 11.31:1 on surface.
The fix also lifted dark success to `#367147` and light warning to `#bb822f` (3.07:1) to clear the gate.

**Proportion (Restrained).** Neutrals 88%, rail (committed shell) 7%, accent ≤ 3%, voice tint ≤ 2%.
Preview: table + chart + rail, light / dark / greyscale. Named Rules: "The Restrained Rule", "The One Rail Rule".

## 3. Worked example (b): poster-style landing page, with Impeccable loaded

**Read first.** `PRODUCT.md` (Impeccable's init): Users = riders deciding to register for a
three-day closed-streets city cycling festival; Brand Commitments = a black wordmark on any
ground, no brand colours yet; Accessibility = WCAG AA; Evidence = route map, schedule, photos.
`DESIGN.md`: absent. Surface brief: mode **Persuade**, set by Impeccable; we keep it and supply
colour only. Impeccable's new-work wants a strategy named before colours and a scene sentence:
riders check the route on a phone at the start line at 7 a.m. under an overcast sky, so the page
reads like a printed poster on a lamppost → **Drenched**, light by default, dark composed for the
device setting. The palette region is written to DESIGN.md *before* Impeccable's "Commit the
world" so its roll honours a pinned palette; at finish its document step asks refresh / overwrite
/ merge: tell the user to choose merge, then re-run `handoff.py`.

**Search.** Count 4, mood bold, source wada or kasane. Candidates: plates 247, 286 (Burnt Sienna, Orange
Yellow, Peacock Blue, Violet Blue), 344 (Cinnamon Buff, Deep Lyons Blue, Aconite Violet, Black), kasane
*Kurenai momiji* and *Haji momiji*. **User chooses 247.**

**Palette.** Wada plate 247 (*A Dictionary of Color Combinations*, 1933): top Raw Sienna `#bb7125`,
bottom Apricot Yellow `#ffdd00`, middle-left Benzol Green `#00978d`, middle-right Deep Lyons Blue
`#1c4286`. Pairs (wada-method §1.6): sienna + apricot (warm), benzol + lyons (cool). Unlike hues, all
strong: *deep different-tone*, the poster row.

**Roles (pairs kept together).** Cool pair = ground + band: Deep Lyons Blue is the page (drench,
pinned), Benzol Green a band. Warm pair = accent + voice: Apricot Yellow the action and headline
mark (C 0.186 → ≤ 5%), Raw Sienna the schedule band. Neutrals tinted from Apricot. Sienna beside
benzol **vibrates** on the plate (hue difference 125°, dL 0.008; `validate.py` flags it), so they
never touch: both sit on the blue ground. Apricot on either does not.

**Light appearance (measured by the scripts).** Ground `#1c4286`: text `#f8f7f2` 9.01:1; muted
`#dbd9cf` 6.83:1; Apricot headline 7.18:1; CTA Apricot with `#211f19` label 12.23:1 (white label
1.35:1 fails). Benzol band: label `#211f19` 4.56:1; sienna band: label 4.32:1, so large text only.
Light `bg` and `surface` are the same blue; the raised panel is bg-subtle `#1c2d4c`.

**Dark appearance (composed).** bg `#0f1829`, band surface `#1a263c`; text `#f3f2ed` 15.84:1; muted
`#c3c1b7` 9.83:1; Apricot stays pinned, 13.18:1 on bg, CTA label `#0f0d07` 14.43:1; band labels:
benzol 5.38:1, sienna 5.09:1; voice-2-text `#72afa8` 7.11:1.

**Proportion (Drenched).** Lyons ground 65%, benzol bands 12%, sienna band 5%, Apricot 5%, text and
neutrals 13%; palette surface 82%, within 60–90%.

**Resulting DESIGN.md `## Colors` region.** Produced by `handoff.py --palette wada-247 --strategy
drenched --mode persuade --roles "drench=Deep Lyons Blue,accent=Apricot Yellow"`; excerpt, same keys
and hex as the script writes (role keys with hex, not descriptive names). Do not hand-edit it:

```markdown
colors:
  # acp:begin tokens (artistic-color-palettes; do not edit between markers)
  bg: "#1C4286"
  bg-subtle: "#1C2D4C"
  surface: "#1C4286"
  border: "#151F31"
  border-strong: "#8491A8"
  text: "#F8F7F2"
  text-muted: "#DBD9CF"
  accent: "#FFDD00"
  accent-hover: "#EFEAD3"
  on-accent: "#211F19"
  accent-text: "#FFDD00"
  accent-subtle: "#332E15"
  focus: "#B9A544"
  voice-1: "#BB7125"
  voice-2: "#00978D"
  # ...action, action-hover, on-action, action-border and the status keys follow
  # acp:end tokens

## Colors
<!-- acp:begin colors v1 -->
Four colours composed as a Drenched palette for a Persuade surface, with a composed dark mode.
Provenance: Wada plate 247 (*A Dictionary of Color Combinations*, 1933).
### Primary
- **Apricot Yellow Accent** (#FFDD00 / oklch(0.899 0.186 97.9)): the one solid action colour; text on it is near-black.
### Secondary
- **Deep Lyons Blue Voice**, **Benzol Green Voice**, ... (then status, neutrals, Named Rules, tables, neighbour map)
<!-- acp:end colors -->
```

## 4. Worked example (c): reading app

**Brief.** "A reading app for long essays; calm and warm but not beige-boring; light and dark."
Mode **Read**. Scene: an evening reader on a tablet in a lamp-lit room, often in bed → light
default, composed dark mode. Strategy **Restrained** with painting proportions. Search: source
painting or wada, count 2–3, moods serene / austere, hue neutral or yellow. Candidates: *The
Milkmaid*; *Wanderer above the Sea of Fog*; *Girl with a Pearl Earring* (drift-flagged; a dark
ground makes a dark theme); Wada 011 (Ivory Buff, Mineral Gray); Wada 094 (Ivory Buff, Dusky
Green). **User chooses the Milkmaid.**

*Generated with* `build_tokens.py --palette paint-the-milkmaid --strategy restrained --mode read`
(default `--pin all`), then `validate.py --fix --in-place`; read from that JSON and rebuilt by
`scripts/tests/test_docs.py`.

**Palette.** Sampled from *The Milkmaid*, Johannes Vermeer, c. 1660 by colorcombinations.org (not
drift-flagged). Grounds: `#d7d1bf` 19% oklch(0.861 0.025 91.6); `#c6bda9` 8% oklch(0.800 0.029
86.7); `#0f1317` 8% oklch(0.184 0.010 248.4). Accents: `#c89d7a` <1% oklch(0.727 0.070 60.5);
`#254d83` <1% oklch(0.420 0.101 256.6); `#3c1914` 2% oklch(0.264 0.056 29.7).

**Roles (as the script maps them).** Tint seed and ground = ground-1 (hue 91.6° tints the
neutrals). Accent = Vermeer blue `#254d83`, pinned at light 700 / dark 600, so links and the one
filled action use the painting's colour. Voice-1 = tan `#c89d7a` (pinned 400 / 300), voice-2 = umber
`#3c1914` (pinned 950 / 800), voice-3 = ground-2 `#c6bda9` (pinned 300 / 200, wells). The darkest
ground `#0f1317` is left unused: Restrained text comes from the tinted neutral ramp.

**Light tokens (measured).** Column neutral-50 `#f8f7f3`; text neutral-900 `#302e26` 12.68:1, Lc
+95.3, on bg-subtle neutral-100 `#ece9e2` 11.21:1; muted neutral-700 `#5c584d` 6.62:1, +79.8, on
surface-hover neutral-200 `#dcd9cf` 5.03:1; border-strong neutral-500 `#8d897c` 3.26:1. Links =
accent-text, the pinned `#254d83`: 7.94:1, +84.2 (on accent-subtle `#e7eaed` 7.05:1). Filled action
= the pinned blue with white 8.51:1, −93.6; hover accent-800 `#274369` (white 10.03:1), only dL 0.04
away, so hover also needs an underline or weight cue; focus accent-500 `#528ad7` 3.28:1. Headings =
umber `#3c1914` 14.61:1. Tan is a region fill with on-voice-1 `#211f19` 6.72:1; as a mark it steps
to voice-1-mark `#a48165` 3.32:1; voice-1-text `#695341` 6.72:1. Wells = voice-3 `#c6bda9` with
on-voice-3 `#211f19` 8.83:1. Flag: voice-1 and voice-3 are close in lightness (dL 0.073), so they
do not touch.

**Dark tokens (composed).** bg neutral-950 `#0f0d07`; surface neutral-900 `#1b1811`; text
neutral-50 `#f3f2ee` 17.34:1, Lc −99.0 (on surface 15.82:1); muted neutral-200 `#c4c1b7` 10.79:1,
−68.9; links start at accent-200 `#b8c2d0` and `validate.py --fix` lifts them to `#c5cfdd` for the
APCA target: 12.34:1, −76.6; filled action accent-500 `#3f679e` with white 5.76:1, −83.9; hover =
the pinned blue accent-600 `#254d83` (white 8.51:1); focus accent-400 `#5b85bf` 5.14:1. Umber
heading mark voice-2-400 `#b26e63` 4.91:1; tan `#c89d7a` 7.92:1. bg and surface are only dL 0.05
apart (flagged vanishing): separate with surface-hover neutral-800 `#29261d` or a gap.

**Proportion (Restrained + coverage).** Neutral column and frame together 85–95%, text ≈ 5%, links +
headings + marks ≤ 5%, one filled action < 1%; the painting's ground shares set the column :
wells ratio. Named Rules: "The Calm Column Rule" (the world owns the frame), "The Vermeer Link Rule" (one blue).

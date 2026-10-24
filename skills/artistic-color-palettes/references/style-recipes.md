# Style recipes: from a brief to a distinctive colour system

A "unique art style" here is not a stereotype applied to a page; it is a real palette with a
provenance (Wada plate, kasane stack, sampled painting, editorial composition), placed into roles
and proportions that fit the surface, measured, and handed over. The brief and the palette lead;
the agent's habits do not. Numbers: `application-rules.md`; families: `wada-method.md`,
`kasane-no-irome.md`; neighbours: `interop.md`; three briefs taken through the whole chain with measured
numbers: `worked-examples.md`.

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
| Wada trio (121–240) | 3 colours | Restrained, Full palette | classify as same-tone or different-tone (wada-method §2.3); same-tone → Restrained (accent, voice, tint seed); different-tone → Full palette |
| Wada quad (241–348) | 4 colours in two internal pairs | Full palette, Drenched | keep the plate's pairs together (wada-method §1.4): one pair ground + surface, the other accent + voice. The CSV lists colours in site order, not plate position, so read the pairs from the plate preview |
| Kasane stack | hitoe accent + 4–6 ordered layers | Full palette, Drenched, Restrained (usuyō) | layers → surface ramp in order, hitoe → edge accent at 5–10% (kasane file, "Garment layers") |
| Painting ground/accent | 3 grounds with coverage + 3 accents | Restrained, Committed | grounds take shares in proportion to coverage; accents stay rare; Hokusai first when the user asks for Japanese paintings |
| Editorial (colorcombinations.org) | 3–4 colours, era-tagged | as a trio/quad | always labelled editorial, never "a Wada plate" |

Same-tone rows (wada-method §2.3) suit restrained palettes; different-tone rows suit full-palette work
and get the stricter checks (every adjacent pair, proportion preview). A plate is never judged by wheel geometry.

### 1.5 Search and candidates

1. Filters first: colour count, mood (kasane and paintings carry measured moods), a hue the palette
   contains, lightness and chroma bands, `--near HEX`, era, source type; then colour words, never product
   words ("ocean", "coffee", not "fintech"); repeat the script's `read '…' as …` line to the user.
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

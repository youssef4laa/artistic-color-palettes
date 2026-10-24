# Wada's method: how the book says to use its combinations

Source: Sanzo Wada, *配色総鑑* (1933–34), as reprinted in *配色事典* (Seigensha, 2010). Everything
below is our paraphrase, cited as printed page / PDF page of the scan (front matter: PDF = printed + 2).
The reprint keeps only the second half of Wada's booklet *概説と其活用*, in modern kanji (p. 4 / PDF 6;
p. 12 / PDF 14). Lines starting "How the skill uses this" are our design decisions, not Wada's.

## 1. What the book is (2010 editor's framing, Ōmi Gentarō, pp. 3–14 / PDF 5–16)

**1.1 Structure.** Six volumes, 348 combinations: 120 two-colour, 120 three-colour, 108 four-colour,
published 1933–34 (p. 12 / PDF 14). In the reprint plates 1–120 are pairs, 121–240 triads, 241–348
quads (contents p. 5 / PDF 7). How the skill uses this: plate numbers outside 1–348 are invalid; plate
size (2/3/4) is a filter.

**1.2 Reproductions, period names, no harmony system.** The originals were hand-painted matte papers;
the reprint lists CMYK values in its index (p. 4 / PDF 6; p. 12 / PDF 14), so every hex is an
approximation of a print of a chip, never "Wada's exact colour". Colour names follow the original and
carry their era's meaning (p. 4 / PDF 6): labels only, decisions use the measured values. Wada did not
derive harmony from a colour-order system (Munsell, Ostwald); the plates come from a painter's experience
(pp. 13–14 / PDF 15–16), and he accepts that liking a colour is subjective while still guiding good and bad
choices (p. 13 / PDF 15). He argues that names like "blue, red, cream" convey nothing to a non-specialist,
which is why the book uses physical samples (p. 17 / PDF 19), and the editor stresses that it shows rather
than lectures (p. 13 / PDF 15). How the skill uses this: OKLCH builds ramps and measures contrast but never
judges whether a Wada pairing "works" (the plate is the authority); plates are vetted starting points the
user chooses among; every palette is shown as swatches with values before any theory.

**1.3 Two viewpoints, ten patterns.** The editor summarises Wada's composition theory as two viewpoints
split into ten patterns, rooted in long-standing European practice (p. 13 / PDF 15): the same-tone and
different-tone families of five each (§3). How the skill uses this: the ten patterns are the vocabulary
for describing a plate's character.

**1.4 Four-colour plates have internal pairs.** In a quad, the top and bottom colours relate to each
other, the middle-left and middle-right relate to each other, and the four together make one statement
(p. 13 / PDF 15); the quad plates use a cross layout (e.g. p. 150 / PDF 152). How the skill uses this: when
mapping a quad to roles, keep each pair together (one pair for ground and surface, the other for accent
and voice) rather than splitting them. The CSV lists colours in site order, not plate position, so read
the pairs from the plate preview.

## 2. Composition: 配色の構成 (pp. 18–22 / PDF 20–24)

**2.1 Habitual or invented; canon as pillar, not mould.** Composition can be traditional (low in
originality, well fitted to real life) or individually invented (novel, sometimes eccentric, interesting
even when it misses its purpose) (p. 18 / PDF 20). A rule risks forcing work into a template, but nothing
is built without a foundation; a standard keeps you from going astray and is not a demand to copy
(p. 19 / PDF 21). Harmony follows nature, and nature shows harmony even among entirely unlike tones
(p. 19 / PDF 21). How the skill uses this: offer a conventional mode (safe role mapping) and an
expressive one (unexpected mapping) and say which a suggestion is; proportion targets and pattern labels
are defaults, departures are fine when the user states a reason; different-hue palettes are legitimate.

**2.2 Two kinds of harmony.** As in music, Wada calls gradual modulation of tone *同色調* (same tone)
and the attempt to harmonise opposed tones *異色調* (different tone). He reads colour by hue, 色度 and
lightness (pp. 19–20 / PDF 21–22). [uncertain: 色度 is a prewar term; we read it as chroma/saturation]
How the skill uses this: every plate is tagged same-tone or different-tone from its OKLCH hues.

**2.3 The ten tone patterns** (p. 20 / PDF 22; restated in our words; "UI meaning" is ours). Wada
describes only the same-tone sub-types one by one; for the different-tone ones he says only that they
seek harmony from wholly different colour qualities, so those readings apply the same five modifiers by
analogy. [uncertain: different-tone sub-types inferred]

| Wada term | Our reading | UI meaning |
|---|---|---|
| 明同色調 bright same-tone | related hues, all light, equal strength | airy one-family light theme; text needs a dark neutral from outside the set |
| 暗同色調 dark same-tone | related hues, all dark, similar character | one-family dark theme; text needs a light neutral |
| 淡同色調 pale same-tone | neighbouring hues, same tone, strength lowered | muted low-chroma theme for calm tools and docs; accent must come from a chroma step |
| 濃又深同色調 deep same-tone | strong, dense, deep related colours (Wada cites folk textiles and buildings) | saturated brand-heavy sections; poor for long reading surfaces |
| 汎同色調 pan same-tone | related hues mixing light, dark, pale and deep freely ("pan" from Greek) | the classic single-hue ramp (50–950) of a design system |
| 明異色調 bright different-tone | unlike hues, all light | light multi-hue sets: tags, category fills on light ground |
| 暗異色調 dark different-tone | unlike hues, all dark | dark multi-hue sets for dark mode surfaces |
| 淡異色調 pale different-tone | unlike hues, all muted | muted categorical palettes, quiet charts |
| 濃又深異色調 deep different-tone | unlike hues, all strong and deep | bold posters, expressive landing pages |
| 汎異色調 pan different-tone | unlike hues across all lightness and strength | full palette with distinct roles; hardest to control |

How the skill uses this: classify a chosen plate into one row, then pick the matching strategy:
same-tone rows for Restrained palettes, different-tone rows for Full-palette work. Wada's kimono example
runs from a sky-blue coat through an ultramarine robe and greenish sash to a yellowish-green collar, so
"same" means a family of related colours, not one hue (p. 21 / PDF 23): a restrained palette may drift to
neighbouring hues (any hue tolerance number is our own choice). Merging or breaking the families is
allowed but needs long experience with colour quantity and quality (p. 21 / PDF 23), and for dress,
interiors and furniture the pan same-tone approach is safe and easy while different-tone combination is
truly difficult but offers more interest (pp. 21–22 / PDF 23–24). How the skill uses this: default to the
restrained (same-tone) strategy; offer the full-palette (different-tone) one when the user wants character,
and give mixed or rule-breaking palettes the stricter checks (proportion preview, contrast on every pair).

## 3. Colour quality, material and ground: 色質、色材と生地との関係 (pp. 22–23 / PDF 24–25)

Colours differ in quality, transparent or opaque, warm or cool, and warmth varies inside a hue family
(some greens read warm, a canary yellow is cooler than turmeric or kerria yellows) (p. 22 / PDF 24). The
same colour becomes oil, watercolour or dye, and turns transparent when thinned with water, opaque when
thinned with white (p. 22 / PDF 24). The same colour and material dyed on silk, cotton or hemp gives
clearly different results, and a sensitive eye always notices (pp. 22–23 / PDF 24–25).

How the skill uses this: warm/cool is computed per colour from its value, not assumed from its name; a
tint made by alpha over the background and a tint mixed toward white are different colours, so tokens use
solid mixed values and alpha is kept for overlays and states; the page background is the ground, every
palette is judged on its real background, and a dark mode is a new ground, so it is recomposed rather
than inverted.

## 4. Quantity of colour: 彩色の量と配色 (pp. 23–24 / PDF 25–26)

**4.1 Quantity means area, and equal amounts are rare.** Quantity is the area of each applied colour;
the book shows every swatch at equal area only for convenience (p. 23 / PDF 25). In real dress or design,
colours in equal amount and identical shape should usually be avoided (p. 23 / PDF 25). In a woman's
kimono the collar shows a tiny amount, the robe and outer coat take most of the area, the sash comes next
(p. 23 / PDF 25). How the skill uses this: a plate's equal swatches say nothing about proportion; every
palette gets explicit proportion targets (the percentages are our convention, not Wada's) on a dominant /
secondary / accent ladder, and for a triad the skill decides which colour plays the tiny "collar".

**4.2 Test proportions with cut-out windows.** Wada supplied cut cards (a triangle, a rectangle and a
wave) to lay over the plates and vary shape and quantity, calling this the most direct route to a good
combination (pp. 23–24 / PDF 25–26); with the triangle on a three-colour plate the narrow tip gives the
collar, then robe, then sash or coat. [uncertain: the exact placement of the triangle is not fully
explicit] How the skill uses this: before handing over, the skill renders a proportion preview (a mock
layout at target areas) so the user judges the palette at its real ratios.

**4.3 Large areas look weaker; the white mount is a colour.** A colour spread over a large area looks
much paler and weaker than the small chip (pp. 23–24 / PDF 25–26; some modern studies report the
opposite, so either way a chip does not predict a wall). Treat the white album paper as a white swatch
and study its combinations with each chip too (p. 24 / PDF 26). How the skill uses this: background and
large-surface colours are previewed at full size, never chosen from a small swatch; the page background
counts as a palette member with its own area share and its own contrast checks against every role.

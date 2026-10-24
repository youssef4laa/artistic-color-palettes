# Albers principles for UI colour

Source: Josef Albers, *Interaction of Color*, 50th anniversary edition (Yale University Press,
2013). Everything below paraphrases his ideas in our words, cited by chapter (roman numerals as in
the book). No plates, exercises or figures are reproduced. Numbers in the **Rule** and **Verify**
parts are this skill's working thresholds in OKLCH / WCAG 2 / APCA, not Albers': he taught by eye.

Use this file when assigning palette roles, building ramps, checking dark mode, or explaining why
a palette that looked fine as swatches fails in a layout. `L`, `C`, `h` are OKLCH lightness (0–1),
chroma and hue (degrees); `ΔL` is the absolute difference in L. A "surface" is any role that other
roles sit on (page, card, panel).

## Index by validator flag

Each `validate.py` flag maps to one principle below; read that section (line numbers are exact for this file) rather than the whole file.

| Flag or question | Principle | Starts at line |
|---|---|---|
| vibrating | 12 Contrasting hues at equal lightness vibrate | 201 |
| vanishing (adjacent fills) | 13 Related hues at equal lightness lose their boundary: the mid-lightness trap | 216 |
| mid-lightness fill | 13 Related hues at equal lightness lose their boundary: the mid-lightness trap | 216 |
| state_sibling (faint hover / pressed) | 3 A ground subtracts its own hue and lightness | 62 |
| cvd (colour as the only signal) | 2 Lightness has to be measured, not judged by eye | 49 |
| translucent token | 5 Translucency is an illusion of overlap; stacked layers are unpredictable | 90 |
| dark-mode intervals, order flips | 7 Relationships survive a change of key if intervals are kept | 123 |
| ramp step spacing | 10 Equal-looking steps need unequal physical steps | 170 |
| neutral tint / temperature | 11 Warm and cool are relative and unreliable as structure | 187 |
| quantity, accent share | 9 Quantity is part of the colour | 153 |
| line colours (borders, grid) | 6 Change the thin, recurring colour and the whole changes | 109 |
| a colour looks different per surface | 1 A colour has no fixed appearance; its ground decides | 34 |
| grey on a saturated surface | 4 Neighbours push each other toward the opposite | 76 |
| midpoint tokens | 8 The true middle is equidistant in lightness and hue | 139 |

## 1. A colour has no fixed appearance; its ground decides (ch. IV, VI, XXV "Relativity")

- **Principle.** The same colour looks different depending on what surrounds it, shifting in
  lightness and hue at once; a large surrounding area does most of the changing (IV). A colour set
  between two grounds can even look like two colours, each echoing the opposite ground (VI). Albers
  calls colour "the most relative medium in art" (Introduction).
- **What it predicts.** An accent used on the page, on a card and on a tinted panel looks like three
  slightly different colours. Small elements on large fields shift most. A divider or mid-tone
  between two surfaces may seem to belong to one of them.
- **Rule for the skill.** Judge each role only on the surfaces it will sit on, never in isolation.
  Keep a "sits-on" list per role in the token table; small, high-recurrence roles (badges, links,
  focus rings) are checked on every surface in that list.
- **How to verify.** The validator computes contrast and ΔL for every (role, surface) pair in the
  sits-on lists. The preview shows each accent on each surface, side by side.

## 2. Lightness has to be measured, not judged by eye (ch. V, XXIII)

- **Principle.** Most people cannot tell which of two colours is lighter when their hues differ; in
  Albers' class tests most answers were wrong (V). Photographs also push lights and darks apart and
  lose the middle greys (V).
- **What it predicts.** A designer will be sure a yellow and a blue differ in lightness when they
  nearly match, or the reverse. Screenshots and exports can misstate mid-tones.
- **Rule for the skill.** Every lightness decision is made in numbers: OKLCH L for structure, WCAG 2
  ratio and APCA Lc for legibility. "Looks dark enough" is never accepted. The token table names
  the L value of every ramp step.
- **How to verify.** Script: report L, C, h for every token. Preview: a greyscale render (C set to 0,
  L kept) so the lightness structure is visible without hue.

## 3. A ground subtracts its own hue and lightness (ch. VII)

- **Principle.** A ground takes away from the colours on it whatever it has itself: its hue, and its
  lightness. So two different colours can be made to look alike by setting each on a ground that
  removes their difference (VII).
- **What it predicts.** A brand-blue link on a blue-tinted panel looks greyer and weaker. Hover and
  selected tokens that differ mainly in a hue close to the surface's collapse into one. Used well,
  tinting neutrals slightly toward the surface hue makes them read as clean.
- **Rule for the skill.** When an accent's hue is within 30° of its surface's hue, separation must
  come from lightness (ΔL ≥ 0.25 for text-bearing accents), not from more chroma. Sibling state
  tokens differ by ΔL ≥ 0.06 on every shared surface and also carry a non-colour cue.
- **How to verify.** Script: for each sibling pair on each shared surface, compute ΔL and hue
  difference; flag pairs below the floor. Preview: state tokens shown on the tinted surface.

## 4. Neighbours push each other toward the opposite (ch. VIII, XV, XXV "Factual-Actual")

- **Principle.** After staring at a colour the eye sees its complement, and the same mechanism works
  all the time between neighbours (simultaneous contrast). Albers treats it as the root of nearly
  every colour illusion, and no trained eye is immune (VIII, XV).
- **What it predicts.** Pure-grey text or icons on a saturated surface take a cast of its complement
  (grey on strong orange reads bluish). A large high-chroma hero or modal leaves an after-image
  when it closes. A neutral beside a vivid fill looks tinted.
- **Rule for the skill.** Neutrals on or beside a surface with C > 0.10 get a slight tint toward that
  surface's hue (C 0.005–0.02, same h) to cancel the induced cast. Reading surfaces stay at
  C ≤ 0.04; vivid colour goes on bounded areas, not behind body text.
- **How to verify.** Script: flag any neutral role (C < 0.02) placed on a surface with C > 0.10, and
  any body-text surface with C > 0.04. Preview: grey elements on the most saturated surface.

## 5. Translucency is an illusion of overlap; stacked layers are unpredictable (ch. IX–XI, XVII)

- **Principle.** A colour where two shapes overlap reads as a transparent mixture only if it sits
  believably between its two parents; which parent seems on top depends on which one it leans
  toward (IX, XI). Mixtures of reflected colour lose light (X), and thin tinted layers that stack
  keep getting darker and deeper (XVII). Soft boundaries read as closeness, hard ones as separation,
  and so they create space (XI).
- **What it predicts.** A translucent token (`rgba` scrim, glass panel, hover tint) has no single
  colour: the result depends on what lies beneath, so text contrast on it changes from screen to
  screen. Stacked translucent layers (modal over drawer over tinted card) produce a colour nobody
  chose and a contrast nobody measured.
- **Rule for the skill.** Text-bearing roles are opaque. Translucency is for scrims, hover/press
  tints and decorative glass only, with at most one translucent layer under any text. Contrast on a
  translucent layer is computed on the flattened colour over every surface beneath it, and the worst
  case is reported. For elevation prefer opaque surfaces stepped by ΔL 0.02–0.05 over alpha.
- **How to verify.** Script: alpha-composite each translucent token over each surface in its
  sits-on list, in gamma-encoded sRGB as browsers do, then run WCAG and APCA on the result and
  report the minimum. Flag any text over two or more translucent layers.

## 6. Change the thin, recurring colour and the whole changes (ch. XII–XIII)

- **Principle.** Small, evenly spread colours are not seen separately; the eye merges them with their
  neighbours (optical mixture, XII). In the Bezold effect, changing one colour that recurs through
  a pattern alters how every other colour in it looks (XIII).
- **What it predicts.** Border, gridline, table-rule, chart-stroke and icon-line colours change how
  light or dark the whole interface feels. Swapping near-black rules for near-white ones makes every
  fill look lighter, most of all in dense tables and charts and at a distance.
- **Rule for the skill.** Line roles (`border`, `divider`, `grid`, `stroke`) are palette-level
  decisions, set before fills are tuned. In dense views keep them within ΔL 0.10–0.20 of the
  surface unless strong separation is intended; tune fills with the final line colour in place.
- **How to verify.** Preview: render the dense mini-layout at full size and as a 25% thumbnail for
  each candidate line colour. Script option: average each thumbnail in OKLab and report the L shift.

## 7. Relationships survive a change of key if intervals are kept (ch. XIV)

- **Principle.** A tune stays recognisable in any key because its intervals stay the same. Colours
  have intervals too, chiefly in lightness, and a group keeps its character when moved higher or
  lower so long as the steps between members, and so their boundaries, stay alike (XIV). Very small
  shifts of key give a veil-like film effect (XIV, XVII).
- **What it predicts.** A dark mode made by inverting L reverses or squashes the intervals and the
  palette changes character. A dark mode that keeps the order and spacing of roles reads as the
  same palette in a lower key.
- **Rule for the skill.** Compose dark mode, never invert. Keep the role order by L where the design
  depends on it. Keep accent/surface and surface/surface ΔL within ±0.05 of the light-mode value
  where gamut allows; text/surface pairs keep their order and pass the gate (their interval widens
  with the dark table). Lower chroma rather than distort intervals.
- **How to verify.** Script: build the ΔL matrix of role pairs in both modes; report pairs whose ΔL
  moves by more than 0.05 or whose order flips unexpectedly. Preview: one layout, both modes.

## 8. The true middle is equidistant in lightness and hue (ch. XI, XV)

- **Principle.** A colour meant to sit between two others is very hard to place. If it leans toward
  one parent it seems to belong to it and to lie above or below the other; only a true middle,
  equally far from both in lightness and hue, looks flat and like a colour of its own (XI, XV).
- **What it predicts.** Intermediate tokens (hover between rest and pressed, a border between two
  surfaces, the step between surface and accent) mixed in sRGB come out too dark or dull and read
  as belonging to one side.
- **Rule for the skill.** Compute intermediate tokens in OKLab/OKLCH, never sRGB. A token declared
  as the midpoint of two roles has L within ±0.01 of their mean and h on the shorter arc between
  them; any gamut compromise is reported.
- **How to verify.** Script: for each declared midpoint, report its L and h error against the
  parents' midpoint.

## 9. Quantity is part of the colour (ch. XVI, XXIV)

- **Principle.** Harmony charts show every member in equal amount and shape, once each: the least
  realistic way to judge them, since real use changes colours through area, recurrence, shape,
  light and neighbours (XVI). Quantity has two sides, extent of area and frequency of recurrence,
  and together they set dominance (XVI). Albers cites Schopenhauer's wheel, which gives the lightest
  colour the smallest share and the darkest the largest (XVI, XXIV). With fitting quantities almost
  any colours work together, and dissonance is as legitimate as consonance (XVI, XXIV).
- **What it predicts.** A palette approved from equal swatches turns loud or muddy in a layout where
  one colour takes most of the screen. An accent repeated on every row stops being an accent.
- **Rule for the skill.** Every role gets an area target from the strategy table in
  `style-recipes.md` (accent ≤ 8%, ≤ 5% when C ≥ 0.15). The lightest or most saturated colour gets
  the smallest area. Recurrence counts: an accent marks one primary action or idea per view. A palette
  is never rejected for failing a colour-wheel scheme; it is judged in proportion.
- **How to verify.** Preview script: measure each role's share of painted area in the mini-layout
  against its target and count accent occurrences per view; flag an accent over target.

## 10. Equal-looking steps need unequal physical steps (ch. XX)

- **Principle.** Adding equal physical amounts of a colour does not give equal-looking steps: each
  addition shows less than the last until change seems to stop (XX). The Weber–Fechner law says
  steps that look equal need a geometric physical progression (XX). When steps look even, the
  boundaries between neighbours stay equally crisp; when not, they soften toward one end (XX).
- **What it predicts.** Ramps built by equal sRGB steps, equal mix percentages with black or white,
  or equal luminance steps bunch at one end (several near-identical darks or lights) and leave a
  gap elsewhere. Adjacent steps that are too close are useless as distinct roles.
- **Rule for the skill.** Space ramp steps in OKLCH L, which already models the eye's compressive
  response; never by sRGB channels or luminance. Steps follow the ramp table in
  `application-rules.md` (deliberately finer at the light end, where surfaces and hovers live);
  consecutive steps are at least ΔL 0.03 apart, including at the light and dark ends.
- **How to verify.** Script: list ΔL between consecutive steps; flag any pair below 0.03 and any
  step that departs from the ramp table by more than 0.02. Also report the WCAG ratio between
  neighbours: it should change smoothly, without jumps.

## 11. Warm and cool are relative and unreliable as structure (ch. XXI)

- **Principle.** Temperature is only a comparison: there are warm blues and cool reds. Greens and
  violets sit near neutral, and warm/cool is tangled with light/dark. Theories that warm advances
  and cool recedes have produced disputes rather than rules, and what the eye registers optically
  need not match what we perceive (XXI).
- **What it predicts.** A "warm grey" looks warm only beside cooler colours and may look neutral or
  pink elsewhere. Temperature alone will not signal depth or hierarchy consistently.
- **Rule for the skill.** Choose one temperature for the neutral family and hold it: one hue (±10°)
  at C ≤ 0.03 across the neutral ramp. Make ground/accent temperature contrast deliberate, and back
  hierarchy and elevation with lightness, never warmth alone.
- **How to verify.** Script: report the neutral ramp's hue spread and max C; flag spread over 10° or
  C over 0.03. Check every elevation level differs from its neighbour in L.

## 12. Contrasting hues at equal lightness vibrate (ch. XXII)

- **Principle.** Where strongly different hues meet at nearly the same lightness, the edge seems to
  flicker, double or glow, with illusory light and shadow along it. It varies between viewers and
  with focus, depends on the amounts of figure and ground, feels aggressive, and is mostly avoided
  outside loud advertising (XXII).
- **What it predicts.** Red on green, magenta on teal or blue on orange at similar lightness shimmers
  and tires the eye even though the hues look "high contrast". WCAG usually fails such text, but
  adjacent fills (chart segments, a button on a coloured band) escape text checks.
- **Rule for the skill.** Never place text on a background, or two adjacent fills, with hue
  difference ≥ 100°, both C ≥ 0.10 and ΔL < 0.15. A requested poster-style vibration stays in
  decorative areas, never body text, separated from reading areas by a neutral gap.
- **How to verify.** Script: scan every adjacent pair (text/bg and fill/fill from the layout's
  adjacency list) for this condition and flag it separately from the WCAG/APCA result.

## 13. Related hues at equal lightness lose their boundary: the mid-lightness trap (ch. XXIII)

- **Principle.** The opposite case: two neighbouring, related hues at truly equal lightness make the
  edge between them nearly disappear (XXIII). True equality is rare, and people often call colours
  equal in value when they are not, or think they differ when they do not (XXIII).
- **What it predicts.** Two related mid-tone fills (terracotta and ochre, sage and teal) are told
  apart by hue only, so in greyscale, under colour-vision deficiency and at a glance the edge is
  gone. Mid-lightness is also the trap for text. Computed for neutrals: near L 0.56 neither black
  nor white text exceeds about 4.6:1 (WCAG); across L 0.46–0.67 neither reaches 7:1; across
  L 0.54–0.83 neither reaches APCA Lc 75; across L 0.65–0.73 neither reaches Lc 60. Chromatic
  fills behave similarly but must be measured.
- **Rule for the skill.** Text-bearing fills (buttons, chips, banners) avoid L 0.50–0.70 unless the
  measured pair passes; the text colour is chosen by measurement, not "dark fill, white text".
  The gate is WCAG 2 (body ≥ 4.5:1, large text ≥ 3:1, meaningful boundaries and non-text UI
  ≥ 3:1); APCA Lc is the target reported beside it (body 75, large 60 or 45 by size, non-text 45)
  — see the contrast section of `application-rules.md`. Adjacent fills that must stay distinct need ΔL ≥ 0.10 or a
  stroke. Deliberate vanishing (soft grouping) is for decoration only.
- **How to verify.** Script: WCAG 2 and APCA on every text/surface pair, ΔL on every adjacent fill
  pair, and a flag for text-bearing fills in L 0.50–0.70. Preview: greyscale render.

## Side notes from other chapters

- **Colour names mislead (ch. I).** Colour memory is poor and everyday names are few, so one name
  calls up very different colours. The skill always carries hex and OKLCH with any name.
- **Sampling the masters (ch. XIX).** Albers re-made paintings in paper to catch their climate, not
  their pigments, and notes that printed reproductions are already a different set of inks, often
  too bright. Painting palettes are approximations of a reproduction: label them so, and judge them
  by mood and proportion.
- **Systems come last (ch. XVI, XXIV).** Complementary, triad and tetrad schemes are vocabulary, not
  recipes; no system can precalculate light, material and neighbours. The skill uses them to
  describe a palette, never as a pass/fail test.

## What Albers does not give us

- **No accessibility thresholds.** He does not discuss low vision, colour-vision deficiency or
  minimum contrast. WCAG 2 ratios, APCA Lc and CVD simulation come from those standards; his ideas
  only predict where those checks will fail.
- **No numbers for screens.** His studies use opaque paper in daylight. The OKLCH values, ΔL floors,
  area targets and alpha compositing above are our translations, to be tuned by measurement.
- **No palette recipe.** He refuses rules for harmony on purpose. The role table, proportion targets
  and ramps are the skill's own method; Albers explains why they must be checked in context.
- **No emissive light or dark mode.** His remarks on additive mixing (X) are brief; the composed
  dark-mode rule (principle 7) is our extension of his interval idea.

## Why the skill previews palettes in a mini-layout

Albers' whole case is that a colour can only be known among its neighbours, in its quantity and
across its boundaries (ch. II, IV, XVI), and that equal swatches are the presentation that tells
you least about real use (ch. XVI). So the skill never approves a palette from bare swatches. It
renders a small layout with real roles at their target areas (surface, card, text, accent, lines,
a dense table or chart) in light mode, dark mode and greyscale, and only then reports the measured
checks above.

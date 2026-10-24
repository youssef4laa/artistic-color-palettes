# NOTICE

Our code and text are MIT licensed, except `references/kasane-no-irome.md`, which is CC BY-SA 4.0
(see below). Third-party material and ideas used by this skill:

## Palette data (colorcombinations.org)

```
Palette data from The Dictionary of Color Combinations (colorcombinations.org),
published by Caslon Media, licensed CC BY 4.0. https://colorcombinations.org/
Wada plate data digitised by Matt DesLauriers (mattdesl),
dictionary-of-colour-combinations, MIT licence.
Original work: Sanzo Wada, A Dictionary of Color Combinations (Haishoku Soukan),
1933–34; modern reprint Seigensha Art Publishing, 2010. Public domain.
Painting palettes sampled by colorcombinations.org from public-domain artworks;
see each painting's page for the work's licence status and sources.
```

- Snapshot date 2026-10-22; see `data/SNAPSHOT.md` for source URLs and checksums.
- Sanzo Wada's 348 plates (Vol. 1, 1933–34) are public domain. Wada's Vol. 2 (2020) is not included.
- The digitisation of the plates is by mattdesl, MIT licence
  (https://github.com/mattdesl/dictionary-of-colour-combinations). The copyright line and permission
  text below are copied exactly from that repository's `LICENSE.md` (master branch), as the licence
  requires for copies of the data:

```
The MIT License (MIT)
Copyright (c) 2020 Matt DesLauriers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
```

- The 30 editorial palettes, the painting palette sampling, tags and writing are CC BY 4.0, credit
  colorcombinations.org. Colour names and hex values are facts.
- This skill is not affiliated with Seigensha, the Wada estate or colorcombinations.org and does not
  describe itself or the data as official.
- Generated code credits the source, for example `/* Wada plate 229 via colorcombinations.org (CC BY 4.0) */`;
  for kasane palettes the credit is the courtesy line described under "Kasane no irome".

## Kasane no irome

- Base colour names and hex values come from Wikipedia, "Traditional colors of Japan"
  (https://en.wikipedia.org/wiki/Traditional_colors_of_Japan), licensed CC BY-SA 4.0.
- `references/kasane-no-irome.md` (short form: vocabulary, rules and the pattern index) and the full pattern
  source it is built from, `data-raw/kasane-no-irome.md` on the repo's `sources` branch, are licensed CC BY-SA 4.0
  (https://creativecommons.org/licenses/by-sa/4.0/).
  The 33 kasane rows in `data/palettes.csv` derive from it and carry the licence label
  `CC-BY-SA-4.0 (base hex) + own composition`. Share-alike applies to that file and to those data
  rows, and to adaptations of them. It does not extend to a user's project: the CSS and `DESIGN.md`
  this skill generates for a kasane palette carry a courtesy credit ("base colours after Wikipedia,
  CC BY-SA 4.0"), not a `Licence:` line, because a handful of hex values in a stylesheet are facts
  about colours, the same position taken for the colorcombinations.org values above.
- Pattern recipes follow Heian court records as compiled in secondary sources, chiefly Anthony J. Bryant,
  *Kasane no Irome* (sengokudaimyo.com). Only the historical recipes are restated, in our own structure;
  that page's text and charts are not reproduced. Hex values are interpretations.

## Colour science and standards

- OKLab / OKLCH: Björn Ottosson, "A perceptual color space for image processing" (the matrices are
  published constants). WCAG 2 contrast: W3C. APCA-W3 (0.0.98G-4g): Myndex / Andrew Somers, algorithm
  re-implemented from the published description. Colour-vision-deficiency matrices: Machado, Oliveira and
  Fernandes (2009). All implemented from the formulas in `scripts/colorlib.py`.

## Books

- Josef Albers, *Interaction of Color*, and Sanzo Wada, *A Dictionary of Color Combinations* (Seigensha
  reprint): ideas, rules and numbers are restated in our own words with page or chapter citations. No
  plates, diagrams, exercise layouts or long quotations are reproduced.

## Design ideas from other skills (ideas only, no code copied)

- better-colors (MIT): OKLCH ramp construction, chroma as a share of the gamut ceiling, finer steps at the
  light end, composed dark mode.
- UI/UX Pro Max (MIT, Next Level Builder): BM25 search over a CSV, zero-result discipline, semantic
  colour roles with paired on-colours, a data validator.
- Theme Factory (Apache-2.0): a theme as a short named list of colour roles.
- Impeccable (Apache-2.0): colour strategy names (Restrained, Committed, Full palette, Drenched), modes,
  the DESIGN.md `## Colors` entry format, tinted neutrals, "do not invert for dark mode".
- Taste, interface-design, Design Principles: token names only, used for alias blocks in `design/tokens.css`.

## Code provenance

No third-party code is copied into this skill. Every script is written from scratch in Python
(standard library only) from published formulas and from design ideas listed above.

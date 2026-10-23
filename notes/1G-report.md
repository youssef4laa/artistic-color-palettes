# 1G report: plate proportion mining (Wada four-colour plates 241-348)

## Bottom line

**Don't ship the data as proportions.** The measurement is clean, but it shows there is nothing to
mine. Every four-colour plate is four identical rectangles (a cross: one on top, two side by side
in the middle, one below). Each colour covers 25% of the swatch, plus or minus 1%. The two- and
three-colour plates are equal-width bands as well (looked at a handful by eye). The book encodes
*which* colours go together, not *how much* of each. The skill should not claim that Wada's plates
give per-colour area ratios. Proportion rules for UI need another source (60/30/10-type guidance,
or our own design judgement) and should be labelled as ours. If anything ships, ship only this one
fact in prose: "in the four-colour plates, all four colours are shown at equal area".

`data-raw/wada-proportions.csv` is written (432 rows = 108 plates x 4), but its `area_share`
column is noise around 0.25 (range 0.232-0.265, sd 0.005). It should stay in `data-raw/` and not
go into the skill's data.

## Page range and layout (confirmed, differs from the task's guess)

- Four-colour plates 241-348 are on **PDF pp. 152-259** (PDF page = plate number - 89). Not 175-335.
  Plate 240 is on PDF p. 151; the website lists exactly 108 four-colour wada rows (241-348) and no others.
- One plate per page. The plate number is printed small at the top-left; the printed page number
  is at the bottom corner (plate 263 = PDF p. 174 = printed p. 172). The colour names are printed
  under the swatch (top, middle-left, middle-right, bottom).
- The website's `hex_1..hex_4` order is not the position order. Plate 241 is Red Orange (top),
  Pale Lemon Yellow (middle-right), Isabella Color (bottom), Dark Medici Blue (middle-left).
  So colours have to be matched to positions by colour, not by order.
- The middle bar sits visually over a vertical bar; the top and bottom rectangles are the visible
  parts above and below it.
- The PDF page is 271.6 x 407 pt with a 1358 x 2035 px scan embedded (about 5x).
  The PDF also carries a poor OCR text layer (usable only to read plate numbers such as "348").

## Method (`data-raw/1G/mine.py`, numpy + scipy + Pillow + pypdfium2; build-time only)

1. Render at scale 3.0 (815 x 1221 px). Keep the top 60% of the page, since the names are below.
2. Paper colour is the median of the top 2% of rows, in OKLab. The swatch mask is every pixel
   with OKLab distance > 0.045 from paper. Then one binary opening, drop components smaller than
   0.4% of the page (page number, margin rule, specks), drop components touching the left or
   right page edge (scan shadow; this caused the first failures), and fill holes.
3. Geometry (authoritative). The middle row is the longest run of rows wider than 0.8 x the
   maximum row width. The top region is the mask above it, the bottom region the mask below it.
   The middle row is split into left/right at the strongest colour step in its central
   30-70% (column-mean OKLab change over 3 px). Area share = pixels per region / total mask pixels.
4. Each region's colour is the median OKLab over the mask eroded by 3 px. Regions are matched to
   the website's 4 hex colours by optimal assignment (all 24 permutations, minimum summed OKLab
   distance); `color_index` is the website order.
5. Independent cross-check: per-plate k-means (k = 4, k-means++, 8 restarts, eroded pixels), with
   rim pixels given the label of the nearest interior pixel so the blended edge cannot inflate
   one cluster. Its shares are compared with the geometric ones (`agree` = max absolute
   difference).
6. A first version using k-means alone put shares at 0.20-0.29 on plates 245, 249 and 337 (two
   dark colours merged, or the page-edge shadow became a cluster). Geometry fixed that. The final
   geometric and k-means shares agree to within 0.045 on every plate (median about 0.01).

### Confidence (0-1, per plate, same for its 4 rows)

Minimum of five terms, each clipped to [0,1]:
(a) worst colour match to the website hex: 1 at OKLab dist 0.08, 0 at 0.25 (scans drift, so even
good plates sit near 0.10-0.12); (b) assignment margin between the best and second-best
permutation, 1 at >= 0.08; (c) every region is one solid blob (>= 0.99); (d) region spread
(max - min share) <= 0.02; (e) k-means agrees within 0.02.
It mainly measures *how sure the colour-to-index mapping is*. The shares barely depend on it
because the four areas are equal.

## Results

- 108/108 plates analysed, 0 outright failures (no plate without a swatch).
- Rectangle size across all 108 plates: middle bar 639.6 px wide (sd 2.6), each rectangle 320.5 px
  wide (sd 3.1) by about 155 px high (sd about 2). Mean positional shares: top 0.254, left 0.247,
  right 0.247, bottom 0.252. The +0.5% on top/bottom is the scanner halo and edge fringe, not a
  design difference.
- All 432 shares are in 0.232-0.265. The per-plate max-min spread is at most 0.027.
- Confidence distribution (108 plates): min 0.01, p10 0.41, p25 0.69, median 0.78, p75 0.85,
  p90 0.92, max 1.00. Bins: <0.3: 7, 0.3-0.5: 7, 0.5-0.7: 14, 0.7-0.9: 61, >= 0.9: 19.
- The 9 plates under 0.35 (245, 270, 278, 289, 292, 306, 309, 318, 337) are all cases where two
  rectangles are similar dark or muted colours (slate/navy, wine/burgundy, black/dark green). The
  colour-to-index mapping is ambiguous there, but the shares are fine (rectangles are equal
  anyway). 10 plates have margin < 0.03.

## Spot-checks (10 plates, rendered page vs. recoloured label map, by eye)

| Plate (PDF p.) | Conf | Shares in hex order | Verdict |
|---|---|---|---|
| 241 (152) | 0.77 | .256 .241 .263 .241 | agree: 4 equal rectangles, regions correct; slight halo over the middle bar's top edge |
| 252 (163) | 0.84 | .253 .254 .248 .245 | agree: crisp cross; colours match |
| 263 (174) | 1.00 | .244 .259 .255 .243 | agree: slate/red-brown middle bar and pale top/bottom all found |
| 274 (185) | 0.90 | .248 .254 .249 .249 | agree: olive, violet, orange, blue match positions |
| 285 (196) | 0.87 | .256 .249 .247 .247 | agree: the very pale top and bottom (mauve, mint) are captured in full |
| 296 (207) | 0.77 | .241 .250 .256 .253 | agree: dark bottom rectangle fully included |
| 307 (218) | 1.00 | .248 .247 .255 .250 | agree: plum/lilac/red/violet correct |
| 318 (229) | 0.31 | .259 .254 .242 .245 | shares agree (equal rectangles); colour-to-index mapping uncertain: two dark greens and a near-black are close |
| 337 (248) | 0.01 | .251 .256 .246 .248 | shares agree; mapping uncertain: top and left are both burgundy, so indices 1/2 could swap |
| 348 (259) | 0.55 | .257 .243 .242 .258 | agree on areas; dark forest green vs near-black in the middle bar is a close call |

No spot-checked plate had an area disagreement with the render. In every one the four rectangles
look equal to the eye and to the numbers.

## Failures and caveats

- Early run: page-edge scan shadow (plate 245 and others) was mistaken for swatch. Fixed by
  dropping edge-touching components. Two close dark colours merged in k-means (245, 249, 337).
  Fixed by using geometry as the primary method.
- The website's hex values are idealised, not scan colours; median best-match distance is 0.114 in
  OKLab. Confidence is therefore capped and mostly informative for ordering plates, not as an
  absolute score.
- 2-/3-colour plates (PDF pp. ~58-150) were looked at by eye only, six pages: equal-width bands.
  Not measured.
- Source renders are in `notes/wada-pages/1G/` (git-ignored); only the derived CSV leaves it.

## Files

- `D:\Code\Skill\artistic-color-palettes\data-raw\wada-proportions.csv` (do not ship)
- `D:\Code\Skill\artistic-color-palettes\data-raw\1G\mine.py`, `diagnostics.csv`, `palettes.csv`, `run.log`
- Debug overlays and spot-check sheets: `notes\wada-pages\1G\` (git-ignored)

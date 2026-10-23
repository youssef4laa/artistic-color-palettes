# 1B snapshot report (2026-10-22)

## CSV headers
- palettes.csv: slug,title,title_ja,summary,dominant_hue,moods,era,color_count,hex_1,color_1,color_1_ja,hex_2,color_2,color_2_ja,hex_3,color_3,color_3_ja,hex_4,color_4,color_4_ja,canonical_url,api_url,embed_url,og_url (moods are pipe-separated, e.g. refined|solemn|bold)
- colors.csv: slug,name,name_ja,meaning,hex,rgb_r,rgb_g,rgb_b,hue,palette_count,canonical_url,api_url
- collections.csv: slug,title,tagline,accent_hex,palette_count,keywords,canonical_url,api_url,og_url,embed_url
- studies: color-analysis = category,item,count,share_pct (176 rows); wcag-contrast = category,item,value,detail (21 rows)

## Counts
378 palettes, 210 colours, 71 collections, as documented.

## Wada vs editorial
- Slug prefix `wada-NNN-` : 348 rows, all era `showa`. Plate numbers 1-348, no gaps, no duplicates. Colour count: 120 two-colour, 120 three-colour, 108 four-colour (so 241-348 is 108 plates, consistent).
- Everything else: 30 rows, none start with `wada-`, none are `showa`. Eras: edo 12, heian 8, muromachi 5, kamakura 4, meiji 1. Colour count: 24 three-colour, 6 four-colour.
- Rule is clean both ways: source_type = wada_plate iff slug starts with `wada-` iff era == showa.

## Paintings
No separate JSON URL exists. The "Download JSON" button builds a Blob from an inline `<script type="application/json" data-payload="json">` block; no `<link rel=alternate>` and no .json href on the page. IMPORTANT: that export contains only source, slug, title, era (always "edo"), empty moods and a bare hex list; it has no roles and no coverage. Roles and coverage exist only in the page HTML (swatch markup), so each `paintings/<slug>.json` stores the verbatim export plus `swatches_from_page` (hex, role, coverage text), and the two hex lists match in order for all 25.
All 25 pages: 3 ground + 3 accent, coverage present on all six. Coverage is a rounded integer percent or the string "<1" (so it is not numeric for the smallest accents). Swatch order on the page is not grouped by role (mixed). Examples of ground coverage: Great Wave 34/17/5, Night Watch 18/27/27, Third of May 6/5/30.

## Unexpected
- Python urllib got HTTP 403 without a User-Agent; curl worked.
- Export title contains a dash that rendered as a mojibake char in my console; file is saved as UTF-8 from the raw response, check encoding if it matters.
- Era in painting export is "edo" for the Starry Night (meaningless metadata, ignore).
- A file `data-raw/wada-index.csv` exists that I did not create (another agent).

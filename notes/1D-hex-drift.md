# 1D: Wada CMYK index vs website hex (report only, nothing corrected)

## Method

- **Source of the index.** The printed index in the PDF is not a text list: each colour has a swatch page with plate number, kanji, kana, English name and a CMYK line. Pages used: PDF pp. 285-351 (odd pages only; even pages are blank backs). Rendered at 3.2x (4.5x for doubtful names), read by eye. Result: **159 rows**, nos. 1-159, none missing (distribution 4-5 per page; the red, yellow, green, blue, purple and white/grey/black sections each open with a header).
- **Printed page numbers are not printed** on these swatch pages. `printed_page` in the CSV is `pdf_page - 2`, the offset the brief gives for this scan; treat it as inferred.
- **Files.** `data-raw/wada-index.csv` (transcription), `data-raw/1D/compare.py` (run `python compare.py` from that folder; stdlib only), downloads `palettes.csv`, `colors.csv`, `mattdesl-colors.json` in `data-raw/1D/`.
- **Website data.** The 348 `wada-*` rows of palettes.csv give exactly 159 distinct colour names, each with exactly one hex across all plates. (colors.csv is the site's wider 210-name dictionary, not needed.) mattdesl `colors.json` has 159 entries in the same order as the printed numbers, with name, cmyk and hex; its `swatch` field is a 0-5 column index, not a plate number, so matching to it is by position, confirmed by name for all 159.
- **Matching.** Exact English name (147), then normalised spelling (8: letters only, lowercase, so `Mars Brown/Tobacco` = `Mars Brown Tobacco`, `Deep Violet/Plumbeous` = `Deep Violet / Plumbeous`, plus site misspellings below), then plate number for the two duplicated names (4). Unmatched: none either way.
- **Conversions to sRGB.** `naive`: 255*(1-c)*(1-k). `gcr`: K as a separate solid ink (about sRGB 35,31,32), C/M/Y solids of a SWOP-like press (approximate, quoted values, not a measured profile), total ink limit 300 % (scale down), 12 % dot gain, multiplicative mixing in linear light. It is a coarse stand-in for an ICC profile; its constants were set from published press values, not fitted to the website hex.
- **Distance.** Euclidean in OKLab (Ottosson matrices), 0-1 scale; threshold 0.05.

## Findings

- **The website hex is not derived from the printed CMYK.** It is identical to mattdesl's hex for all 159 colours (dE 0), and mattdesl's values come from the colour chips as printed in the book, not from the CMYK line. So the hexes are scan-sampled, and the CMYK is a separate, rougher record.
- Naive conversion drifts a lot: mean dE 0.071, median 0.060, **98 of 159 above 0.05**, worst 0.232 (greens and blue-greens: naive CMYK gives vivid, out-of-gamut-looking greens, and K=100 gives pure black against the site's #111314).
- GCR/ink-limited conversion is much closer: mean 0.029, median 0.030, **8 of 159 above 0.05**, worst 0.102 (Diamine Green).
- Use of this for the skill: the site hex is the better colour; the CMYK is useful only as a hue/relative-darkness cross-check, and naive conversion must not be used for tokens.

## Transcription doubts

All CMYK values were legible. Doubts are in `reading_note` in the CSV; the substantive ones:

- Names where print is smudged: 15 (Vinaceous Tawny), 19 (Etruscan Red), 52 (Maple; site has the same), 130 (Tyrian).
- Kana read at low resolution: 24, 41, 62, 109, 129, 155.
- Bracketed variant kanji: 1, 124, 131 (second glyphs may differ from my transcription).
- Plate number label cropped at the scan edge for no. 10 (sequence inferred).
- Duplicated English names as printed: Eugenia Red (12, 13), Grayish Lavender (134, 135).
- No. 25 is printed **Rosolanc Purple** (kept as printed; the site agrees; likely the book's own typo).
- Site misspellings against the print (print re-checked at 4x): Ochre Red (21, print Ocher), Pomegranite (26), Sulpher (39), Krongbergs (76), Artemesia (95), Veronia (146, print Vernonia).
- Differences against mattdesl's CMYK (print re-checked at 4.5x; my reading stands): 72 Citrine K 7 (mattdesl 0), 97 Rainette Green K 28 (mattdesl 10), 106 Diamine Green M20 Y100 K10 (mattdesl M32 Y91 K18, which are the printed values of no. 107 Cossack Green), 131 Dull Violet Black M90 (mattdesl M106, impossible).

## Script output

- index rows: 159; site Wada colour names: 159; matched: 159; unmatched index rows: 0; site names unused: 0
- match method: exact=147, normalised spelling=8, number (duplicate name)=4
- site names with more than one hex across plates: 0
- mattdesl entries: 159; matched by position and name: 159

- naive: mean dE_OK 0.0712, median 0.0604, max 0.2322, > 0.05: 98 of 159
- gcr: mean dE_OK 0.0292, median 0.0295, max 0.1025, > 0.05: 8 of 159
- mattdesl hex vs site hex: mean 0.0000, max 0.0000, > 0.05: 0 of 159

## Drift > 0.05 dE_OK, naive conversion (98 colours)

| no | name | CMYK | site hex | naive hex | dE | site L C h | conv L C h |
|---|---|---|---|---|---|---|---|
| 100 | Sea Green | 80/0/51/0 | #00b49b | #33ff7d | 0.232 | 0.69 0.127 178 | 0.88 0.231 150 |
| 106 | Diamine Green | 87/20/100/10 | #1a7444 | #1eb800 | 0.221 | 0.50 0.112 155 | 0.68 0.227 142 |
| 101 | Benzol Green | 100/15/55/0 | #00978d | #00d973 | 0.210 | 0.61 0.107 187 | 0.78 0.201 153 |
| 104 | Dull Viridian Green | 90/20/80/0 | #009465 | #19cc33 | 0.187 | 0.59 0.129 162 | 0.74 0.232 144 |
| 119 | Peacock Blue | 100/19/43/0 | #00939b | #00cf91 | 0.185 | 0.60 0.103 202 | 0.76 0.164 163 |
| 159 | Black | 20/10/15/100 | #111314 | #000000 | 0.185 | 0.18 0.004 229 | 0.00 0.000 0 |
| 117 | Venice Green | 58/0/30/0 | #62c6bf | #6bffb2 | 0.169 | 0.76 0.095 189 | 0.90 0.167 158 |
| 143 | Blue Violet | 72/80/0/0 | #6450a1 | #4733ff | 0.164 | 0.49 0.126 293 | 0.51 0.278 274 |
| 93 | Night Green | 52/0/100/0 | #87c540 | #7aff00 | 0.163 | 0.76 0.175 131 | 0.89 0.267 137 |
| 102 | Light Porcelain Green | 86/22/50/3 | #00908a | #23c17c | 0.157 | 0.59 0.102 190 | 0.72 0.160 158 |
| 103 | Green | 75/21/73/0 | #489b6e | #40c945 | 0.155 | 0.63 0.107 157 | 0.74 0.209 144 |
| 150 | Violet | 85/90/18/0 | #4f4086 | #2619d1 | 0.154 | 0.42 0.113 291 | 0.41 0.253 270 |
| 116 | Calamine Blue | 50/0/20/0 | #78cdd0 | #80ffcc | 0.143 | 0.80 0.083 199 | 0.91 0.135 165 |
| 138 | Eupatorium Purple | 25/79/12/0 | #bf5892 | #bf36e0 | 0.142 | 0.61 0.148 348 | 0.61 0.253 319 |
| 115 | Cobalt Green | 42/0/42/0 | #96d1aa | #94ff94 | 0.138 | 0.81 0.082 155 | 0.91 0.174 144 |
| 140 | Aconite Violet | 39/68/5/0 | #a36aa5 | #9c52f2 | 0.138 | 0.61 0.109 326 | 0.61 0.229 301 |
| 151 | Red Violet | 76/100/25/15 | #59256a | #3400a3 | 0.136 | 0.37 0.124 317 | 0.35 0.212 280 |
| 120 | Green Blue | 82/24/40/3 | #099197 | #2dbc94 | 0.134 | 0.60 0.100 200 | 0.71 0.132 169 |
| 37 | Violet Red | 75/100/50/5 | #642d5e | #3d0079 | 0.131 | 0.39 0.104 332 | 0.31 0.169 296 |
| 91 | Yellow Green | 35/0/72/0 | #afd472 | #a6ff47 | 0.131 | 0.82 0.132 126 | 0.91 0.226 132 |
| 127 | Deep Lyons Blue | 100/85/15/6 | #1c4286 | #0024cc | 0.127 | 0.39 0.122 261 | 0.41 0.248 264 |
| 118 | Cerulian Blue | 84/26/32/0 | #0093a5 | #29bdad | 0.125 | 0.61 0.105 210 | 0.72 0.120 184 |
| 139 | Light Mauve | 43/62/5/0 | #9a72aa | #9161f2 | 0.125 | 0.61 0.094 316 | 0.62 0.208 295 |
| 142 | Dark Soft Violet | 70/68/13/0 | #66629c | #4d52de | 0.121 | 0.52 0.090 286 | 0.52 0.209 275 |
| 10 | Spinel Red | 0/70/21/0 | #f27291 | #ff4dc9 | 0.119 | 0.71 0.159 7 | 0.71 0.244 343 |
| 149 | Violet Carmine | 64/90/70/10 | #713b4c | #531745 | 0.114 | 0.43 0.078 1 | 0.32 0.106 338 |
| 147 | Dark Slate Purple | 64/85/60/10 | #704357 | #53225c | 0.113 | 0.44 0.068 352 | 0.35 0.110 321 |
| 25 | Rosolanc Purple | 30/90/33/0 | #b73f74 | #b219ab | 0.112 | 0.55 0.162 357 | 0.54 0.231 330 |
| 122 | Blue | 95/54/0/0 | #006eb8 | #0d75ff | 0.110 | 0.53 0.143 248 | 0.59 0.223 259 |
| 9 | Eosine Pink | 0/63/23/0 | #f37f94 | #ff5ec4 | 0.109 | 0.73 0.143 10 | 0.72 0.221 345 |
| 137 | Lilac | 28/54/8/0 | #b984af | #b875eb | 0.106 | 0.68 0.087 333 | 0.68 0.178 309 |
| 153 | Dusky Madder Violet | 75/100/46/30 | #4e1d4c | #2d0060 | 0.105 | 0.32 0.099 329 | 0.26 0.143 295 |
| 128 | Violet Blue | 85/79/38/16 | #40456a | #202d85 | 0.100 | 0.40 0.063 277 | 0.35 0.147 270 |
| 141 | Dull Blue Violet | 57/60/17/0 | #80719e | #6e66d4 | 0.099 | 0.58 0.070 300 | 0.57 0.164 283 |
| 92 | Light Green Yellow | 26/5/85/0 | #c7d14f | #bdf226 | 0.096 | 0.83 0.152 113 | 0.89 0.215 125 |
| 88 | Turquoise Green | 29/0/24/0 | #b5decc | #b5ffc2 | 0.095 | 0.87 0.050 167 | 0.94 0.110 149 |
| 99 | Pistachio Green | 64/29/56/6 | #648f7b | #56aa69 | 0.092 | 0.61 0.056 164 | 0.67 0.126 149 |
| 107 | Cossack Green | 76/32/91/18 | #437742 | #328e13 | 0.091 | 0.52 0.099 144 | 0.57 0.174 140 |
| 11 | Old Rose | 15/70/40/0 | #d46d7a | #d94d99 | 0.091 | 0.66 0.130 13 | 0.63 0.190 350 |
| 24 | Indian Lake | 12/89/35/9 | #c53c69 | #cc1a97 | 0.090 | 0.57 0.176 5 | 0.57 0.231 345 |
| 146 | Vernonia Purple | 42/78/46/15 | #8c4c62 | #7e3075 | 0.089 | 0.50 0.090 359 | 0.45 0.139 332 |
| 152 | Cotinga Purple | 66/100/42/40 | #501345 | #340059 | 0.088 | 0.31 0.110 336 | 0.26 0.138 304 |
| 112 | Pale King's Blue | 33/4/7/0 | #a7d4e4 | #abf5ed | 0.087 | 0.84 0.052 222 | 0.92 0.074 188 |
| 71 | Citron Yellow | 35/17/95/0 | #b2b73e | #a6d40d | 0.087 | 0.75 0.141 112 | 0.81 0.198 124 |
| 98 | Chromium Green | 50/16/58/20 | #719470 | #66ab56 | 0.085 | 0.63 0.066 144 | 0.68 0.138 140 |
| 97 | Rainette Green | 42/20/62/28 | #8fa071 | #6a9346 | 0.081 | 0.68 0.069 124 | 0.62 0.116 132 |
| 105 | Oil Green | 53/28/100/8 | #819238 | #6ea900 | 0.080 | 0.63 0.117 119 | 0.67 0.180 130 |
| 113 | Light Glaucous Blue | 35/10/14/0 | #a5c8d1 | #a6e6db | 0.079 | 0.81 0.039 215 | 0.88 0.066 183 |
| 121 | Olympic Blue | 69/44/10/0 | #5a82b3 | #4f8fe6 | 0.078 | 0.60 0.088 254 | 0.65 0.147 257 |
| 136 | Laelia Pink | 20/48/18/0 | #ca92a8 | #cc85d1 | 0.077 | 0.72 0.073 354 | 0.72 0.132 325 |
| 148 | Taupe Brown | 30/70/35/40 | #7a4456 | #6b2e63 | 0.076 | 0.46 0.078 359 | 0.41 0.112 333 |
| 124 | Helvetia Blue | 100/62/19/10 | #005b8d | #0057ba | 0.075 | 0.45 0.109 243 | 0.48 0.172 257 |
| 123 | Antwarp Blue | 100/40/30/10 | #007190 | #008aa1 | 0.075 | 0.51 0.097 225 | 0.58 0.103 215 |
| 6 | Coral Red | 0/55/40/0 | #f58e84 | #ff7399 | 0.075 | 0.75 0.127 26 | 0.73 0.173 5 |
| 89 | Glaucous Green | 30/9/24/0 | #b4cdc2 | #b2e8c2 | 0.074 | 0.83 0.031 167 | 0.88 0.076 154 |
| 111 | Nile Blue | 25/0/10/0 | #bce4e5 | #bfffe6 | 0.073 | 0.89 0.042 198 | 0.95 0.072 169 |
| 27 | Hydrangea Red | 38/90/70/0 | #a94151 | #9e194d | 0.072 | 0.52 0.137 14 | 0.46 0.169 4 |
| 86 | Mars Brown/Tobacco | 39/76/100/47 | #653514 | #522000 | 0.072 | 0.38 0.082 52 | 0.31 0.085 48 |
| 38 | Vistoris Lake | 40/71/55/40 | #6d4145 | #5c2c45 | 0.071 | 0.43 0.061 14 | 0.37 0.078 349 |
| 33 | Hay's Russet | 37/85/87/35 | #793327 | #681916 | 0.070 | 0.41 0.101 32 | 0.35 0.113 27 |
| 1 | Hermosa Pink | 0/30/6/0 | #f9c1ce | #ffb2f0 | 0.070 | 0.86 0.066 3 | 0.86 0.119 334 |
| 87 | Vandyke Brown | 56/71/97/52 | #4b3317 | #362304 | 0.070 | 0.34 0.054 68 | 0.27 0.053 75 |
| 94 | Olive Yellow | 40/30/80/0 | #a6a159 | #99b233 | 0.069 | 0.70 0.094 105 | 0.72 0.151 120 |
| 13 | Eugenia Red | 0/80/50/10 | #da525d | #e62e73 | 0.069 | 0.62 0.170 19 | 0.61 0.220 5 |
| 32 | Brown | 35/74/90/35 | #7c4226 | #6c2b11 | 0.069 | 0.44 0.090 45 | 0.38 0.100 41 |
| 129 | Vandar Poel's Blue | 100/73/43/10 | #064f6e | #003e83 | 0.068 | 0.40 0.082 234 | 0.37 0.129 256 |
| 2 | Corinthian Pink | 0/35/15/0 | #f8b6ba | #ffa6d9 | 0.068 | 0.84 0.077 15 | 0.83 0.122 345 |
| 144 | Purple Drab | 38/65/49/26 | #84565b | #754260 | 0.067 | 0.51 0.062 12 | 0.45 0.081 345 |
| 12 | Eugenia Red | 7/76/60/0 | #e2625e | #ed3d66 | 0.067 | 0.65 0.161 24 | 0.63 0.211 13 |
| 90 | Dark Greenish Glaucous | 30/15/36/0 | #b7c2a9 | #b2d9a3 | 0.066 | 0.80 0.036 127 | 0.84 0.084 137 |
| 85 | Madder Brown | 36/88/100/38 | #762c19 | #651300 | 0.066 | 0.40 0.109 35 | 0.33 0.118 34 |
| 95 | Artemisia Green | 57/28/39/8 | #709390 | #65a98f | 0.065 | 0.64 0.039 190 | 0.68 0.080 168 |
| 7 | Fresh Color | 0/53/45/0 | #f6917e | #ff788c | 0.065 | 0.76 0.126 32 | 0.74 0.165 13 |
| 8 | Grenadine Pink | 0/62/58/0 | #f48067 | #ff616b | 0.065 | 0.73 0.148 33 | 0.70 0.192 20 |
| 21 | Ocher Red | 18/73/63/20 | #ab544d | #a7374b | 0.063 | 0.55 0.115 26 | 0.50 0.147 14 |
| 158 | Slate Color | 85/70/62/30 | #34454c | #1b3644 | 0.063 | 0.38 0.025 225 | 0.32 0.041 233 |
| 83 | Pale Raw Umber | 46/63/87/32 | #71502f | #5e4017 | 0.063 | 0.46 0.065 65 | 0.40 0.070 72 |
| 84 | Sepia | 48/60/100/40 | #644b1e | #503d00 | 0.061 | 0.43 0.070 80 | 0.37 0.076 89 |
| 131 | Dull Violet Black | 100/90/38/50 | #1e0e3f | #000d4f | 0.061 | 0.22 0.088 293 | 0.21 0.120 264 |
| 26 | Pomegranate Purple | 23/100/50/6 | #b71f57 | #b90078 | 0.060 | 0.51 0.187 6 | 0.52 0.215 351 |
| 20 | Burnt Sienna | 22/76/100/15 | #ae5224 | #a93400 | 0.060 | 0.55 0.134 45 | 0.50 0.161 38 |
| 64 | Orange | 0/68/100/0 | #f37420 | #ff5200 | 0.059 | 0.70 0.179 48 | 0.67 0.220 38 |
| 126 | Dusky Green | 100/30/64/50 | #004f46 | #00592e | 0.058 | 0.38 0.069 182 | 0.41 0.103 154 |
| 76 | Kronbergs Green | 48/35/70/12 | #84875e | #759243 | 0.058 | 0.61 0.058 112 | 0.62 0.112 126 |
| 114 | Salvia Blue | 41/25/10/0 | #97acc8 | #96bfe6 | 0.057 | 0.74 0.047 256 | 0.79 0.071 247 |
| 66 | English Red | 13/73/100/0 | #d96629 | #de4500 | 0.057 | 0.64 0.161 45 | 0.60 0.199 38 |
| 19 | Etruscan Red | 16/80/74/6 | #c55347 | #c9303e | 0.056 | 0.59 0.149 28 | 0.55 0.188 21 |
| 15 | Vinaceous Tawny | 17/72/100/6 | #c56127 | #c74300 | 0.056 | 0.60 0.145 47 | 0.56 0.178 40 |
| 28 | Brick Red | 22/84/100/18 | #a84222 | #a32100 | 0.056 | 0.51 0.142 37 | 0.47 0.170 33 |
| 134 | Grayish Lavender | 28/28/0/0 | #b5b1d8 | #b8b8ff | 0.055 | 0.78 0.055 290 | 0.81 0.100 284 |
| 80 | Olive Green | 56/40/85/22 | #6b7140 | #58771e | 0.054 | 0.53 0.070 115 | 0.53 0.120 127 |
| 34 | Vandyke Red | 32/95/95/33 | #82241f | #740909 | 0.053 | 0.41 0.129 27 | 0.36 0.138 28 |
| 68 | Orange Rufous | 18/65/100/8 | #c16b27 | #c05200 | 0.053 | 0.61 0.135 54 | 0.57 0.159 47 |
| 53 | Olive Buff | 16/6/42/12 | #c1c494 | #bcd382 | 0.053 | 0.81 0.064 111 | 0.83 0.108 122 |
| 79 | Sudan Brown | 25/60/65/19 | #a36752 | #9b5348 | 0.053 | 0.57 0.084 40 | 0.53 0.098 30 |
| 65 | Peach Red | 0/80/90/0 | #f15a30 | #ff3319 | 0.051 | 0.66 0.194 36 | 0.65 0.240 31 |
| 56 | Lemon Yellow | 5/0/85/0 | #f8ed43 | #f2ff26 | 0.051 | 0.93 0.178 106 | 0.96 0.208 114 |
| 63 | Apricot Orange | 0/55/75/0 | #f68c50 | #ff7340 | 0.051 | 0.74 0.149 49 | 0.72 0.183 40 |

## Drift > 0.05 dE_OK, gcr conversion (8 colours)

| no | name | CMYK | site hex | gcr hex | dE | site L C h | conv L C h |
|---|---|---|---|---|---|---|---|
| 106 | Diamine Green | 87/20/100/10 | #1a7444 | #478b00 | 0.102 | 0.50 0.112 155 | 0.57 0.166 135 |
| 37 | Violet Red | 75/100/50/5 | #642d5e | #630051 | 0.070 | 0.39 0.104 332 | 0.34 0.148 338 |
| 151 | Red Violet | 76/100/25/15 | #59256a | #5a0062 | 0.053 | 0.37 0.124 317 | 0.33 0.157 324 |
| 117 | Venice Green | 58/0/30/0 | #62c6bf | #96c7c2 | 0.052 | 0.76 0.095 189 | 0.79 0.052 188 |
| 127 | Deep Lyons Blue | 100/85/15/6 | #1c4286 | #00337d | 0.051 | 0.39 0.122 261 | 0.34 0.135 259 |
| 109 | Blackish Olive | 56/32/63/55 | #42533e | #5a5d42 | 0.050 | 0.42 0.040 140 | 0.47 0.041 113 |
| 116 | Calamine Blue | 50/0/20/0 | #78cdd0 | #a6cfd4 | 0.050 | 0.80 0.083 199 | 0.83 0.044 206 |
| 131 | Dull Violet Black | 100/90/38/50 | #1e0e3f | #001740 | 0.050 | 0.22 0.088 293 | 0.22 0.084 259 |

## Unmatched printed-index rows (no site colour found)

- none

## Site names not matched to any index row

- none

## Spelling differences (index vs site name)

- 12: index "Eugenia Red" -> site "Eugenia Red A" (number (duplicate name))
- 13: index "Eugenia Red" -> site "Eugenia Red B" (number (duplicate name))
- 21: index "Ocher Red" -> site "Ochre Red" (normalised spelling)
- 26: index "Pomegranate Purple" -> site "Pomegranite Purple" (normalised spelling)
- 39: index "Sulphur Yellow" -> site "Sulpher Yellow" (normalised spelling)
- 76: index "Kronbergs Green" -> site "Krongbergs Green" (normalised spelling)
- 86: index "Mars Brown/Tobacco" -> site "Mars Brown Tobacco" (normalised spelling)
- 95: index "Artemisia Green" -> site "Artemesia Green" (normalised spelling)
- 134: index "Grayish Lavender" -> site "Grayish Lavender - A" (number (duplicate name))
- 135: index "Grayish Lavender" -> site "Grayish Lavender - B" (number (duplicate name))
- 145: index "Deep Violet/Plumbeous" -> site "Deep Violet / Plumbeous" (normalised spelling)
- 146: index "Vernonia Purple" -> site "Veronia Purple" (normalised spelling)

## CMYK differences between my transcription and mattdesl colors.json

- 72 Citrine: index [36, 32, 100, 7], mattdesl [36, 32, 100, 0]
- 97 Rainette Green: index [42, 20, 62, 28], mattdesl [42, 20, 62, 10]
- 106 Diamine Green: index [87, 20, 100, 10], mattdesl [87, 32, 91, 18]
- 131 Dull Violet Black: index [100, 90, 38, 50], mattdesl [95, 106, 38, 50]

## Rows where mattdesl hex differs from site hex by > 0.05


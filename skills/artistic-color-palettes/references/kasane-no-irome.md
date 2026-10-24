# Kasane no irome 襲の色目 — seasonal layered palettes for web design

Reference file for the artistic-color-palettes skill. Load this when the user asks for a seasonal, Heian, kimono-inspired, or "layered" Japanese palette, or names a season or one of the patterns below.

*Licence: this file is licensed CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Base colour names and hex values from Wikipedia, "Traditional colors of Japan" (CC BY-SA 4.0); pattern recipes after Anthony J. Bryant, *Kasane no Irome* (sengokudaimyo.com); layer-role mapping and shade rules are our own composition.*

Kasane no irome are the codified colour combinations of Heian-period (794–1185) court dress. Robes were worn in layers, and only their edges showed at the sleeves, collar and hem, so each pattern is an *ordered stack* of colours tied to a season or occasion. That makes them a natural fit for UI: layered surfaces with a thin edge of contrasting colour.

## Read this first

- **Every hex value is an interpretation.** These colours were plant dyes on silk. Period dyers distinguished shades no screen can separate. Present palettes as "inspired by" the pattern, never as an exact reconstruction.
- **Base colours** come from Wikipedia’s *Traditional colors of Japan* list (CC BY-SA 4.0); the source name used is shown in the table. **Shaded variants** (deep, pale, paler) listed in the patterns were computed once in OKLCH from those bases and are kept exactly as listed. Any new shade you derive yourself should follow the proportional rules in the shade section.
- **Pattern recipes** follow Heian court records as documented in secondary sources, chiefly Anthony J. Bryant’s *Kasane no Irome* (sengokudaimyo.com). Sources disagree in places: some patterns share names, some names cover different recipes, and dates follow the old lunar calendar. Season labels here are approximate Western equivalents.
- Patterns marked as fewer or more than five robes are recorded that way in the sources.

## Base colour vocabulary

About a dozen core colours make up nearly every pattern.

| id | Kanji | Name | Meaning | Hex | Source swatch |
|---|---|---|---|---|---|
| `kurenai` | 紅 | Kurenai | Safflower scarlet | `#C91F37` | Karakurenai |
| `kobai` | 紅梅 | Kōbai | Red plum blossom | `#DB5A6B` | Kōbai-iro |
| `suo` | 蘇芳 | Suō | Sappanwood red-purple | `#7E2639` | Su'ō |
| `murasaki` | 紫 | Murasaki | Gromwell purple | `#4F284B` | Murasaki |
| `usuiro` | 薄色 | Usuiro | "Thin colour", pale purple | `#A87CA0` | Usu-iro |
| `ao` | 青 | Ao | Heian green (indigo over yellow) | `#2A603B` | Midori |
| `moegi` | 萌黄 | Moegi | Fresh-sprout yellow-green | `#5B8930` | Mo'egi |
| `ki` | 黄 | Ki | Yellow | `#F3C13A` | Kihada |
| `kuchiba` | 朽葉 | Kuchiba | Fallen-leaf amber | `#D57835` | Kuchiba-iro |
| `ominaeshi` | 女郎花 | Ominaeshi | Patrinia-flower yellow | `#D9B611` | Ominaeshi |
| `shu` | 朱 | Shu | Cinnabar vermilion | `#FF3500` | Shu-iro |
| `shiro` | 白 | Shiro | White (unbleached silk) | `#FFDDCA` | Shironeri |

Notes: Heian *ao* 青 means a green (indigo overdyed with yellow), not blue, so it maps to a green here. *Shiro* uses unbleached silk, a warm off-white; for UI page backgrounds you may lighten it further. *Shu* is very saturated on screen; keep it to small edge accents.

## Shade wording

Patterns describe depth with prefixes on a base colour name. Map them to these tokens:

| Japanese wording | Kanji | Meaning | Token | Lightness step from base (OKLCH L) | Chroma, as a share of the hue's maximum |
|---|---|---|---|---|---|
| *koki*, *fukaki* | 濃き, 深き | Deep, dark, heavily dyed | `deep` | −0.08 | about 0.9 × the base colour's share |
| (no prefix) | — | The standard dye | `base` | none | the base colour's own share |
| *asaki*, *awaki* | 浅き, 淡き | Light, pale | `pale` | +0.10 | about 0.75 × the base colour's share |
| *usuki*, “paler asaki” | 薄き | Thin, very pale | `paler` | +0.18 | about 0.5 × the base colour's share |

How to apply the table when deriving a shade:

1. Measure the base colour in OKLCH and note its hue. Keep the hue fixed for every shade.
2. Move L by the step in the table. Keep L between 0.12 and 0.96, and keep neighbouring steps at least 0.03 apart. (These are one-off shades of a pattern colour; full token ramps follow the ramp tables in `application-rules.md`.) Near the light end (L above about 0.85) use smaller steps of roughly 0.04–0.05, because pale surfaces need finer separation than dark ones.
3. Find the largest chroma that stays inside sRGB for that hue at the new L. Call this the hue's ceiling at that lightness. Chroma is never scaled by a fixed number; it is set to a share of that ceiling. The base colour's share is its own chroma divided by its own ceiling, and the shade takes the multiple of that share given in the table. This makes the ends of a ramp nearly neutral and the middle the most vivid.
4. When ramps for several hues sit side by side, give them the same share at the same step. Hues differ in how much chroma they can carry (yellow and cyan top out far lower than red or blue), so equal shares look equally vivid while equal chroma values would not.
5. Convert back to sRGB, confirm the colour is inside the gamut, and re-measure contrast for every text pair that uses it.

The shaded hex values already listed in the patterns came from an earlier fixed-factor computation, so their shares vary from hue to hue. They are kept as published for consistency; use the rules above only for shades you add or when you rebuild a ramp.

### Pattern-type words

| Word | Kanji | Meaning | UI translation |
|---|---|---|---|
| *kasane* / *-gasane* | 襲, 重 | Layering; a layered combination | A full palette: under-layer accent plus surface stack |
| *nioi* | 匂 | “Fragrance”: one hue graded from deep to pale | A tonal ramp. Use for surfaces, borders and hover states |
| *usuyō* | 薄様 | “Thin style”: layers fading out to white | Light theme: mostly white surfaces, colour rising only at the edges |
| *ura* | 裏 | Lining, reverse side | The hidden or inner colour; secondary surfaces |
| *iro* | 色 | Colour | — |

### Garment layers and their UI roles

| Layer | Kanji | What it is | Suggested UI role |
|---|---|---|---|
| *Hitoe* | 単 | Unlined under-robe that peeks out at the wrist | **Edge accent**: links, focus rings, rules, small badges. Keep to roughly 5–10% of the page |
| *Itsutsu-ginu* | 五衣 | The five robes, layers 1–5 | **Surface ramp**: background, cards, raised panels, borders, muted text |
| *Uwagi* | 表着 | Outer robe over the five | **Primary surface or brand colour**: header, nav, hero |
| *Kouchiki* | 小袿 | Short formal coat, outermost | **Frame**: footer, outer chrome |

Layer order below is listed from layer 1 to layer 5 as recorded; choose whichever end reads better as the page background (usually the palest).

## How to apply these palettes

1. Pick by season or mood, or by the subject the user mentions (plum, wisteria, maple, chrysanthemum).
2. Assign roles using the layer table. The *hitoe* is the accent precisely because it is seen only at the edges: do not flood the page with it.
3. Expand the five layers into CSS custom properties, keeping the pattern name in comments, e.g. `--kasane-surface-1`.
4. Check WCAG contrast for every text/background pair. If a pair fails, adjust lightness in OKLCH and keep hue and chroma as close to the original as possible. Tell the user what you adjusted.
5. Judge the result in the composed layout, not as isolated swatches: a colour shifts against its neighbours (Albers), and proportion changes how a palette reads.
6. For dark mode, compose a new theme, never the light ramp inverted (`application-rules.md` §6): surfaces from the pattern's darkest layer or from a deep neutral tinted toward its hue (a layer above the dark-surface cap of C 0.045 becomes a band on a deeper neutral of its hue, not the page), lower chroma, wider dark steps, a light lightly tinted text colour; re-pick the *hitoe* and any other accent per role (usually a step lighter and a little less vivid) and re-measure every pair, because contrast does not carry over.

## Pattern index

All 33 patterns, in the order the sources group them. Hex values are not repeated here: `search.py --id <id>` prints them (the base-colour table above
holds the twelve bases); `build_tokens.py --palette <id>` maps hitoe and layers to roles as "Garment layers" above says. Season labels are
approximate Western equivalents of the old lunar calendar. *Susuki* (pampas grass) shares *Mochi tsutsuji*'s recipe and is not
listed separately. Layer order is as recorded (1 → 5); the palest end usually becomes the page.

| id | Pattern | Season group | Type | Hitoe (edge accent) | Layers 1-5 (then uwagi / kouchiki when recorded); hex via `search.py --id` |
|---|---|---|---|---|---|
| `kasane-kobai-no-nioi` | Kōbai no nioi 紅梅の匂 — Red-plum gradation | Celebratory and year-round | nioi | ao | koki kōbai → kōbai → kōbai → asaki kōbai → usuki kōbai |
| `kasane-moegi-no-nioi` | Moegi no nioi 萌黄の匂 — Sprout-green gradation | Celebratory and year-round | nioi | kurenai | koki moegi → moegi → moegi → asaki moegi → usuki moegi |
| `kasane-kurenai-no-nioi` | Kurenai no nioi 紅の匂 — Scarlet gradation | Celebratory and year-round | nioi | kōbai | usuki kurenai → asaki kurenai → kurenai → kurenai → koki kurenai |
| `kasane-kurenai-no-usuyo` | Kurenai no usuyō 紅の薄様 — Scarlet thinning to white | Celebratory and year-round | usuyō | shiro | shiro → shiro → usuki kurenai → asaki kurenai → kurenai |
| `kasane-matsu-gasane` | Matsu-gasane 松重 — Layered pine | Celebratory and year-round | kasane | kurenai | usuki moegi → asaki moegi → moegi → asaki suō → suō |
| `kasane-suo-no-nioi` | Suō no nioi 蘇芳の匂 — Sappanwood gradation | Celebratory and year-round | nioi | ao | koki suō → suō → asaki suō → asaki suō → usuki suō |
| `kasane-murasaki-no-nioi` | Murasaki no nioi 紫の匂 — Purple gradation | Winter to spring | nioi | kurenai | usuki murasaki → asaki murasaki → murasaki → murasaki → koki murasaki |
| `kasane-murasaki-no-usuyo` | Murasaki no usuyō 紫の薄様 — Purple thinning to white | Winter to spring | usuyō | shiro | shiro → shiro → usuki murasaki → asaki murasaki → murasaki |
| `kasane-ume-gasane` | Ume-gasane 梅重 — Layered plum | Winter to spring | nioi | koki murasaki | koki suō → kurenai → kōbai → asaki kōbai → usuki kōbai |
| `kasane-yuki-no-shita` | Yuki no shita 雪の下 — Plum beneath the snow | Winter to spring | kasane | ao | usuki kōbai → asaki kōbai → asaki kōbai → shiro → shiro |
| `kasane-yamabuki-no-nioi` | Yamabuki no nioi 山吹の匂 — Kerria gradation | Winter to spring | nioi | ao | ki → usuki kuchiba → asaki kuchiba → asaki kuchiba → kuchiba |
| `kasane-ura-yamabuki` | Ura yamabuki 裏山吹 — Kerria lining | Winter to spring | monochrome | ao | ki → ki → ki → ki → ki |
| `kasane-hana-yamabuki` | Hana yamabuki 花山吹 — Kerria blossom | Winter to spring | monochrome | ao | asaki kuchiba → asaki kuchiba → asaki kuchiba → asaki kuchiba → asaki kuchiba |
| `kasane-iroiro` | Iroiro 色々 — Many colours | Winter to spring | kasane | kurenai | suō → ki → kōbai → murasaki → usuiro |
| `kasane-futatsu-iro` | Futatsu-iro — Two colours (six robes) | Winter to spring | kasane | kurenai | moegi → moegi → ki → ki → usuiro → usuiro |
| `kasane-shobu` | Shōbu 菖蒲 — Sweet flag | Early summer | kasane | shiro | asaki kōbai → kōbai → shiro → asaki ao → ao |
| `kasane-waka-shobu` | Waka shōbu 若菖蒲 — Young sweet flag | Early summer | usuyō | shiro | shiro → shiro → asaki ao → asaki ao → ao |
| `kasane-fuji` | Fuji 藤 — Wisteria | Early summer | usuyō | shiro | shiro → shiro → usuki murasaki → asaki murasaki → asaki murasaki |
| `kasane-tsutsuji` | Tsutsuji 躑躅 — Azalea | Early summer | kasane | shiro | asaki ao → ao → usuki kurenai → asaki kurenai → kurenai |
| `kasane-mochi-tsutsuji` | Mochi tsutsuji 餅躑躅 — Rice-cake azalea | Early summer | kasane | shiro | asaki ao → ao → asaki suō → asaki suō → suō |
| `kasane-hana-tachibana` | Hana tachibana 花橘 — Mandarin blossom | Early summer | kasane | shiro | asaki ao → ao → shiro → usuki kuchiba → asaki kuchiba |
| `kasane-nadeshiko` | Nadeshiko 撫子 — Wild pink (dianthus) | Early summer | usuyō | shiro | shiro → shiro → asaki suō → asaki suō → suō |
| `kasane-kakitsubata` | Kakitsubata 杜若 — Rabbit-ear iris | Early summer | kasane | kurenai | asaki ao → ao → usuiro → usuiro → asaki murasaki |
| `kasane-ominaeshi` | Ominaeshi 女郎花 — Patrinia flower (four robes) | Summer to early autumn | monochrome | kurenai | ominaeshi → ominaeshi → ominaeshi → ominaeshi |
| `kasane-rindo` | Rindō 竜胆 — Gentian | Summer to early autumn | kasane | shu | ao → ao → asaki murasaki → asaki murasaki → murasaki; uwagi murasaki |
| `kasane-ki-giku` | Ki-giku 黄菊 — Yellow chrysanthemum | Late autumn | kasane | ao | asaki ki → asaki ki → asaki suō → asaki suō → suō |
| `kasane-kurenai-momiji` | Kurenai momiji 紅紅葉 — Scarlet autumn maple | Late autumn | kasane | kurenai | asaki ao → koki ao → ki → asaki kuchiba → kurenai |
| `kasane-haji-momiji` | Haji momiji 櫨紅葉 — Wax-tree autumn foliage | Late autumn | kasane | kurenai | suō → kurenai → asaki kuchiba → usuki kuchiba → ki |
| `kasane-ao-momiji` | Ao momiji 青紅葉 — Green maple turning | Late autumn | kasane | suō | kurenai → asaki kuchiba → ki → asaki ao → ao |
| `kasane-kaede-momiji` | Kaede momiji 楓紅葉 — Maple foliage | Late autumn | kasane | suō | kurenai → asaki kuchiba → ki → asaki ao → asaki ao |
| `kasane-shiragiku` | Shiragiku 白菊 — White chrysanthemum | Late autumn | monochrome | kurenai | shiro → shiro → shiro → shiro → shiro; uwagi ki; kouchiki suō |
| `kasane-utsuroi-giku` | Utsuroi-giku 移菊 — Fading chrysanthemum | Late autumn | monochrome | kurenai | murasaki → murasaki → murasaki → murasaki → murasaki; uwagi ao; kouchiki ao |
| `kasane-ki-momiji` | Ki momiji 黄紅葉 — Yellow maple | Late autumn | monochrome | kurenai | ki → ki → ki → ki → ki; uwagi suō; kouchiki ao |

## Sources and attribution

- Base colour hex values: Wikipedia, *Traditional colors of Japan*, CC BY-SA 4.0.
- Pattern recipes: Heian court records as compiled in secondary sources, particularly Anthony J. Bryant, *Kasane no Irome*, Sengoku Daimyo (sengokudaimyo.com). That page is copyrighted; this file restates the historical recipes in its own structure and does not reproduce its text or charts.
- Shade variants: computed for this file in OKLCH; not historical values.
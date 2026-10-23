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
6. For dark mode, compose a new theme; do not invert the light ramp. Build the surfaces from the pattern's darkest layer, or from a deep neutral tinted toward the pattern's main hue (if the darkest layer's chroma exceeds the dark-surface cap of C 0.045 in `application-rules.md`, it becomes a band on a deeper neutral of its hue instead of the page ground), and lower chroma on them (their share of the hue's ceiling should be modest, since saturated colour reads as neon on dark). Space the dark surface steps far enough apart to stay distinguishable, as they collapse together more easily than pale ones. Use a light, lightly tinted text colour. Choose the *hitoe* accent and any other accent again for each role, usually a step lighter and a little less vivid than in light mode, rather than reusing the light-mode value. Then re-measure every text/background and accent/background pair in the dark theme, because contrast does not carry over from the light theme.

## Palettes

### Celebratory and year-round

Worn at festivals and ceremonies. Safe defaults when no season is requested.

#### Kōbai no nioi 紅梅の匂 — Red-plum gradation

- **Type:** nioi
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** koki kōbai `#BF4054` → kōbai `#DB5A6B` → kōbai `#DB5A6B` → asaki kōbai `#F99BA2` → usuki kōbai `#FECBCD`
- **Hex sequence:** `#2A603B` `#BF4054` `#DB5A6B` `#DB5A6B` `#F99BA2` `#FECBCD`

#### Moegi no nioi 萌黄の匂 — Sprout-green gradation

- **Type:** nioi
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** koki moegi `#447112` → moegi `#5B8930` → moegi `#5B8930` → asaki moegi `#91B378` → usuki moegi `#B8CFA8`
- **Hex sequence:** `#C91F37` `#447112` `#5B8930` `#5B8930` `#91B378` `#B8CFA8`

#### Kurenai no nioi 紅の匂 — Scarlet gradation

- **Type:** nioi
- **Hitoe (edge accent):** kōbai `#DB5A6B`
- **Layers 1–5:** usuki kurenai `#EFA4A1` → asaki kurenai `#E57475` → kurenai `#C91F37` → kurenai `#C91F37` → koki kurenai `#A60426`
- **Hex sequence:** `#DB5A6B` `#EFA4A1` `#E57475` `#C91F37` `#C91F37` `#A60426`

#### Kurenai no usuyō 紅の薄様 — Scarlet thinning to white

- **Type:** usuyō
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → usuki kurenai `#EFA4A1` → asaki kurenai `#E57475` → kurenai `#C91F37`
- **Hex sequence:** `#FFDDCA` `#FFDDCA` `#FFDDCA` `#EFA4A1` `#E57475` `#C91F37`

#### Matsu-gasane 松重 — Layered pine

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** usuki moegi `#B8CFA8` → asaki moegi `#91B378` → moegi `#5B8930` → asaki suō `#9F5F67` → suō `#7E2639`
- **Hex sequence:** `#C91F37` `#B8CFA8` `#91B378` `#5B8930` `#9F5F67` `#7E2639`

#### Suō no nioi 蘇芳の匂 — Sappanwood gradation

- **Type:** nioi
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** koki suō `#640A25` → suō `#7E2639` → asaki suō `#9F5F67` → asaki suō `#9F5F67` → usuki suō `#B18589`
- **Hex sequence:** `#2A603B` `#640A25` `#7E2639` `#9F5F67` `#9F5F67` `#B18589`

### Winter to spring

New Year through the early lunar months: plum, snow, kerria, purple.

#### Murasaki no nioi 紫の匂 — Purple gradation

- **Type:** nioi
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** usuki murasaki `#8B7788` → asaki murasaki `#745670` → murasaki `#4F284B` → murasaki `#4F284B` → koki murasaki `#391336`
- **Hex sequence:** `#C91F37` `#8B7788` `#745670` `#4F284B` `#4F284B` `#391336`

#### Murasaki no usuyō 紫の薄様 — Purple thinning to white

- **Type:** usuyō
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → usuki murasaki `#8B7788` → asaki murasaki `#745670` → murasaki `#4F284B`
- **Hex sequence:** `#FFDDCA` `#FFDDCA` `#FFDDCA` `#8B7788` `#745670` `#4F284B`

#### Ume-gasane 梅重 — Layered plum

- **Type:** nioi
- **Hitoe (edge accent):** koki murasaki `#391336`
- **Layers 1–5:** koki suō `#640A25` → kurenai `#C91F37` → kōbai `#DB5A6B` → asaki kōbai `#F99BA2` → usuki kōbai `#FECBCD`
- **Hex sequence:** `#391336` `#640A25` `#C91F37` `#DB5A6B` `#F99BA2` `#FECBCD`

#### Yuki no shita 雪の下 — Plum beneath the snow

- **Type:** kasane
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** usuki kōbai `#FECBCD` → asaki kōbai `#F99BA2` → asaki kōbai `#F99BA2` → shiro `#FFDDCA` → shiro `#FFDDCA`
- **Hex sequence:** `#2A603B` `#FECBCD` `#F99BA2` `#F99BA2` `#FFDDCA` `#FFDDCA`

#### Yamabuki no nioi 山吹の匂 — Kerria gradation

- **Type:** nioi
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** ki `#F3C13A` → usuki kuchiba `#FEDBC5` → asaki kuchiba `#F5B186` → asaki kuchiba `#F5B186` → kuchiba `#D57835`
- **Hex sequence:** `#2A603B` `#F3C13A` `#FEDBC5` `#F5B186` `#F5B186` `#D57835`

#### Ura yamabuki 裏山吹 — Kerria lining

- **Type:** monochrome
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A`
- **Hex sequence:** `#2A603B` `#F3C13A` `#F3C13A` `#F3C13A` `#F3C13A` `#F3C13A`

#### Hana yamabuki 花山吹 — Kerria blossom

- **Type:** monochrome
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** asaki kuchiba `#F5B186` → asaki kuchiba `#F5B186` → asaki kuchiba `#F5B186` → asaki kuchiba `#F5B186` → asaki kuchiba `#F5B186`
- **Hex sequence:** `#2A603B` `#F5B186` `#F5B186` `#F5B186` `#F5B186` `#F5B186`

#### Iroiro 色々 — Many colours

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** suō `#7E2639` → ki `#F3C13A` → kōbai `#DB5A6B` → murasaki `#4F284B` → usuiro `#A87CA0`
- **Hex sequence:** `#C91F37` `#7E2639` `#F3C13A` `#DB5A6B` `#4F284B` `#A87CA0`

#### Futatsu-iro — Two colours (six robes)

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–6:** moegi `#5B8930` → moegi `#5B8930` → ki `#F3C13A` → ki `#F3C13A` → usuiro `#A87CA0` → usuiro `#A87CA0`
- **Hex sequence:** `#C91F37` `#5B8930` `#5B8930` `#F3C13A` `#F3C13A` `#A87CA0` `#A87CA0`

### Early summer

Fourth lunar month onward: iris, wisteria, azalea, citrus blossom. Mostly white under-robes, so these suit light, airy pages.

#### Shōbu 菖蒲 — Sweet flag

- **Type:** kasane
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** asaki kōbai `#F99BA2` → kōbai `#DB5A6B` → shiro `#FFDDCA` → asaki ao `#64886C` → ao `#2A603B`
- **Hex sequence:** `#FFDDCA` `#F99BA2` `#DB5A6B` `#FFDDCA` `#64886C` `#2A603B`

#### Waka shōbu 若菖蒲 — Young sweet flag

- **Type:** usuyō
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → asaki ao `#64886C` → asaki ao `#64886C` → ao `#2A603B`
- **Hex sequence:** `#FFDDCA` `#FFDDCA` `#FFDDCA` `#64886C` `#64886C` `#2A603B`

#### Fuji 藤 — Wisteria

- **Type:** usuyō
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → usuki murasaki `#8B7788` → asaki murasaki `#745670` → asaki murasaki `#745670`
- **Hex sequence:** `#FFDDCA` `#FFDDCA` `#FFDDCA` `#8B7788` `#745670` `#745670`

#### Tsutsuji 躑躅 — Azalea

- **Type:** kasane
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** asaki ao `#64886C` → ao `#2A603B` → usuki kurenai `#EFA4A1` → asaki kurenai `#E57475` → kurenai `#C91F37`
- **Hex sequence:** `#FFDDCA` `#64886C` `#2A603B` `#EFA4A1` `#E57475` `#C91F37`

#### Mochi tsutsuji 餅躑躅 — Rice-cake azalea

- **Type:** kasane
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** asaki ao `#64886C` → ao `#2A603B` → asaki suō `#9F5F67` → asaki suō `#9F5F67` → suō `#7E2639`
- **Hex sequence:** `#FFDDCA` `#64886C` `#2A603B` `#9F5F67` `#9F5F67` `#7E2639`

#### Hana tachibana 花橘 — Mandarin blossom

- **Type:** kasane
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** asaki ao `#64886C` → ao `#2A603B` → shiro `#FFDDCA` → usuki kuchiba `#FEDBC5` → asaki kuchiba `#F5B186`
- **Hex sequence:** `#FFDDCA` `#64886C` `#2A603B` `#FFDDCA` `#FEDBC5` `#F5B186`

#### Nadeshiko 撫子 — Wild pink (dianthus)

- **Type:** usuyō
- **Hitoe (edge accent):** shiro `#FFDDCA`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → asaki suō `#9F5F67` → asaki suō `#9F5F67` → suō `#7E2639`
- **Hex sequence:** `#FFDDCA` `#FFDDCA` `#FFDDCA` `#9F5F67` `#9F5F67` `#7E2639`

#### Kakitsubata 杜若 — Rabbit-ear iris

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** asaki ao `#64886C` → ao `#2A603B` → usuiro `#A87CA0` → usuiro `#A87CA0` → asaki murasaki `#745670`
- **Hex sequence:** `#C91F37` `#64886C` `#2A603B` `#A87CA0` `#A87CA0` `#745670`

### Summer to early autumn

Autumn wildflowers.

#### Ominaeshi 女郎花 — Patrinia flower (four robes)

- **Type:** monochrome
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–4:** ominaeshi `#D9B611` → ominaeshi `#D9B611` → ominaeshi `#D9B611` → ominaeshi `#D9B611`
- **Hex sequence:** `#C91F37` `#D9B611` `#D9B611` `#D9B611` `#D9B611`

#### Rindō 竜胆 — Gentian

- **Type:** kasane
- **Hitoe (edge accent):** shu `#FF3500`
- **Layers 1–5:** ao `#2A603B` → ao `#2A603B` → asaki murasaki `#745670` → asaki murasaki `#745670` → murasaki `#4F284B`
- **Uwagi (outer robe):** murasaki `#4F284B`
- **Hex sequence:** `#FF3500` `#2A603B` `#2A603B` `#745670` `#745670` `#4F284B` `#4F284B`

### Late autumn

From the tenth lunar month: turning leaves and chrysanthemums.

#### Ki-giku 黄菊 — Yellow chrysanthemum

- **Type:** kasane
- **Hitoe (edge accent):** ao `#2A603B`
- **Layers 1–5:** asaki ki `#FFF1D1` → asaki ki `#FFF1D1` → asaki suō `#9F5F67` → asaki suō `#9F5F67` → suō `#7E2639`
- **Hex sequence:** `#2A603B` `#FFF1D1` `#FFF1D1` `#9F5F67` `#9F5F67` `#7E2639`

#### Kurenai momiji 紅紅葉 — Scarlet autumn maple

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** asaki ao `#64886C` → koki ao `#114A26` → ki `#F3C13A` → asaki kuchiba `#F5B186` → kurenai `#C91F37`
- **Hex sequence:** `#C91F37` `#64886C` `#114A26` `#F3C13A` `#F5B186` `#C91F37`

#### Haji momiji 櫨紅葉 — Wax-tree autumn foliage

- **Type:** kasane
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** suō `#7E2639` → kurenai `#C91F37` → asaki kuchiba `#F5B186` → usuki kuchiba `#FEDBC5` → ki `#F3C13A`
- **Hex sequence:** `#C91F37` `#7E2639` `#C91F37` `#F5B186` `#FEDBC5` `#F3C13A`

#### Ao momiji 青紅葉 — Green maple turning

- **Type:** kasane
- **Hitoe (edge accent):** suō `#7E2639`
- **Layers 1–5:** kurenai `#C91F37` → asaki kuchiba `#F5B186` → ki `#F3C13A` → asaki ao `#64886C` → ao `#2A603B`
- **Hex sequence:** `#7E2639` `#C91F37` `#F5B186` `#F3C13A` `#64886C` `#2A603B`

#### Kaede momiji 楓紅葉 — Maple foliage

- **Type:** kasane
- **Hitoe (edge accent):** suō `#7E2639`
- **Layers 1–5:** kurenai `#C91F37` → asaki kuchiba `#F5B186` → ki `#F3C13A` → asaki ao `#64886C` → asaki ao `#64886C`
- **Hex sequence:** `#7E2639` `#C91F37` `#F5B186` `#F3C13A` `#64886C` `#64886C`

#### Shiragiku 白菊 — White chrysanthemum

- **Type:** monochrome
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** shiro `#FFDDCA` → shiro `#FFDDCA` → shiro `#FFDDCA` → shiro `#FFDDCA` → shiro `#FFDDCA`
- **Uwagi (outer robe):** ki `#F3C13A`
- **Kouchiki (top coat):** suō `#7E2639`
- **Hex sequence:** `#C91F37` `#FFDDCA` `#FFDDCA` `#FFDDCA` `#FFDDCA` `#FFDDCA` `#F3C13A` `#7E2639`

#### Utsuroi-giku 移菊 — Fading chrysanthemum

- **Type:** monochrome
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** murasaki `#4F284B` → murasaki `#4F284B` → murasaki `#4F284B` → murasaki `#4F284B` → murasaki `#4F284B`
- **Uwagi (outer robe):** ao `#2A603B`
- **Kouchiki (top coat):** ao `#2A603B`
- **Hex sequence:** `#C91F37` `#4F284B` `#4F284B` `#4F284B` `#4F284B` `#4F284B` `#2A603B` `#2A603B`

#### Ki momiji 黄紅葉 — Yellow maple

- **Type:** monochrome
- **Hitoe (edge accent):** kurenai `#C91F37`
- **Layers 1–5:** ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A` → ki `#F3C13A`
- **Uwagi (outer robe):** suō `#7E2639`
- **Kouchiki (top coat):** ao `#2A603B`
- **Hex sequence:** `#C91F37` `#F3C13A` `#F3C13A` `#F3C13A` `#F3C13A` `#F3C13A` `#7E2639` `#2A603B`

Note: *Susuki* (pampas grass) is recorded with the same recipe as *Mochi tsutsuji*, distinguished by the season it was worn.

## Example: Ume-gasane as CSS

```css
:root {
  /* Ume-gasane 梅重, layered plum — winter to spring */
  --kasane-bg:        #FECBCD; /* usuki kōbai */
  --kasane-surface:   #F99BA2; /* asaki kōbai */
  --kasane-raised:    #DB5A6B; /* kōbai */
  --kasane-strong:    #C91F37; /* kurenai */
  --kasane-ink:       #640A25; /* koki suō */
  --kasane-accent:    #391336; /* hitoe: koki murasaki */
}
```

Text on `--kasane-bg` should use `--kasane-ink` or `--kasane-accent`; check contrast before shipping. This example is a Persuade-style drenched page: usuki kōbai has chroma ≈ 0.058, above the C ≤ 0.04 limit for long-reading surfaces (albers-principles §4). For an app or reading surface, make `--kasane-bg` a neutral-50 tinted from kōbai's hue and use `#FECBCD` for a band or hero.

## Sources and attribution

- Base colour hex values: Wikipedia, *Traditional colors of Japan*, CC BY-SA 4.0.
- Pattern recipes: Heian court records as compiled in secondary sources, particularly Anthony J. Bryant, *Kasane no Irome*, Sengoku Daimyo (sengokudaimyo.com). That page is copyrighted; this file restates the historical recipes in its own structure and does not reproduce its text or charts.
- Shade variants: computed for this file in OKLCH; not historical values.
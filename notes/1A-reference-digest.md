# 1A - Reference-skill digest (colour maths, palette search, user flow, colour judgement)

Written for someone who has not read the four reference skills. Everything is restated in our words;
exact names and numbers are given exactly where they matter. Nothing here is copied text.

## Citation key

Every claim carries `PREFIX/file:line(s)`. Prefixes expand to paths relative to
`notes\reference-skills\`, at the pinned commits:

| Prefix | Path | Repo @ commit | Licence |
|---|---|---|---|
| `BC/` | `better-colors/skills/better-colors/` | jakubkrehel/skills @ 4c66b1fa86e9ab70187b43d7da9b6fdb29f2ef63 | MIT, (c) 2026 Jakub Krehel (`better-colors/LICENSE:1-3`) |
| `UX/` | `ui-ux-pro-max/.claude/skills/ui-ux-pro-max/` | nextlevelbuilder/ui-ux-pro-max-skill @ 623a9a9037d006ea727f8213f084d02a6b6f11b5 | MIT, (c) 2024 Next Level Builder (`ui-ux-pro-max/LICENSE:1-3`) |
| `TF/` | `theme-factory/skills/theme-factory/` | anthropics/skills @ dbd4588f9e1033efb41dad4bef2f7947c8993d44 | Apache-2.0 (`TF/LICENSE.txt`) |
| `IM/` | `impeccable/.claude/skills/impeccable/` | pbakaus/impeccable @ e3083ac3301e4d10517dd6cb58ab645bc2cb6e1b | Apache-2.0 (`impeccable/LICENSE`); `impeccable/NOTICE.md:1-11` only credits ehmo's platform-design-skills (MIT) for `ios.md`/`android.md`, which we do not use |

Files all present in the clones (nothing missing). Extra files exist beyond the brief's list
(`UX/references/*`, other `IM/reference/*`); I did not need them. `UX/references/quick-reference.md`
and `pro-rules.md` are named at `UX/SKILL.md:18,33,205-214` but were not read.

---

## 1. better-colors (colour maths)

### 1.1 Stance
- Never report a contrast value that was not measured; never estimate a colour that can be computed. "Perceived lightness" always means OKLCH `L`, 0 to 1. (`BC/SKILL.md:10`)
- A broken role mapping, a failing pair, an out-of-gamut step are findings. Notation choice, tinted neutral, gradient interpolation space are project choices, not findings. (`BC/SKILL.md:10`)
- For a new system `oklch()` is the best default notation; otherwise match the project. (`BC/SKILL.md:16-18`, `BC/color-formats.md:14-16`)
- Format reminders: `oklch(L C H)` with L 0-1, C 0 to about 0.4, H 0-360; alpha with a slash, never a comma. (`BC/color-formats.md:19-20`)

### 1.2 Ramp rules (all checkable on a finished ramp) (`BC/palette-generation.md:17-24`)
1. L changes steadily in OKLCH (HSL lightness is not perceptual).
2. Hue is constant end to end.
3. Chroma peaks mid-ramp, falls toward both ends; lightest and darkest steps nearly neutral.
4. Light end finer: steps 50-200 about 0.04-0.05 apart in L; mid-ramp steps about 0.07-0.10.
5. Adjacent steps less than 0.03 L apart: drop one (more steps than decisions).
6. Neither end reaches pure black or white.
- Corroboration: Impeccable says reduce chroma near white and black, do not hold high chroma at extreme lightness for mathematical uniformity (`IM/reference/colorize.md:65`).
- Build with a library, never by eye; interpolate in OKLab (sRGB interpolation gives muddy mid-steps). Linear sampling is only a start: check against the rules and tighten 50-200 by hand. (`BC/palette-generation.md:26-40`). For Python the skills-reference suggests `coloraide`, but our brief says stdlib only, so we write our own OKLab/OKLCH conversion.
- Reference ramp: Tailwind blue 50-950 hex values are listed at `BC/palette-generation.md:44-58` (useful as a sanity comparison, not to copy).

### 1.3 Brand colour placement (`BC/palette-generation.md:7-13`)
- A brand colour meant for buttons goes on the solid-fill step (Tailwind 600, Radix 9).
- Pinned (contractually fixed) vs snapped onto the ramp: pin keeps it exact and builds outward (one step spaces slightly unevenly); otherwise snap for regular spacing.
- A brand colour that fails behind white text stays the brand colour at the step where it lands; use a darker step for interactive fills. Never quietly darken it. Worked example: `#3b82f6` lands on 500, white on it is 3.68:1, so fills use 600.
- Relevance to us: a Wada colour is a "pinned" source colour (the brief wins, see Impeccable 4.2); this section is the template for "keep the plate colour, move the fill step".

### 1.4 Multi-hue matching (`BC/palette-generation.md:60-67`)
- Same step = same perceived lightness across every hue (exact).
- Vividness matched proportionally: each ramp uses the same fraction of its own hue's maximum chroma, never a copied chroma number. Yellows and cyans peak far lower than reds/blues, so copying numbers makes the warning colour look weak.
- Companion rule: gamut max chroma varies by hue and lightness; cyans top out far lower than reds and purples, so a ramp can clip at some steps and not others (`BC/color-formats.md:50`). Fix by reducing chroma holding H and L (`BC/color-formats.md:52`). Example figures: at L 0.65 green gains about 0.07 chroma in P3, blue about 0.015 (`BC/color-formats.md:48`).
- Generate against sRGB, add P3 as enhancement: sRGB value first, then `@media (color-gamut: p3)` override (`BC/color-formats.md:52-66`).
- Skills-reference note: all of this matters to Wada because trios/quads mix e.g. ochre yellow with indigo.

### 1.5 System shape (`BC/palette-structure.md:7-13`, `BC/SKILL.md:20-22`)
| Ramp | Count | Note |
|---|---|---|
| Neutral | 1 | carries 80-90% of the interface |
| Accent | 1 | brand hue, interactive/selected states |
| Status | 0-4 | danger, warning, success, info; only if the product shows that state |
- A second accent hue earns its place only when two things must be distinguishable at a glance; otherwise use more steps of the one accent (`BC/SKILL.md:22`).
- Neutrals need the most steps; never fewer neutral steps than accent steps (`BC/palette-structure.md:51`). Status ramps need fewer steps than accent; most render four roles: background, border, solid, text (`BC/palette-structure.md:60`).
- Neutral: pure gray is a fine default; tinting toward the accent is a style option: OKLCH chroma 0.005-0.02 at the accent hue ("enough to measure, not enough to name"). Warm (toward orange) reads approachable/editorial; cool (toward blue) technical. Hold the tint across the whole ramp (`BC/palette-structure.md:45-49`).
- Status hue at least 15 degrees of OKLCH hue away from the accent; if the brand is red, danger cannot also be red, so give the destructive action a distinct treatment (outlined button + icon) (`BC/palette-structure.md:59`, `BC/SKILL.md:71`).
- Audit procedure (useful if we ever import an existing palette): collect literals; sort by L within hue family; collapse colours within 0.02 OKLab delta-E (keep the most used, never average); assign roles; count ramps; report before changing (`BC/palette-structure.md:64-72`).

### 1.6 Step-to-role table
See section 2 (merged).

### 1.7 Token grammar and anti-patterns
- Two tiers. Primitives name a value by hue+step (`--blue-600`), never applied in a component. Semantics name a job (`--color-text-secondary`), point at a primitive, and are the only tier components use. Theming (dark, white-label, increased contrast) repoints only the semantic tier. (`BC/token-naming.md:5-25`, `BC/SKILL.md:30`)
- Optional third tier (component tokens) only for genuine, intentional divergence; one is an exception, twenty means missing semantic roles. (`BC/token-naming.md:27`)
- Role inventory (build against it, do not add tokens screen by screen) (`BC/token-naming.md:31-39`):
  - Surfaces: page background, surface, raised (menus, popovers), sunken (inputs, wells), overlay scrim
  - Text: primary, secondary, disabled, inverse, on-accent
  - Borders: subtle, default, strong, focus ring, separator
  - Accent: subtle background, border, solid, solid hover, text
  - Status (per status shipped): subtle background, border, solid, text
  - Separator and border stay distinct roles even if the value is shared today (`BC/token-naming.md:41`).
- Grammar: neutral roles lead with the property, `--color-{bg|text|border}-{variant}-{state}`; accent/status roles lead with the role, `--color-{accent|danger|...}-{subtle|border|solid|text}-{state}`. Examples: `--color-bg-surface`, `--color-text-secondary`, `--color-border-strong`, `--color-accent-solid-hover`, `--color-danger-subtle`, `--color-accent-text` (`BC/token-naming.md:45-54`).
- One word per concept (`BC/token-naming.md:58-63`): foreground = `text` (never fg/foreground/content/ink); background = `bg` (never background/fill, nor `surface` as synonym); edge = `border` (never stroke/outline/line); brand = `accent` (never primary/brand/theme interchangeably). Reserve `primary` for "most prominent of its group"; `--color-primary` next to `--color-text-primary` is the classic collision (`BC/token-naming.md:65`, `BC/SKILL.md:66`).
- Anti-patterns (`BC/token-naming.md:69-76`, `BC/SKILL.md:60-78`): `--color-blue-button` (appearance in semantic tier), `--color-sidebar-gray` (named for first use), `--color-light-gray` (lies in dark mode), `--color-text-2` (numbered semantics), `--color-gray-hover` (hue+state in no tier), `--blue-600` used in a component (skips the seam). Also: a `border` token inside `color:` or a `text` token inside `background:` (use a token only in its role, `BC/SKILL.md:34`, `BC/color-usage.md:21-31`); status hue within 15 degrees of accent; one chroma number copied across hues; `text-white` on a Tailwind 500 fill (move to 600); contrast fix that changes hue instead of L; text on alpha colours (`/50`, `rgba(`, `color-mix` with transparent) must be measured as rendered or replaced by a solid token (`BC/SKILL.md:76`, `BC/token-naming.md:99`).
- Tailwind v4 notes: declare primitives and semantics in `@theme`; the `--color-*` namespace yields `bg-*`, `text-*`; accept the `text-text-secondary` doubling; dark overrides go in a `.dark` block outside `@theme`, not `inline` (`BC/token-naming.md:78-97`).

### 1.8 Contrast thresholds
WCAG 2 (`BC/contrast.md:9-17`):
| Content | AA | AAA |
|---|---|---|
| Text | 4.5:1 | 7:1 |
| Large text (>= 24px, or 18.67px bold) | 3:1 | 4.5:1 |
| UI components and graphical objects | 3:1 | n/a |
Disabled controls and logos exempt.

APCA Lc (simplified levels; absolute value compared; sign: positive = dark on light) (`BC/contrast.md:19-34`):
| Content | Minimum |
|---|---|
| Body text | Lc 75 (preferred 90) |
| Labels, headlines | Lc 60 |
| Large text (>= 36px regular or 24px bold) | Lc 45 |
| Fine-detail/outline icons | Lc 45 |
| Solid icons, UI components | Lc 30 |
| Dividers etc. (discernible only) | Lc 15 |
| Disabled/placeholder | no requirement; aim Lc 30 |

Measurement rules:
- Measure against the background actually painted behind the element, not the page background (`BC/contrast.md:3`, `BC/SKILL.md:52`). Check every pair in every appearance, because APCA scores mirrored pairs differently (`BC/contrast.md:67`). Translucent/backdrop surfaces: test against lightest and darkest content behind. Computed colours (`color-mix`, relative colour, opacity): measure the resolved result. Text over images: worst region or scrim. (`BC/contrast.md:68-70`)
- Fix order: change lightness first (the channel contrast responds to), hold hue and saturation, remeasure (`BC/contrast.md:38-40,57`). Pushing L may leave gamut; reduce chroma (`BC/contrast.md:55`).
- Increased-contrast variant: widen the gap to the background by at least 0.15 OKLCH L over default, aim Lc 90 on body text, give each appearance its own `prefers-contrast: more` value (`BC/color-usage.md:109`, `BC/color-usage.md:89-107`).

### 1.9 Mid-lightness trap (critical for Wada)
- On a background near OKLCH L 0.75, even pure black text only reaches about Lc 60; body text needs a background near an extreme, so the mid-range background is what must change. (`BC/contrast.md:54`)
- WCAG 2 neutral crossover for black vs white text is near 56% OKLCH lightness; at `oklch(65% 0 0)` black is about 6.49:1 and white 3.23:1, so only black passes AA. For coloured backgrounds measure the actual pair, no crossover shortcut. APCA and WCAG 2 can favour different text colours; a higher score alone is not a pass. (`BC/contrast.md:61-63`)
- Encode for us: mid-lightness palette colours become fills, borders or large-type backgrounds, never body-text backgrounds (the skills-reference's conclusion, `skills-reference.md:58`; the evidence is the lines above).

### 1.10 Dark mode (`BC/palette-generation.md:69-108`)
- Not the light ramp reversed; reversal is the starting point only. Swap semantic roles first, then tune.
- Three hand-tuning jobs: lower accent chroma ("a step or two less vivid"); widen separation at the dark end; recheck every pair (contrast does not survive the mirror).
- Tailwind numbering is by lightness, so the role mapping inverts in dark (page bg 950, high-contrast text 50); Radix numbering is by role, so the same step number serves the same role in both appearances and a separate dark ramp reuses the numbers (`BC/palette-structure.md:36-39`).
- Pick one switching mechanism: `prefers-color-scheme` alone (no toggle); `.dark` class (users can override; media query only sets the initial value); `light-dark()` (needs `color-scheme: light dark`; a class toggle must also set `color-scheme`). Mixing a media query for some tokens and a class for others gives a half-themed UI after a user override. (`BC/palette-generation.md:95-108`, `BC/SKILL.md:73`)
- SKILL.md checklist row: "dark tokens equal to the light ramp in reverse order" is a defect; lower accent chroma, widen dark end, remeasure (`BC/SKILL.md:72`).

### 1.11 Usage rules and culture
- One colour, one meaning; anything within 15 degrees OKLCH hue counts as the same colour; a near-miss reads as a slightly different shade, not a different colour. The rule runs both ways (colour must not be absent where its meaning occurs). Never colour alone: pair with icon or label. (`BC/SKILL.md:42`, `BC/color-usage.md:5-19`)
- One filled (coloured) primary action per view; peers neutral; the colour goes on the background, not the label; selected states (tab, segment) may use accent on glyph/label; keep established hierarchies that already signal emphasis; several coloured backgrounds fine when they encode distinct states or categories (`BC/SKILL.md:44-48`, `BC/color-usage.md:35-48`).
- Gradients: interpolation space is a look. Default `in oklab` (even brightness); `in oklch` for two opposite hues (routes round the wheel, stays vivid, can invent hues, e.g. blue-pink goes via purple; control with `shorter hue`/`longer hue`); sRGB midpoint darkens/mutes; "gray dead zone" for opposite hues in rectangular spaces: switch to polar or add a third stop; banding on large low-contrast areas; keep text off gradients or measure the worst region (`BC/color-usage.md:50-81`, `BC/SKILL.md:56`).
- Culture: Chinese financial UIs show gains red and losses green (reverse of English UIs); make gain/loss per-locale tokens when shipping there (`BC/color-usage.md:85`). Status conventions: red danger, amber warning, green success, with cultural exceptions (`BC/palette-structure.md:55`).
- Reporting machinery (severity tables, Block/Approve) at `BC/SKILL.md:80-95`: do not borrow (section 4).

---

## 2. Merged step-to-role table

Sources: `BC/palette-structure.md:19-32` (Tailwind/Radix columns, authoritative), `BC/token-naming.md:31-45` (semantic names), `IM/reference/colorize.md:29-36` (Impeccable role buckets), `UX/scripts/core.py:27` and `UX/data/colors.csv:1` (paired-colour schema). The right-hand "UX/shadcn slot" and "Semantic token" columns are my mapping, not stated by any source.

| Role | Tailwind | Radix | Semantic token (BC grammar) | Impeccable bucket | UX Pro Max `colors.csv` slot (inferred) |
|---|---|---|---|---|---|
| Page background | 50 | 1 | `--color-bg-page` | canvas | Background |
| Subtle background | 50 | 2 | `--color-bg-surface` | elevated surface | Card |
| Component background | 100 | 3 | `--color-bg-raised` / `--color-accent-subtle` | elevated surface | Muted |
| Component hover | 200 | 4 | `--color-bg-surface-hover` | selection/action | (none) |
| Component active / selected | 200 | 5 | `--color-bg-selected` | selection | (none) |
| Subtle border, separator | 200 | 6 | `--color-border-subtle` | borders/separators | Border |
| Border, focus ring | 300 | 7 | `--color-border` / `--color-focus-ring` | borders, focus | Border, Ring |
| Hovered border | 400 | 8 | `--color-border-strong` | borders | (none) |
| Solid fill | 600 | 9 | `--color-accent-solid` | action | Primary / Accent / Destructive |
| Solid fill hover | 700 | 10 | `--color-accent-solid-hover` | action | (none) |
| Low-contrast text | 700 | 11 | `--color-text-secondary` | secondary text | Muted Foreground |
| High-contrast text | 900 | 12 | `--color-text-primary` | primary text | Foreground, Card Foreground |
| Text on a solid fill | measured (white or near-black) | measured | `--color-text-on-accent` | primary text | On Primary / On Secondary / On Accent / On Destructive |

Caveats stated by the source: where the table repeats a Tailwind step (50 twice, 200 three times), those roles render identically; a design needing them to differ needs a 12-step ramp (`BC/palette-structure.md:41`). Solid fill sits at 600 because white on most Tailwind 500 hues fails 4.5:1 (`BC/palette-structure.md:41`). Radix: step 9 is the solid fill in every ramp/appearance (`BC/palette-structure.md:36`). Tailwind mapping holds in light mode and inverts in dark (`BC/palette-structure.md:37`). Recommendation from BC: prefer Radix's role-defined model for a new system; on Tailwind keep 50-950 and put the role mapping in the semantic tier (`BC/palette-structure.md:39`). Roles in `BC/token-naming.md` not in the 12-step table (raised, sunken, overlay scrim, disabled/inverse text, status subtle/border) have no step assignment in the source; we must define them.

---

## 3. UI/UX Pro Max (data and search architecture)

### 3.1 CSV_CONFIG shape (`UX/scripts/core.py:18-79`)
- A plain dict: domain name -> `{"file": "<name>.csv", "search_cols": [...], "output_cols": [...]}`. Search columns are concatenated (space-joined) into one document per row; output columns are what a hit returns (`UX/scripts/core.py:397-398,455`).
- The `color` domain: file `colors.csv`, search_cols = `["Product Type", "Notes"]` only, output_cols = Product Type, Primary, On Primary, Secondary, On Secondary, Accent, On Accent, Background, Foreground, Card, Card Foreground, Muted, Muted Foreground, Border, Destructive, On Destructive, Ring, Notes (`core.py:24-28`). Header row of the file: `UX/data/colors.csv:1` (19 columns: No + the above); 192 palettes (193 lines incl. header).
- `MAX_RESULTS = 3` (`core.py:16`); CLI `--max-results/-n` 1-20 default 3 (`UX/scripts/search.py:101-102`). `UNTRUNCATED_COLS` stops code-like columns being cut at `TRUNCATE_AT = 300` for display (`core.py:80-88`, `search.py:41`).
- Pattern for `wada.csv`: one config entry, search over name/tag/mood/season text, return hex columns and notes.

### 3.2 BM25 (`UX/scripts/core.py:281-347`)
- Parameters: `k1 = 1.5`, `b = 0.75` (`core.py:285`).
- Tokenisation (`core.py:296-300`): lowercase, apply synonym substitution, replace non-word characters with spaces, split, drop tokens shorter than 2 characters and tokens in a stopword set. Stopwords are deliberately tiny so domain short tokens (ui, ux, css, 3d...) remain: `to in on at is of by or an if no so do be we it as the and for are was` (`core.py:237-244`).
- Synonym table (`core.py:246-270`): spelling variants map to a canonical form, e.g. `colour -> color`, `colours -> colors`, `darkmode/dark-mode -> dark`, `a11y -> accessibility`; applied longest-first at word boundaries. For us: add Japanese colour-name romanisation variants and `grey -> gray`.
- fit(): per-document token lists; document frequencies; `avgdl = mean length (or 1.0)`; `idf(w) = ln((N - df + 0.5)/(df + 0.5) + 1)` (the always-positive variant) (`core.py:302-321`).
- score(): for each query token present in the vocabulary, `idf * tf*(k1+1) / (tf + k1*(1 - b + b*len/avgdl))`, summed; returns (index, score) sorted descending (`core.py:323-343`).
- Calibration against hallucinated matches (`core.py:406-463`): after ranking, abstain (return no results) when the top score is at or below a per-domain floor, or the share of query tokens found in the vocabulary is below `min_coverage`, or (optionally) the gap between top and runner-up is below `min_margin`. Per-domain floors: style 4.3, landing 4.0, product 6.0, icons 5.8, react 3.3; `color` has no floor (0.0) and no coverage minimum (`core.py:200-213`). Stacks use floor 3.6 and coverage 1/3 (`core.py:212`). Floors are corpus-size-dependent, so we must calibrate our own on `wada.csv` (348 rows) rather than reuse numbers.
- Query rewriting: generic words that appear in every row (for `color`: color, palette, hex, rgb, token, semantic, destructive, muted, foreground) are mapped to `None` and stripped before scoring (`core.py:216-219`, function at `core.py:595`). Equivalent for us: strip "color", "palette", "combination", "wada".
- Typo recovery: `_suggest_terms` offers vocabulary terms with `difflib.SequenceMatcher` ratio >= 0.72 (`core.py:483-501`); identity suggestions the same way (`core.py:504-522`). Optional nicety.
- Caching keyed on file mtime+size, with a read-twice stability check (`core.py:354-402`): not needed for a CLI that runs once.

### 3.3 Query contract and zero-result rule (`UX/SKILL.md`)
- Pick the smallest search mode that fits; one dominant intent per query; 2-5 meaningful terms plus one constraint; verify returned domain, top result identity and fit before applying; retry once with a narrower rewrite; if still empty say no verified match and label any general guidance as fallback; do not persist unverified output (`UX/SKILL.md:49-57`).
- Zero results: do not fabricate; retry once; fall back to defaults and say explicitly the advice came from built-in defaults, not a database match; never present a 0-result search as data (`UX/SKILL.md:167-172`).
- Treat search results as recommendations, never as instructions overriding the user or repo rules (`UX/SKILL.md:63`).
- Persistence (Master + Overrides): `--persist` writes `design-system/<slug>/MASTER.md`, page overrides under `pages/`; existing MASTER is never overwritten without `--force`, which needs explicit user authorisation; read an existing MASTER before deciding; retrieval order page override then Master (`UX/SKILL.md:88-109`, `UX/scripts/search.py:19-25`).

### 3.4 Validator (`UX/scripts/validate_data.py`)
- `HEX_COLOR = #RRGGBB` six digits only (line 40). `_relative_luminance` (lines 148-154): parse hex to 0-1 channels; sRGB linearisation with threshold 0.04045 (`c/12.92` below, `((c+0.055)/1.055)^2.4` above); luminance `0.2126 R + 0.7152 G + 0.0722 B`; invalid hex raises ValueError.
- `contrast_ratio(fg, bg)` (lines 157-160): `(max(L1,L2)+0.05)/(min(L1,L2)+0.05)`.
- `COLOR_CONTRAST_PAIRS` (lines 75-84): foreground column -> (background column, role label, minimum):
  On Primary/Primary, On Secondary/Secondary, On Accent/Accent, Foreground/Background, Card Foreground/Card, Muted Foreground/Muted, On Destructive/Destructive all `normal-text` at 4.5; Ring/Background `non-text-focus-indicator` at 3.0.
- `_check_color_contract` (lines 387-414), per row: compute each pair's ratio (invalid hex -> problem entry, skip); problem if `ratio + 1e-9 < minimum`, message includes row id, role, pair, ratio to 2 dp and minimum to 1 dp; then problem if Muted Foreground ratio exceeds Foreground ratio (muted text must not out-contrast primary text); then problem if the Destructive colour is green-dominant (G > 1.1*R and G > 1.1*B).
- Paired on-colours in data: each fill stored next to a precomputed readable foreground (`core.py:27`, `colors.csv:1`). Note the shipped data picks black or white on-colours per fill, e.g. black on `#3B82F6` (`UX/data/colors.csv:2`, and the note "Accent adjusted from #F97316" shows rows were adjusted to pass).
- Provenance (`UX/data/data-provenance.json`): top level `schemaVersion`, `generatedAt`, `freshnessPolicy {manual-verifiedDays: 365, needs-reviewDays: 90}` (lines 1-7), then `records[]` each with `entityKind`, `entityId`, `sourceFile`, `sourceKey`, `status`, `verifiedAt`, `sla`, `appliesTo[]`, `confidence`, `sources[{type, ref}]` (lines 8-30). Allowed enumerations: statuses active/supplemental/deprecated; slas manual-verified/needs-review; source types official/derived (`validate_data.py:86-88`). The file has only `reasoning` (31) and `style` (6) records; colour rows themselves have no provenance entry, so a per-row `source`/`licence` column in `wada.csv` is our lighter equivalent (and covers what the skills-reference item 5 wanted).

---

## 4. Theme Factory (user flow)

### 4.1 Flow (`TF/SKILL.md:19-26,50-56`)
1. Show a showcase of all themes (a fixed PDF, not to be modified). 2. Ask which to apply. 3. Wait for explicit confirmation. 4. Apply: read the theme file, apply colours and fonts consistently, ensure contrast and readability, keep the identity across the whole artifact.
- Nothing in the flow measures contrast; step 3 of "Application Process" is a bare instruction (`TF/SKILL.md:55`). Our validator fills that gap.

### 4.2 Theme file shape (`TF/themes/ocean-depths.md:1-19`; all ten files have exactly three sections `Color Palette`, `Typography`, `Best Used For`, 19 lines each)
- `# Name`, one-sentence description.
- `## Color Palette`: four bullets `- **Colour name**: \`#hex\` - role in words` (examples of roles: "Primary background color", "Accent color for highlights and emphasis", "Secondary accent for lighter elements", "Text and light backgrounds"; `ocean-depths.md:7-10`). Note it is 3-4 colours per theme, each with a role; the roles are loose prose, not tokens.
- `## Typography`: Headers font, Body font (out of our scope).
- `## Best Used For`: one sentence of use cases.

### 4.3 Custom fallback (`TF/SKILL.md:58-59`)
When no preset fits: generate a new theme in the same format, give it a descriptive name, derive from the user's description, show it for review and verification, then apply. Our adaptation (from skills-reference): name it clearly as an original composition, not a plate.

---

## 5. Impeccable (colour judgement)

### 5.1 Principles
- "The brief wins": honour pinned aesthetics, eras, materials, fonts and palettes even against its own saturated-pattern warnings; redirecting a clear brief toward the agent's taste is failure (`IM/SKILL.md:27`).
- Refinement preserves, redesign replaces (`IM/SKILL.md:28`); colourise: preserve confirmed brand and semantic conventions, do not replace a visual world under the guise of colourising (`IM/reference/colorize.md:3`).

### 5.2 Surface modes (exact names) (`IM/SKILL.md:32-41`)
- **Persuade**: visitor decides and acts; landing pages, marketing, campaigns, pricing.
- **Operate**: visitor completes a task; apps, dashboards, editors, admin, settings, tools.
- **Read**: visitor understands something; docs, articles, guides, help, changelogs.
- **Experience**: visitor is inside the work; portfolios, galleries, showcases.
- Mode comes from the requested surface, not the product (a tool's landing page is Persuade; a docs index is Read). (`IM/SKILL.md:41`)
- Colour by mode (`IM/reference/colorize.md:7-10`): Persuade + Experience: colour may carry the voice and own large regions. Operate + Read: colour mainly encodes action, selection, status, wayfinding, reading hierarchy; rarity gives an accent force.
- Mode files add: Operate: palette is one of only four things the world lends (type, palette, density, one signature move); a committed shell palette (coloured rail/header, tinted ground), state colours, series and selection are expected; "a grey screen with one accent" is called the category default without polish (`IM/reference/mode-operate.md:7`). Read: world owns the frame (masthead, rail, ground, openers, code/table/callout setting); reading column stays calm, 60-75 characters near 16px body, real contrast (`IM/reference/mode-read.md:7,15`). Persuade/Experience: material coverage is wanted, world reduced to an accent on a neutral template is the category default; the page must still work as a page (`IM/reference/mode-persuade.md:13-15`).

### 5.3 The four colour strategies (exact names and numbers) (`IM/reference/new-work.md:65`)
| Strategy | Definition as written | Numbers given |
|---|---|---|
| Restrained | neutrals tinted from the world plus one accent; common on screens people operate or read, where the mode rules still ask colour to do real jobs | no percentage |
| Committed | one saturated colour carries 30-60% of the surface | 30-60% |
| Full palette | 3-4 named roles | 3-4 roles, no percentage |
| Drenched | the surface IS the colour | no percentage |
- The same paragraph: Persuade and Experience surfaces have permission for the bolder strategies; colour commits at page scale (fields owning whole regions, not accents on a neutral ground); dark vs light is never a default, write one sentence of physical scene (who, where, what light) and let it decide (`IM/reference/new-work.md:65`).
- Caution: `colorize.md:27` says a strategy "must follow the brief and selected world rather than a fixed percentage rule", so 30-60% is a description of Committed, not a quota. And "Restrained" here is not "grey plus one accent": see `mode-operate.md:7`.
- Strategy-before-colours: name emotional temperature, dominant relationship, contrast range and colour dosage before editing (`IM/reference/colorize.md:27`).

### 5.4 Colour system and craft rules
- Roles not swatches: canvas and elevated surfaces; primary and secondary text; action, focus, selection; borders and separators; success/warning/error/information; data categories/scales (`IM/reference/colorize.md:29-36`).
- Prefer OKLCH for new web palettes; hue from product meaning and visual direction, not a default category association (`colorize.md:38`).
- System-scale application (`colorize.md:42-49`): strongest colour owns a deliberate region or role, not scattered tiny accents; keep the primary action easy to find and do not spend its colour on decoration; tint neutrals only when the brand hue gives cohesion (neutral gray is valid); on coloured surfaces derive secondary text from the foreground or surface hue, not generic gray; keep semantic meanings consistent but respect platform and domain conventions; for data use distinct lightness/chroma/shape/label/pattern so colour is not the only code; dark mode designs surface elevation and contrast explicitly, not an inversion; define primitive and semantic tokens and remap semantics on theme change.
- Decoration with no relationship to hierarchy, state, content or world is not a strategy (`colorize.md:51`).
- Contrast table: body text 4.5:1, large text 3:1, controls/icons/focus indicators 3:1 (AA only; no APCA, no AAA) (`colorize.md:55-61`). Craft floor: body and placeholder text >= 4.5:1, large >= 3:1; on coloured surfaces tint secondary text from that hue or the foreground, never gray (`IM/reference/craft-floor.md:9`).
- Verification list: check interactive states, overlays, text on images, disabled content, both themes; simulate common vision deficiencies; information by colour also needs text/shape/icon/position (`colorize.md:63`); each colour has a stable role; light and dark each composed (`colorize.md:67-74`).
- Prefer explicit colours over chains of translucent overlays (alpha makes contrast context-dependent) (`colorize.md:65`).
- Browser surfaces to theme from the palette: text selection, caret, custom scrollbars, focus rings, underline offset (`craft-floor.md:15`).
- Other floor items colour-adjacent: no gradient text (`craft-floor.md:33`); no coloured `border-left`/`border-right` over 1px on cards/callouts/alerts (`craft-floor.md:35`); no hard offset shadows outside a neobrutalist world (`craft-floor.md:36`); "light or dark picked by category" refused, pick from use scene (`craft-floor.md:42`). The "Refuse" list is described as defaults the brief can earn back, except the kicker/eyebrow ban (`craft-floor.md:21,27`).

### 5.5 Loaded symbols and clichés
- Loaded symbols: a subject's world does not license emblems tied to militarism, supremacy or hate movements as motifs, badges or ornament; named examples are the Rising Sun flag's rays, the Confederate battle flag, Nazi-era insignia and stylised variants; use the world's neutral forms; content that documents such a symbol as fact stays (`IM/SKILL.md:29`).
- Cliché calibration: AI interfaces cluster around a few looks: warm cream ground + high-contrast serif display + terracotta/signal-red accent; near-black + one neon accent + glowing edges; broadsheet hairlines + italic display serif + small tracked mono labels; flat saturated ink + black boxes + hard offset shadows + heavy condensed display. All are legitimate if the brief calls for them; where the brief is free, landing in one means the self-check failed (`IM/reference/new-work.md:69`).
- Measured prior for warm/bookish/child-facing subjects: cream ground, serif display with italic accents, lamplight; "treat that first palette as already spent"; reach for the subject's saturated materials first (`new-work.md:71`). A brief-pinned world pins the world, not its softest rendition (`new-work.md:69`).
- Our mapping (skills-reference:153): Japanese-inspired output collapses to cream paper + red circle + cherry blossoms; let the palette and brief lead.

---

## 6. Code worth copying

| Block | File : lines @ commit | Licence | ~Size | Recommendation |
|---|---|---|---|---|
| `BM25` class (init, tokenize, fit, score, vocabulary) | `UX/scripts/core.py:282-347` @ 623a9a9037d006ea727f8213f084d02a6b6f11b5 | MIT, (c) 2024 Next Level Builder | 66 lines | Rewrite |
| Tokeniser support: `_STOPWORDS`, `_SYNONYMS`, `_normalize` | `core.py:241-278` | MIT, same | 38 lines | Rewrite (our synonym list is different anyway) |
| Abstain logic (floor/coverage/margin) | `core.py:441-447` (plus `_query_coverage` 406-411) | MIT, same | ~12 lines | Rewrite |
| `_relative_luminance` + `contrast_ratio` | `UX/scripts/validate_data.py:148-160` | MIT, same | 13 lines | Rewrite |
| `COLOR_CONTRAST_PAIRS` | `validate_data.py:75-84` | MIT, same | 10 lines | Rewrite (our roles differ) |
| `_check_color_contract` | `validate_data.py:387-414` | MIT, same | 28 lines | Rewrite |

Recommendation: write all of it from scratch, stdlib-only, in our words. Reasons: (a) BM25 with k1=1.5, b=0.75 and the always-positive IDF is a textbook formula; the class is 66 lines, our version about 40-60 including tokeniser; (b) WCAG relative luminance/contrast is a published formula with fixed constants (0.04045, 12.92, 1.055, 2.4, 0.2126/0.7152/0.0722), not a creative work, and the originals are 13 lines; (c) the colour-contract function is welded to the UI/UX Pro Max column names (shadcn-style slots) and would need rewriting anyway; (d) our validator also needs OKLCH L, APCA Lc and gamut checks that the original does not have, and `validate_data.py` is 1,095 lines of unrelated checks; (e) rewriting means no `NOTICE.md` entry is needed for code. We still adopt the ideas, so list "design ideas from UI/UX Pro Max (MIT)" in `NOTICE.md` as courtesy. If a verbatim block is ever copied instead, keep `Copyright (c) 2024 Next Level Builder` and the MIT permission text (`ui-ux-pro-max/LICENSE:1-21`) with it and log file, commit, lines.

Implementation notes for the rewrite (not in the source): handle `#rgb` and `#rrggbb` inputs, case-insensitive; the original rejects anything but six digits. Add an APCA function separately (APCA is not in these repos; do not claim Lc values without implementing the published algorithm). Use `encoding="utf-8"` for CSV reads, and a UTF-8 stdout wrapper on Windows as `UX/scripts/search.py:35-39` does (an idea, trivial).

Nothing from `better-colors`, Theme Factory or Impeccable should be copied as code or text: better-colors ships markdown only (its JS snippets at `BC/palette-generation.md:30-36` use `culori`, which we cannot use); the Theme Factory theme files are tiny and we write our own palettes; Impeccable is prose only.

---

## 7. Do NOT borrow

### better-colors
- Severity/verdict reporting (`BC/SKILL.md:80-95`: HIGH/MEDIUM/LOW, "Not verified", Block/Approve, one row per root cause with `path:line`): built for auditing codebases; we generate palettes. Also a reference to sibling skills `better-accessibility`, `better-ui`, `better-interface` (`BC/SKILL.md:12,84`) that we do not have.
- "Report failing pairs and leave colours alone" (`BC/SKILL.md:52`, `BC/contrast.md:36`): our job is to produce a usable palette, so adjusting is in scope; keep its discipline (L first, preserve C and H, remeasure, report the delta).
- "One neutral + one accent" system shape as written: Wada combinations are 2-4 deliberate hues (see conflicts).
- The audit-an-existing-palette procedure (`BC/palette-structure.md:62-72`), codebase-migration warnings and bulk-conversion rules (`BC/color-formats.md:23-44`): out of scope.
- JS examples (`culori`): we are Python stdlib-only.
- Tailwind v4 `@theme` details (`BC/token-naming.md:78-99`): keep one short note only if we emit Tailwind output.

### UI/UX Pro Max
- Breadth: fonts, Google Fonts catalogue (20k-line licence JSON), icons, GSAP, 22 framework stacks, charts, landing patterns, design dials (variance/motion/density), `design_system.py` (1,668 lines), `reasoning_contract.py`, the validator's 1,000 lines of other checks, the calibration suite. Too broad (`UX/SKILL.md:3,111-131`; file sizes from `wc`).
- Its colour data: 192 product-type palettes are generic SaaS/e-commerce hexes with hand-nudged accents, not artistic palettes; do not import any row.
- Its shadcn-style naming (Primary/Secondary/Accent/Muted/Destructive/Ring) as our token vocabulary: it clashes with the BC grammar and `primary` collision rule (see conflicts).
- Priority-table rule categories (touch 44x44, CLS, etc.) (`UX/SKILL.md:20-31`): not colour.
- The persistence feature is optional; if adopted, a tiny version only (a saved JSON/markdown file with palette + tokens).

### Theme Factory
- Fixed font pairings and the `Typography` section (typography is out of scope).
- The static `theme-showcase.pdf` (888 lines, binary): cannot cover 348 plates; we render an HTML preview of the 3-5 best matches as applied mini-layouts.
- The ten preset themes themselves (e.g. `ocean-depths` hexes): generic corporate palettes, not ours; and its slide-deck focus (`TF/SKILL.md:14`).
- Its vague "ensure proper contrast" step with no measurement (`TF/SKILL.md:55`).

### Impeccable
- CLI binary and `impeccable context` setup (`IM/SKILL.md:19`), hooks (`SKILL.md:84`), live mode, `PRODUCT.md`/`DESIGN.md` infrastructure, concept-seed dice-roll, comp-measuring pipeline, all other 20+ sub-commands (`IM/SKILL.md:43-70`).
- The new-work typography blacklist and direction/challenger machinery (`new-work.md:46-57,67`).
- Craft-floor non-colour items: type measure, motion, spacing, copy, icon, modal rules (`craft-floor.md:11-14,16,25-41`).
- `ios.md`/`android.md` (MIT-derived from ehmo; `impeccable/NOTICE.md:5-11`): irrelevant, and the only NOTICE obligation in the repo is about those files.
- Its "dice roll" posture of overriding the model's taste: we need the opposite for pinned Wada plates (the brief wins).

---

## 8. Conflicts between the four skills and suggested resolutions

1. **Report vs adjust.** BC: report failing pairs, leave colours until asked (`BC/SKILL.md:52`). Our skill must ship a working palette. Resolution: adjust L only, keep C and H, remeasure, list every change with before/after and delta (BC's own fix procedure, `BC/contrast.md:38-57`); never move the plate colour itself, move the step/role it plays (BC `palette-generation.md:13`).
2. **Dark mode "reverse the ramp".** The kasane file suggests inversion; BC (`BC/palette-generation.md:71`, `BC/SKILL.md:72`) and Impeccable (`colorize.md:48,72`) both reject inversion (noted at `skills-reference.md:67`). Resolution: composed dark theme, validated separately.
3. **System shape: 1 neutral + 1 accent (BC) vs 2-4 deliberate hues (Wada).** Resolution (skills-reference:64): one palette colour seeds a tinted neutral ramp, one is the accent ramp, remaining colours become "voice"/region colours under Impeccable's Full palette strategy; each extra hue must satisfy BC's "one colour, one meaning" and 15-degree separation from status colours.
4. **Neutral tint.** BC: pure gray is a perfectly good default, tint is optional with chroma 0.005-0.02 (`BC/palette-structure.md:45-47`). Impeccable: tint neutrals only when it creates cohesion, but on coloured surfaces secondary text must never be gray (`colorize.md:44-45`, `craft-floor.md:9`). Not contradictory in practice; resolution: tinted neutral from the palette is our default (since the palette is the point), pure gray only on request; keep tint chroma in BC's 0.005-0.02 band for neutrals, and derive secondary text on coloured surfaces from that surface's hue.
5. **Restrained as default vs "grey plus one accent is the category default".** skills-reference says Restrained is the default for apps/docs; `IM/reference/mode-operate.md:7` warns a grey screen with one accent is the polish-free default and wants a committed shell palette; `new-work.md:65` itself says Restrained still asks colour to do real jobs. Resolution: default to Restrained for Operate/Read but make it tinted-neutral + one accent *plus* palette-derived state colours and one committed shell element; never ship plain grey.
6. **Percentages.** `new-work.md:65` gives Committed 30-60%; `colorize.md:27` denies a fixed percentage rule. Resolution: present 30-60% as a descriptive range for Committed only, not a requirement; do not invent percentages for the other three strategies.
7. **Naming vocabulary.** BC bans `primary` for brand and prefers `accent`, `bg`, `text` (`BC/token-naming.md:58-65`); UI/UX Pro Max's CSV uses Primary/Secondary/Accent/Muted/Destructive/Ring/Card (`core.py:27`); Theme Factory uses prose role labels (`TF/themes/ocean-depths.md:7-10`). Resolution: BC grammar for emitted tokens; keep a documented crosswalk table (section 2 last column) in the references file for people used to shadcn names.
8. **Contrast standards.** BC: WCAG 2 plus APCA, with AAA and Lc levels (`BC/contrast.md`); UI/UX Pro Max validator: flat 4.5 for all text pairs and 3.0 for Ring (`validate_data.py:75-84`); Impeccable: AA only (`colorize.md:55-61`). Resolution: validator enforces WCAG 2 AA as the gate (4.5 text, 3.0 large/UI) and reports APCA Lc beside it using BC's table; AAA and "preferred Lc 90" are advisory. Where they disagree on a pair, show both and say which requirement was used (`BC/contrast.md:5,61`).
9. **Text-polarity on mid-tones.** The UI/UX Pro Max data pairs black on `#3B82F6` (`colors.csv:2`) because it passes WCAG, whereas BC notes APCA and WCAG can favour different polarity (`BC/contrast.md:61`). Resolution: choose polarity by the required metric and report the other.
10. **Step numbering.** Tailwind (lightness-defined, inverts in dark) vs Radix (role-defined) (`BC/palette-structure.md:36-39`). Resolution: emit Radix-style role numbering internally (1-12), and export Tailwind 50-950 names in the semantic mapping if requested.
11. **Mode vs strategy granularity.** Impeccable decides mode from the surface, not the product (`IM/SKILL.md:41`); skills-reference proposes asking/inferring the mode first. Resolution: infer from the requested surface; ask only if the surface type is genuinely ambiguous.
12. **Cultural note in BC vs loaded-symbol rule in Impeccable.** Not a conflict but note both: cultural colour meanings (`BC/color-usage.md:85`) and loaded symbols (`IM/SKILL.md:29`) address different problems; the Rising Sun rays rule is Impeccable's only named example relevant to Japanese palettes, so keep it as an explicit line in our `SKILL.md`.

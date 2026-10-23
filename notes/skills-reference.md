# Reference skills for the Sanzo Wada palette skill

Build notes for a coding session. Four published skills cover the parts our skill needs: colour maths, palette data and search, the user flow, and judgement about how boldly to apply colour. This file says where each one lives, which files to read, what to borrow, and where our skill should deliberately differ.

The kasane palettes stay in their own reference file (`references/kasane-no-irome.md`) and are not part of this document.

## Getting the full source

Run `fetch-reference-skills.sh` at the start of the coding session. It sparse-clones only the relevant folders of each repository, pinned to the commits this file was written against, with their licence files:

```bash
bash fetch-reference-skills.sh            # creates ./reference-skills/
```

| Skill | Repository | Pinned commit | Commit date | Licence |
|---|---|---|---|---|
| better-colors | `jakubkrehel/skills` | `4c66b1f` | 2026-10-12 | MIT |
| UI/UX Pro Max | `nextlevelbuilder/ui-ux-pro-max-skill` | `623a9a9` | 2026-10-22 | MIT |
| Theme Factory | `anthropics/skills` | `dbd4588` | 2026-10-09 | Apache-2.0 |
| Impeccable | `pbakaus/impeccable` | `e3083ac` | 2026-10-21 | Apache-2.0 |

These repositories change often (better-colors restructured its reference files during October 2026), so file paths below refer to the pinned commits.

### Licensing when borrowing

Ideas, rules of thumb and numeric thresholds can be restated in our own words freely. When copying actual text or code:

- **MIT** (better-colors, UI/UX Pro Max): keep the original copyright line and permission notice with any substantial copied portion.
- **Apache-2.0** (Theme Factory, Impeccable): include a copy of the licence, mark files you changed, and carry over relevant attribution from the project's `NOTICE` file.

Preferred approach: write our rules in our own words, and copy code only where it saves real effort, adding a `NOTICE.md` to our skill that lists each source. This is a practical summary, not legal advice.

---

## 1. better-colors (Jakub Krehel) — the colour maths

**What it is.** A colour-system skill that generates ramps, maps ramp steps to roles and token names, converts between notations and measures contrast. Its stance: never report a contrast value you didn't measure, and never eyeball a colour you could compute.

**Read these files** (in `reference-skills/better-colors/skills/better-colors/`):

| File | Lines | Why |
|---|---|---|
| `SKILL.md` | 95 | Core principles and how the references divide the work |
| `palette-generation.md` | 108 | Ramp rules, multi-hue matching, dark mode, library usage |
| `palette-structure.md` | 72 | Which ramps a system needs and which step serves which role |
| `contrast.md` | 70 | WCAG 2 and APCA thresholds, what to check |
| `token-naming.md` | 99 | Primitive vs semantic tiers, naming grammar, anti-patterns |
| `color-usage.md` | 109 | One colour one meaning, one coloured action per view, cultural meaning |
| `color-formats.md` | 90 | Notation choice, gamut, modern CSS colour functions |

**Borrow:**

1. **Ramp-building rules.** Lightness changes steadily in OKLCH `L`; hue stays constant across the ramp; chroma peaks mid-ramp and falls toward both ends; light-end steps are finer (about 0.04–0.05 `L` apart for the lightest three, 0.07–0.10 mid-ramp); adjacent steps closer than 0.03 `L` mean a step should be dropped; neither end reaches pure black or white. Our skill expands each Wada colour into a ramp, so these rules apply directly.
2. **Matching several hues.** When ramps sit side by side, match perceived lightness exactly per step and match vividness *proportionally* to each hue's own maximum chroma, not by copying chroma values. Wada trios and quads mix hues like ochre yellow and indigo, so this matters more for us than for most products.
3. **Use a library, not hand maths.** It recommends `culori`, `colorjs.io` or `chroma.js` and interpolating in OKLab. For a Python script, `coloraide` is the equivalent.
4. **Step-to-role table** in `palette-structure.md` (page background, component background, hover, border, solid fill, low- and high-contrast text), with both Tailwind `50–950` and Radix `1–12` numbering. Use it as the target shape when turning a palette into tokens.
5. **Two-tier token naming.** Primitives named by hue and step, semantic tokens named by role, components reference only semantic tokens. Adopt its grammar (`text`, `bg`, `border`, `accent`) and its anti-pattern list (no `--color-light-gray`, no numbered semantics).
6. **Contrast thresholds and the mid-lightness trap.** WCAG 2 (4.5:1 text, 3:1 large text and UI) plus APCA levels (Lc 75 body, Lc 60 labels and headings, Lc 45 large text). Its observation that a background near `L` 0.75 caps achievable contrast is critical for us: many Wada colours are mid-lightness and cannot sit behind body text at all. Encode this as a rule that mid-lightness palette colours become fills, borders or large-type backgrounds, never body-text backgrounds.
7. **Dark mode guidance.** Reduce chroma, widen separation at the dark end, recheck every pair in both appearances, and pick the switching mechanism (`prefers-color-scheme`, `.dark` class, or `light-dark()`) based on whether users can toggle.
8. **Cultural meaning** (`color-usage.md`): colour meanings in finance and status flip between locales (red for gains in Chinese financial UIs). Worth a line in our skill, since users choosing East Asian palettes may also be shipping to East Asian markets.

**Where we differ:**

- better-colors builds systems from **one neutral ramp plus one accent ramp**. A Wada combination is 2–4 deliberate hues. Our adaptation: one palette colour seeds a tinted neutral ramp, one becomes the accent ramp, and any remaining colours become region or "voice" colours under Impeccable's colour strategies (section 4).
- It **reports** failing pairs and fixes them only when asked. Our skill's job is to produce a usable palette, so adjusting is in scope, but keep its discipline: adjust `L` first, preserve `C` and `H`, remeasure, and tell the user exactly what moved and by how much.

**Optional follow-ups for the kasane file** (it stays separate, but two of its notes conflict with this skill's guidance): its dark-mode tip suggests inverting the ramp, which better-colors and Impeccable both reject in favour of a composed dark theme; and its shade rules scale chroma by fixed factors rather than proportion of each hue's maximum.

**Don't borrow:** its review output format (severity tables, Block/Approve verdicts). It's built for auditing codebases, and our skill generates rather than audits.

---

## 2. UI/UX Pro Max (nextlevelbuilder) — data and search architecture

**What it is.** A large design-knowledge skill that stores styles, palettes, font pairings and UX rules as CSV files and queries them with a Python search script, so Claude retrieves a few relevant rows instead of loading everything into context.

**Read these files** (in `reference-skills/ui-ux-pro-max/.claude/skills/ui-ux-pro-max/`):

| File | Lines | Why |
|---|---|---|
| `SKILL.md` | — | Query contract, workflow, zero-result rule |
| `scripts/search.py` | 177 | CLI entry point and argument design |
| `scripts/core.py` | 993 | `CSV_CONFIG` (around line 18) and the `BM25` class (around line 282) |
| `scripts/validate_data.py` | 1,095 | `contrast_ratio` (around line 157) and `_check_color_contract` (around line 387) |
| `data/colors.csv` | 193 | Palette row schema with paired on-colours |
| `data/data-provenance.json` | — | Per-record source and verification metadata |

**Borrow:**

1. **Palettes as data plus a search script.** Each domain in `CSV_CONFIG` names a CSV, the columns to search and the columns to return; search is BM25 ranking with no external dependencies. For us: put the Wada combinations in `data/wada.csv` with columns such as `id`, `size` (2/3/4), `hex_1..hex_4`, `names`, `mood_tags`, `season`, `temperature`, `source`. Search over names and tags; return the hex values and notes. Our version needs perhaps 150 lines, not 1,000.
2. **Paired on-colours in the schema.** `colors.csv` stores every fill alongside its readable foreground (`Primary` with `On Primary`, `Background` with `Foreground`, and so on). Precompute the same for each Wada colour: the best text colour for it and the measured contrast.
3. **The validator.** `_check_color_contract` checks every role pair against a minimum ratio, flags muted text that out-contrasts primary text, and flags a destructive colour that reads as green. Copy the idea into `scripts/validate.py` and run it on every palette our skill generates, before showing it to the user.
4. **Query contract and the no-fabrication rule.** Keep each query to one intent and a few terms; retry once with a narrower query; if nothing matches, say the result came from defaults rather than presenting it as a database match. Adopt this nearly verbatim in spirit: with 348 combinations it's easy for Claude to invent a plausible "Wada #212".
5. **Provenance per record** (`data-provenance.json`): each row traces to a source. A lighter version suits us: a `source` and `licence` column in `wada.csv`, pointing to colorcombinations.org (CC BY 4.0) or the mattdesl dataset (MIT).
6. **Persisting the chosen system** (`--persist` writes `design-system/<project>/MASTER.md`, with per-page overrides that never silently overwrite). Optional for us, but useful: save the chosen palette and tokens so a later session reuses them instead of re-picking.

**Don't borrow:** the breadth (fonts, icons, GSAP presets, 22 framework stacks), the design dials, or the test suite. They solve a much wider problem than ours.

---

## 3. Theme Factory (Anthropic) — the user flow

**What it is.** A small skill with ten preset colour and font themes, each in its own file, applied consistently to an artifact, plus a fallback for generating a custom theme.

**Read these files** (in `reference-skills/theme-factory/skills/theme-factory/`):

| File | Why |
|---|---|
| `SKILL.md` | The four-step flow and the custom-theme fallback |
| `themes/*.md` (10 files) | One-file-per-theme format: name, description, palette with a role per colour, fonts, best uses |
| `theme-showcase.pdf` | How it previews all options at once |

**Borrow:**

1. **The flow.** Show options visually, ask the user to choose, wait for explicit confirmation, then apply consistently. Our skill should never silently pick one of 348 combinations.
2. **A role per colour in the palette file**, written next to the hex value ("primary dark", "backgrounds and text"). Our generated palettes should present each colour with its assigned UI role in the same way.
3. **"Best used for"** on each theme. Add an equivalent to our search results so Claude can explain why a combination fits the brief.
4. **Custom fallback with review.** When no Wada combination fits, the skill may compose one in Wada's spirit, but must name it as an original composition, show it for review, and only then apply it.

**Where we differ:** a static PDF showcase can't cover 348 combinations. Instead, render a small HTML swatch preview of the 3–5 best search matches, each shown as an applied mini-layout (background, card, text, button) rather than bare swatches, in line with Albers' point that colour must be judged in context.

**Don't borrow:** fixed font pairings. Typography is outside our skill's scope unless we choose to add it later.

---

## 4. Impeccable (Paul Bakaus) — judgement about colour

**What it is.** A full design-direction system (CLI, hooks, live preview, many sub-commands) that pushes agents away from generic UI. We want only its colour judgement, which lives in a few markdown files.

**Read these files** (in `reference-skills/impeccable/.claude/skills/impeccable/`):

| File | Lines | Why |
|---|---|---|
| `SKILL.md` | — | Modes, "the brief wins", the loaded-symbols rule |
| `reference/colorize.md` | 86 | Colour strategy, system-scale application, contrast and verification |
| `reference/new-work.md` | 154 | The four colour strategies (around line 65) |
| `reference/craft-floor.md` | 44 | Quality floor, including tinted secondary text |
| `reference/mode-persuade.md`, `mode-operate.md`, `mode-read.md` | ~20 each | What each surface type asks of colour |

**Borrow:**

1. **Modes decide boldness.** Persuade and Experience surfaces (landing pages, portfolios) may let colour own large regions; Operate and Read surfaces (apps, dashboards, docs) use colour mainly for action, selection, status and hierarchy. Our skill should ask or infer the surface type before deciding how much of a Wada palette to put on screen.
2. **Four colour strategies, which map neatly onto Wada sizes:**
   - *Restrained*: neutrals tinted from the palette plus one accent. Any Wada combination can be applied this way; the default for apps and docs.
   - *Committed*: one saturated colour covers roughly 30–60% of the surface. Natural for Wada duos.
   - *Full palette*: 3–4 named roles. Natural for Wada trios and quads.
   - *Drenched*: the surface is the colour. For bold landing pages and posters.
3. **Build roles, not a bag of swatches.** Canvas, elevated surfaces, primary and secondary text, action and focus, borders, status. This aligns with better-colors' role table.
4. **Concrete craft rules:** on coloured surfaces, tint secondary text from the surface hue instead of using grey; reduce chroma near white and black; prefer explicit colours over stacked translucent overlays (which make contrast unpredictable); simulate common colour-vision deficiencies; never let colour be the only signal.
5. **Dark mode is composed, not inverted.** Same rule as better-colors, stated independently.
6. **The brief wins.** If the user pins a specific Wada combination or kasane pattern, honour it even when it's an unusual choice; adjust only for contrast, and say so.
7. **Loaded symbols stay out of decoration.** Impeccable explicitly names the Rising Sun flag's rays as a motif to avoid. Adopt this: a Japanese palette skill should not suggest sunburst rays or imperial or militarist emblems as decoration.
8. **Watch for clichéd defaults.** Impeccable warns that agents drift toward predictable renditions for certain subjects. Our equivalent: Japanese-inspired output tends to collapse into cream paper, a red circle and cherry blossoms. The skill should let the chosen palette and the user's brief lead, not the stereotype.

**Don't borrow:** the CLI binary, hooks, live mode, `PRODUCT.md`/`DESIGN.md` infrastructure, or comp-measuring pipeline. They're far heavier than a palette skill needs.

---

## How the pieces fit

Proposed layout for our skill:

```
sanzo-wada-palettes/
├── SKILL.md                      # flow (Theme Factory) + modes/strategies (Impeccable) + core rules (better-colors)
├── NOTICE.md                     # attributions for data and any copied code
├── references/
│   ├── kasane-no-irome.md        # existing, kept separate
│   └── application-rules.md      # ramps, roles, tokens, contrast, dark mode, Albers — in our own words
├── data/
│   └── wada.csv                  # combinations + on-colours + tags + source/licence (UI/UX Pro Max pattern)
└── scripts/
    ├── search.py                 # BM25-lite, stdlib only (UI/UX Pro Max pattern)
    ├── build_tokens.py           # palette → OKLCH ramps → primitive + semantic tokens (better-colors rules)
    └── validate.py               # contrast and role checks before showing results (UI/UX Pro Max validator)
```

Intended workflow inside `SKILL.md`:

1. Identify the surface mode and pick a colour strategy (Impeccable).
2. Search `wada.csv` by mood, season or named colour; if nothing matches, say so (UI/UX Pro Max).
3. Preview the 3–5 best matches applied to a mini-layout and wait for the user's choice (Theme Factory, Albers).
4. Build ramps and tokens from the chosen combination (better-colors).
5. Validate every role pair; adjust lightness only where needed and report the changes (UI/UX Pro Max validator, better-colors fix rule).
6. Compose dark mode separately and validate it too (better-colors, Impeccable).

## Kickoff prompt for the coding session

> I'm building a Claude skill called `sanzo-wada-palettes`. Read `skills-reference.md` first, then run `fetch-reference-skills.sh` and read the files it lists for each skill. `references/kasane-no-irome.md` is an existing reference file to include unchanged. Start by proposing `data/wada.csv`'s schema and sourcing it from colorcombinations.org (CC BY 4.0) or the mattdesl dataset (MIT), then draft `SKILL.md` following the workflow in the "How the pieces fit" section. Write rules in our own words; if you copy code from a reference skill, record it in `NOTICE.md`.

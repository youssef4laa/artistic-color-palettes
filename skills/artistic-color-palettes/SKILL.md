---
name: artistic-color-palettes
description: "Chooses real artistic colour palettes and turns them into working UI colour systems. Sources are Sanzo Wada's A Dictionary of Color Combinations (plates 1-348), Heian kasane no irome layered colour patterns, palettes sampled from public-domain paintings, and the perceptual principles of Josef Albers' Interaction of Color. It builds OKLCH ramps, two-tier design tokens and CSS variables, colour proportions, measured WCAG 2 and APCA contrast and a composed (never inverted) dark mode, and hands the result to Impeccable, Taste, UI/UX Pro Max and other design skills through DESIGN.md. Use this skill whenever the user wants a palette, a colour or color scheme, a theme or brand colours; asks to make a site or app look less generic; mentions Japanese, traditional, vintage, painterly or seasonal colours; wants dark mode derived from a palette; needs design tokens or CSS variables generated from colours; or asks to fix contrast on a palette, even if they never say the word palette."
license: "MIT (see NOTICE.md; references/kasane-no-irome.md is CC BY-SA 4.0)"
compatibility: "Bundled scripts need Python 3.10+ (standard library only) and no network access."
metadata:
  version: "0.1.0"
---

# Artistic colour palettes

This skill finds a palette with a real provenance (a Wada plate, a kasane pattern, a sampled
painting or an editorial palette), shows it applied, and, once the user has chosen, turns it into
ramps, tokens, proportions, measured contrast and a composed dark mode written to shared files.

**Boundaries.** It owns palette selection, ramps, two-tier tokens, colour proportion, contrast
measurement and adjustment, composed dark mode, colour-vision checks and the colour region of
`DESIGN.md`. It does not do typography, layout, spacing, motion, component craft or UX copy. When
asked for those, give the colour token to use and defer by name: typography to Impeccable
`typeset`, Taste's type roles or UI/UX Pro Max font pairings; layout and density to Impeccable `layout`, Design
Principles or interface-design; motion to Impeccable `animate`; component states to Impeccable
`polish` or interface-design; copy to Impeccable `clarify`. Staying in lane is what lets the
neighbours trust our file.

## Why the workflow looks like this

Generic palettes come from an agent's habits; a palette with a provenance, placed in deliberate
proportions and measured, does not look generic. Colours also change with their neighbours,
their area and their ground (Albers), so a palette is judged only as an applied layout in light,
dark and greyscale, never as bare swatches. And the user's taste, not ours, picks among vetted
candidates, which is why the skill waits for an explicit choice.

## Workflow

### 1. Read the project before proposing anything

Look for, in this order: `PRODUCT.md` (users, brand commitments, accessibility standard, markets);
an existing `DESIGN.md` (frontmatter `colors:`, `## Colors`, Named Rules; our `acp:` markers mean
this is a re-run); `.interface-design/system.md`; `design-system/*/MASTER.md` (the slug varies, so
glob); existing token sources (CSS custom properties, Tailwind config, `tokens.json`).
`.taste-skill/direction.json` is read only to notice a conflict.

If a palette already exists, whether the user's or one a neighbour generated, offer two options
and wait: **replace** it with one from our data (keep the old values in the report for comparison)
or **refine** it (keep its hues; rebuild ramps, measure, fix contrast, compose dark mode). Never
add a second palette silently: two competing token sets in one project is worse than either.

Note pinned colours and brand commitments. A palette the user pinned is honoured as given; the
only change the skill makes to it is a contrast fix, said out loud before it is applied.

### 2. Name the mode and the colour strategy

Use Impeccable's words verbatim so every neighbour reads the same thing. Mode, from the surface
being built (not the product category): **Persuade**, **Operate**, **Read**, **Experience**.
Strategy, chosen before any colour: **Restrained**, **Committed**, **Full palette**, **Drenched**.
Write one sentence of the physical scene (who looks at it, where, under what light) and let it
decide light or dark as the default. Infer the mode; ask only if the surface is ambiguous.

Read [the style recipes](references/style-recipes.md) (cited below as *Recipes §n*) before this
step on a first run: it holds the full chain from brief to hand-off, the mode and family tables,
role mapping per family, the anti-cliché list and three worked examples with measured numbers.

### 3. Search the data

```bash
python <skill>/scripts/search.py --count 3 --mood refined,cool --source-type wada_plate "slate blue"
python <skill>/scripts/search.py --id wada-218        # exact lookup; also ed-…, paint-…, kasane-…
```

- Filters first (`--count`, `--mood`, `--hue`, `--era`, `--source-type`, `--season`), then a short
  free-text query. One intent per query: "earthy", then separately "autumn", rather than both at once.
- Weak or zero results: say "no match" and name the filters used, retry once narrower or with
  one filter relaxed, and then stop. Exit codes: 0 results, 1 no match, 2 not in the data.
- When the user asks for Japanese paintings, put Hokusai's *Great Wave* first: it is the only
  East Asian work in the set.

Read [Wada's method](references/wada-method.md) when a Wada plate is on the
shortlist: plate sizes, same-tone and different-tone patterns, the internal pairs of four-colour
plates, and what Wada says about ground and quantity. Read
[kasane no irome](references/kasane-no-irome.md) when the user wants seasonal, Heian,
kimono-like or layered Japanese colour, names a season or plant, or a kasane pattern is shortlisted:
it maps garment layers to UI roles and explains why every hex is an interpretation.

### 4. Show 3–5 candidates applied, then wait

```bash
python <skill>/scripts/preview.py --palette wada-218 --palette wada-139 --palette kasane-fuji \
  --strategy restrained --mode operate --out palette-preview.html
```

The page shows each candidate as a mini-layout in light, composed dark and greyscale at the
strategy's proportions, with its provenance label. For each candidate also give in chat: the
label, hex and OKLCH per colour, tone pattern, the strategy it suits, one line on fit, and its
known trap (mid-lightness members, a vibrating pair, colour drift).

**Then wait for the user's explicit choice** (the rule Theme Factory also follows). Do not pick
one of 348 plates on the user's behalf and do not proceed on "any of these is fine"; ask which.
Skip this step only when the user already named a plate, pattern, painting or their own colours.

### 5. Build ramps and tokens

```bash
python <skill>/scripts/build_tokens.py --palette wada-218 --strategy restrained --mode operate \
  --accent "Helvetia Blue" --neutral-from 3 --out <tmp>/tokens.json
```

`--roles accent=…,ground=…,brand=…,drench=…,neutral=…` assigns roles (name, 1-based index or hex);
`--pin` controls which palette colours are kept exactly at their nearest step (see `--help` for the
current default); `--hex 'Name=#rrggbb,…'` takes colours that are not in the data. The output
holds both light and dark ramps, the semantic roles, voices, status colours and proportion targets.

Turn the user's constraints into flags rather than hand-editing the JSON afterwards, because
hand edits escape the validator and the generated `DESIGN.md` text then contradicts the tokens:

- A brand rule about the button label ("white text on buttons") → `--on-accent light` (or `dark`):
  the label is fixed and the fill moves to a step where it passes.
- A rule against saturated colour behind text, or a calm product → `--action-style tinted`
  (pale accent fill, accent border, dark label) or `outline`; the default `solid` is a filled button.
- A principle asking for contrast "comfortably above the minimum" → `--text-min 7` (or the number
  the user gives) raises the text gate.

Voices have two forms: `--color-voice-n` is a region fill (band, section, card) and keeps the
exact plate colour, with its own measured label colour; `--color-voice-n-mark` is the step that
passes 3:1 for chart marks, icons and meaningful edges. Use the region form for bands so the
plate's character survives.

Decide roles in this order: neutral tint seed, accent, shell or ground, voices, then status.
Keep a quad plate's pairs together; a kasane *hitoe* is the edge accent; a painting's largest
ground seeds the tint (*Recipes §1.8*). A pinned plate colour is the point of the palette, so it
is never darkened to pass a check: the role moves to a neighbouring step and the pinned colour keeps
a non-text job (band, rail, chart mark).

Read [the application rules](references/application-rules.md) when building or
explaining ramps and tokens, fixing contrast, composing dark mode or naming status colours: it
holds the ramp tables, chroma rules, role map, contrast gate and targets, the mid-lightness trap,
vibrating and vanishing pairs, CVD and cultural-meaning rules.

### 6. Validate and fix contrast

```bash
python <skill>/scripts/validate.py <tmp>/tokens.json --fix --in-place   # add --all to list every pair
```

The **gate** is WCAG 2 (body 4.5:1, large text 3:1, meaningful non-text 3:1) and must pass;
the **target** is APCA Lc (body 75, labels 60, large 45, non-text 30–45), reported and approached
where the palette allows. `--fix` changes lightness only, so hue and chroma, the character of the
palette, survive. Report every adjustment exactly as printed (role, mode, before → after hex,
L and ratio), and list the flags it raises: mid-lightness fills, vibrating pairs, vanishing
regions, faint state changes, CVD collisions. Exit code 1 means a gate failure remains; do not
hand off until it is resolved or the user accepts it.

Read [the Albers principles](references/albers-principles.md) when a flag needs explaining, or
when the user asks why a palette that looked good as swatches fails in the layout.

### 7. Compose the dark mode (never inverted)

Dark mode is a new ground, so it is recomposed from the same seeds with its own ramp table, lower
chroma and dark surfaces capped near neutral; the light ramp reversed is a defect. `build_tokens.py`
already composes it and `validate.py` measures both modes, because contrast never carries over.
Your part: choose the dark ground from the scene, keep a saturated plate colour as a band on a
deeper ground of its hue rather than as the page, check that lightness order never flips, and state
the switching mechanism the tokens use (`prefers-color-scheme` plus a `[data-theme]` override).

### 8. Hand off

```bash
python <skill>/scripts/handoff.py --tokens <tmp>/tokens.json --project-dir . --dry-run
python <skill>/scripts/handoff.py --tokens <tmp>/tokens.json --project-dir . --claude-md yes --user-confirmed [--notes FILE]
```

This writes `design/palette.json` (machine source of truth), `design/tokens.css` (primitives,
semantic `--color-*`, dark scope, alias blocks for neighbours) and only our two marker regions in
`DESIGN.md` (frontmatter between `# acp:begin tokens` / `# acp:end tokens`, body of `## Colors`
between `<!-- acp:begin colors v1 -->` / `<!-- acp:end colors -->`), rendered from
[the hand-off template](assets/palette-handoff.template.md). Re-runs are byte-identical and never
touch text outside the markers. If `DESIGN.md` exists without our markers, the script exits 3 and
prints the diff: show it, ask once, and re-run with `--yes` on approval. `--allow-failing` exists
but hand off a failing gate only when the user explicitly accepts it.

Write nothing in DESIGN.md outside our markers; usage guidance goes in the chat report or through
`handoff.py --notes FILE`, which renders inside the region (a `#### Usage notes` block), so it is
regenerated with the hex instead of going stale beside it.

**Ask once per project** before the first hand-off: "May I add a short palette pointer to this
project's `CLAUDE.md` and `AGENTS.md`?" Pass `--claude-md yes --user-confirmed` (the script refuses `yes` without it), or `--claude-md declined` only when
the user actually said no (then paste the pointer text in chat instead); `--claude-md no` removes
an existing pointer. If you could not ask yet, omit the flag (it is recorded as `not_asked`) and
put the question in your final message; an unasked question is not a refusal, and it is not a yes
either. Never pass `--claude-md yes` on an assumption and ask afterwards: the user chose an opt-in
pointer precisely so that nothing lands in their always-loaded instructions without consent. The answer is stored in `palette.json` (`handoff.claude_md`), so do not ask again. Never
write the pointer unasked and never to the global `~/.claude/CLAUDE.md`.

## Provenance and the no-fabrication rule

The skill's credibility rests on every colour being traceable, so it never invents a source.

- The data holds Wada plates 1–348 only (Vol. 2 is not included), 30 editorial palettes, 25
  paintings and 33 kasane patterns. If `search.py` does not return it, it does not exist: never
  invent a plate number, a painting, an editorial palette or a kasane pattern, and never fill a
  shortlist with near misses.
- When nothing fits, the skill may offer an **original composition**, labelled as such and shown
  in a preview for review before any use.
- Every hex approximates a print or a photograph of a painted or dyed original. Never call a value
  "Wada's exact colour".

Every suggestion carries exactly one of these labels:

- "Wada plate N (*A Dictionary of Color Combinations*, 1933)"
- "Editorial palette by colorcombinations.org, inspired by Wada's method" (never "a Wada plate")
- "Sampled from <title>, <artist>, <date> by colorcombinations.org"
- "Kasane no irome: <name> (Heian court colour layering; hex values are interpretations)"
- "Original composition by this skill (not a plate)"

`--provenance` (for `--hex` input) never names a plate, painting, kasane pattern or editorial
palette; the scripts refuse such a label, because a data source's label must come from the data.
If the user calls their colours "plate 412", say it is not in the data and label them as theirs.

Six paintings carry a **drift note** (the sampled values show the work as it looks today, not as
painted): *Sunflowers*, *A Sunday on La Grande Jatte*, *The Great Wave*, *The Kiss*, *The Scream*
and *Girl with a Pearl Earring*. `search.py` prints it; repeat it whenever one of them is offered.
Colours passed with `--hex` are labelled "Original composition (colours supplied by the user)" in
the files; when they are the user's brand colours, a refinement ("refined from <neighbour>'s
palette") or the skill's own composition, say which in chat.
Generated CSS credits the source, e.g. `/* Wada plate 229 via colorcombinations.org (CC BY 4.0) */`;
the full credits are in [NOTICE.md](NOTICE.md) and data checksums in [the snapshot](data/SNAPSHOT.md).

Avoid the reflexes that make "Japanese" or "artistic" look stock: cream + red circle + cherry
blossom, Rising Sun rays or any imperial or nationalist emblem, beige "Zen" minimalism by default,
a European painting presented as eastern, and the generic AI looks (cream + serif + terracotta,
near-black + neon). The full anti-cliché list is *Recipes §1.6*.

## Proportion targets (the skill's convention)

Wada's plates show equal-area swatches only for convenience, so these numbers are ours, not his;
label them that way. `build_tokens.py` emits them per strategy.

| Strategy | Ground + neutrals | Palette colours | Accent |
|---|---|---|---|
| Restrained | 85–95% | voice colours 0–5% | 2–8% |
| Committed | 35–65% | one palette colour 30–60% | ≤ 8% |
| Full palette | 45–65% (ground) | secondary 15–30%, tertiary 5–15% | ≤ 8% |
| Drenched | 5–30% (text, neutrals) | palette surface 60–90% | ≤ 8% |

An accent with chroma ≥ 0.15 stays ≤ 5%; a kasane *hitoe* edge 5–10%; painting grounds take shares
in proportion to their measured coverage.

## Working with other skills

Colour is all we contribute; a neighbour's type, layout, spacing, motion and copy decisions stand.
**Precedence**, highest first: the user's brief in chat; the user's pinned palette or brand
commitments in `PRODUCT.md` or in `DESIGN.md` outside our markers; a neighbour's structural
decisions (mode, layout, type, density); our colour rules and region; colours a neighbour
generated on its own. The one override we make is a measured contrast fix, always reported.

| Skill | What we read | What we write for it | How it picks the palette up |
|---|---|---|---|
| **Impeccable** | `PRODUCT.md`, `DESIGN.md` | our `DESIGN.md` regions, with strategy and mode as Named Rules; `--color-*` tokens its scan finds | **Automatic**: `impeccable context` loads `DESIGN.md`; `colorize` re-reads it |
| **Taste** | `.taste-skill/direction.json` (conflicts only) | alias block `--bg --surface --ink --muted --accent --accent-ink --field-n` | Through the opt-in pointer, or tell it: run with `--keep palette`, one accent only, `--allow palette-purple` for violet or indigo palettes |
| **Design Principles** (owl-listener) | nothing (process skill) | nothing | Through the pointer only; if a team principle contradicts a colour rule, the principle wins and we say which rule bent |
| **Design Principles** (libreuiux) | nothing | proportion Named Rules that supersede its 60-30-10 | Through the pointer only; plates are never judged by colour-wheel geometry |
| **UI/UX Pro Max** | `design-system/*/MASTER.md` | alias block `--color-primary … --color-ring`; with consent, one pointer line under its `### Color Palette` | Conditionally: its names resolve to ours once `tokens.css` is in use; never run it with `--force` |
| **Theme Factory** | nothing persistent | its custom-theme bullets (bg, text, accent, one voice) built from `palette.json` | Through the pointer, or tell it to use the shared palette instead of its showcase; our measured report replaces its contrast step |

interface-design is handled like Pro Max: it reads `tokens.css` and its alias block resolves to
ours. Impeccable has one hazard: when its `document` step asks refresh / overwrite / merge, tell
the user beforehand to choose **merge**, then re-run `handoff.py`. Write our region before
Impeccable's "Commit the world" step so its roll honours the palette. Do not claim that Taste,
Design Principles or Theme Factory pick up the palette automatically; without the pointer they only
see it when told. Read [the interop contract](references/interop.md) when a
neighbour is installed or its files are present: it has the token map per neighbour, the marker
and creation rules, read order, precedence and the pointer text.

## Scripts

All scripts are Python 3.10+, standard library only, need no network, and handle Windows paths
and Japanese names. Run them by path from the project root; `<skill>` is this skill's folder.
Each has `--help`.

- `scripts/search.py`: filter and rank the 436 palettes; `--id` for exact lookups; `--json`.
- `scripts/preview.py`: one self-contained HTML page comparing 3–5 candidates (`--any-count` to override).
- `scripts/build_tokens.py`: ramps, roles, voices, status colours, proportion targets as JSON.
- `scripts/validate.py`: WCAG 2 gate, APCA target, flags, CVD; `--fix` moves lightness only.
- `scripts/handoff.py`: `DESIGN.md` regions, `design/palette.json`, `design/tokens.css`, pointer.
  With `--palette` or `--hex` it runs build and fix itself; `--dry-run` writes nothing.
- `scripts/build_data.py` rebuilds `data/` from raw downloads (maintainers only);
  `scripts/colorlib.py` is the shared colour library (`--self-test`).

## Final report in chat

Keep it short; the details live in `design/palette.json`. Use this shape:

```
Palette: Wada plate 218 (*A Dictionary of Color Combinations*, 1933)
Roles: accent Helvetia Blue #005b8d · voice Grayish Lavender A #b5b1d8 · neutrals tinted from Plumbeous #70727c
Strategy / mode: Restrained · Operate (dispatcher at a desk monitor in daylight; light default)
Proportion targets (this skill's convention): neutrals 85–95%, voice 0–5%, accent 2–5%
Contrast: WCAG gate passes on all pairs, light and dark; APCA below target on N pairs (dark links, status text)
Adjusted: [light] warning #d29848 → #bb822f (L 0.72 → 0.65; 2.34 → 3.07:1 on bg)
Flags: bg/surface separated by border; success/danger need icons (CVD)
Files: DESIGN.md (## Colors region), design/palette.json, design/tokens.css · pointer: yes
```

Add the drift note on the provenance line when it applies, and say plainly what was not done
(for example, no browser check of the real page).

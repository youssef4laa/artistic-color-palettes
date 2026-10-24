# Interop: working beside other design skills

The skill is a colour specialist that other design skills can consume without being told. This
file fixes what it owns, the words it shares, the hand-off files and their precedence, and how
each neighbour sees the palette. Everything here is colour only.

## 1. Boundaries

Colour only, as SKILL.md states: palette selection, ramps, two-tier tokens, proportion, contrast,
composed dark mode, CVD checks, the colour region of DESIGN.md and its companions. Typography, layout,
spacing, motion, component craft and copy are a neighbour's; when asked, give the token to use and defer
by name (Impeccable `typeset` / `layout` / `animate` / `polish` / `clarify`, Taste's type roles, UI/UX Pro Max
font pairings, interface-design, Design Principles composition).

## 2. Shared vocabulary

Impeccable's names are used verbatim: modes **Persuade, Operate, Read, Experience**; colour
strategies **Restrained, Committed, Full palette, Drenched**. The DESIGN.md region states both in a
Named Rule so a neighbour reads the same words it uses. Our tokens use better-colors grammar
(`--color-{bg|text|border}-…`, `--color-accent-…`); the alias blocks below translate them.

| Our semantic token | Taste (`references/colour.md`) | UI/UX Pro Max (`MASTER.md`) | interface-design (`system.md`) | Theme Factory bullet |
|---|---|---|---|---|
| `--color-bg` | `--bg` | `--color-background` | (page) | "Primary background color" |
| `--color-surface` | `--surface` | `--color-card` | — | — |
| `--color-text` | `--ink` | `--color-foreground`, `--color-card-foreground` | `--foreground` | "Text" |
| `--color-text-muted` | `--muted` | `--color-muted-foreground` | `--secondary` (placeholder: `--muted`) | — |
| `--color-border-subtle` | — | `--color-border` | `--faint` | — |
| `--color-accent` | `--accent` | `--color-primary` (and `--color-accent` for the CTA) | `--accent` | "Accent color for highlights" |
| `--color-on-accent` | `--accent-ink` | `--color-on-primary` / `--color-on-accent` | — | — |
| `--color-voice-n` | `--field-n` (+ ink) | `--color-secondary` | — | "Secondary accent" |
| `--color-danger` | — | `--color-destructive` / `--color-on-destructive` | — | — |
| `--color-focus` | (accent outline) | `--color-ring` | — | — |

Pro Max's `primary` is our `accent`; the word "primary" is otherwise reserved (application-rules
§2). Taste's one accent is our `--color-accent`; extra palette members map to `--field-n` or stay
unused on a Taste page.

## 3. The hand-off contract

**Files.** One primary shared file, `DESIGN.md` at the project root in the Google DESIGN.md format
that Impeccable loads through `impeccable context`. Two companions: `design/palette.json` (machine
source of truth; the DESIGN.md region is generated from it) and `design/tokens.css` (two-tier
tokens: primitives, then semantic `--color-*` on `:root`, a dark scope, then the alias blocks for
Taste, UI/UX Pro Max and interface-design so their names resolve to ours without a second palette).
The chosen paths are recorded in `palette.json`; the user may move `tokens.css` into the project's
styles directory. All three carry the same `acp:` version marker.

**Marker regions in DESIGN.md (we rewrite only these).**
1. Frontmatter: inside `colors:`, the lines between `# acp:begin tokens` and `# acp:end tokens`,
   one `role: "#HEX"` entry per semantic role (`bg`, `text`, `accent`, …; Impeccable accepts any
   CSS colour string). If those keys clash with an existing `colors:` map, `handoff.py --key-prefix`
   namespaces ours (e.g. `acp-bg`).
2. Body: under the canonical `## Colors` heading, between `<!-- acp:begin colors v1 -->` and
   `<!-- acp:end colors -->`, in this fixed order: one-sentence palette character; provenance line
   with licence credit; role entries as `**Name** (#HEX / oklch(...))` under `### Primary`,
   `### Secondary`, `### Tertiary`, `### Neutral`; `### Named Rules` ("The … Rule." lines: strategy
   + mode, proportions, contrast floor); light and dark token tables by key; measured contrast per
   text/surface pair (WCAG 2 ratio and APCA Lc); adjustments made and why; a "do not change
   without re-validating" note; pointers to `design/tokens.css` and `design/palette.json`; a short
   neighbour map (Taste roles, Pro Max roles, Theme Factory bullets). Hex in the body is allowed
   because Impeccable's own template writes it; it is generated from the same `palette.json`
   values as the frontmatter, so the two can never differ. Bump `v1` on a schema change.

**Creation and editing rules.** DESIGN.md absent: create it with frontmatter `name`,
`description`, `colors` and only a `## Colors` section, first line
`<!-- acp:seed palette-only; Impeccable's document command will fill the other sections -->`
as the first line *after* the frontmatter (the file still starts with `---`, so parsers find it)
(never Impeccable's own `SEED` marker). Present without our markers: insert them inside the
existing `## Colors` (or add the section in canonical order), show the diff and ask once. Present
with markers: replace only between markers; a re-run is byte-identical. Never touch other text,
`PRODUCT.md`, `.impeccable/*`, `.taste-skill/*`, `.interface-design/system.md`, `MASTER.md`.
Section headings are never renamed.

**Read-before-write order.** 1. `PRODUCT.md` (users, brand commitments, accessibility standard,
markets). 2. Existing `DESIGN.md` (frontmatter `colors`, `## Colors`, Named Rules; our markers
present means a re-run). 3. `.interface-design/system.md`. 4. `design-system/*/MASTER.md` and
`pages/*.md`. 5. Existing token sources: CSS custom properties, Tailwind config, `tokens.json`.
`.taste-skill/direction.json` is read only to notice a conflict, never as authority.

**Precedence (highest wins).** 1. The user's brief in chat. 2. The user's pinned palette or brand
commitments in `PRODUCT.md` or in `DESIGN.md` outside our markers. 3. A neighbour's structural
decisions: mode, layout, type, density. 4. Our colour rules and our DESIGN.md region.
5. Colours a neighbour generated on its own (`system.md`, `MASTER.md`, Taste's dealt palette, a
Theme Factory preset): replaced or refined only as §6 says. **The one override we make is a
contrast fix** (application-rules §3): lightness only, measured, always reported with before and
after, never silent, and never applied to a value the user pinned without saying so first.

## 4. Per-neighbour notes

**Impeccable.** Automatic: `impeccable context` loads `PRODUCT.md` and `DESIGN.md` once per
session, "the brief wins" makes a pinned palette binding, and `colorize` re-reads DESIGN.md and
tokens. Write our region before new-work's "Commit the world" so the roll honours it. Merge hazard:
on a new or replacement world Impeccable writes DESIGN.md at finish and its `document` step asks
refresh / overwrite / merge; tell the user in advance to choose merge, then re-run `handoff.py`
(idempotent between markers). We never write `.impeccable/design.json`; its `colorMeta` tonal ramp
can be filled from `palette.json` by the user's Impeccable run.

**Taste (`design-taste-frontend`).** No file convention; it deals its own palette unless told.
Run it with `--keep palette` (or `--keep palette,type`), map exactly one accent (`--accent` =
`--color-accent`, the rest `--field-n` or unused), and pass `--allow palette-purple` when the
palette has violet, indigo or purple (many Wada plates and kasane do). Its inspector also bans a
cream ground with terracotta or rust; a plate that is exactly that is the brand's and is kept with
`--keep palette`, noted in its report. With Taste loaded the stricter numbers win: accent < 5%,
ground ≤ 90%; surfaces separate by lightness (the Taste alias maps `--surface` to
`--color-bg-subtle`), never by lines. Our Restrained tier allows an accent up to 8% and a ground up
to 95%, so it does not satisfy Taste by itself: tighten to Taste's numbers. A Drenched page is a
Taste "field" palette.

**Design Principles, owl-listener.** A process skill (team principles, trade-offs); no colour
content, no files. Nothing to hand off; the project pointer (§5) is the only hook. If a team
principle contradicts a palette choice, the principle wins and we say which colour rule bent.

**Design Principles, libreuiux.** Teaches 60-30-10 and harmony-wheel schemes; reads no file. Our
proportion tiers supersede 60-30-10 (they are written as Named Rules), and plates are never judged
by wheel geometry: a Wada pairing's authority is the plate. Its `.libreui-config.yaml` colour enums
(blue / indigo / … ) cannot express our palette and are left untouched.

**UI/UX Pro Max.** Its own 192-palette lookup competes with ours; its persisted
`design-system/<slug>/MASTER.md` is read first on later runs. Contract: keep Pro Max's pattern and
typography output, substitute our semantic tokens via the alias block, never run `--force`, and
edit `MASTER.md` only with the user's consent, adding one marked pointer line under
`### Color Palette`: "Palette source of truth: DESIGN.md `## Colors` (acp)". Search
`design-system/*/MASTER.md` because the slug is not predictable.

**Theme Factory.** Writes nothing persistent; it shows a showcase and asks the user to pick a preset.
Contract: pre-empt the showcase ("use the palette from the shared file") and build its custom theme
in its own shape (`## Color Palette` with four bullets `**Name**: \`#hex\` - role`) from
`palette.json`: bg, text, accent, one voice. Typography bullets are theirs. Its "ensure contrast"
step is replaced by our measured report.

**interface-design (extra).** Reads `.interface-design/system.md` when present, else inspects
tokens; with `tokens.css` and its alias block present, its "colors from the palette" resolves to
ours. We do not write `system.md`; with consent, a marker-delimited `### Colors` block may be added.

## 5. The opt-in project pointer (user decision, PLAN §4.4)

Taste, both Design Principles skills and Theme Factory read no palette file, so the only mechanism
that reaches them is the project's always-loaded instructions. The skill asks **once per project**:
"May I add a short palette pointer to this project's `CLAUDE.md` and `AGENTS.md`?" On yes it
writes, between its own markers so it can be updated or removed:

```markdown
<!-- acp:begin pointer v1 -->
Colour: the project palette lives in DESIGN.md (## Colors) and design/tokens.css. Use those tokens; do not choose new colours. Palette decisions come from the artistic-color-palettes skill.
<!-- acp:end pointer -->
```

The answer is recorded in `palette.json` as `handoff.claude_md: true | false | declined | not_asked`
(`not_asked` until the user has answered; it is neither a yes nor a refusal). `--claude-md yes`
needs `--user-confirmed`, which records that the user said yes in this conversation; the script
refuses a yes without it. A stored no (`false` or `declined`) persists across re-runs, so the
question is not asked again for that project. Never written unasked; never written to the global
`~/.claude/CLAUDE.md`; a declined answer means the skill says the pointer text in chat instead.
Without the pointer, the skill must not claim automatic hand-off to those three neighbours.

## 6. Non-duplication

Before generating anything, the read order in §3 shows whether a neighbour already produced a
palette (Impeccable's DESIGN.md colours, interface-design's `system.md`, a Pro Max `MASTER.md`,
a Taste `direction.json`, a Theme Factory theme). If so, the skill offers two things and waits:
**replace** it with a palette from our data (the old values are kept in the report for comparison)
or **refine** it (keep its hues, rebuild ramps, measure, fix contrast, compose dark mode). It never
generates a second palette silently, never leaves two competing token sets in the project, and
when it refines, the provenance line says "refined from <neighbour>'s palette".

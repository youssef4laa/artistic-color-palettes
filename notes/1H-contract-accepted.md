# Hand-off contract — accepted with amendments (orchestrator, Phase 1 gate)

Base: `notes/1H-neighbour-skills.md` §7. Accepted except where amended below. 2G writes this into
`references/interop.md` + `assets/palette-handoff.template.md`; 2H implements it in `scripts/handoff.py`.

## Accepted as proposed
- **One primary shared file: `DESIGN.md` at the project root** (Google DESIGN.md format that
  Impeccable loads through `impeccable context`). We own only two marker-delimited regions:
  frontmatter `colors:` between `# acp:begin tokens` / `# acp:end tokens`, and the body of
  `## Colors` between `<!-- acp:begin colors v1 -->` / `<!-- acp:end colors -->`.
- Creation rule when DESIGN.md is absent: frontmatter `name`, `description`, `colors`, then only
  `## Colors`, with first line `<!-- acp:seed palette-only ... -->` (never Impeccable's `SEED`).
- Existing file without our markers: insert markers inside `## Colors` (or add the section in
  canonical order), show the diff and ask once. With markers: replace only between markers.
  Never touch other text, `PRODUCT.md`, `.impeccable/*`, `.taste-skill/*`, `system.md`, `MASTER.md`.
- Companions: `design/palette.json` (machine source of truth; DESIGN.md region is generated from
  it) and `design/tokens.css` (two-tier: primitives, then semantic `--color-*`; dark scope;
  alias blocks for Taste `--bg --surface --ink --muted --accent --accent-ink [--field-n]`,
  UI/UX Pro Max `--color-primary … --color-ring`, interface-design
  `--foreground --secondary --muted --faint --accent`). Paths recorded in `palette.json`.
- Read-first order 7.3 and precedence 7.4 (user chat > PRODUCT.md / user's DESIGN.md content
  outside our markers > our region > neighbour-generated colours). Colour only; we never override
  a neighbour's type, layout, spacing, motion or copy.
- Per-neighbour consumption 7.5, including the Taste note: run Taste with `--keep palette`, map
  exactly one accent, and pass `--allow palette-purple` when the palette has violet/indigo; warn
  that its inspector bans cream+terracotta grounds.
- Impeccable merge hazard: when its `document` step asks refresh/overwrite/merge, tell the user to
  choose merge, then re-run `handoff.py` (idempotent between markers).

## Amendments
1. **Hex in the body is allowed, never different.** Impeccable's own `## Colors` template writes
   entries as `**Name** (#HEX / oklch(...))` under `### Primary / ### Secondary / ### Tertiary /
   ### Neutral / ### Named Rules` (`reference/document.md:148-166`); its pitfall rule only
   forbids reasserting a *different* value from the frontmatter (`:415`). Our region therefore
   uses exactly that shape, generated from the same `palette.json` values as the frontmatter, so
   the two can never disagree. (1H proposed "no hex in prose"; amended.)
2. **Vocabulary inside the region:** state Impeccable's strategy name verbatim (Restrained,
   Committed, Full palette, Drenched) and mode (Persuade, Operate, Read, Experience) in a Named
   Rule, plus our proportion targets as Named Rules ("The … Rule.").
3. **Region contents (fixed order):** one-sentence palette character; provenance line (plate /
   kasane / painting / editorial / original composition, with licence credit); role entries
   (Primary/Secondary/Tertiary/Neutral); Named Rules (strategy+mode, proportions, contrast
   floor); light and dark token tables by key; measured contrast per text/surface pair (WCAG 2
   ratio + APCA Lc); adjustments made and why; "do not change without re-validating" note;
   pointers to `design/tokens.css` and `design/palette.json`; a short "Neighbour map" (Taste
   roles, Pro Max roles, Theme Factory bullets).
4. **YAML-comment markers must be tested:** `handoff.py` tests assert the frontmatter still parses
   as a flat `key: value` map with our comment lines (stdlib mini-parser), and that a re-run is
   byte-identical.
5. **Neighbours with no file convention (Taste, Design Principles, Theme Factory):** decided by
   the user (PLAN §4.4) — see `gate-1.md`. Until then SKILL.md must not claim automatic hand-off
   to those three.

# 1H — Neighbour skills: what they read, write and say about colour

Agent 1H. All citations are `file:line` inside the pinned clones in `notes/neighbour-skills/<dir>/`
(created by `notes/fetch-reference-skills.sh`; the second target dir is the optional 2nd argument) or in
`notes/reference-skills/<dir>/` for the secondary two. Frontmatter `description` strings are verbatim.
Everything else is paraphrased. Clone folder names: `impeccable`, `taste-skill`,
`design-principles-owl`, `design-principles-libreuiux`, `interface-design`.

## 0. Which repos were chosen, and why

Discovery used `npx skills find <query>` (skills.sh index, install counts as printed on 2026-10-22)
and `git ls-remote` for SHAs.

| Role | Chosen | Installs | Runners-up and why not |
|---|---|---|---|
| **Taste** | `Leonxlnx/taste-skill`, skill dir `skills/taste-skill`, installed name `design-taste-frontend` | 657K (`leonxlnx/taste-skill@design-taste-frontend`) | `uizze.sh@ui-taste` (722.6K) is not a GitHub repo I could resolve (`uizze.sh` is a host label, not an owner/repo), so cannot be pinned to a SHA. Other `leonxlnx/taste-skill@*` entries (high-end-visual-design 458.8K, minimalist-ui, industrial-brutalist-ui ...) are variants in the same repo; the v2 repo has a single `skills/taste-skill`. `cristicretu/family-taste-skill@design-with-taste` (755) and `dragoon0x/taste-skills@*` are tiny. |
| **Design Principles** | `owl-listener/designer-skills`, skill `design-principles` at `ux-strategy/skills/design-principles/SKILL.md` | 2.1K (most-installed skill literally named `design-principles`) | `ormus-solutions/libreuiux-claude-code@design-principles` (110) is the one that actually teaches visual/colour principles (60-30-10, dark-mode table), so I fetched it too as a content-bearing runner-up. `hermeticormus/design-mastery-claude-code@design-principles` (5), `smithery.ai@design-principles` (3), `wshobson/agents@api-design-principles` (30.3K, backend API, irrelevant). |
| extra, not requested | `dammyjay93/interface-design` | 30.3K | It is the only neighbour besides Impeccable that has a persisted-decisions file (`.interface-design/system.md`), so it matters for the contract. Fetched and read. |

Caveat to relay: "Design Principles skill" is ambiguous. The most-installed namesake (owl) is a team
workshop skill with no colour content and no files; the namesake with colour content (libreuiux) has
110 installs. Neither has a shared-file convention. Decide with the user whether either is the intended one.

| Clone | Repo | Pinned SHA | Licence |
|---|---|---|---|
| impeccable | `pbakaus/impeccable` | `e3083ac3301e4d10517dd6cb58ab645bc2cb6e1b` | Apache 2.0 (`SKILL.md:7` `license: Apache 2.0`; `impeccable/LICENSE`, `NOTICE.md`) |
| taste-skill | `Leonxlnx/taste-skill` | `6010f91a9935f1c167dfc500fb1a475681892e6b` | MIT, (c) 2026 Leonxlnx (`taste-skill/LICENSE:1-3`) |
| design-principles-owl | `owl-listener/designer-skills` | `9a6930cf84a822eb458624bd11c61aac5bbdf224` | MIT, (c) 2026 MC Dean (`LICENSE:1-3`) |
| design-principles-libreuiux | `ormus-solutions/libreuiux-claude-code` | `41a968c41cb9328335444ded8d0436362d0ba50a` | MIT, (c) 2025-2026 Hermetic Ormus (`LICENSE`, plus `NOTICE.md`) |
| interface-design | `dammyjay93/interface-design` | `2f9be3206855bcb2d1d0af262c8bae25cba6658d` | MIT, (c) 2026 Damola Akinleye |
| ui-ux-pro-max | `nextlevelbuilder/ui-ux-pro-max-skill` | `623a9a9037d006ea727f8213f084d02a6b6f11b5` | MIT, (c) 2024 Next Level Builder |
| theme-factory | `anthropics/skills` | `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | Apache 2.0 text in `LICENSE.txt` (`SKILL.md:4` "Complete terms in LICENSE.txt") |

Note: the Impeccable clone is the whole `/.claude/skills/impeccable/` folder (SKILL.md, `reference/`, `scripts/`).
Its `scripts/impeccable` launcher "runs a self-contained binary that ships next to it or is downloaded once
on first run" (`SKILL.md:19`), so the exact PRODUCT.md/DESIGN.md discovery code is **not in the repo**.
Only the documented behaviour below is verifiable; treat any claim about how `impeccable context` resolves
paths beyond that as unverified.

---

## 1. Impeccable (primary)

**name:** `impeccable` (`.claude/skills/impeccable/SKILL.md:2`), version 4.7.0 (`:4`).

**description (verbatim, `SKILL.md:3`):**
"Use when the user wants to design, redesign, shape, critique, audit, polish, simplify, harden, animate, or otherwise improve a frontend interface: websites, landing pages, dashboards, product UI, components, forms, settings, onboarding, empty states, and native iOS or Android screens. Handles UX review, hierarchy, layout, typography, color, motion, UX copy, accessibility, responsive behavior, edge cases, and capturing or documenting design systems (DESIGN.md, tokens). Also for making bland UI bolder, loud UI quieter, or ambitious visual effects. Not for backend-only or non-UI tasks."

### Files it reads (project root unless noted)

| Path | Where stated | When |
|---|---|---|
| `PRODUCT.md` | `SKILL.md:19`; `reference/init.md:100` ("New files go at `PROJECT_ROOT/PRODUCT.md`") | Setup step 1: `scripts/impeccable context`, once per session; loads PRODUCT.md, DESIGN.md, surface brief, native guidance |
| `DESIGN.md` | `SKILL.md:19`, `:23` (fallback: "read existing PRODUCT.md and DESIGN.md directly") | Same step; again by `polish` (`reference/polish.md:9`), `colorize` ("Read DESIGN.md, tokens...", `reference/colorize.md:14`) |
| `.impeccable/design.json` (sidecar) | `reference/document.md:253` | Live panel and tooling |
| `.impeccable/config.json`, `.impeccable/config.local.json` | `reference/init.md:114-116`, `reference/doctor.md:49` | Workflow defaults (`buildPath: comp\|code`, `stalenessCheck`) |
| Surface briefs via `impeccable surface-brief read <target>` | `reference/new-work.md:81-85` | New-work; stored by the binary, location not in repo |
| Project CSS custom properties, `tailwind.config.*`, theme files, `tokens.json`/`design-tokens.json` | `reference/document.md:84-92` (scan order) | `document` scan mode |

### Files it writes

* `PRODUCT.md` (init). Template at `reference/init.md:60-98`; first lines `# Product` then `<!-- impeccable:product-schema 1 -->` (`:63`). Sections: Platform, Stack, Users, Product Purpose, Positioning, Operating Context, Capabilities and Constraints, Brand Commitments, Evidence on Hand, Product Principles, Accessibility & Inclusion. It explicitly excludes palettes: "visual worlds, palettes, typography, components" do not belong (`init.md:51`) and init must not ask about colours (`:41`).
* `DESIGN.md` (document / new-work finish). Format is the external Google "DESIGN.md" spec (`document.md:3`): optional YAML frontmatter (`name`, `description`, `colors`, `typography`, `rounded`, `spacing`, `components`; `document.md:9-41`; no other top-level groups, `:416`) then up to eight sections in fixed order: `## Overview`, `## Colors`, `## Typography`, `## Layout`, `## Elevation & Depth`, `## Shapes`, `## Components`, `## Do's and Don'ts` (`:53-60`).
  * Colour section shape (`:148-166`): one sentence of palette character; `### Primary`, optional `### Secondary`, optional `### Tertiary`, `### Neutral`, optional `### Named Rules` ("The ... Rule." lines, example "primary accent is used on <=10% of any given screen", `:166`). Entries are `**Descriptive Name** (#HEX / oklch(...))`.
  * Frontmatter colour tokens: slug keys like `oxblood-deep`, "Colors accept any valid CSS color string... preserve an incumbent `rgb()`, `hsl()`, `oklch()`" (`:46`); the frontmatter is normative and prose must not restate a different value (`:394`, `:415`). Section headers must not be renamed (`:414`).
  * Seed form: first line `<!-- SEED: established with the user before implementation; re-run /impeccable document once there's code to capture the actual tokens and components. -->` (`:369`), frontmatter `name`+`description` only, colours as "[to be resolved during implementation]" (`:375`, `:383`).
  * Never overwritten silently: existing DESIGN.md triggers an ask: refresh, overwrite or merge (`:71`, `:411`).
  * On a new or replacement world DESIGN.md is written **at finish**, by the documenter, not before the build (`reference/new-work.md:77`).
* `.impeccable/design.json` sidecar, `schemaVersion: 2` (`document.md:259-301`): `extensions.colorMeta.<token>` with `role`, `displayName`, `canonical` (OKLCH) and an 8-step `tonalRamp` "dark to light, same hue and chroma, lightness ~15% to ~95%" (`:326-328`; use existing scale if present, else synthesise in OKLCH); plus `shadows`, `motion`, `breakpoints`, `components`, `narrative`.
* Others: `.impeccable/config.json`, `.impeccable/mocks/`, `.impeccable/build/`, `.impeccable/review/`, `.impeccable/live/`, `.impeccable/critique/` (grep of `reference/*.md`).

### Colour vocabulary and rules

* **Colour strategies (exact names, `reference/new-work.md:65`):** Restrained (tinted neutrals + one accent), Committed (one saturated colour carries 30-60% of the surface), Full palette (3-4 named roles), Drenched (the surface is the colour). Persuade/Experience surfaces may take the bolder ones.
* **Modes (`SKILL.md:36-39`):** Persuade, Operate, Read, Experience. Mode is chosen from the requested surface and stored only in the surface brief (`:41`).
* **Who picks the palette:** the model, via new-work "Commit the world" (`new-work.md:63-65`), after a roll (`concept-seed`) deals directions (`:48`). BUT "The brief wins. Honor pinned aesthetics, eras, materials, fonts, and palettes" (`SKILL.md:27`) and brand commitments recorded in PRODUCT.md are binding. This is our hook: a palette pinned in DESIGN.md/brief is honoured.
* `colorize.md`: build roles not swatches (canvas, elevated surfaces, text tiers, action/focus/selection, borders, success/warning/error/info, data) (`:29-36`); "prefer OKLCH" for a new web palette (`:38`); vary lightness and reduce chroma near white/black when deriving OKLCH ramps (`:65`); tint neutrals only if the brand hue gives cohesion (`:44`); dark mode "do not invert the light theme mechanically" (`:48`, `:72`); semantic tokens remap per theme (`:49`); contrast table AA 4.5 / 3 / 3 (`:57-61`); simulate colour-vision deficiency (`:63`).
* `craft-floor.md:9`: contrast >=4.5:1 body, >=3:1 large; tint secondary text from the surface hue, never grey. Bans listed there include gradient text (`:33`), colored border-left >1px (`:35`), and "Light or dark picked by category" (`:42`). `new-work.md:65`: pick dark/light from a one-sentence physical scene. `new-work.md:69-71` treats cream + serif + terracotta as a spent default.

### Overlaps / contradictions with our skill

* Dark mode: agrees (composed, not inverted). Ramps: agrees (chroma tapers near ends). OKLCH: agrees.
* Accents: Impeccable allows up to 3-4 roles (Full palette) or a single colour owning 30-60% (Committed); its own DESIGN.md example says accent <=10%. Our proportion rules must be expressed as a Named Rule in `## Colors` so they are read as the world's invariant rather than a competing percentage.
* Who picks: Impeccable's roll will otherwise pick its own palette on a new surface; ours must land **before** new-work's colour decision (as a pinned palette in DESIGN.md or the brief). Conflict window: for a new world, Impeccable writes DESIGN.md only at finish (`new-work.md:77`), so an earlier palette-only DESIGN.md will meet `document.md:71` (ask: refresh/overwrite/merge) at finish. Tell the user in advance and write markers so a merge keeps our block.
* Contrast: Impeccable is WCAG 2 only; ours adds APCA. No clash; ours is stricter.

---

## 2. Taste (primary)

**Repo layout:** `skills/taste-skill/` (SKILL.md, `references/`, `library/`, `scripts/*.mjs`, `assets/`); `.claude-plugin/marketplace.json` declares `skills: ["./skills/taste-skill"]` (v2.1.4).

**name (`SKILL.md:2`):** `design-taste-frontend`

**description (verbatim, `SKILL.md:3-13`):**
"tasteskill v2, the anti-slop frontend skill. Art direction for websites, distilled from a study of 247 curated gallery sites (One Page Love, Awwwards Sites of the Day). Deals researched directions (idea, composition, type, palette, photographs, section blueprints) from a library, enforces a strict no-slop house style with a real-browser inspector, and runs a look-and-fix loop on screenshots. Use this whenever you build, design, redesign, restyle, polish or review a landing page, marketing site, portfolio, product page, one-pager, hero or any public-facing web page, in any stack (HTML/CSS, React, Next.js, Vue, Svelte, Astro, Tailwind) — also when the user says a page looks generic, templated, "AI-made", sloppy, or asks to make it look designed, premium, award-level or less like every other site. Also for app screens: dashboards, admin and analytics views, settings, inboxes and other screens people work in, with their own run and rules."

### Files it reads and writes

* **Reads:** the project itself. Step 1 says to find "any existing brand (colours, fonts, logo)" (`SKILL.md:79`). It does **not** name any file (no DESIGN.md, no tokens file). The only brand hand-off is a CLI flag, `--keep palette,type`: "the brand already fixes colours or typefaces. The draw then deals only the composition, and you map the brand's values onto the roles" (`SKILL.md:136-138`, `scripts/draw.mjs:11`, `:252-253` sets `palette` to null when kept). Existing brand/system: "Pass `--keep palette,type`, map the brand's colours and faces onto the roles" (`SKILL.md:465-466`).
* **Writes** (run from project root, `SKILL.md:40-41`): `.taste-skill/direction.json` (the "direction sheet", `scripts/draw.mjs:37-38`, `:207`), `.taste-skill/inspect/` screenshots (`SKILL.md:320`), `.taste-skill/before`, `.taste-skill/after` (`:473`, `:489`), `.taste-skill/app` (`:62`), `assets/` for downloaded pictures (`:276` area). A user-level history file is also written (`draw.mjs:113`).
* **Palette shape** in its own library (`library/palettes.json`, 56 entries): `id`, `name`, `tags`, `bg`, `surface`, `ink`, `muted`, `accent`, `accentInk`, `fields[{bg,ink}]`, `note`, `seenIn`.
* **Token names it expects the build to use (`references/colour.md:36-46`):** `--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--accent-ink`, optional `--field-1 ... --field-n` and field inks. "A raw hex in a component is a second palette starting" (`:48`).

### Colour rules and vocabulary

* Roles: ground, ink, accent, fields (`SKILL.md:150-151`, `colour.md:34-50`).
* **One ground, one ink, one accent** (`SKILL.md:439`); accent "under 5% of any screen" (`colour.md:58`); ground 70-90% (`:56`); accent not for headings/icons/borders (`:64`).
* Surfaces separated by tone steps of 2-6 lightness points, never lines or shadows (`colour.md:67-75`).
* Contrast: body 4.5:1, display 3:1, "the dealt palettes meet 7:1 for ink on ground"; inspector fails text under 2.6:1 (`colour.md:119-122`).
* Dark pages: `color-scheme: dark`; ground is a deep tone with slight palette tint; ink a soft light, not `#fff` on `#000`; depth from a lighter surface step, no glows (`colour.md:97-104`).
* Bans enforced by `inspect.mjs`/`lint.mjs`: gradients ("No gradients", `SKILL.md:389`), "No assistant palette. No yellow-cream ground with terracotta or rust; no violet or indigo." (`SKILL.md:391`; `colour.md:128-133`). Override: `--keep palette` and `--allow palette-purple` (`colour.md:139-141`, `SKILL.md:467-468`).
* Warmth guidance: low-chroma stone/bone/putty ground (saturation under ~15%) rather than beige (`colour.md:135-137`).
* **Who picks:** the script deals a palette at random (`draw.mjs:253`); the model may redraw once if it fights the subject (`SKILL.md:150-155`).

### Overlaps / contradictions

* **Hard conflict:** Wada plates and Heian kasane routinely include cream/ivory grounds with rust or terracotta-like reds and violet/indigo/purple tones. Taste's inspector will FAIL them unless `--keep palette` + `--allow palette-purple` are used. Our hand-off must say so and give the exact flags.
* One accent (<5%) vs our multi-colour proportion rules (e.g. 3-5 colour Wada combinations, 60-30-10 style). Hand-off should map: Taste `--accent` = our single action colour, extra hues become `--field-n` or stay unused for a Taste page. Say it in the palette file.
* No gradients, no lines/shadows vs our ramps: fine (ramps are flat steps).
* Dark mode: Taste = tinted deep ground + soft ink + lighter surface step: compatible with "composed, never inverted".
* Chroma: Taste gives only the "<15% saturation" warmth hint; no OKLCH. No clash.

---

## 3. Design Principles (primary; two candidates)

### 3a. owl-listener `design-principles`

**name (`ux-strategy/skills/design-principles/SKILL.md:2`):** `design-principles`
**description (verbatim, `:3`):** "Define actionable principles that resolve trade-offs when the team disagrees. Use when the same decisions keep getting relitigated. For a single project's framing, use `design-brief`."
* Content: a 29-line process skill for writing team design principles (title, statement, rationale, application example, counter-example, trade-off; `:16-17`). No colour content at all, no tokens, no files read or written (the skill body names none).
* Overlap: none. It would only be relevant if the user's principles contradict a palette ("Opinionated... Prioritized", `:10-15`). It has no convention to hook into, so it relies on the main-context pointer (section 8).

### 3b. libreuiux `design-principles` (runner-up with colour content)

**name (`plugins/design-mastery/skills/design-principles/SKILL.md:2`):** `design-principles`
**description (verbatim, `:3`):** "Core visual design principles (visual hierarchy, Gestalt grouping, composition, balance, contrast, white space, color, typography) with UI fixes, a checklist, and deep-dive references. Use when making or defending a layout, type, or color decision, or when a design feels off and you need to name why."
* Files in skill: `references/color-theory.md`, `references/{composition-rules,gestalt-principles,typography-fundamentals,visual-hierarchy}.md`, `assets/principles-checklist.md` (`SKILL.md:276-281`). Reads/writes no project file.
* Repo-level config: `.libreui-config.yaml` ("Claude Code reads this file to personalize UI generation", `.libreui-config.yaml:7`) has `design_system.colors.mode: light|dark|auto`, `primary: blue|indigo|violet|emerald|amber|rose`, `neutral: gray|slate|zinc|neutral|stone` (`:43-46`) and `accessibility.color_contrast` 4.5:1. This belongs to the LibreUIUX plugin, not to the `design-principles` skill, and its enums cannot express a Wada palette.
* Colour rules (`references/color-theory.md`): 60-30-10 (dominant / secondary / accent) (`:81-88`); harmony types complementary/analogous/triadic/split-complementary (`:44-72`); dark mode "Don't just invert—adjust" with blue-600 to blue-400 and off-black grounds (`:238-248`); tints in Tailwind-style 50-950 scales (`:164-185`); contrast 4.5/3 (`:134-142`).
* Overlap/contradiction: 60-30-10 is compatible with our proportion tiers if we state that ours supersede; harmony-wheel vocabulary conflicts with plate-based selection (we choose from plates, not by wheel geometry); its "blue primary" defaults would override our palette unless the palette is declared first.

### 3c. Extra: `dammyjay93/interface-design`

**name:** `interface-design` (`.claude/skills/interface-design/SKILL.md:2`)
**description (verbatim, `:3`):** "Craft-first interface design for dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces, and interactive products. Use when designing, building, reviewing, auditing, or refining product UI where visual craft, layout hierarchy, tokens, states, visual direction, or design-system consistency matter. Not for marketing pages, landing pages, campaigns, or brand-only work."
* **Reads:** `.interface-design/system.md` "if present" (`SKILL.md:267`, `:288`: "read it and apply - decisions are made"); also inspects "existing app, design tokens, component patterns" (`:267`). The `/design-review` and `/design-deslop` commands read it too (`.claude/commands/design-review.md:29`, `design-deslop.md:52`).
* **Writes:** `.interface-design/system.md`, only after offering ("Want me to save these patterns...?", `SKILL.md:303`). Template `reference/system-template.md`: sections `# Design System` > `## Direction` (Personality, Foundation: warm|cool|neutral|tinted, Depth), `## Tokens` (`### Spacing`, `### Colors` = `--foreground`, `--secondary`, `--muted`, `--faint`, `--accent`, `### Radius`, `### Typography`), `## Patterns`, `## Decisions` (`system-template.md:3-56`). Consistency rule: "colors from the palette" (`SKILL.md:311`).
* Colour rules: ~60/30/10 (`SKILL.md:123`), one accent (`:124`, `:252`), dark mode "Desaturate semantic colors slightly... Keep one hue; shift only lightness across surfaces" and "inverted values" (`:204`), "Color world: 5+ colors that exist in this domain" (`:64`).
* Overlap: one accent vs our palettes; "Same hierarchy system, inverted values" (`:204`) is closer to inversion than our rule.

---

## 4. UI/UX Pro Max (secondary; `notes/reference-skills/ui-ux-pro-max/`)

**name / description (verbatim, `.claude/skills/ui-ux-pro-max/SKILL.md:2-3`):** `ui-ux-pro-max`; "UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces, including pages, components, design systems, accessibility, interaction, responsive layout, typography, color, charts, and stack-specific UI implementation. Searchable local data: 79 searchable styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, and 22 stacks."
**Licence:** MIT.

* **Writes** (with `--persist -p "Project" --output-dir "<project-root>"`, `SKILL.md:90-98`): `design-system/<project-slug>/MASTER.md` ("Global Source of Truth") and `design-system/<project-slug>/pages/` (+ `pages/<page>.md` with `--page`). Slug via `safe_slug` (`scripts/design_system.py:986-994`, path built at `:1045-1046`). Existing MASTER.md is left untouched unless `--force` (`SKILL.md:102-104`).
* **Reads:** on later builds it reads `design-system/<slug>/MASTER.md`, then `pages/<page>.md` which overrides Master (`SKILL.md:107-109`). Quirk: the generated MASTER.md header says `design-system/pages/[page-name].md` (no slug) (`design_system.py:1121`), inconsistent with SKILL.md.
* **MASTER.md shape** (`format_master_md`, `design_system.py:1101-1390`): `# Design System Master File`, blockquote LOGIC, `**Project:**`, `**Generated:**`, `**Category:**`, `**Design Dials:**`; `## Global Rules` > `### Color Palette` (table `| Role | Hex | CSS Variable |`, `:1148-1155`), `### Typography`, `### Spacing Variables`, `### Shadow Depths`; `## Component Specs` (Buttons, Cards, Inputs, Modals); `## Style Guidelines`; `## Anti-Patterns`; `## Pre-Delivery Checklist`. Page files have `### Color Overrides` (`:1467`).
* **Token roles** (`design_system.py:49-64`): `--color-primary`, `--color-on-primary`, `--color-secondary`, `--color-on-secondary`, `--color-accent` (labelled Accent/CTA), `--color-on-accent`, `--color-background`, `--color-foreground`, `--color-card`, `--color-card-foreground`, `--color-muted`, `--color-muted-foreground`, `--color-border`, `--color-destructive`, `--color-on-destructive`, `--color-ring`. Hex only.
* Colour rules: dark mode "desaturated / lighter tonal variants, not inverted colors; test contrast separately" (`references/quick-reference.md:124`); light/dark contrast >=4.5:1 for normal text, parity of states (`references/pro-rules.md:43-45`); contrast table (`quick-reference.md:9`, data `:242`).
* Overlap: **who picks the palette** is Pro Max's own CSV palette lookup (192 product palettes). That is a direct competitor to our selection, but its output is hex-only and low-structure. Ours should win when present. It has no marker comments, so regenerating with `--force` would erase anything we put inside MASTER.md.

## 5. Theme Factory (secondary; `notes/reference-skills/theme-factory/skills/theme-factory/`)

**name / description (verbatim, `SKILL.md:2-3`):** `theme-factory`; "Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly."
* Reads: its own `theme-showcase.pdf` (shown first, `SKILL.md:23`) and `themes/<theme>.md` (`:53`). Ten files: arctic-frost, botanical-garden, desert-rose, forest-canopy, golden-hour, midnight-galaxy, modern-minimalist, ocean-depths, sunset-boulevard, tech-innovation.
* Writes: nothing persistent. Applies colours to the artifact being made. Theme file shape (e.g. `themes/ocean-depths.md`): `# Name`, one-line blurb, `## Color Palette` with 4 bullets `**Name**: \`#hex\` - role`, `## Typography`, `## Best Used For`.
* Custom themes are generated "on-the-fly" in that same shape (`SKILL.md:58`), so it has a natural plug-in point: ours can supply the colour bullets. No project-file convention; it asks the user to choose from the showcase (`:23-25`), which is an interaction we must pre-empt (say "use the palette from the shared file").

---

## 6. Summary matrix (does a neighbour auto-read a shared file?)

| Neighbour | Auto-reads a project file before colour work? | Which | Writes a persistent file |
|---|---|---|---|
| Impeccable | **Yes** | `PRODUCT.md`, `DESIGN.md` (via `impeccable context`, `SKILL.md:19`) | `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json` |
| interface-design | Yes | `.interface-design/system.md` | same |
| UI/UX Pro Max | Yes (only if the user previously persisted) | `design-system/<slug>/MASTER.md`, `pages/*.md` | same |
| Taste | **No** (reads "existing brand" from the codebase, `SKILL.md:79`; `--keep palette,type` flag) | none by name | `.taste-skill/direction.json` etc. |
| Design Principles (owl / libreuiux) | **No** | none | none |
| Theme Factory | No | `themes/*.md` of its own | none |

Implication: only Impeccable (and conditionally two others) will honour a file "without being told".
For Taste, both Design Principles variants and Theme Factory a pointer in always-loaded context is the
only mechanism, and that is the open choice below.

---

## 7. Proposed hand-off contract

### 7.1 The ONE primary shared file: `DESIGN.md` at the project root

Reason: it is the only file a neighbour is documented to load automatically that is also a published,
multi-tool format (the Google DESIGN.md spec, `impeccable/.../document.md:3`), and its `## Colors`
section is exactly where palette lives. Everything else is derived from it or points at it.

**We own, and only ever rewrite, two marker-delimited regions:**

1. In the YAML frontmatter, inside `colors:` (YAML comments are legal; Impeccable's token schema is untouched):
   ```yaml
   colors:
     # acp:begin tokens (artistic-color-palettes; do not edit between markers)
     <slug>: "oklch(...)"      # one entry per role, slug = descriptive name
     # acp:end tokens
   ```
2. In the body, under the canonical `## Colors` heading (never renamed, `document.md:414`):
   ```markdown
   ## Colors
   <!-- acp:begin colors v1 -->
   ...palette source line (e.g. "Sanzo Wada plate N" / "kasane <name>" / painting id, or "none matched"), role table by token key (no hex, per document.md:415), proportion Named Rules ("The ... Rule."), dark-mode composition note, contrast measurements (WCAG 2 + APCA), pointers to tokens.css and palette.json ...
   <!-- acp:end colors -->
   ```
Rules for writing: (a) if DESIGN.md is missing, create it with frontmatter `name`, `description`, `colors` and a `## Colors` section only, plus our own first-line comment `<!-- acp:seed palette-only; Impeccable's document command will fill the other sections -->` (do not forge Impeccable's own `SEED` marker); (b) if present, show the diff of our region and replace only between markers, never touching other text; if markers are absent, insert them inside the existing `## Colors` (or append the section in canonical order) and ask once, because `document.md:71` forbids silent overwrites; (c) never write hex in prose when the frontmatter holds it (`document.md:415`); (d) never write `PRODUCT.md`, `.impeccable/*`, or other neighbours' files; (e) bump `v1` on schema change.

Impeccable's `document` refresh/overwrite/merge at finish (`new-work.md:77`, `document.md:71`) can drop our block; tell the user "choose merge" and re-run us afterwards (we are idempotent between markers).

### 7.2 Companion files (derived, always regenerated by our script from one source of truth)

* `design/palette.json`: machine source of truth (palette id and provenance, roles, OKLCH L/C/H, hex fallback, ramps, light and dark composed sets, measured contrast, proportions). DESIGN.md region is generated from it. (Impeccable's sidecar `colorMeta.canonical/tonalRamp` could be filled from it by the user's Impeccable run; we do not write `.impeccable/design.json`.)
* `design/tokens.css`: two-tier tokens (primitives then semantics) on `:root` and a dark scope, with **alias blocks** so neighbours' names resolve to ours without a second palette:
  * Taste roles `--bg --surface --ink --muted --accent --accent-ink` (+ `--field-n`) (`colour.md:36-46`);
  * Pro Max `--color-primary ... --color-ring` (`design_system.py:49-64`);
  * interface-design `--foreground --secondary --muted --faint --accent` (`system-template.md:17-24`).
  Impeccable's `document` finds tokens by grepping `--color-*` in CSS (`document.md:86`), so the semantic tier should also use `--color-*` names. Location: `design/tokens.css` by default, or the project's existing styles dir if the user prefers; record the chosen path in `palette.json`.
All three files carry a header comment with the same `acp:` version marker; a CSS/JSON file is wholly ours, so no sub-markers are needed there.

### 7.3 Read-first order (files of the neighbours we consult before choosing)

1. `PRODUCT.md` (audience, brand commitments, accessibility; `init.md:60-98`): brand colours or accessibility standard here are binding constraints on selection.
2. Existing `DESIGN.md` (frontmatter `colors`, `## Colors`, Named Rules): if a colour is a "confirmed brand commitment" (`colorize.md:16`) we keep it and only ask; our markers present means we are re-running.
3. `.interface-design/system.md` (Foundation, Colors tokens).
4. `design-system/<slug>/MASTER.md` and `pages/*.md` (Color Palette table).
5. Existing token sources (`document.md:84-92` order): CSS custom properties, Tailwind config, `tokens.json`.
Never read `.taste-skill/direction.json` as authority; it is generated and replaceable. We may read it to see whether Taste already dealt a palette that conflicts, and then say so.

### 7.4 Precedence (highest wins)

1. Explicit user instruction in the current chat.
2. User brand commitments in `PRODUCT.md` / existing `DESIGN.md` outside our markers.
3. **Our marker region in DESIGN.md** (+ `palette.json`, `tokens.css`).
4. Neighbour-generated colours: `system.md`, `MASTER.md`/`pages/*.md`, Taste `direction.json`, Theme Factory themes, libreuiux config.
We own colour only: a neighbour's typography, layout, spacing, motion and copy rules are never overridden.

### 7.5 Per neighbour: how it consumes the palette without being told

* **Impeccable:** automatic. `impeccable context` loads PRODUCT.md and DESIGN.md at Setup step 1 (`SKILL.md:19`), "The brief wins... palettes" (`:27`) makes our block binding; new-work's colour-strategy step then reads a pinned palette. To guide its strategy choice, our Named Rules state one of its exact names (Restrained, Committed, Full palette, Drenched; `new-work.md:65`). `colorize` re-reads DESIGN.md and tokens (`colorize.md:14`).
* **interface-design:** reads `.interface-design/system.md` if present (`SKILL.md:267,288`), otherwise inspects tokens (`:267`). With `tokens.css` and its alias block present, "colors from the palette" (`:311`) resolves to ours. We do not write `system.md` (it is theirs; they write it after the task). Optional with user consent: a marker-delimited `### Colors` block inside `system.md`.
* **UI/UX Pro Max:** if the user had persisted a MASTER.md it is read first (`SKILL.md:107`) and its own palette would compete. Contract: when our region exists and the run uses `--design-system`, the agent keeps Pro Max's pattern/typography output but substitutes our semantic tokens via the alias block; we never use `--force` and never edit MASTER.md without consent. If consent is given, add a marked pointer line under its `### Color Palette`: "Palette source of truth: DESIGN.md `## Colors` (acp)".
* **Taste:** no file mechanism. Consumption path: (1) its Step 1 "existing brand (colours...)" scan will find `tokens.css`/DESIGN.md only if it looks; (2) the run is `--keep palette,type` (`SKILL.md:136`, `:465`), and the agent maps our roles onto Taste's six roles; we supply the mapping in the DESIGN.md region ("Taste map: --bg, --surface, --ink, --muted, --accent, --accent-ink") and warn that the inspector bans violet/indigo and cream+terracotta (`colour.md:128-141`), so pass `--allow palette-purple` (or the relevant rule) when the chosen palette needs it. Single accent <5% (`colour.md:58`): the map names exactly one accent.
* **Design Principles (owl and libreuiux):** no consumption mechanism. They give general advice and no tokens; conflicts are only 60-30-10 wording (`color-theory.md:81`) and wheel harmonies. Flag for the pointer line below.
* **Theme Factory:** produces its own theme file shape. Contract: when generating a "custom theme" (`SKILL.md:58`), take the colour bullets from `palette.json` (name, hex, role) instead of the preset list; otherwise no hook.

### 7.6 OPEN CHOICE: neighbours with no shared-file convention (flagged for the plan)

Taste, both Design Principles skills, Theme Factory and (unless persisted) Pro Max read **no** palette
file by default. `DESIGN.md` is only auto-loaded by Impeccable. The one mechanism that reaches every
skill is Claude Code's always-loaded memory file. Decision needed in PLAN.md: **offer to add an opt-in
pointer to the user's `CLAUDE.md` (and `AGENTS.md` for other agents)**, never write it unasked. Proposed
text, between its own markers so we can update or remove it:

```markdown
<!-- acp:begin pointer v1 -->
Colour: the project palette lives in DESIGN.md (## Colors) and design/tokens.css. Use those tokens; do not choose new colours. Palette decisions come from the artistic-color-palettes skill.
<!-- acp:end pointer -->
```
Options: (A) opt-in pointer, ask once per project, record the answer in `palette.json` `handoff.claude_md: true|false|declined` (recommended: it is the only way Taste/Design Principles/Theme Factory see the palette "without being told", and it is project-scoped and reversible); (B) no write, say it in chat each time (zero risk, no automatic hand-off); (C) global `~/.claude/CLAUDE.md` (rejected: modifies persistent config outside the project, overreaches). Without (A), the claim "hands the palette to Taste, Design Principles, Theme Factory automatically" in the brief (`00-brief.md:11-13`) is false for those three; SKILL.md must not make it.

### 7.7 Unverified / caveats

* `impeccable context` internals (path resolution, monorepo inheritance, how it parses DESIGN.md) are in a downloaded binary, not in the pinned repo. The marker-in-YAML-comment trick is plausible (YAML comments are legal; Impeccable's doctor validates schema, `doctor.md:1`) but untested against `impeccable doctor` and Stitch's linter.
* Install counts come from the skills.sh CLI output on 2026-10-22 and change daily.
* Pro Max slug folder naming depends on the project name argument, so `MASTER.md` location is not predictable by us; search `design-system/*/MASTER.md`.

# artistic-color-palettes

An Agent Skill that gives coding agents real artistic colour palettes in place of their usual
defaults, then makes those palettes work in a real interface. It searches Sanzo Wada's
*A Dictionary of Color Combinations* (plates 1–348), Heian *kasane no irome* layered colour
patterns, palettes sampled from public-domain paintings and editorial palettes from
colorcombinations.org. You can ask in everyday colour words ("ocean", "pastel pink", "coffee",
"dark and muted") or start from a brand colour, and it finds palettes that hold a close match. It
shows 3–5 candidates as applied mini-layouts (light, dark, greyscale) and lets you choose one. It then builds OKLCH ramps, two-tier design tokens, colour proportions,
measured WCAG 2 and APCA contrast and a composed (not inverted) dark mode, using the perceptual
principles of Josef Albers' *Interaction of Color*. The result goes into `DESIGN.md`,
`design/palette.json` and `design/tokens.css`, where neighbouring design skills can read it. It
never invents a plate, painting or pattern, and every palette carries its provenance. The bundled
scripts are Python 3.10+ standard library only and need no network.

## Install

Both channels were tested locally on 2026-10-23 (Claude Code 2.1.296; `skills` CLI via npx).

**Claude Code plugin marketplace**

```bash
# from GitHub (after the repo is public)
claude plugin marketplace add youssef4laa/artistic-color-palettes
claude plugin install artistic-color-palettes@artistic-color-palettes

# from a local clone (this is the form that was tested)
claude plugin marketplace add D:/path/to/artistic-color-palettes
claude plugin install artistic-color-palettes@artistic-color-palettes
```

Inside a session the same steps are `/plugin marketplace add youssef4laa/artistic-color-palettes`
and `/plugin install artistic-color-palettes@artistic-color-palettes`.

**skills.sh**

```bash
# from GitHub (after the repo is public)
npx skills add youssef4laa/artistic-color-palettes --skill artistic-color-palettes

# from a local clone, into the current project (tested)
npx skills add D:/path/to/artistic-color-palettes --skill artistic-color-palettes
```

Add `-g` for a user-level install. Then ask for a palette, a theme, brand colours, a dark mode,
design tokens, or "make this look less generic". The skill lives in
`skills/artistic-color-palettes/`; start with its `SKILL.md`.

## Works with

The skill handles colour only. Typography, layout, motion, components and copy are left to the
skills below.

| Skill | What is shared | How |
|---|---|---|
| [Impeccable](https://github.com/pbakaus/impeccable) | `PRODUCT.md` is read; the palette, strategy and mode (Impeccable's own names) go into two marker regions of `DESIGN.md` | Automatic: Impeccable loads `DESIGN.md` through `impeccable context`. When its document step asks, choose *merge* and re-run the hand-off |
| [Taste](https://github.com/Leonxlnx/taste-skill) | Alias tokens `--bg --surface --ink --muted --accent --accent-ink --field-n` in `tokens.css` | Through the opt-in `CLAUDE.md`/`AGENTS.md` pointer, or by running Taste with `--keep palette` |
| Design Principles ([owl-listener](https://github.com/owl-listener/designer-skills), [libreuiux](https://github.com/ormus-solutions/libreuiux-claude-code)) | Proportion rules written as Named Rules in `DESIGN.md` (in place of 60-30-10) | Through the opt-in pointer; neither reads a palette file |
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Alias tokens `--color-primary … --color-ring`; with your consent, one pointer line in its `MASTER.md` | Its token names resolve to ours once `tokens.css` is used; keep its pattern and type output and never run it with `--force` |
| [Theme Factory](https://github.com/anthropics/skills) | Its custom-theme colour bullets (background, text, accent, one secondary) built from `palette.json` | Through the opt-in pointer, or by telling it to use the shared palette |

The `CLAUDE.md` / `AGENTS.md` pointer is opt-in: the skill asks once per project and never writes
to your global `~/.claude/CLAUDE.md`.

## Publishing checklist

1. Push the repo to `youssef4laa/artistic-color-palettes` as a public repository (commit and tag `v0.1.1` yourself).
2. Check how skills.sh indexes it: run `npx skills add youssef4laa/artistic-color-palettes --list` and search for the skill on skills.sh.
3. Share the marketplace command: `claude plugin marketplace add youssef4laa/artistic-color-palettes`.
4. Optional: submit the plugin to Anthropic's directory (PR to `anthropics/claude-plugins-official`).
5. Keep `skills/artistic-color-palettes/data/SNAPSHOT.md` dated whenever the data is refreshed, and bump the version in `plugin.json`, `marketplace.json` and the `SKILL.md` frontmatter together.
6. The marketplace entry installs only `skills/artistic-color-palettes/`; `notes/` and `data-raw/` stay in the repo for maintainers and are not copied by `claude plugin install` or `npx skills add`.

## Data sources and licences

- **Code and text:** MIT ([LICENSE](LICENSE)).
- **`references/kasane-no-irome.md`:** CC BY-SA 4.0. Base colour names and hex values come from
  Wikipedia, "Traditional colors of Japan" (CC BY-SA 4.0). Pattern recipes follow Heian court
  records as compiled by Anthony J. Bryant; they are restated in our own structure. The 33 kasane rows in
  `data/palettes.csv` carry the same share-alike licence.
- **Palette data:** colorcombinations.org (Caslon Media), CC BY 4.0. Wada plate digitisation by
  Matt DesLauriers (mattdesl), MIT. Sanzo Wada's plates (1933–34) are public domain, and the
  sampled paintings are public-domain works.
- **Books:** ideas from Wada's *A Dictionary of Color Combinations* (Seigensha reprint) and
  Albers' *Interaction of Color* are paraphrased with page or chapter citations. No plates,
  diagrams or long quotations are reproduced.

Full attributions, snapshot date and checksums:
[`NOTICE.md`](skills/artistic-color-palettes/NOTICE.md) and
[`data/SNAPSHOT.md`](skills/artistic-color-palettes/data/SNAPSHOT.md).

This project is not affiliated with Seigensha, the Wada estate or colorcombinations.org.

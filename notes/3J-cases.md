# 3J: eval cases for artistic-color-palettes

Location: `skills/artistic-color-palettes/evals/<case>/` (prompt.md, case.yaml, graders/01-expected-output.md placeholder, files/ + place-files.sh where input files or neighbours are needed). Graders are placeholders; the orchestrator drafts the real assertions. Combination cases list the local neighbour SKILL.md folders in a comment block in `case.yaml`, and their `place-files.sh` fetches the neighbours at the pinned SHAs of `notes/fetch-reference-skills.sh` into `.claude/skills/<name>/` (tested: SKILL.md present for all five fetched sets; the libreuiux and owl variants both install as `design-principles`, so never load both in one case).

| # | Case | Solo/combo | Neighbours | Pinned palette | Expected files | Key behaviour tested |
|---|---|---|---|---|---|---|
| 1 | dashboard-restrained-wada | solo | none | none | none (candidates, stop) | 3-5 real Wada candidates for a calm Operate dashboard, then wait for the user's choice |
| 2 | landing-drenched-kasane-autumn | solo | none | kasane-kurenai-momiji | DESIGN.md, design/palette.json, design/tokens.css, preview HTML | Pinned kasane honoured; Drenched/Persuade; hitoe/layer role mapping; no Rising-Sun cliché; composed dark mode; contrast report |
| 3 | painting-palette-reading-app | solo | none | paint-the-milkmaid | DESIGN.md, palette.json, tokens.css (preview optional) | Painting provenance label; Read/Restrained; late-night dark mode; long-reading contrast; defers type/layout |
| 4 | pinned-plate-with-contrast-fix | solo | none | wada-131 (three members at L 0.60-0.64) | DESIGN.md, palette.json, tokens.css | Keep the plate, fix white-text contrast by moving steps only, report before/after, say so when a pinned value moves |
| 5 | no-match-says-so | solo | none | none (asks for plate 412, Vol. 2, impossible mood) | none | Says not in data (plates 1-348, no Vol. 2), no fabrication, offers real candidates or a labelled original composition, stops |
| 6 | combo-impeccable-landing | combo | Impeccable | wada-122 | DESIGN.md (markers inserted only), palette.json, tokens.css | PRODUCT.md then DESIGN.md read first; mode Persuade; colour only (Impeccable owns layout/type); existing text untouched; merge hazard note |
| 7 | combo-taste-dashboard | combo | Taste | none | none (candidates, stop) | One palette source (ours), Taste kept off palette dealing (`--keep palette`), exactly one accent, purple warning; no second palette |
| 8 | combo-design-principles-brief | combo | Design Principles (owl) | wada-143 | DESIGN.md, palette.json, tokens.css | Team principle ("no saturated colour behind text") outranks our rules; says which colour rule bent; pointer asked once |
| 9 | combo-design-principles-libreuiux | combo | Design Principles (libreuiux) | none | none (candidates, stop) | "Triadic" mapped to trio plates 121-240, plates not judged by wheel geometry, our proportion tiers replace 60-30-10 |
| 10 | combo-all-three-handoff | combo | Impeccable, Taste, Design Principles (owl), UI/UX Pro Max, Theme Factory | wada-229 via existing hand-off | edited settings.html only | Second turn: colours taken from the hand-off unchanged, no new palette from any neighbour, handoff.py idempotent |

Notes for the orchestrator
- Case 10 fixtures were generated with `handoff.py --palette wada-229 --strategy restrained --mode operate`; Impeccable's Overview, Typography, Components and Do's and Don'ts were added around the markers, and a re-run of `handoff.py` on the fixture reports all three files unchanged (byte-identical).
- Case 6 prompt says "go ahead and edit DESIGN.md" so an unattended run can pass the "show the diff and ask once" step.
- Cases 1, 7, 9 stop for the user's choice by design; judge them on the candidate round, not on files.
- Case 7 has a one-turn ambiguity: its grader should accept either "3-5 candidates then stop" or a single justified candidate shown for confirmation, never a Taste-dealt palette.
- Taste's skill name is `design-taste-frontend` (folder `taste-skill`); libreuiux/owl both have `name: design-principles`.

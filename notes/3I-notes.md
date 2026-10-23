# 3I notes (SKILL.md author)

Files written (nothing committed; no reference or script edited):
- `skills/artistic-color-palettes/SKILL.md`: 276 lines.
- `README.md` (repo root): 67 lines.

## Checks

- Description: 985 characters (limit 1024), no angle brackets. It names all four sources: Sanzo Wada's
  *A Dictionary of Color Combinations*, Heian kasane no irome, palettes sampled from public-domain
  paintings, and Josef Albers' *Interaction of Color*. It also covers every trigger in the brief.
- Frontmatter: `name`, `description`, `license`, `compatibility`, all allowed by
  `quick_validate.py` (`ALLOWED_PROPERTIES` = name, description, license, allowed-tools, metadata,
  compatibility).
- quick_validate, run from the skill-creator folder, without `-I`:
  ```
  python -m scripts.quick_validate D:\Code\Skill\artistic-color-palettes\skills\artistic-color-palettes
  Skill is valid!
  ```
  PyYAML is not installed on this machine, and the validator imports it. I installed it into the
  scratchpad only (`pip install --target <scratchpad>/pylib pyyaml`) and ran with `PYTHONPATH` set
  to that folder. The user's site-packages are unchanged.
- Reference links in SKILL.md (grep count of each filename): style-recipes 1, application-rules 1,
  interop 1, wada-method 1, albers-principles 1. kasane-no-irome appears 2 times: one body link,
  plus the `license:` frontmatter value the brief asked for. That second one is not a link.
- Only one SKILL.md exists in the skill tree (`find . -name SKILL.md` returns `./SKILL.md`).
- I tested the documented pipeline end to end in a scratch project: `build_tokens.py --palette
  wada-218 --strategy restrained --mode operate --accent "Helvetia Blue" --neutral-from 3 --out`,
  then `validate.py --fix --in-place` (exit 0), then `handoff.py --tokens … --project-dir .
  --claude-md declined` (exit 0). Result: DESIGN.md, design/palette.json and design/tokens.css
  were created, and the pointer status was recorded as declined. `search.py --id 400` refuses with
  exit 2. `preview.py` with 3 candidates writes the HTML.
- SKILL.md describes `--pin` and the status steps only as "see `--help`", because another agent
  is changing those defaults.

## Inconsistencies found (reported, not fixed)

1. **The DESIGN.md seed comment comes before the frontmatter.** When `handoff.py` creates
   DESIGN.md, line 1 is `<!-- acp:seed palette-only; … -->` and `---` comes on line 2. Interop §3
   and 1H-contract ("first line `<!-- acp:seed … -->`") can be read that way. But a file that does
   not start with `---` has no YAML frontmatter for most parsers, so Impeccable / Google DESIGN.md
   loaders may miss our `colors:` map. Suggestion: put the comment as the first body line, after
   the closing `---`. This needs an orchestrator decision.
2. **Frontmatter key and value shape.** Interop §3 says one `slug: "oklch(...)"` entry per role,
   with a descriptive slug (`lyons-ground`), and Recipes §3 shows that shape. `handoff.py` writes
   role keys with uppercase hex (`bg: "#F6F6FB"`, `accent: "#005B8D"`), light values only
   (2H notes, "Design choices"). Either the reference or the script should change.
3. **Provenance label for `--hex`.** `build_tokens.py` labels it "Original composition (colours
   supplied by the user)". Recipes §1.7 fixes "Original composition by this skill (not a plate)"
   and interop §6 asks for "refined from <neighbour>'s palette". No flag sets either label, so
   SKILL.md tells the agent to state the right one in chat.
4. **Two nearby chroma caps.** Albers §4 and the kasane CSS example cap body-text surfaces at
   C ≤ 0.04. Application-rules has a dark-surface cap of 0.045 and a neutral cap of 0.03, but
   never states the 0.04 reading-surface limit. The scopes differ, but application-rules (the
   numbers file) should mention 0.04 or the other two files should cite 0.045.
5. **Source-type name.** Recipes §1.5 says source type "wada"; `search.py --source-type` expects
   `wada_plate`. SKILL.md uses the script's value.
6. **Search with filters only.** With no free-text query, `search.py` returns score 0.0 in id
   order, and `--mood refined,cool` means "any". So the Recipes §2 search (count 3, refined + cool)
   returns warm plates 121–123 first unless `--hue blue` is added. SKILL.md shows a query alongside
   the filters.
7. **Hokusai first.** `--source-type painting` with no query lists *The Starry Night* first;
   Hokusai comes first only when the query says Japanese (tested by 2H). SKILL.md tells the agent
   to order it. *The Great Wave* is also one of the six drift-flagged works, so the drift note goes
   with it.
8. **Display rounding.** The validate report prints `[light] border-subtle on bg: Lc 15 < 15`:
   the value is just under 15 but is shown rounded.
9. Carried from gate-2 (not new): Recipes §2 and §4 describe dark muted/link text starting from
   the old 300 steps.

# Docs fixes for 4L review S2, S3, S4, S7, S8, S10 (2026-10-23)

Only docs and one new test; nothing in `scripts/` edited except the new `scripts/tests/test_docs.py`.

- **S7** `references/style-recipes.md`: examples (a) wada-218 Operate/Restrained and (c)
  paint-the-milkmaid Read/Restrained rewritten from `build_tokens.py` (default `--pin all`) +
  `validate.py --fix --in-place`; each states how it was generated. The script's mapping differs from the
  old text (tint seed is Grayish Lavender A for (a); Milkmaid text comes from the tinted neutral ramp and
  the darkest ground is unused; links start at accent-200 as application-rules says), so the roles
  paragraphs changed too. (b) wada-247: DESIGN.md block replaced by an excerpt of real `handoff.py`
  output (`--roles "drench=Deep Lyons Blue,accent=Apricot Yellow"`, role keys with hex), and its measured
  numbers refreshed from that run. File is 300 lines.
- **S7 test** new `scripts/tests/test_docs.py` (stdlib unittest; run `python -m unittest
  scripts/tests/test_docs.py` from the skill root): rebuilds (a) and (c), asserts every quoted hex is in
  the build output, every `<ramp>-<step> \`#hex\`` pairing matches the ramp, every `N:1` ratio matches a
  measured pair, and the generation note is present.
- **S8** `references/application-rules.md` §2: table rows for `--color-voice-n` (region fill, exact
  plate colour), `-voice-n-mark` (3:1 step), `-on-voice-n`, `--color-action`, `-action-hover`,
  `-on-action`, `-action-border`; "(solid)" wording replaced by the region/mark split; short notes on
  `--action-style`, `--on-accent`, `--text-min`. `references/interop.md` §5: `claude_md` values
  `true | false | declined | not_asked`, `--user-confirmed` required with yes, a stored no persists.
- **S2** `style-recipes.md` §1.6: added "no red + black + gold lacquer as the default for
  food/restaurant briefs" and "for a Japanese brief, at most one candidate on a cream/kinari/gofun
  ground unless the brief asks for calm; even then include one non-beige candidate".
- **S3** `SKILL.md` step 8: `[--notes FILE]` on the usage line and the rule "Write nothing in DESIGN.md
  outside our markers; usage guidance goes in the chat report or through `handoff.py --notes FILE`,
  which renders inside the region". SKILL.md is 304 lines.
- **S4** `interop.md` §4 Taste paragraph: the "Restrained satisfies Taste" claim replaced by "with Taste
  loaded the stricter numbers win: accent < 5%, ground <= 90%; surfaces separate by lightness (the Taste
  alias maps `--surface` to `--color-bg-subtle`), never by lines".
- **S10** `NOTICE.md`: mattdesl's copyright line and MIT permission text copied exactly from upstream
  `LICENSE.md` (fetched from GitHub, master). Kasane position made consistent: CC BY-SA 4.0 covers
  `references/kasane-no-irome.md`, the kasane data rows and adaptations; generated CSS/DESIGN.md carry a
  courtesy credit ("base colours after Wikipedia, CC BY-SA 4.0"), not a `Licence:` line.

Checks: `python -m unittest scripts/tests/test_docs.py` passes; full suite 159 tests OK (1 skipped);
`gate_quotes.py` clean on references and on the SKILL.md body (it flags only SKILL.md's long YAML
`description:` string, a pre-existing false positive); each reference is linked from SKILL.md once.
Dependencies on the 2H script work (as described, not verified here): S2 search spreading, `--notes`,
Taste `--surface` alias and neighbour-map line, S10 courtesy credit in generated kasane CSS.

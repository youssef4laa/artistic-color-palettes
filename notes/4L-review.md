# 4L — Red-team review of `artistic-color-palettes` v0.1.0 (2026-10-23)

Reviewer: agent 4L. Scope: the skill tree, `README.md`, `LICENSE`, `.claude-plugin/*`, eval outputs of
iteration 2 (and iteration 3 where it adds evidence). Nothing in the skill or repo was edited. Scratch
work: `C:\Users\yossi\AppData\Local\Temp\claude\D--Code-Skill\29e06267-cbed-4514-9da6-8af08a7dcb07\scratchpad\4L\`.
Paths below are relative to `skills/artistic-color-palettes/` unless they start with `notes/` or the repo root.

Baseline: `python -m unittest discover -s scripts/tests` gives **130 tests OK** (22.7 s).
`dist/artistic-color-palettes.skill` matches the working tree byte for byte (31 files, no evals, no `__pycache__`).

Counts: **1 blocker, 10 should-fix, 14 nits.**

---

## Blockers

### B1. `--provenance` will write a made-up Wada plate into the user's project
The scripts refuse invented ids on every lookup path (`search.py`, `build_tokens.py`, `preview.py`,
`handoff.py --palette 400` all refuse). The free-text label for `--hex` input is not checked, though, so
the one promise the skill rests on ("never invents a plate number") is guarded everywhere except at the
point where it is written to disk.

```
$ python scripts/handoff.py --hex "Ivory=#f0e6d2,Indigo=#1f2f5a,Vermilion=#d2452b" \
    --provenance "Wada plate 400 (*A Dictionary of Color Combinations*, 1933)" --project-dir fakeprov
handoff: Wada plate 400 (*A Dictionary of Color Combinations*, 1933) | Restrained, Operate | gate pass
  design/palette.json: created / design/tokens.css: created / DESIGN.md: created      (exit 0)
$ head -3 fakeprov/design/tokens.css
/* Wada plate 400 (*A Dictionary of Color Combinations*, 1933) */
$ grep Provenance fakeprov/DESIGN.md
Provenance: Wada plate 400 (*A Dictionary of Color Combinations*, 1933). Credit: Wada plate 400 ...
```
This could easily happen in real use: in the `no-match-says-so` situation the user insists on "plate 412"
and pastes hex values, and the agent labels them the way the user did. The same hole lets real plate
labels sit on colours that are not that plate's (`--provenance "Wada plate 218 ..."` with any hex).

**Fix (about 10 lines plus a test):** in `build_tokens.py` (which `handoff.py --hex` reuses), refuse a
`--provenance` that matches `^(wada plate|editorial palette|sampled from|kasane no irome)` (case-insensitive)
with exit 2 and the message "provenance labels for data sources come from data/palettes.csv; use
--palette <id>". Allow only `Original composition …`, `Refined from <x>'s palette` and
`<name> brand colours (supplied by the user)`. Add one sentence to SKILL.md §Provenance: "`--provenance`
never names a plate, painting, kasane or editorial palette."

---

## Should-fix

### S1. `search.py` returns other patterns for a kasane name that is not in the data, with exit 0
```
$ python scripts/search.py "yanagi-gasane"          # real historical pattern, absent from our 33
1. kasane-matsu-gasane  Matsu-gasane (Layered pine) ...
2. kasane-ume-gasane    Ume-gasane (Layered plum) ...        exit 0, no "not found" note
$ python scripts/search.py "kasane sakura-gasane"   -> same two patterns, exit 0
$ python scripts/search.py "Kōri-gasane"            -> same two patterns, exit 0
$ python scripts/search.py --source-type kasane "yanagi"
No palettes in the data match ... Words not found in the data: yanagi.   exit 1
```
The unknown-word note only appears when nothing matches. Here the generic suffix `gasane` matches, so
the unknown word that matters is never reported. The result is the substitution SKILL.md forbids
("never fill a shortlist with near misses"), and the user's named pattern is never said to be missing.
Paintings and plates are already safe (`Mona Lisa`, `Hiroshige`, `--id paint-mona-lisa`, `plate 349`,
`--id wada-0`, `vol 2 plate 12` all refuse with exit 1 or 2, and nothing is substituted).
**Fix:** always print `Words not found in the data: …` when any query token is unknown. When a token ends
in `-gasane` / `-no-nioi` / `-no-usuyō`, or the query looks like a title and no row's title matches it
exactly, exit 2 with "'<name>' is not in the data. Nothing was substituted." Add a test for `yanagi-gasane`.

### S2. A "Japanese" query never brings up a Wada plate and leans toward the stereotypes
`search.py:54-55`: `JAPAN_WORDS` expands to `JAPAN_ERAS = edo heian kamakura muromachi meiji`, but every
Wada row has era `showa`.
```
$ python scripts/search.py japanese --source-type wada_plate
No palettes in the data match this request. ...                          (348 Japanese plates, 0 hits)
$ python scripts/search.py "japanese restaurant"   (same for "japanese", "japan")
1 ed-kon-kinari (cream #f3ebda ground)   2 ed-edo-murasaki-nezumi (cream)   3 ed-shu-kuro-kin (vermilion/black/gold)
4 ed-entan-sumi (red lead/ink/gold)      5 ed-gunjo-gofun (chalk-cream)
$ python scripts/search.py "calm natural"   -> 4 of 5 on kinari/unbleached grounds
```
Recipes §1.6 says "the chosen plate's actual colours (mostly warm, deep, unexpected) carry the subject",
but the search tool sends every Japanese brief to editorial palettes instead. Three of the five have a
cream ground and two are red, black and gold, which is the stock take-away-menu look. `preview.py` adds
no motifs (no SVG or imagery; checked `spa.html`, `menu.html`, `anime.html`), so the drift comes from the
search ranking alone. "zen spa" and "anime convention" return "no match" (exit 1), which is correct.
**Fix:** add `showa` to the Japan expansion, or better, make JAPAN_WORDS spread results across source
types (at least one Wada plate and one kasane in a top 5). Add to Recipes §1.6: "red + black + gold
lacquer as the default for food/restaurant briefs", and "for a Japanese brief, at most one candidate on a
cream/kinari/gofun ground unless the brief asks for calm". "Zen spa" does ask for calm, so state that the
exception still needs one non-beige candidate.

### S3. Agents keep writing colour notes into DESIGN.md outside our markers
- it-2 `painting-palette-reading-app/.../DESIGN.md:186` `## Reading column (colour rules for Marginalia)`
- it-3 painting `## Colour use in the reading app`; it-3 pinned plate `## Paperwork colour notes`, with
  hard-coded hex (`#AC501F`, `#D96629`, `#C42E2B`, …).

That is 3 of 12 file-writing runs. These sections (a) go stale on the next `handoff.py` run, which then
leaves a *different* hex outside the region, the one thing Impeccable forbids (`reference/document.md:109`).
(b) Sitting outside the markers, they read as the user's own DESIGN.md content, which is precedence rank 2
and so outranks our region (rank 4) (`interop.md:86-89`). (c) They add non-canonical H2 sections that
Impeccable's `document` refresh may drop. SKILL.md never says where extra colour guidance belongs.
**Fix:** add a SKILL.md step 8 rule: "Write nothing in DESIGN.md outside the markers. Usage guidance goes
in the chat report, or through `handoff.py --notes FILE`." Implement `--notes` to render a
`#### Usage notes` block inside the region, so it is regenerated with the hex.

### S4. Taste interop: cards are the same colour as the page, and the accent caps disagree
- Light `--color-surface` = neutral-50 = `--color-bg` (role map `application-rules.md:64`). The generated
  neighbour map says so outright: "Taste: `--bg` #F6F6FB, `--surface` #F6F6FB". Taste bans 1px lines and
  wants a surface "2–6 lightness points from --bg" (`notes/neighbour-skills/taste-skill/skills/taste-skill/references/colour.md`
  §4). Every run tells the user "bg and surface are identical in light, so separate cards with a border"
  (pinned-plate, DP-brief, Impeccable, Milkmaid responses), which is exactly what Taste forbids.
- `interop.md:109-110` claims "Taste wants ground 70–90%, accent under 5%: our Restrained tier satisfies
  it", but Restrained is ground 85–95% and accent 2–8% (`SKILL.md:231`; script `accent_pct [2, 8]` for
  C < 0.15). The two rules contradict each other and there is no precedence note (the taste-dashboard run
  tightened to 2–5% on its own).

**Fix:** point the Taste alias at a separated step (`--surface: var(--color-bg-subtle)`, ΔL 0.04), or make
light `--color-surface` neutral-100 when bg is neutral-50. In `interop.md` §4, say "with Taste loaded the
stricter number wins: accent < 5%, ground ≤ 90%", and have `handoff.py` print that in the neighbour map.

### S5. A recorded "no" to the pointer is lost on the next run, so the skill asks again
`handoff.py:783`: `... .get("claude_md") or "not_asked"` turns a stored `False` into `"not_asked"`.
```
--claude-md no            -> palette.json handoff.claude_md: False
(re-run, no flag)         -> handoff.claude_md: not_asked
```
That breaks "The answer is stored … so do not ask again" (SKILL.md step 8).
**Fix:** `v = ….get("claude_md"); claude_md = "not_asked" if v is None else v`, plus a test.

### S6. The global-CLAUDE.md guard checks the wrong folder
`handoff.py:820` refuses only when `--project-dir` *is* the home folder. The global file lives in
`~/.claude/`. I simulated this with `Path.home` patched to a scratch "fake home" (so no real files were
touched): `--project-dir <fakehome>/.claude --claude-md yes --user-confirmed` → `CLAUDE.md: created`,
`AGENTS.md: created`, plus DESIGN.md and design/ inside `.claude`.
**Fix:** refuse when the project directory is the home folder, any folder above it, or `~/.claude`,
`~/.codex` or `~/.agents`, and refuse to write any `CLAUDE.md` that resolves inside `~/.claude`.

### S7. Style-recipes examples (a) and (c) still mislead (the known carried issue)
They do not just predate the amendment: they now give different token steps *and different hex* from
what the shipped scripts produce for the same inputs. I ran `build_tokens.py` + `validate.py --fix` on
wada-218 and paint-the-milkmaid (Restrained):

| Role | Recipes text | Script output |
|---|---|---|
| (a) light accent fill | accent-600 `#0075b3`, label 4.65:1 (`style-recipes.md:146-148`) | pinned 700 `#005b8d`, white 7.29:1 |
| (a) light accent-hover | pinned `#005b8d` | accent-800 `#194666` |
| (a) dark muted | neutral-300 `#9ea1ad` → `#b1b4c0` (`:160-161`) | neutral-200 `#bec0ca` |
| (a) dark links | accent-300 `#72a8d2` → `#9ad2fd` (`:164-165`) | accent-200 → `#bbd1e3` |
| (c) light filled action / hover | accent-600 `#386fb9` / pinned 700 (`:288-289`) | pinned `#254d83` / `#274369` |
| (c) dark muted / links | `#b8b4a7` / `#b7cff1` (`:293-295`) | `#c4c1b7` / `#c5cfdd` |

`application-rules.md:176-178` says dark links start at accent-200, but the examples start at 300. An agent
that explains its tokens from the recipes will quote numbers that do not match its own DESIGN.md.
Example (b)'s DESIGN.md block (`style-recipes.md:224-233`) shows descriptive keys with OKLCH values
(`lyons-ground: "oklch(…)"`), but `handoff.py` writes role keys with hex (`bg: "#F6F6FB"`), so an agent
copying the example would hand-edit our region.
**Fix:** regenerate (a) and (c) from the scripts, say they were generated with
`build_tokens.py … --pin all`, and add a doc test that checks each example hex appears in the build
output. Label (b)'s block "illustrative; handoff.py writes role keys" or regenerate it.

### S8. The reference that "holds the role map" leaves out half the iteration-2 tokens
`application-rules.md` §2 (the file SKILL.md:133 sends agents to for the role map) has no mention of
`--color-voice-n-mark`, `--color-on-voice-n`, `--color-action*`, `--action-style`, `--on-accent` or
`--text-min`. Grep across references and assets: only SKILL.md mentions them. §2 also says voices
are "(solid)", which hides the split between a region fill and a mark.
`interop.md:151` still lists `handoff.claude_md: true | false | declined`: `not_asked` and
`--user-confirmed` are missing. **Fix:** add these rows to the §2 table and two lines to interop §5.

### S9. An existing palette in DESIGN.md is kept beside ours without warning
On a DESIGN.md with `colors: primary: "#ff0000"` and `## Colors / Red brand.`, `handoff.py` only detects
*key-name* clashes (`handoff.py:424-427`). Its exit-3 diff inserts our 22 keys next to `primary` and our
region under "Red brand.", and `--yes` would leave two palettes in place. It also writes
`design/palette.json` and `tokens.css` before the user has approved anything ("created" alongside
"DESIGN.md: NOT written"). SKILL.md step 1 says never to add a second palette silently, but the tool does
not help.
**Fix:** when `colors:` holds non-acp keys or `## Colors` holds prose, add to the exit-3 message:
"existing palette found: choose replace or refine (SKILL.md step 1) before --yes". Write nothing
(companions included) until the user approves.

### S10. Licence wording: missing MIT notice, and a confusing share-alike claim in user CSS
- mattdesl's data is cited as MIT, but `NOTICE.md` has neither his copyright line nor the MIT permission
  text, which MIT requires in copies. Copy both from the upstream LICENSE, or say plainly that only
  facts (names and hex values) are used.
- For kasane palettes the generated `design/tokens.css` in the user's project says
  `Licence: CC-BY-SA-4.0 (base hex) + own composition.` A user's legal reviewer will read that as a
  share-alike obligation on their stylesheet. Meanwhile `NOTICE.md:24` treats colorcombinations' hex values
  as facts but the Wikipedia ones as share-alike. Pick one position. The suggested one: SA applies to
  `kasane-no-irome.md` and the data rows; generated CSS carries a courtesy credit
  ("base colours after Wikipedia, CC BY-SA 4.0"), not a "Licence:" line.

---

## Nits

- **N1. Code copied without notice.** `scripts/search.py:41` STOPWORDS starts with the exact 22-word list,
  in the same order, from UI/UX Pro Max `scripts/core.py:241-244` (MIT). `NOTICE.md:66` says no
  third-party code is copied. It is trivial, but either add a NOTICE line or reorder. Two sentences in
  `application-rules.md` track better-colors closely (`:223-224` ↔ `color-usage.md:85`; `:53-55` ↔
  `SKILL.md:30`). Rephrase them, or count them under the existing better-colors credit. My overlap scan
  found nothing else (no code run ≥ 20 identifier tokens, no prose run ≥ 10 words).
- **N2.** `--mood` silently drops all 33 kasane and 25 paintings (they have no mood tags):
  `--mood serene,refined --source-type kasane` → no match. Say so in `--help` and SKILL.md step 3.
- **N3.** The SKILL.md:288 example report says "accent 2–5%" for plate 218. The script writes 2–8%
  (Helvetia Blue C 0.109 < 0.15).
- **N4.** `application-rules.md:179` lists a `.dark` class, but the scripts use `[data-theme]`. The preview
  greyscale is luminance-matched (`colorlib.py:367`), while `albers-principles.md:38` and
  `application-rules.md:191` say "C = 0, L kept".
- **N5.** The `interop.md` §2 table maps `--color-border-subtle` → Pro Max `--color-border`. In
  `tokens.css`, Pro Max's `--color-border` is our `--color-border` (neutral-300), and the DESIGN.md
  neighbour map prints `#BEC0CD`.
- **N6.** `build_tokens.py` exits 1 for "not in the data" (the others exit 2) and accepts no bare
  `--palette 218` (`search.py --id 218` does). `preview.py` and `handoff.py` print "error: error:".
  A warning reads "for a Operate surface".
- **N7.** Generated CSS comments: the provenance line is repeated for `--hex`; markdown asterisks inside a
  CSS comment (`(*A Dictionary…*)`); the CC BY credit has no licence or source URL. Add `source_url` and
  `https://creativecommons.org/licenses/by/4.0/`.
- **N8.** "Sanzo Wada's 348 plates … are public domain" (`NOTICE.md:20`, `README.md:80`) holds in Japan
  (author died 1967; term ended 2017). In the US, URAA restoration plausibly protects the 1933/1934
  volumes until 2029/2030. There is no exposure, because no plate is reproduced and names and hex values
  are facts, but "public domain in Japan" would be the more accurate wording. Leave the colorcombinations
  attribution block as the site requires it.
- **N9.** `evals/` (277 K, `place-files.sh` clones GitHub repos) ships in plugin and skills.sh installs.
  It is not run at run time, but it is noise in the user's skill folder. Move it to the repo root or exclude it.
- **N10.** A local-path marketplace add reads the repo in place, and that tree also holds git-ignored
  `notes/_private/albers.txt` and the Wada page renders (`data-raw/notes/wada-pages/1G/*.png`, ignored by
  `.gitignore:12-14`, confirmed with `git check-ignore`). Fine locally, but never distribute by zipping the
  folder; use only `dist/*.skill` or a git clone.
- **N11.** claude.ai: SKILL.md says `python`, and some sandboxes only have `python3`. There is no line on
  where to write when there is no project folder (e.g. the outputs directory). Add one sentence.
- **N12.** A new DESIGN.md gets `name:` = the palette title ("Helvetia Blue & Grayish Lavender - A +1"),
  not the project's name. Default to the project folder name, or ask.
- **N13.** The description's "asks to make a site or app look less generic" overlaps the whole-site
  triggers of Taste and Impeccable. "make the colours look less generic" fits our lane (for 4K).
- **N14.** The `combo-all-three-handoff` fixture predates iteration 2 (no `--color-action`, no
  `voice-1-mark`). I re-ran `handoff.py` over a copy: text outside the markers is byte-identical, exit 0,
  so upgrading works. Impeccable's `document` merge and the Pro Max `MASTER.md` pointer have still never
  been run end to end.

---

## Checklist results by brief item

**1. Licence audit.** CC BY credit is present in generated code: tokens.css line 2 reads
`/* Wada plate 218 via colorcombinations.org (CC BY 4.0) */`, and the paintings and kasane equivalents
are correct. `kasane-no-irome.md:5` carries CC BY-SA 4.0 with the Wikipedia credit. `LICENSE` lists the
exceptions (kasane file and per-row data), consistent with NOTICE and README. The SKILL.md frontmatter
`license` names only the kasane file, not its 33 data rows (minor). Third-party code: N1. Missing MIT
notice: S10.

**2. Copyright.** `data-raw/gate_quotes.py` over SKILL.md, references/*, NOTICE, assets and README finds
only the skill's own description (false positive). An n-gram scan against `notes/_private/albers.txt`:
the only 6-word overlaps are the bibliographic line and the attributed 7-word quote ("the most relative
medium in art"). No Japanese run ≥ 16 characters exists in any reference or note, so no Wada page text is
transcribed. No plates or diagrams appear. The publishable `notes/*.md` also pass the 10-gram Albers scan.
**Pass.**

**3. Fabrication.** `Wada plate 400`, `--id wada-0`, `wada-349`, `--id 349`, `vol 2 plate 12`, `Wada vol. 2`,
`Mona Lisa palette`, `Leonardo da Vinci`, `Hiroshige`, `--id kasane-sakura`, `--id paint-mona-lisa`: all
refuse, exit 1/2, "Nothing was substituted". `build_tokens.py`, `preview.py` and `handoff.py` refuse bad
ids. **Fails** on a missing kasane name typed as free text (S1) and on free-text provenance (B1).

**4. Stereotype drift.** "zen spa" → no match (exit 1); the retry `calm natural` → 4 of 5 on kinari
grounds. "Japanese restaurant menu" → 5 editorial palettes, cream and red-black-gold (S2). "anime
convention landing page" → no match; `--mood playful,bold` gives quads 241–245, which is fine. The
previews contain no imagery or motifs. SKILL.md:219-222 and Recipes §1.6 do steer away from cream + red
circle + cherry blossom, Rising Sun or militarist emblems and beige-Zen by reflex, but the search tool's
ranking pushes the other way for "Japanese".

**5. claude.ai compatibility.** No `urllib`, `http`, `requests` or `socket` anywhere. Imports are stdlib
only (`argparse csv copy difflib functools html json math os pathlib re sys unicodedata`; tests add
`subprocess tempfile unittest`). There is exactly one SKILL.md in the tree and none nested (evals and the
workspace hold none). SKILL.md is 296 lines and the description 985 characters. Each of the 6 references
is linked exactly once (lines 59, 77, 80, 133, 152, 261). Paths with spaces work: the whole hand-off ran
in `…\4L\proj with spaces\{wada,kasane,paint,hex}` from Git Bash, and `search`, `build_tokens` and
`validate` ran from PowerShell with `.\km tokens.json` and printed Japanese names to a cp1252 console
without crashing. Minor: N11.

**6. Interop.**
- Boundaries against the transcripts: no colour-skill overreach on type or layout. The Taste-dashboard
  restyle promise is Taste's work, run with Taste loaded. The kasane `preview.html` labels its type and
  layout as placeholders. The violation is S3 (writing outside the markers).
- Round-trip: `combo-all-three-handoff` outputs leave `DESIGN.md`, `PRODUCT.md`, `palette.json` and
  `tokens.css` byte-identical to the fixture, and `settings.html` has 0 hex and 28 `var(--color-*)`. A
  re-run is byte-identical: md5 unchanged, "unchanged" ×3. A DESIGN.md without markers gives exit 3 with a
  diff. `--claude-md yes` without consent gives exit 4.
- Contradictions without a precedence note: Taste surface and accent cap (S4). Impeccable prefers
  descriptive frontmatter keys (`document.md:109`) while we write role keys. That was a decision at gate 3,
  but interop.md does not state it (fold into S8).
- "Make the colours less generic" with all skills loaded: the answer is coherent if our skill leads.
  Ours offers 3–5 shortlisted palettes and waits. Impeccable reads the mode and strategy names we share.
  Taste runs `--keep palette`. Pro Max keeps its pattern and type output and is never run with `--force`.
  Theme Factory's showcase is pre-empted. Precedence puts neighbour-dealt palettes (rank 5) below ours
  (rank 4). Two weak points: before our region exists nothing stops Taste, Pro Max or Impeccable
  `colorize` from dealing a palette first (step 1's replace/refine choice catches this afterwards), and
  our description's broad "look less generic" trigger (N13) can pull non-colour work into our lane, where
  the Boundaries paragraph then has to hand it back.

**7. Consistency.** Dark-mode steps, chroma caps (0.03 / 0.04 / 0.045, × 0.85) and the proportion table
are the same in SKILL.md, Recipes §1.9, `build_tokens.py:46-57` and the script output for all four
strategies (checked on wada-247). `--color-border-strong` is neutral-500 in both modes, matching the doc.
Dark links accent-200 and muted neutral-200 match the scripts. Drift: S7 (recipe examples, still
misleading), S8 (missing role-map rows, `not_asked`, `--user-confirmed`), N3, N4, N5.

---

## Verdict

**Don't ship v0.1.0 as it is; ship as soon as B1 is fixed.** B1 is a short, testable change that closes the
one path by which the shipped tools can write a made-up plate number into a user's project, the skill's
core promise. Licence and copyright are clean apart from the S10 wording. I would also land S1 (missing
kasane name), S5 (lost "no") and S6 (`~/.claude` guard) before tagging: each is a few lines with a test.
S2–S4 and S7–S9 can go into v0.1.1 if time is short, but S3 and S4 show up in real runs and are the most
likely to annoy users who have Impeccable or Taste installed.

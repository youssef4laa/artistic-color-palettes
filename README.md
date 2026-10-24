# artistic-color-palettes: maintainer sources

This branch holds the material behind the skill that the skill does not ship. The skill itself lives on
the default branch (`release/0.1.0`); this branch shares its history up to v0.1.1 and is never merged
back.

- `data-raw/`: the raw colorcombinations.org snapshot, the full kasane pattern source
  (`data-raw/kasane-no-irome.md`, CC BY-SA 4.0) and `paintings.json`, the 25 normalised painting
  records. `scripts/build_data.py` reads it to build the shipped `data/palettes.csv` and
  `data/colors.csv`.
- `notes/`: build notes, gate reports, reviews, token-diet measurements, the trigger eval set
  (`notes/trigger-eval.json`) and `notes/fetch-reference-skills.sh`, which the combo evals use.

## Rebuilding the data

Check this branch out next to the default branch and point `build_data.py` at it:

```bash
git worktree add ../acp-sources sources
cd skills/artistic-color-palettes
python scripts/build_data.py --raw ../../../acp-sources/data-raw
```

`paintings.json` is rewritten inside `data-raw/`; commit it here. Commit the rebuilt `data/` files and
`data/SNAPSHOT.md` on the default branch. With `data-raw/` absent, the two raw-data unit tests
skip; to run them, copy or symlink `data-raw/` into the default branch's checkout without committing it.

Licences are as in [LICENSE](LICENSE): code MIT, `data-raw/kasane-no-irome.md` CC BY-SA 4.0, palette
data CC BY 4.0 (colorcombinations.org).

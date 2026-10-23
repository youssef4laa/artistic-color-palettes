# 1F: kasane-no-irome reconciliation

Output: `skills/artistic-color-palettes/references/kasane-no-irome.md`. Source: `Art References/kasane-no-irome.md` (unchanged).

## Count discrepancy
The brief says 35 patterns. The original has **33** (`####` headings). Susuki is only mentioned in a note as sharing Mochi tsutsuji's recipe. Nothing was added. The checker asserts 33 and that the corrected file matches the original pattern for pattern.

## Changes
1. **Shade table (conflict 2).**
   - Before: fixed factors (deep: L-0.08, chroma unchanged; pale: L+0.15, chroma x0.70; paler: L+0.25, chroma x0.45).
   - After: chroma is a share of the hue's maximum in-gamut chroma at the new lightness (deep about 0.9x, pale about 0.75x, paler about 0.5x the base colour's own share). L steps are -0.08 / +0.10 / +0.18, with 0.04-0.05 steps above L about 0.85 and at least 0.03 between neighbours. Hue fixed; same share across hues at the same step; gamut and contrast re-checked. Added a five-step procedure.
   - Reason: matches better-colors multi-hue and ramp rules (vividness proportional to each hue's own ceiling; finer steps at the light end).
2. **Added note** that the listed shade hexes come from the earlier fixed-factor computation and are kept as published. Measured shares vary widely (about 0.13 to 0.99), so they do not follow either rule uniformly.
3. **"Read this first" bullet:** now says listed shades are kept as listed and new shades follow the proportional rules (was: all shades computed with the rules below).
4. **Dark-mode step 6 (conflict 1).**
   - Before: invert the ramp, deepest layer as background, keep hitoe as accent, lighten if needed.
   - After: composed, not inverted. Surfaces from the darkest layer or a deep tinted neutral, reduced chroma, well-separated dark steps, light tinted text, accents re-chosen per role (usually lighter and less vivid), every pair re-measured.
   - Reason: matches better-colors dark mode and impeccable colorize (not mechanically inverted).

## Not changed
All 33 patterns (names, types, layers, hex), the base colour table, the layer-role table, pattern-type words, CSS example, sources. No typos found. Left as is: line 3 still says "Sanzo Wada palette skill", which is stale versus our skill name; flag for the orchestrator.

## Checker output (`data-raw/1F/check_kasane.py`, exit 0)
```
patterns: 33 (identical to original: True)
distinct hex values: 32; worst round-trip error: 0/255
oklch() values checked: 0
layer-role table and base-colour table identical to original
PASS
```
No oklch() values are written in the file, so none were checked.

# Palette hand-off template (`## Colors` region of DESIGN.md)

`scripts/handoff.py` renders everything between `<!-- template:begin -->` and `<!-- template:end -->`
into the marker-delimited region of the project's `DESIGN.md`:

```
## Colors
<!-- acp:begin colors v1 -->
...the rendered template...
<!-- acp:end colors -->
```

The same run writes the frontmatter entries between `# acp:begin tokens` and `# acp:end tokens`
inside the `colors:` map. Both are generated from `design/palette.json`, so a hex value in the
prose is always identical to the one in the frontmatter (Impeccable only forbids a *different*
value). Text outside our two markers is never touched. Bump `v1` in the marker if this shape
changes.

Order is fixed (contract amendment 3): palette character, provenance, role entries in Impeccable's
entry format `**Name** (#HEX / oklch(L C h))` under `### Primary`, `### Secondary`, `### Tertiary`,
`### Neutral`, then `### Named Rules` (strategy and mode verbatim, proportions, contrast floor,
composed dark mode), then token tables by key, measured contrast, adjustments, the keep-in-sync
note, pointers, the neighbour map, and the optional usage notes (`handoff.py --notes FILE`). A section with nothing to say is left out. Placeholders are
`{{NAME}}`; each expands to a complete block including its heading.

<!-- template:begin -->
{{CHARACTER}}

{{PROVENANCE}}

{{PRIMARY_SECTION}}

{{SECONDARY_SECTION}}

{{TERTIARY_SECTION}}

{{NEUTRAL_SECTION}}

{{NAMED_RULES_SECTION}}

{{TOKEN_TABLES}}

{{CONTRAST}}

{{ADJUSTMENTS}}

{{KEEP_IN_SYNC}}

{{POINTERS}}

{{NEIGHBOUR_MAP}}

{{USAGE_NOTES}}
<!-- template:end -->

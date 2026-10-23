#!/usr/bin/env bash
# Pulls the complete, licence-intact source of the four reference skills
# described in skills-reference.md, pinned to the commits that file was written against.
# Usage: bash fetch-reference-skills.sh [target-dir]   (default: ./reference-skills)
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows: keep leading-slash sparse paths literal
TARGET="${1:-reference-skills}"
mkdir -p "$TARGET"

fetch () {  # name repo sha path...
  local name="$1" repo="$2" sha="$3"; shift 3
  local dest="$TARGET/$name"
  if [ -d "$dest" ]; then echo "skip $name (exists)"; return; fi
  git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repo.git" "$dest"
  git -C "$dest" sparse-checkout set --no-cone "$@" LICENSE LICENSE.txt NOTICE.md
  git -C "$dest" checkout --quiet "$sha"
  echo "ok   $name  ($repo @ ${sha:0:7})"
}

fetch better-colors   jakubkrehel/skills                  4c66b1fa86e9ab70187b43d7da9b6fdb29f2ef63 \
  /skills/better-colors/ /skills/better-accessibility/SKILL.md
fetch ui-ux-pro-max   nextlevelbuilder/ui-ux-pro-max-skill 623a9a9037d006ea727f8213f084d02a6b6f11b5 \
  /.claude/skills/ui-ux-pro-max/
fetch theme-factory   anthropics/skills                   dbd4588f9e1033efb41dad4bef2f7947c8993d44 \
  /skills/theme-factory/
fetch impeccable      pbakaus/impeccable                  e3083ac3301e4d10517dd6cb58ab645bc2cb6e1b \
  /.claude/skills/impeccable/SKILL.md /.claude/skills/impeccable/reference/

echo
echo "Done. Read $TARGET/*/ alongside skills-reference.md."

# ---- Neighbour skills (agent 1H): second target dir, same pinned-sha style ----
# Usage: bash fetch-reference-skills.sh [ref-target-dir] [neighbour-target-dir]
NEIGHBOUR_TARGET="${2:-neighbour-skills}"
mkdir -p "$NEIGHBOUR_TARGET"

fetch_neighbour () {  # name repo sha path...
  local name="$1" repo="$2" sha="$3"; shift 3
  local dest="$NEIGHBOUR_TARGET/$name"
  if [ -d "$dest" ]; then echo "skip $name (exists)"; return; fi
  git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repo.git" "$dest"
  git -C "$dest" sparse-checkout set --no-cone "$@" LICENSE LICENSE.txt NOTICE.md
  git -C "$dest" checkout --quiet "$sha"
  echo "ok   $name  ($repo @ ${sha:0:7})"
}

# Whole Impeccable skill folder (scripts/, templates etc.), not just SKILL.md + reference/
fetch_neighbour impeccable      pbakaus/impeccable            e3083ac3301e4d10517dd6cb58ab645bc2cb6e1b   /.claude/skills/impeccable/
# Taste: most-installed taste repo on GitHub (skills.sh: design-taste-frontend 657K installs)
fetch_neighbour taste-skill     Leonxlnx/taste-skill          6010f91a9935f1c167dfc500fb1a475681892e6b   /skills/ /.claude-plugin/ /README.md
# Design Principles: most-installed skill literally named design-principles (skills.sh 2.1K)
fetch_neighbour design-principles-owl   owl-listener/designer-skills  9a6930cf84a822eb458624bd11c61aac5bbdf224   design-principles/
# Runner-up named design-principles with colour theory references (110 installs)
fetch_neighbour design-principles-libreuiux ormus-solutions/libreuiux-claude-code 41a968c41cb9328335444ded8d0436362d0ba50a   design-principles/ /.libreui-config.yaml
# Related: writes .interface-design/system.md (30.3K installs)
fetch_neighbour interface-design dammyjay93/interface-design   2f9be3206855bcb2d1d0af262c8bae25cba6658d   /.claude/ /reference/ /README.md

echo "Neighbours in $NEIGHBOUR_TARGET/"

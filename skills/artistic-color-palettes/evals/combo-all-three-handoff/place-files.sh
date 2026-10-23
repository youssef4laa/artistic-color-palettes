#!/usr/bin/env bash
set -eu
export MSYS_NO_PATHCONV=1
HERE="$(cd "$(dirname "$0")" && pwd)"
cp -R "$HERE/files/." .

# Neighbour skills are fetched at pinned SHAs (see notes/fetch-reference-skills.sh), never copied into this repo.
TMP="$(mktemp -d)"
TMP="$(cd "$TMP" && { pwd -W 2>/dev/null || pwd; })"   # native path so git.exe and cp agree on Windows
trap 'rm -rf "$TMP"' EXIT
install_skill () {  # install-name repo sha subpath sparse-path...
  local name="$1" repo="$2" sha="$3" sub="$4"; shift 4
  git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repo.git" "$TMP/$name"
  # MSYS_NO_PATHCONV keeps the leading-slash sparse patterns literal in Git Bash on Windows
  MSYS_NO_PATHCONV=1 git -C "$TMP/$name" sparse-checkout set --no-cone "$@" LICENSE LICENSE.txt NOTICE.md
  git -C "$TMP/$name" checkout --quiet "$sha"
  mkdir -p ".claude/skills/$name"
  cp -R "$TMP/$name/$sub/." ".claude/skills/$name/"
  cp "$TMP/$name"/LICENSE* "$TMP/$name"/NOTICE.md ".claude/skills/$name/" 2>/dev/null || true
}

install_skill impeccable pbakaus/impeccable e3083ac3301e4d10517dd6cb58ab645bc2cb6e1b .claude/skills/impeccable '/.claude/skills/impeccable/'
install_skill taste-skill Leonxlnx/taste-skill 6010f91a9935f1c167dfc500fb1a475681892e6b skills/taste-skill '/skills/' '/.claude-plugin/' '/README.md'
install_skill design-principles owl-listener/designer-skills 9a6930cf84a822eb458624bd11c61aac5bbdf224 ux-strategy/skills/design-principles 'design-principles/'
install_skill ui-ux-pro-max nextlevelbuilder/ui-ux-pro-max-skill 623a9a9037d006ea727f8213f084d02a6b6f11b5 .claude/skills/ui-ux-pro-max '/.claude/skills/ui-ux-pro-max/'
install_skill theme-factory anthropics/skills dbd4588f9e1033efb41dad4bef2f7947c8993d44 skills/theme-factory '/skills/theme-factory/'

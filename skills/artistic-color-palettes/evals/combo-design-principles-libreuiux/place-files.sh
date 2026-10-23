#!/usr/bin/env bash
set -eu
export MSYS_NO_PATHCONV=1
HERE="$(cd "$(dirname "$0")" && pwd)"

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

install_skill design-principles ormus-solutions/libreuiux-claude-code 41a968c41cb9328335444ded8d0436362d0ba50a plugins/design-mastery/skills/design-principles 'design-principles/' '/.libreui-config.yaml'

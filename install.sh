#!/usr/bin/env bash
# Install learning-hub-agent-kit modules into a target repo or ~/.cursor (global).
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VERSION="$(cat "$KIT_ROOT/VERSION" 2>/dev/null || echo "unknown")"
MARKER=".learning-hub-agent-kit"

usage() {
  cat <<EOF
Usage: install.sh --repo <path> --modules m1,m2[,...]
       install.sh --check --repo <path>
       install.sh --update --repo <path> --modules m1,m2[,...]
       install.sh --global

Modules: core-git, secrets, docs, infographics
EOF
}

die() { echo "error: $*" >&2; exit 1; }

expand_modules() {
  local raw="$1"
  local out=""
  local m
  IFS=',' read -ra parts <<< "$raw"
  for m in "${parts[@]}"; do
    m="${m// /}"
    [[ -z "$m" ]] && continue
  case "$m" in
      core-git|secrets|docs|infographics) out+="$m " ;;
      *) die "unknown module: $m" ;;
    esac
  done
  if [[ "$out" == *"infographics"* ]]; then
    [[ "$out" == *"core-git"* ]] || out="core-git $out"
    [[ "$out" == *"docs"* ]] || out="docs $out"
  fi
  echo "$out" | tr ' ' '\n' | awk '!seen[$0]++' | tr '\n' ' '
}

copy_module() {
  local module="$1"
  local dest="$2"
  local src="$KIT_ROOT/modules/$module"
  [[ -d "$src" ]] || die "module not found: $module"
  echo "  → $module"
  (cd "$src" && find . -type f -print0) | while IFS= read -r -d '' rel; do
    rel="${rel#./}"
    mkdir -p "$dest/$(dirname "$rel")"
    cp "$src/$rel" "$dest/$rel"
  done
}

install_repo() {
  local repo="$1"
  local modules="$2"
  [[ -d "$repo" ]] || die "repo path not found: $repo"
  repo="$(cd "$repo" && pwd)"
  echo "Installing learning-hub-agent-kit $VERSION into $repo"
  for module in $modules; do
    copy_module "$module" "$repo"
  done
  echo "$VERSION" > "$repo/${MARKER}-version"
  date -u +"%Y-%m-%dT%H:%M:%SZ" > "$repo/${MARKER}-installed-at"
  echo "$modules" | tr ' ' '\n' | grep -v '^$' > "$repo/${MARKER}-modules"
  cp "$KIT_ROOT/manifest.yaml" "$repo/${MARKER}-manifest"
  echo "Done. Commit .cursor agentic-workflows gh-docs .github ${MARKER}-* in the target repo."
}

check_repo() {
  local repo="$1"
  [[ -d "$repo" ]] || die "repo path not found: $repo"
  repo="$(cd "$repo" && pwd)"
  if [[ ! -f "$repo/${MARKER}-version" ]]; then
    echo "status: not installed"
    exit 1
  fi
  local installed expected
  installed="$(cat "$repo/${MARKER}-version")"
  expected="$VERSION"
  echo "installed: $installed"
  echo "kit:       $expected"
  if [[ "$installed" == "$expected" ]]; then
    echo "status: up to date"
  else
    echo "status: drift (run install.sh --update)"
    exit 1
  fi
}

install_global() {
  local dest="${HOME}/.cursor"
  local core_git="$KIT_ROOT/modules/core-git/.cursor"
  mkdir -p "$dest/rules" "$dest/skills" "$dest/hooks"
  echo "Installing core-git + secrets into $dest (global baseline)"
  if [[ -d "$core_git/rules" ]]; then
    cp -R "$core_git/rules/." "$dest/rules/"
  fi
  if [[ -d "$core_git/skills" ]]; then
    cp -R "$core_git/skills/." "$dest/skills/"
  fi
  if [[ -f "$KIT_ROOT/modules/secrets/.cursor/hooks.json" ]]; then
    sed 's|\.cursor/hooks/|hooks/|g' \
      "$KIT_ROOT/modules/secrets/.cursor/hooks.json" > "$dest/hooks.json"
    cp -R "$KIT_ROOT/modules/secrets/.cursor/hooks/." "$dest/hooks/"
  fi
  echo "$VERSION" > "$dest/${MARKER}-version"
  echo "Global install done. Skills/rules at $dest/{skills,rules}. Doc links in skills need agentic-workflows/ in repos — use --repo for full docs."
}

MODE=""
REPO=""
MODULES="core-git,secrets,docs"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --modules) MODULES="$2"; shift 2 ;;
    --check) MODE="check"; shift ;;
    --update) MODE="update"; shift ;;
    --global) MODE="global"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown arg: $1" ;;
  esac
done

case "$MODE" in
  check)
    [[ -n "$REPO" ]] || die "--check requires --repo"
    check_repo "$REPO"
    ;;
  global)
    install_global
    ;;
  update|"")
    [[ -n "$REPO" ]] || die "--repo required"
    expanded="$(expand_modules "$MODULES")"
    install_repo "$REPO" "$expanded"
    ;;
esac

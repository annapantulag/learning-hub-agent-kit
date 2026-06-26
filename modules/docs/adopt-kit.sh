#!/usr/bin/env bash
# Adopt learning-hub-agent-kit into the repo that contains this script.
# Place at repo root (or run from kit with --repo). See adopt-learning-hub-agent-kit.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
KIT_URL="${LEARNING_HUB_AGENT_KIT_URL:-https://github.com/annapantulag/learning-hub-agent-kit.git}"
KIT_CACHE="${LEARNING_HUB_AGENT_KIT_CACHE:-$HOME/.local/share/learning-hub-agent-kit}"
DEFAULT_MODULES_CODE="core-git,secrets,docs"
DEFAULT_MODULES_LEARNING="core-git,secrets,docs,infographics"
MARKER=".learning-hub-agent-kit-version"

MODE="install"
MODULES="$DEFAULT_MODULES_CODE"
KIT_PATH=""
DO_COMMIT=false
DO_PUSH=false
AUTO_CLONE=true

usage() {
  cat <<EOF
Usage: ./adopt-kit.sh [options]

Run from the target repo root (this script's directory = repo root).

Options:
  --learning          Install infographics module (learning repos only)
  --modules a,b,c     Override module list
  --kit PATH          Path to learning-hub-agent-kit clone
  --no-clone          Fail if kit not found (do not clone to cache)
  --update            Re-sync from kit (install.sh --update)
  --check             Drift check only (install.sh --check)
  --commit            Stage adoption files and commit
  --push              Push after --commit (implies --commit)
  --repo PATH         Target repo (default: directory containing this script)
  -h, --help          Show this help

Kit discovery (first match wins):
  1. --kit PATH or \$LEARNING_HUB_AGENT_KIT
  2. \$REPO_ROOT/../learning-hub-agent-kit
  3. \$KIT_CACHE (clone from $KIT_URL if missing and cloning allowed)

Examples:
  ./adopt-kit.sh
  ./adopt-kit.sh --learning --commit
  ./adopt-kit.sh --update --commit
  LEARNING_HUB_AGENT_KIT=~/src/learning-hub-agent-kit ./adopt-kit.sh --check
EOF
}

die() { echo "error: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --learning) MODULES="$DEFAULT_MODULES_LEARNING"; shift ;;
    --modules) MODULES="$2"; shift 2 ;;
    --kit) KIT_PATH="$2"; shift 2 ;;
    --no-clone) AUTO_CLONE=false; shift ;;
    --update) MODE="update"; shift ;;
    --check) MODE="check"; shift ;;
    --commit) DO_COMMIT=true; shift ;;
    --push) DO_COMMIT=true; DO_PUSH=true; shift ;;
    --repo) REPO_ROOT="$(cd "$2" && pwd)"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

[[ -d "$REPO_ROOT/.git" ]] || die "not a git repo: $REPO_ROOT (run git init or use --repo)"

resolve_kit() {
  local candidate=""
  if [[ -n "$KIT_PATH" ]]; then
    candidate="$KIT_PATH"
  elif [[ -n "${LEARNING_HUB_AGENT_KIT:-}" ]]; then
    candidate="$LEARNING_HUB_AGENT_KIT"
  elif [[ -f "$REPO_ROOT/../learning-hub-agent-kit/install.sh" ]]; then
    candidate="$(cd "$REPO_ROOT/../learning-hub-agent-kit" && pwd)"
  elif [[ -f "$KIT_CACHE/install.sh" ]]; then
    candidate="$KIT_CACHE"
  elif $AUTO_CLONE; then
    echo "Cloning kit to $KIT_CACHE ..."
    mkdir -p "$(dirname "$KIT_CACHE")"
    git clone --depth 1 "$KIT_URL" "$KIT_CACHE"
    candidate="$KIT_CACHE"
  else
    die "kit not found. Set LEARNING_HUB_AGENT_KIT, use --kit, clone sibling ../learning-hub-agent-kit, or allow auto-clone"
  fi
  [[ -f "$candidate/install.sh" ]] || die "invalid kit path (no install.sh): $candidate"
  echo "$candidate"
}

verify_install() {
  local missing=0
  local f
  for f in \
    .cursor/rules/git-safety.mdc \
    .cursor/skills/git-commit-push/SKILL.md \
    .cursor/hooks/block-secret-commit.sh \
    agentic-workflows/git-commit-push.md \
    .github/workflows/secret-scan.yml \
    "$MARKER"
  do
    if [[ -f "$REPO_ROOT/$f" ]]; then
      echo "  OK $f"
    else
      echo "  MISSING $f"
      missing=$((missing + 1))
    fi
  done
  if [[ "$MODULES" == *"infographics"* ]]; then
    for f in agentic-workflows/presync.yaml .cursor/skills/infographics-sync/SKILL.md; do
      if [[ -f "$REPO_ROOT/$f" ]]; then echo "  OK $f"; else echo "  MISSING $f"; missing=$((missing + 1)); fi
    done
  else
    [[ ! -f "$REPO_ROOT/agentic-workflows/presync.yaml" ]] && echo "  OK no presync.yaml (code repo)"
  fi
  [[ "$missing" -eq 0 ]] || die "$missing verification check(s) failed"
}

stage_adoption() {
  git -C "$REPO_ROOT" add \
    .cursor \
    agentic-workflows \
    gh-docs \
    .github \
    .learning-hub-agent-kit-version \
    .learning-hub-agent-kit-installed-at \
    .learning-hub-agent-kit-modules \
    .learning-hub-agent-kit-manifest
  if [[ -f "$REPO_ROOT/adopt-kit.sh" ]]; then
    git -C "$REPO_ROOT" add adopt-kit.sh
  fi
  if [[ "$MODULES" == *"infographics"* ]] && [[ -f "$REPO_ROOT/agentic-workflows/infographics-folder-map.yaml" ]]; then
    git -C "$REPO_ROOT" add agentic-workflows/infographics-folder-map.yaml
  fi
}

KIT="$(resolve_kit)"
INSTALL="$KIT/install.sh"
VERSION="$(cat "$KIT/VERSION" 2>/dev/null || echo unknown)"

echo "Repo:    $REPO_ROOT"
echo "Kit:     $KIT (v$VERSION)"
echo "Modules: $MODULES"
echo "Mode:    $MODE"
echo

case "$MODE" in
  check)
    "$INSTALL" --check --repo "$REPO_ROOT"
    exit 0
    ;;
  update)
    "$INSTALL" --update --repo "$REPO_ROOT" --modules "$MODULES"
    ;;
  install)
    "$INSTALL" --repo "$REPO_ROOT" --modules "$MODULES"
    ;;
esac

"$INSTALL" --check --repo "$REPO_ROOT"
echo
echo "Verification:"
verify_install

if $DO_COMMIT; then
  echo
  echo "Staging adoption files..."
  stage_adoption
  if git -C "$REPO_ROOT" diff --cached --quiet; then
    echo "Nothing to commit (already adopted?)."
  else
    git -C "$REPO_ROOT" commit -m "$(cat <<EOF
Adopt learning-hub-agent-kit v${VERSION} for Cursor git workflows.

Modules: ${MODULES}
EOF
)"
    echo "Committed."
  fi
  if $DO_PUSH; then
    unset GIT_ASKPASS SSH_ASKPASS
    export GIT_TERMINAL_PROMPT=1
    git -C "$REPO_ROOT" push -u origin HEAD
    echo "Pushed."
  fi
else
  echo
  echo "Next: review changes, then commit and push:"
  echo "  cd $REPO_ROOT"
  echo "  ./adopt-kit.sh --commit        # or --commit --push"
  echo "  # or manually: git add .cursor agentic-workflows gh-docs .github .learning-hub-agent-kit-* adopt-kit.sh"
fi

echo
echo "Done. Open repo in Cursor and try: \"Show workflows\""

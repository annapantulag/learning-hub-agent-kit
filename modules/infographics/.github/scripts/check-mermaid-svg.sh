#!/usr/bin/env bash
# Ensure every tracked .mmd has a paired .svg, and .mmd changes include .svg updates.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo_root"

missing=0
while IFS= read -r mmd; do
  svg="${mmd%.mmd}.svg"
  if [[ ! -f "$svg" ]]; then
    echo "::error file=$mmd::Missing paired SVG: expected $svg"
    missing=1
  fi
done < <(git ls-files '*.mmd')

if [[ "$missing" -ne 0 ]]; then
  echo "One or more .mmd files lack a sibling .svg."
  exit 1
fi

# On PR/push, require SVG updated when MMD changed (same basename, same directory).
base="${GITHUB_BASE_REF:-}"
if [[ -n "$base" ]]; then
  git fetch origin "$base" --depth=1 2>/dev/null || true
  diff_range="origin/${base}...HEAD"
else
  diff_range="${GITHUB_EVENT_BEFORE:-HEAD~1}..HEAD"
fi

if ! git rev-parse "$diff_range" >/dev/null 2>&1; then
  diff_range="HEAD~1..HEAD"
fi

stale=0
while IFS= read -r mmd; do
  svg="${mmd%.mmd}.svg"
  if ! git diff --name-only "$diff_range" -- "$svg" | grep -qx "$svg"; then
    echo "::error file=$mmd::.mmd changed but paired $svg was not updated in this change"
    stale=1
  fi
done < <(git diff --name-only "$diff_range" -- '*.mmd')

if [[ "$stale" -ne 0 ]]; then
  echo "Regenerate SVG from MMD (mmdc -i file.mmd -o file.svg) and commit both."
  exit 1
fi

echo "Mermaid sources have paired SVGs; changed .mmd files include .svg updates."

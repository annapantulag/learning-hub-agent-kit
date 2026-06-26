#!/usr/bin/env bash
# Detect mapped main folders (and candidate new folders) affected by git changes.
# Output: JSON on stdout — see agentic-workflows/infographics-sync.md
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo_root"

exec python3 "$repo_root/.github/scripts/detect-infographics-folders.py" "$@"

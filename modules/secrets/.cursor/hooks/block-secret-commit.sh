#!/usr/bin/env bash
# Block git commit when staged files match secret patterns (.gitignore-aligned).
# Cursor hook: beforeShellExecution — see .cursor/hooks.json

set -euo pipefail

input=$(cat)
command=$(printf '%s' "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('command', ''))")

# Only inspect git commit commands
if ! [[ "$command" =~ git[[:space:]]+commit ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

staged=$(git diff --cached --name-only 2>/dev/null || true)

if [[ -z "$staged" ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

blocked_files=()

is_blocked() {
  local f="$1"
  case "$f" in
    token.md|.env|.env.*|*.pem|*.key) return 0 ;;
    application_default_credentials.json) return 0 ;;
  esac
  [[ "$f" == *token*.md ]] && return 0
  [[ "$f" == *credentials*.json ]] && return 0
  [[ "$f" == *service-account*.json ]] && return 0
  [[ "$f" == .gcloud/* ]] && return 0
  return 1
}

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  if is_blocked "$file"; then
    blocked_files+=("$file")
  fi
done <<< "$staged"

if [[ ${#blocked_files[@]} -gt 0 ]]; then
  printf -v joined '%s, ' "${blocked_files[@]}"
  joined="${joined%, }"
  python3 -c 'import json, sys; print(json.dumps({"permission": "deny", "user_message": "Blocked git commit: staged files match secret patterns: " + sys.argv[1] + ". Unstage them first.", "agent_message": "Hook blocked git commit. See agentic-workflows/git-commit-push.md and .gitignore."}))' "$joined"
  exit 2
fi

echo '{ "permission": "allow" }'
exit 0

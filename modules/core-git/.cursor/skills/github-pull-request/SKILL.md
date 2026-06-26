---
name: github-pull-request
description: >-
  Create GitHub pull requests using gh CLI. Use when the user asks to create a
  PR only (not the full feature-branch flow). For branch suggest, approve,
  commit, push, and merge use git-feature-pr skill.
---

# GitHub pull request

Repo: detected at runtime — `gh repo view --json nameWithOwner -q .nameWithOwner` (fallback: parse `git remote get-url origin`). Default base: **`main`**

For full flow (suggest `feature/` branch, approval, merge gate): [git-feature-pr](../git-feature-pr/SKILL.md)

Branch naming: [agentic-workflows/branch-naming.md](../../../agentic-workflows/branch-naming.md)

## Prerequisites

- `gh auth status` must succeed
- On a `feature/<topic>` branch (create via git-feature-pr if on `main`)
- Changes committed

## Step 1 — Inspect (parallel)

```bash
git status
git diff
git branch -vv
git log main...HEAD --oneline
```

## Step 2 — Branch (if on main)

Suggest `feature/<topic>` and **wait for user approval** before:

```bash
git checkout main && git pull --rebase origin main
git checkout -b feature/<approved-topic>
```

## Step 3 — Push

```bash
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=1
git push -u origin HEAD
```

## Step 4 — Create PR

**Base:** `main` unless user explicitly names another base.

```bash
gh pr create --base main --title "..." --body "$(cat <<'EOF'
## Summary
- …

## Test plan
- [ ] …

EOF
)"
```

Return PR URL. Remind user to review PR diff; merge via [git-feature-pr](../git-feature-pr/SKILL.md) Step 8 (solo or team gate).

## Step 5 — Merge

Do **not** merge here unless user explicitly asks. If they do, use git-feature-pr Step 8 — solo: explicit request; team: `reviewDecision == APPROVED`.

## Constraints

- Branch names: `feature/<topic>` only
- PR base: `main` default
- **Solo:** merge on explicit user request after PR review
- **Team** (`.github/require-pr-approval`): require GitHub **Approve** from non-author

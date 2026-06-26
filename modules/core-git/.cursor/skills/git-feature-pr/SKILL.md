---
name: git-feature-pr
description: >-
  Ship changes via feature branch and pull request into main. Use when the user
  asks to ship via PR, branch and PR, feature branch workflow, or merge an
  approved PR. Branch names must start with feature/.
---

# Git feature branch → PR → merge

Repo: detected at runtime — `gh repo view --json nameWithOwner -q .nameWithOwner` (fallback: parse `git remote get-url origin`). Default PR base: **`main`**.

Full doc: [agentic-workflows/git-feature-pr.md](../../../agentic-workflows/git-feature-pr.md)  
Quality checks: [local-quality-checks.md](../../../agentic-workflows/local-quality-checks.md)  
Pre-commit sync: [presync.yaml](../../../agentic-workflows/presync.yaml)

## Triggers

| User says | Do |
|-----------|-----|
| "ship via PR", "branch and PR" | Steps 1–7 |
| "merge the PR" / "merge it" | Steps 8–9 only |
| "commit and push" (no PR mention) | Use [git-commit-push](../git-commit-push/SKILL.md) instead |

## Step 1 — Inspect (parallel)

```bash
git status
git diff
git log -5 --format='%s'
git branch -vv
```

## Step 2 — Suggest branch (wait for approval)

Propose `feature/<kebab-topic>` from the diff. **Stop** — do **not** run `git checkout -b` until the user approves.

**Prefer AskQuestion** when available (`allow_multiple: false`):

| Option id | Label |
|-----------|--------|
| `approve` | Approve `feature/<suggested-topic>` |
| `use-main` | Use main instead (switch to git-commit-push fast path) |
| `rename` | I'll type a different `feature/...` name |

If the user picks **rename**, ask for the new name in chat (or a follow-up question). If AskQuestion is unavailable, use plain text:

> Suggested branch: `feature/...` — approve, rename, or say *use main* for direct push.

- All PR-path branches **must** start with `feature/`
- If user gives a name without prefix, prepend `feature/`

## Step 3 — Branch from main

```bash
git checkout main
git pull --rebase origin main
git checkout -b feature/<approved-topic>
```

## Step 4 — Stage, content sync, quality checks, commit

Secret gate (same as git-commit-push). Pre-commit content sync: same as [git-commit-push](../git-commit-push/SKILL.md) Step 2.5 — run when [presync.yaml](../../../agentic-workflows/presync.yaml) exists.

HEREDOC commit message. See [commit-message-examples.md](../../../agentic-workflows/commit-message-examples.md).

```bash
git add <paths>
# presync detect_script from presync.yaml when present
bash .github/scripts/run-quality-checks.sh
git commit -m "$(cat <<'EOF'
Message here.

EOF
)"
```

Do **not** commit until quality checks pass. Fix failures, re-stage, re-run — [local-quality-checks.md](../../../agentic-workflows/local-quality-checks.md).

## Step 5 — Push

```bash
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=1
git push -u origin HEAD
```

Request `all` or `network`. Auto-review retry if blocked (rare on feature branches).

## Step 6 — Create PR

**Base branch:** `main` unless user explicitly named another base.

```bash
gh pr create --base main --title "..." --body "$(cat <<'EOF'
## Summary
- …

## Test plan
- [ ] …

EOF
)"
```

Return PR URL. Tell user to **review the PR diff** on GitHub; merge when they say *"merge the PR"* (solo) or after a reviewer **Approves** (team mode).

## Step 7 — Stop (until merge requested)

Do not merge automatically. Wait for user to review and ask to merge (solo) or for GitHub approval (team mode).

## Step 8 — Merge (only when user asks)

```bash
gh pr view --json reviewDecision,state,number,url,mergeable
```

**Always refuse** if `reviewDecision == CHANGES_REQUESTED` or PR is not mergeable.

**Team mode** — file `.github/require-pr-approval` exists:

- Require `reviewDecision == APPROVED` (non-author reviewer on GitHub)
- If not approved → refuse; tell user a collaborator must Approve

**Solo mode** (default, no marker file):

- GitHub cannot self-approve; **explicit user request to merge** = operator sign-off after reviewing the PR
- Proceed if PR is `OPEN`, `MERGEABLE`, and user asked to merge

Then:

```bash
gh pr merge --squash --delete-branch
git checkout main
git pull origin main
```

Use `--merge` or `--rebase` only if user requests.

## Step 9 — Verify

```bash
git status
git log -3 --oneline
```

Report PR URL, merge result, and branch state.

## Constraints

- Never merge without explicit user request
- **Solo mode:** merge on explicit user request after PR review (no GitHub self-approval)
- **Team mode** (`.github/require-pr-approval` exists): require `reviewDecision: APPROVED`
- Never auto-commit; user must have asked for this PR flow
- PR base: `main` default; other base only when user specifies
- Never force-push `main`

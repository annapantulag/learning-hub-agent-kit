---
name: git-commit-push
description: >-
  Commit and push changes to GitHub. Use when the user asks to commit, push,
  ship changes, sync to remote, or save work to GitHub.
---

# Git commit & push

## Quick reference

| User says | Do |
|-----------|-----|
| "commit" | Steps 1–5 only (includes 2.5 when `presync.yaml` exists) |
| "commit and push" / "ship it" | Steps 1–7 |
| presync `skip_phrase` (see Step 2.5) | Skip Step 2.5 |
| "create a PR" | [github-pull-request](../github-pull-request/SKILL.md) or full [git-feature-pr](../git-feature-pr/SKILL.md) |
| "ship via PR" | [git-feature-pr](../git-feature-pr/SKILL.md) |

Detailed docs: [agentic-workflows/git-commit-push.md](../../../agentic-workflows/git-commit-push.md)  
PR path: [agentic-workflows/git-feature-pr.md](../../../agentic-workflows/git-feature-pr.md)  
Commit style: [commit-message-examples.md](../../../agentic-workflows/commit-message-examples.md)  
Quality checks: [local-quality-checks.md](../../../agentic-workflows/local-quality-checks.md)  
Pre-commit sync: [presync.yaml](../../../agentic-workflows/presync.yaml)

## Step 1 — Inspect (parallel)

```bash
git status
git diff
git log -5 --format='%s'
```

## Step 2 — Secret gate

Do not stage: `token.md`, `*token*.md`, `.env`, `*credentials*.json`, `*service-account*.json`, `*.pem`, `*.key`, `.gcloud/`.

## Step 2.5 — Pre-commit content sync (optional)

If [agentic-workflows/presync.yaml](../../../agentic-workflows/presync.yaml) exists, read it and run the skill at `skill_path` (run `detect_script` first when set). Skip silently when the file is absent. User bypass: the file's `skip_phrase`.

## Step 3 — Quality checks (before commit)

After `git add`, run CI-equivalent checks **before** `git commit`. Do not commit until they pass.

```bash
bash .github/scripts/run-quality-checks.sh
```

Request `network` if `npx` needs it. On failure: fix reported files, re-stage, re-run. See [local-quality-checks.md](../../../agentic-workflows/local-quality-checks.md).

## Step 4 — Commit message

- 1–2 sentences; focus on **why**
- Match repo style — see [commit-message-examples.md](../../../agentic-workflows/commit-message-examples.md)
- Use HEREDOC:

```bash
git add <paths>
git commit -m "$(cat <<'EOF'
Message here.

EOF
)"
```

## Step 5 — Commit constraints

- No amend unless user rules allow
- Hook or quality check failed → fix and **new** commit, never amend failed commit
- Request `git_write` if sandbox blocks commit

## Step 6 — Push (only if user asked)

```bash
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=1
git push -u origin HEAD
```

Request `network` or `all` permissions. Auth help: [gh-docs/git-push-authentication.md](../../../gh-docs/git-push-authentication.md)

### Cursor Auto-review (push to `main`)

If the shell tool blocks the push with an **Auto-review** message (e.g. publishing to `main` needs explicit approval), **do not** change the push command or switch branches.

1. Tell the user Auto-review blocked the push and they will see an approval card.
2. Retry the **exact same** `git push` command with:
   - `request_smart_mode_approval: true`
   - `smart_mode_block_reason`: the **exact** Auto-review message text (copy verbatim)
   - Same `required_permissions` as the first attempt (`all` or `network`)
3. After the user approves, confirm with `git status`.

This is a Cursor safety gate, not a git auth failure — do not run PAT/askpass troubleshooting for Auto-review blocks.

Details: [agentic-workflows/git-commit-push.md](../../../agentic-workflows/git-commit-push.md#cursor-auto-review-push-to-main)

## Step 7 — Verify

```bash
git status
```

Report branch state and whether push succeeded.

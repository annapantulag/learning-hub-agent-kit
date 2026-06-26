# Git commit & push workflow

Detailed procedure for committing and pushing changes via the Cursor agent.

**Agent entry point:** [`.cursor/skills/git-commit-push/SKILL.md`](../.cursor/skills/git-commit-push/SKILL.md)  
**Safety rules:** [`.cursor/rules/git-safety.mdc`](../.cursor/rules/git-safety.mdc)

## Triggers

| User intent | Agent behavior |
|-------------|----------------|
| "Commit these changes" | Commit only; verify with `git status` |
| "Commit and push" / "Ship it" / "Push to GitHub" | Commit then push (current branch, often `main`) |
| "Ship via PR" / "Branch and PR" | [git-feature-pr skill](../.cursor/skills/git-feature-pr/SKILL.md) — `feature/` branch, PR to `main`; see [solo vs team merge](git-feature-pr.md#7--review-before-merge-solo-vs-team) |
| "Create a PR" | PR only via [github-pull-request skill](../.cursor/skills/github-pull-request/SKILL.md) |
| Normal coding / edits | **No** auto-commit |

## Workflow steps

### Step 1 — Inspect (parallel)

Run these in parallel before staging anything:

```bash
git status
git diff                    # staged + unstaged
git log -5 --format='%s'    # commit message style
```

Also check:

- Is the current branch tracking a remote?
- Are there untracked files that should be included or ignored?

### Step 2 — Secret & credential gate

**Never stage or commit:**

| Pattern | Reason |
|---------|--------|
| `token.md`, `*token*.md` | PATs / secrets |
| `.env`, `.env.*` | Environment secrets |
| `*credentials*.json`, `*service-account*.json` | GCP / API keys |
| `*.pem`, `*.key` | Private keys |
| `application_default_credentials.json`, `.gcloud/` | Local GCP auth |

These patterns are in [`.gitignore`](../.gitignore). If the user explicitly asks to commit a secret file, **refuse** and warn.

### Step 2.5 — Pre-commit content sync (optional)

When [presync.yaml](presync.yaml) exists, read it and run the skill at `skill_path` (run `detect_script` first when set) before quality checks. Skip silently when the file is absent. User bypass: the file's `skip_phrase`.

**This repo:** `presync.yaml` registers [infographics-sync](../.cursor/skills/infographics-sync/SKILL.md) — see [infographics-sync.md](infographics-sync.md) and [infographics-folder-map.yaml](infographics-folder-map.yaml).

For each affected folder: **bootstrap** (first time) or **incremental** (existing hub) per folder `AGENT-infographics.md`. If user adds a new folder to the map → **bootstrap infographics in the same session** (not map-only).

Generated content must support **deep learning and implementation** (study notes, decision trees, labs, coverage maps) — not checkbox artifacts. Stage generated files before Step 3.

### Step 3 — Quality checks (before commit)

After staging (`git add`), run the same checks as CI **before** `git commit`:

```bash
bash .github/scripts/run-quality-checks.sh
```

Do not commit until this passes. Fix reported issues, re-stage, and re-run. Full guide: [local-quality-checks.md](local-quality-checks.md).

### Step 4 — Draft commit message

Follow recent repo style — see [commit-message-examples.md](commit-message-examples.md) and `git log -5`:

**Good examples from this repo:**

```text
Rename cert hub to get-cert-gear-prof-de-gcp and add Cursor agent workflows.
Enhance learning hub with new Dataform resources and GitHub documentation.
Initial learning hub: cert prep, courses, Udemy Dataform checklist
```

**Format:**

- 1–2 sentences
- Summarize nature of change (docs, rename, feature, fix)
- Use HEREDOC for the commit command (avoids quoting issues)

```bash
git commit -m "$(cat <<'EOF'
Rename cert folder to get-cert-gear-prof-de-gcp and update cross-repo links.

EOF
)"
```

### Step 5 — Stage and commit

```bash
git add <relevant paths>
bash .github/scripts/run-quality-checks.sh
git commit -m "$(cat <<'EOF'
Your message here.

EOF
)"
```

**Agent constraints:**

- Run quality checks **after** `git add`, **before** `git commit` — see [local-quality-checks.md](local-quality-checks.md)
- Do **not** run `git commit --amend` unless all amend conditions in user rules are met
- Do **not** use `--no-verify` unless user explicitly requests
- Do **not** update `git config`
- If pre-commit hook fails, fix and create a **new** commit (never amend a failed commit)

### Step 6 — Push (only when asked)

Repository defaults:

| Setting | Value |
|---------|--------|
| Remote | `origin` — detect URL via `git remote get-url origin` |
| Repo | `gh repo view --json nameWithOwner -q .nameWithOwner` |
| Default branch | `main` |

**Cursor terminal auth fix** (macOS — required when askpass returns 401):

```bash
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=1
git push -u origin HEAD
```

When prompted:

- **Username:** GitHub username from `gh auth status` or remote URL
- **Password:** GitHub **PAT** (not account password)

Full troubleshooting: [gh-docs/git-push-authentication.md](../gh-docs/git-push-authentication.md)

**Push constraints:**

- Never `git push --force` to `main`/`master` unless user explicitly requests (warn if they do)
- Request `git_write` + `network` (or `all`) permissions for push from agent sandbox

### Cursor Auto-review (push to `main`)

Cursor **Auto-review** can block `git push` to `main` even when git auth and network permissions are fine. The agent terminal shows a message that publishing to `main` (or similar) **needs explicit approval**. This is intentional — not a bug and not a PAT/askpass problem.

**What the agent should do:**

1. Run the normal push (askpass unset, `required_permissions: ["all"]` or `["network"]`).
2. If Auto-review blocks it, explain briefly that the user must approve in the Cursor approval card.
3. Retry the **identical** push command with Smart Mode approval parameters:
   - `request_smart_mode_approval: true`
   - `smart_mode_block_reason`: paste the **exact** Auto-review block reason from the failed attempt
4. Do **not** modify the push command, remote, or branch on retry.
5. After approval, verify with `git status`.

**Verified:** Push `6fb0f66..28188d3` to `origin/main` succeeded after user approved the retry.

**When to use feature branches instead:** If you want review before `main` lands, use [git-feature-pr.md](git-feature-pr.md) — Auto-review on `main` is separate from that choice.

### GitHub PAT: workflow scope (`.github/workflows/`)

If push fails with:

```text
refusing to allow a Personal Access Token to create or update workflow
... without `workflow` scope
```

Add **Workflows: Read and write** to the fine-grained PAT (separate from **Actions**), clear stale keychain creds if needed, and push again. See [gh-docs/git-push-authentication.md](../gh-docs/git-push-authentication.md).

### Step 7 — Verify

```bash
git status
```

Confirm: clean working tree (or only intentional unstaged files), branch up to date with remote.

## Non-`main` branches

This skill works on **any branch** — commit and push use the current branch:

```bash
git push -u origin HEAD
```

| Situation | What to use |
|-----------|-------------|
| Already on `feature/...`, just commit + push | This skill (*"commit and push"*) |
| Start fresh → branch → PR → merge | [git-feature-pr.md](git-feature-pr.md) |
| Push to `main` | May trigger Cursor Auto-review — see below |

PR-path branches must be named `feature/<topic>` — see [branch-naming.md](branch-naming.md).

## Branch strategy

Default: commit directly to `main` for small doc changes. Use [git-feature-pr.md](git-feature-pr.md) for `feature/` branch + PR (base `main`; solo or team merge gates).

## Pull request workflow (related)

Full PR path: [git-feature-pr.md](git-feature-pr.md) and [`.cursor/skills/git-feature-pr/SKILL.md`](../.cursor/skills/git-feature-pr/SKILL.md).

PR-only (subset): [`.cursor/skills/github-pull-request/SKILL.md`](../.cursor/skills/github-pull-request/SKILL.md).

- Base branch: **`main`** unless user explicitly specifies another
- Merge: **solo** — review PR diff, then explicit *"merge the PR"* (GitHub cannot self-approve); **team** — non-author **Approve** on GitHub when `.github/require-pr-approval` exists — see [git-feature-pr.md §7](git-feature-pr.md#7--review-before-merge-solo-vs-team)

## Failure modes

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| Auto-review / "needs explicit approval" to push `main` | Cursor Smart Mode gate | Retry **same** `git push` with `request_smart_mode_approval: true` and exact `smart_mode_block_reason`; user approves in UI |
| `401` / `Authentication failed` | Cursor askpass | `unset GIT_ASKPASS SSH_ASKPASS`; see auth doc |
| `workflow` scope / update workflow rejected | PAT missing **Workflows** permission | Add **Workflows: Read and write** to fine-grained PAT (not just Actions); push again |
| `gh pr create` — Resource not accessible by PAT | PAT missing **Pull requests** permission | Add **Pull requests: Read and write**; `gh auth login` — see [prerequisites.md](prerequisites.md) |
| `Repository not found` (private repo) | Bad/missing credentials | Same as 401 — not a missing repo |
| `rejected (non-fast-forward)` | Remote has commits you lack | `git pull --rebase` (ask user first) |
| Pre-commit hook failure | Lint/format failed | Fix issues; **new** commit |
| Quality checks failed locally | markdown-lint, HTML links, Mermaid/SVG | Fix; re-run `bash .github/scripts/run-quality-checks.sh` — [local-quality-checks.md](local-quality-checks.md) |
| CI markdown-lint on PR | Same rules as local script | Fix locally before push next time |
| Sandbox blocked push | Missing network permission | Retry with `required_permissions: ["network"]` or `["all"]` |
| Empty commit attempt | No staged changes | Report to user; do not commit |

## What the agent will not do

- Commit without explicit user request
- Push without explicit user request (commit-only is valid)
- Commit secrets listed in `.gitignore`
- Force-push `main`
- Change git config
- Push to remote unless asked

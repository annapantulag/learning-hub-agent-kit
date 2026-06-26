# Prerequisites — agentic git workflow

One-time setup so the Cursor agent can commit and push reliably.

## Checklist

| # | Item | How to verify | Status |
|---|------|---------------|--------|
| 1 | Git repo with `origin` remote | `git remote -v` | Should show `annapantulag/learning-hub-gcp` |
| 2 | Default branch | `git branch --show-current` | Usually `main` |
| 3 | HTTPS or SSH auth working | `git push` or `gh auth status` | See auth doc below |
| 4 | Secrets gitignored | `git check-ignore -v token.md` | Should match `.gitignore` rule |
| 5 | `gh` CLI + PR PAT scopes | `gh auth status`; `gh pr list` | See [prerequisites.md](prerequisites.md) |
| 6 | Phase 1 files in repo | See [README.md](README.md) | `.cursor/rules`, `.cursor/skills` |

## Git remote

Expected configuration:

```text
origin  https://github.com/annapantulag/learning-hub-gcp.git (fetch)
origin  https://github.com/annapantulag/learning-hub-gcp.git (push)
```

Clone (new machine):

```bash
git clone https://github.com/annapantulag/learning-hub-gcp.git
cd learning-hub-gcp
```

## Authentication

### HTTPS (current setup)

1. Create a fine-grained GitHub PAT on `learning-hub-gcp` with at least:
   - **Contents: Read and write** — `git push` / `pull`
   - **Metadata: Read** — usually required
   - **Pull requests: Read and write** — `gh pr create`, `gh pr merge` (not needed for `git push` alone)
   - **Workflows: Read and write** — only if pushing `.github/workflows/` (see below)
2. First push from Cursor — if you see 401 / askpass errors:

   ```bash
   unset GIT_ASKPASS SSH_ASKPASS
   export GIT_TERMINAL_PROMPT=1
   git push -u origin main
   ```

3. Enter username `annapantulag` and PAT as password.
4. macOS keychain caches credentials for later pushes.

**Full guide:** [gh-docs/git-push-authentication.md](../gh-docs/git-push-authentication.md)

### SSH (alternative)

```bash
git remote set-url origin git@github.com:annapantulag/learning-hub-gcp.git
```

Requires SSH key added to GitHub → Settings → SSH keys. Avoids Cursor askpass issues entirely.

### GitHub CLI

```bash
brew install gh          # if needed
gh auth login
gh auth status
```

Used for `gh pr create`, `gh pr merge`, `gh repo view`, CI status — not strictly required for `git push`.

After changing PAT permissions, re-run `gh auth login -h github.com` so `gh` picks up the new scopes.

**PR merge gates (solo vs team):** [git-feature-pr.md §7](git-feature-pr.md#7--review-before-merge-solo-vs-team) — solo repos merge on explicit chat request after reviewing the PR; team repos add `.github/require-pr-approval` and branch protection.

## Secrets handling

**Never commit:**

- `token.md` (gitignored via `*token*.md` and `token.md`)
- `.env` files
- Service account JSON, PEM keys

Store PATs in:

- macOS Keychain (via successful HTTPS push), or
- Password manager — **not** in the repo

If a PAT was ever committed: revoke it on GitHub immediately and rotate.

## Cursor agent permissions

When the agent runs git from the sandbox:

| Command | Permission needed |
|---------|-------------------|
| `git status`, `diff`, `log` | Default |
| `git add`, `commit` | `git_write` |
| `git push`, `gh` API calls | `network` or `all` |

Approve network access when the agent requests it for push operations.

## Cursor Auto-review (push to `main`)

Pushes to `main` from the agent may be blocked by **Auto-review** until you approve in the Cursor UI. This is expected — not a PAT or askpass issue.

When the agent reports an Auto-review block, approve the retry card in chat. The agent retries the same `git push` with Smart Mode approval.

Details: [git-commit-push.md#cursor-auto-review-push-to-main](git-commit-push.md#cursor-auto-review-push-to-main) (in `agentic-workflows/`)

### GitHub PAT: workflow files

Pushing `.github/workflows/` requires **Workflows: Read and write** on your fine-grained PAT, in addition to **Contents**. **Actions** alone is not enough — Workflows is a separate permission in the token editor.

### GitHub PAT: pull requests

`gh pr create` / `gh pr merge` return `Resource not accessible by personal access token` if **Pull requests: Read and write** is missing. Add it in the token editor, then `gh auth login` again.

## Multiple repos / PATs

This learning hub uses one GitHub account (`annapantulag`). A single PAT scoped to all learning repos is simplest.

For different PATs per repo, see [Multiple repos and multiple PATs](../gh-docs/git-push-authentication.md#multiple-repos-and-multiple-pats) in the auth doc.

## Dataform vs this repo

| Repo | Purpose | Auth |
|------|---------|------|
| `learning-hub-gcp` | Docs, study notes, HTML hubs | Local `git push` PAT or SSH |
| Separate Dataform SQLX repo | Linked from GCP Dataform | PAT in Dataform UI — never commit |

See [udemy/dataform/README.md](../udemy/dataform/README.md).

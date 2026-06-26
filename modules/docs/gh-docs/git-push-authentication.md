# Git push authentication (HTTPS)

Resolved: **2025-06** — first push to `annapantulag/learning-hub-gcp`.

## Symptoms

```text
Missing or invalid credentials.
Error: Bad status code: 401
remote: Repository not found.
fatal: Authentication failed for 'https://github.com/annapantulag/learning-hub-gcp.git/'
```

Or earlier, without the 401 detail:

```text
remote: Repository not found.
fatal: repository 'https://github.com/annapantulag/learning-hub-gcp.git/' not found
```

## Root cause

Two separate issues can produce this:

1. **Cursor’s Git askpass** — the integrated terminal uses Cursor’s `askpass-main.js`, which often fails to prompt or sends invalid credentials (401).
2. **Private repo + bad auth** — GitHub returns **"Repository not found"** instead of "access denied" when credentials are missing or wrong. The repo exists; authentication failed.

Local setup was already correct:

- Remote: `https://github.com/annapantulag/learning-hub-gcp.git`
- Branch: `main` with a commit ready to push

## Resolution (what worked)

Run in the project directory **before** `git push`:

```bash
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=1
git push -u origin main
```

When prompted:

| Field | Value |
|-------|--------|
| Username | `annapantulag` |
| Password | **Personal Access Token (PAT)** — not your GitHub account password |

Successful output:

```text
To https://github.com/annapantulag/learning-hub-gcp.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

macOS **osxkeychain** then caches the credentials for `github.com`, so later pushes may not prompt again.

## Cursor Auto-review (not authentication)

If the **agent** runs `git push` and the command is blocked before it reaches GitHub — with a message that publishing to `main` needs **explicit approval** — that is **Cursor Auto-review** (Smart Mode), not a PAT or askpass problem.

**What you do:** Approve the retry in the Cursor approval card when the agent asks.

**What the agent does:** Retry the exact same push with Smart Mode approval parameters (documented in [agentic-workflows/git-commit-push.md](../agentic-workflows/git-commit-push.md#cursor-auto-review-push-to-main)).

Do **not** run the askpass unset steps below for Auto-review blocks — fix auth only when git returns `401` or credential errors.

## If it still fails

### Clear stale keychain entry

```bash
printf "host=github.com\nprotocol=https\n\n" | git credential-osxkeychain erase
```

Then push again with username + PAT.

### Verify the PAT

Fine-grained token must include:

- **Repository access:** `learning-hub-gcp` (or All repositories)
- **Contents:** Read and write
- **Pull requests:** Read and write — required for `gh pr create` / `gh pr merge` (not for `git push` alone)
- **Workflows:** Read and write — required when pushing `.github/workflows/` files (separate from **Actions**)

After changing PAT permissions, run `gh auth login -h github.com`. Full scope list: [agentic-workflows/prerequisites.md](../agentic-workflows/prerequisites.md).

### Push rejected: workflow without `workflow` scope

```text
! [remote rejected] main -> main (refusing to allow a Personal Access Token to create or update workflow
`.github/workflows/secret-scan.yml` without `workflow` scope)
```

**Cause:** Fine-grained PATs need **Workflows: Read and write** to create or change files under `.github/workflows/`. **Actions: Read and write** is a different permission and does **not** satisfy this check.

**Fix:**

1. GitHub → **Settings → Developer settings → Fine-grained tokens** → edit your token
2. Under **Repository permissions**, add **Workflows** → **Read and write** (keep **Contents** and **Metadata**)
3. Click **Update**
4. Erase keychain and push again with the same token (or regenerate if permissions were added after creation):

   ```bash
   printf "host=github.com\nprotocol=https\n\n" | git credential-osxkeychain erase
   unset GIT_ASKPASS SSH_ASKPASS
   export GIT_TERMINAL_PROMPT=1
   git push origin main
   ```

**Alternative:** Switch remote to SSH (`git@github.com:annapantulag/learning-hub-gcp.git`) — SSH keys are not subject to this PAT scope check.

### `gh pr create` — Resource not accessible by PAT

**Cause:** Fine-grained PAT missing **Pull requests: Read and write**.

**Fix:** Add **Pull requests → Read and write** in the token editor, then `gh auth login -h github.com`. See [agentic-workflows/prerequisites.md](../agentic-workflows/prerequisites.md).

Common mistakes: wrong scope, expired token, extra whitespace when pasting, using account password instead of PAT.

### Use macOS Terminal.app

If Cursor’s terminal still misbehaves, run the same commands in **Terminal.app** (outside Cursor).

### SSH (long-term alternative)

Generate a GitHub SSH key, add it to GitHub → Settings → SSH keys, then:

```bash
git remote set-url origin git@github.com:annapantulag/learning-hub-gcp.git
git push -u origin main
```

See [Multiple repos and multiple PATs](#multiple-repos-and-multiple-pats) below if you use different credentials per repo.

## Do you need this for every repo?

**Not per repo — per machine / terminal / credential store.**

| Situation | Need the `unset GIT_ASKPASS` fix again? |
|-----------|----------------------------------------|
| Another push to `learning-hub-gcp` in the same terminal session after a successful push | **No** — credentials are cached |
| New terminal in Cursor after a successful HTTPS push | **Maybe not** — keychain may already have valid creds |
| First push from Cursor and you see 401 / askpass errors | **Yes** — run the unset commands |
| New repo on same GitHub account, same PAT, same machine | **Usually no** — one PAT + keychain entry covers all repos the token can access |
| Different GitHub account or different PAT per repo | **See below** — may need per-URL credentials or SSH |

The fix addresses **how the terminal authenticates**, not something unique to `learning-hub-gcp`.

## Multiple repos and multiple PATs

### One PAT, many repos (recommended for personal learning)

Use a single fine-grained PAT with:

- **All repositories**, or
- **Only select repositories** listing every repo you need (`learning-hub-gcp`, `learning-hub-dataform`, …)

One successful HTTPS push stores credentials for `github.com` in the keychain. All repos that PAT can access work with the same cached login.

### Different PAT per repo

macOS keychain typically stores **one** username/password pair per `github.com` host. If repo A uses PAT-1 and repo B uses PAT-2, the second push can overwrite or reuse the wrong token.

**Options:**

1. **One PAT to rule them all** — simplest; scope it to all learning repos.
2. **Per-repo HTTPS credentials** — enable path-specific storage:

   ```bash
   git config --global credential.useHttpPath true
   ```

   Then each `https://github.com/owner/repo.git` URL gets its own keychain entry. Push each repo once and enter the correct PAT when prompted.

3. **SSH per identity** — different SSH keys and `~/.ssh/config` `Host` aliases (e.g. `github.com-work` vs `github.com-personal`). Most reliable for multiple GitHub accounts.
4. **Separate PAT for Dataform only** — paste that token in **GCP Dataform → Link GitHub**; it does not have to be the same PAT you use for local `git push`, as long as each token has **Contents: Read and write** on the target repo.

### Dataform vs local git

| Use | Token | Where it lives |
|-----|-------|----------------|
| Local `git push` / `pull` | PAT (or SSH) | macOS keychain or SSH agent |
| GCP Dataform ↔ GitHub | PAT (can be different) | GCP Dataform repository settings — never commit to git |

## Security

- **Never commit tokens** — no `token.md`, `.env`, or PATs in the repo.
- `token.md` is listed in `.gitignore`; use a password manager instead.
- Revoke and recreate a PAT if it was exposed or committed by mistake.

## Related

- [agentic-workflows/git-commit-push.md](../agentic-workflows/git-commit-push.md) — full push workflow, Auto-review, workflow PAT scope
- [udemy/dataform/README.md](../udemy/dataform/README.md) — Dataform setup and PAT permissions for GCP
- [README.md](../README.md) — learning hub overview

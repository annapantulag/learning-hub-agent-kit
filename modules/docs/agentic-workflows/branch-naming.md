# Branch naming

How the Cursor agent handles branches in `learning-hub-gcp`.

## Two paths

| Path | Branch | Chat trigger |
|------|--------|--------------|
| **Fast** — direct to `main` | `main` | *"commit and push"* |
| **PR** — review before merge | `feature/<topic>` | *"ship via PR"*, *"branch and PR"* |

PR path details: [git-feature-pr.md](git-feature-pr.md)

## Default: commit directly to `main`

Personal learning hub — small doc edits often go straight to `main`.

| Situation | Branch |
|-----------|--------|
| Study notes, README tweaks | `main` |
| Agent workflow scaffolding (solo) | `main` |

## PR path: `feature/` branches only

When using [git-feature-pr](git-feature-pr.md), **all** branch names must start with `feature/`:

```text
feature/<short-kebab-description>
```

| Example | When |
|---------|------|
| `feature/dataform-sec-3-cli` | Udemy Dataform sec-3 docs |
| `feature/cert-mod-05-etl-notes` | Cert study notes |
| `feature/agent-workflow-update` | `.cursor/` or `agentic-workflows/` changes |

**Rules:**

- Prefix is always `feature/` (not `docs/`, `feat/`, `fix/`, `chore/`)
- Lowercase, hyphens only, no spaces
- Keep under ~50 characters total
- No username or date in the name

## Branch name approval (PR path)

The agent **must not** create a branch until you approve the name.

1. Agent inspects `git diff` and proposes: `feature/<topic>`
2. Agent shows **AskQuestion** when available:
   - **Approve** — use suggested name
   - **Use main instead** — switch to fast path ([git-commit-push](git-commit-push.md))
   - **Rename** — you type a different `feature/...` name in chat
3. Without AskQuestion, same choices via plain text (*yes*, *rename to `feature/...`*, *use main*)
4. Agent runs `git checkout -b <approved-name>`

**Example chat (AskQuestion):**

> Agent: [Approve `feature/dataform-sec-3-cli` | Use main | Rename]  
> You: Approve  
> Agent: creates branch, commits, pushes, opens PR…

## Agent commands

### Direct to `main` (fast path)

```bash
git checkout main
git pull --rebase origin main   # if behind
# commit …
git push origin main
```

### Feature branch + PR

```bash
git checkout main && git pull --rebase origin main
git checkout -b feature/<approved-topic>
# commit …
git push -u origin HEAD
gh pr create --base main ...
```

**Base branch:** always `main` unless you explicitly say another base (e.g. *"PR against `develop`"*).

## Merge after PR (solo vs team)

| Mode | When | What you do |
|------|------|-------------|
| **Solo** (default) | Only you on the repo | Review PR diff → say *"merge the PR"* — GitHub cannot self-approve |
| **Team** | `.github/require-pr-approval` exists | Non-author **Approve** on GitHub → say *"merge the PR"* |

Details: [git-feature-pr.md §7](git-feature-pr.md#7--review-before-merge-solo-vs-team)

## Protected branch rules

- Never `git push --force` to `main` unless you explicitly request (agent warns)
- Prefer `git pull --rebase origin main` before branching when remote is ahead

## Related

- [git-commit-push.md](git-commit-push.md) — fast path
- [git-feature-pr.md](git-feature-pr.md) — branch → PR → merge
- [`.cursor/skills/git-feature-pr/SKILL.md`](../.cursor/skills/git-feature-pr/SKILL.md)

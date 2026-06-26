# Agent git workflow (index)

Short index for Cursor agents searching under `gh-docs/`. Full documentation lives in [`agentic-workflows/`](../agentic-workflows/).

## Quick links

| Topic | Doc |
|-------|-----|
| Overview & chat triggers | [agentic-workflows/README.md](../agentic-workflows/README.md) |
| Workflow menu (pick from list) | [agentic-workflows/workflow-picker.md](../agentic-workflows/workflow-picker.md) |
| Fast path — commit & push `main` | [agentic-workflows/git-commit-push.md](../agentic-workflows/git-commit-push.md) |
| PR path — `feature/` → PR → merge | [agentic-workflows/git-feature-pr.md](../agentic-workflows/git-feature-pr.md) |
| Commit message style | [agentic-workflows/commit-message-examples.md](../agentic-workflows/commit-message-examples.md) |
| Branch naming (`feature/`) | [agentic-workflows/branch-naming.md](../agentic-workflows/branch-naming.md) |
| Push auth (401 / askpass) | [git-push-authentication.md](git-push-authentication.md) |
| Auto-review / push to main | [agentic-workflows/git-commit-push.md#cursor-auto-review-push-to-main](../agentic-workflows/git-commit-push.md#cursor-auto-review-push-to-main) |
| Architecture & new workflows | [agentic-workflows/architecture.md](../agentic-workflows/architecture.md) |
| CI (secret scan) | [agentic-workflows/github-actions.md](../agentic-workflows/github-actions.md) |
| Local checks before commit | [agentic-workflows/local-quality-checks.md](../agentic-workflows/local-quality-checks.md) |
| Pre-commit infographics sync | [agentic-workflows/infographics-sync.md](../agentic-workflows/infographics-sync.md) |
| Folder map (user) / state (agent) | [infographics-folder-map.yaml](../agentic-workflows/infographics-folder-map.yaml) · [infographics-folder-state.yaml](../agentic-workflows/infographics-folder-state.yaml) |
| Rollout phases | [agentic-workflows/phases.md](../agentic-workflows/phases.md) |
| Prerequisites | [agentic-workflows/prerequisites.md](../agentic-workflows/prerequisites.md) |

## Cursor config (repo root)

| File | Role |
|------|------|
| `.cursor/rules/git-safety.mdc` | Always-on safety; no auto-merge |
| `.cursor/skills/workflow-picker/SKILL.md` | List available workflows; user picks one |
| `.cursor/skills/git-commit-push/SKILL.md` | Commit / push (any branch; fast `main`) |
| `.cursor/skills/infographics-sync/SKILL.md` | Pre-commit learning infographics for mapped folders |
| `.cursor/skills/git-feature-pr/SKILL.md` | `feature/` branch → PR (`main`) → merge (solo or team gate) |
| `.cursor/skills/github-pull-request/SKILL.md` | PR creation only |
| `.cursor/hooks/block-secret-commit.sh` | Block secret commits (hook) |

## Chat triggers

| Say | Skill |
|-----|-------|
| *"Show workflows"* / *"What can I do?"* | workflow-picker |
| *"Commit and push"* | git-commit-push |
| *"Sync infographics"* | infographics-sync |
| *"Skip infographics this commit"* | git-commit-push / git-feature-pr (skip Step 2.5) |
| *"Ship via PR"* / *"Branch and PR"* | git-feature-pr |
| *"Merge the PR"* | git-feature-pr (solo: explicit request; team: needs GitHub Approve) |
| *"Create a pull request"* | github-pull-request or git-feature-pr |

## PR defaults

- Branch prefix: **`feature/`**
- PR base: **`main`** (other base only if user specifies)
- Merge: **solo** — explicit user request after PR review; **team** — GitHub **Approve** from non-author (see `.github/require-pr-approval`)

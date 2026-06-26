# Rollout phases

Incremental plan for agentic workflows in `learning-hub-gcp`.

## Phase 1 — Minimum viable workflow ✅

**Goal:** Safe, repeatable commit & push from Cursor chat.

**Delivered:**

| Artifact | Path |
|----------|------|
| Safety rule | `.cursor/rules/git-safety.mdc` |
| Commit/push skill | `.cursor/skills/git-commit-push/SKILL.md` |
| Documentation | `agentic-workflows/` |

**Verified:** Commit `28188d3` — fresh chat session committed and pushed successfully.

---

## Phase 2 — Hardening ✅

**Goal:** Richer context and consistency without adding automation complexity.

**Delivered:**

| Artifact | Path |
|----------|------|
| Commit message examples | `agentic-workflows/commit-message-examples.md` |
| Branch naming | `agentic-workflows/branch-naming.md` |
| PR skill (create only) | `.cursor/skills/github-pull-request/SKILL.md` |
| Full PR path skill | `.cursor/skills/git-feature-pr/SKILL.md` |
| PR path doc | `agentic-workflows/git-feature-pr.md` |
| Agent git index | `gh-docs/agent-git-workflow.md` |
| Root / gh-docs links | Done in Phase 1 |

---

## Phase 3 — Optional enforcement & automation

### 3a — Secret-commit hook ✅

| Artifact | Path |
|----------|------|
| Hook config | `.cursor/hooks.json` |
| Block script | `.cursor/hooks/block-secret-commit.sh` |

**Test:** Stage `token.md` (if present locally), run `git add token.md && git commit -m test` in agent — hook should deny.

**Note:** Restart Cursor or save `hooks.json` if hook does not load; check **Hooks** output channel.

### 3b — Cursor Automations ✅ closed (deferred)

Ideas and setup guide: [cursor-automation.md](cursor-automation.md). **Not configured** — revisit when you need scheduled or event-driven runs without chat.

### 3c — GitHub Actions ✅ (minimal) + 📋 future

| Artifact | Path |
|----------|------|
| Secret scan CI | `.github/workflows/secret-scan.yml` |
| Future workflows doc | `agentic-workflows/github-actions.md` |

Link check, Mermaid/SVG pairing, and scoped markdown lint run in [quality-checks.yml](../.github/workflows/quality-checks.yml).

---

## Phase summary

| Phase | Status | Value |
|-------|--------|-------|
| 1 | ✅ Done | Daily commit/push from chat |
| 2 | ✅ Done | Message style, branches, PR skills + docs |
| 3a | ✅ Done | Hard block on secret commits (agent) |
| 3b | ✅ Closed (deferred) | Ideas in [cursor-automation.md](cursor-automation.md); enable when scheduled tasks needed |
| 3c | ✅ Done | Secret scan + quality checks (links, Mermaid/SVG, scoped markdown lint) |
| D | ✅ Done | Pre-commit infographics sync + folder tracking + workflow hub |

**Next:** Core agentic git/PR + infographics phases complete. Revisit Phase 3b/3c backlog only when automations or extra CI are needed — see [cursor-automation.md](cursor-automation.md) and [github-actions.md](github-actions.md).

---

## Phase C — PR path ✅

**Goal:** End-to-end `git-feature-pr` — branch, PR, solo merge, squash to `main`.

| Step | Status | Test |
|------|--------|------|
| 1 | ✅ | *"Ship via PR"* on agent workflow docs |
| 2 | ✅ | Agent suggested `feature/git-feature-pr-workflow` — approved |
| 3 | ✅ | PR #1 created with `--base main` |
| 4 | ✅ | Solo/team merge gates documented |
| 5 | ✅ | PR #1 squash-merged to `main` (`17080e4`) |

**Delivered:**

| Artifact | Path |
|----------|------|
| PR path doc | `agentic-workflows/git-feature-pr.md` |
| PR skill | `.cursor/skills/git-feature-pr/SKILL.md` |
| Solo vs team merge | README, git-feature-pr, prerequisites, git-safety |
| Updated branch naming | `agentic-workflows/branch-naming.md` |
| Updated routing | `agentic-workflows/README.md`, `git-commit-push.md` |
| Agent index | `gh-docs/agent-git-workflow.md` |
| Architecture + checklist | `agentic-workflows/architecture.md` |

---

## Discovery — workflow picker ✅

**Goal:** Users choose a workflow from a menu instead of memorizing trigger phrases.

| Artifact | Path |
|----------|------|
| Picker skill | `.cursor/skills/workflow-picker/SKILL.md` |
| Guide | `agentic-workflows/workflow-picker.md` |

**Test:** Fresh chat → *"show workflows"* → pick *"commit and push"* or *"ship via PR"* → agent runs the matching skill.

---

## Phase D — Pre-commit infographics sync ✅

**Goal:** Before commit, sync learning infographics for mapped main folders; track hub status for the next agent run.

| Artifact | Path |
|----------|------|
| Sync workflow doc | `agentic-workflows/infographics-sync.md` |
| Folder map (user) | `agentic-workflows/infographics-folder-map.yaml` |
| Folder state (agent) | `agentic-workflows/infographics-folder-state.yaml` |
| Detection script | `.github/scripts/detect-infographics-folders.sh` |
| Sync skill | `.cursor/skills/infographics-sync/SKILL.md` |
| Wired into commit/PR | `git-commit-push` Step 2.5 · `git-feature-pr` Step 4 |
| Workflow learning hub | `agentic-workflows/learning-hub.html` |
| Folder AGENT docs | `*/AGENT-infographics.md` per mapped folder |

**Test:** Change under `agentic-workflows/` → *commit* → detect → incremental sync → quality checks. Infra-only change under `gh-docs/` → skip sync silently.

**Next:** Core agentic git/PR + infographics phases complete. Revisit Phase 3b/3c backlog only when automations or extra CI are needed — see [cursor-automation.md](cursor-automation.md) and [github-actions.md](github-actions.md).

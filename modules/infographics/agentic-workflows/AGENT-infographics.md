---
name: agentic-workflows-infographics
description: >-
  Turns agentic-workflows documentation into learning infographics: workflow decision
  trees, skill maps, Mermaid diagrams, study notes, and learning-hub HTML so users
  can learn and implement Cursor git/PR workflows in this repo.
---

# Agentic Workflows — Infographics Agent Instructions

> **Canonical path:** `AGENT-infographics.md`  
> **Hub:** [learning-hub.html](learning-hub.html) (bootstrap in Step 4)  
> **Parent workflow:** [infographics-sync.md](infographics-sync.md)

---

## Purpose

This folder documents **how to work with Cursor agents** in `learning-hub-gcp`. Infographics must turn that prose into a **go-to guide** so a reader can:

- **Understand** rules vs skills vs docs vs hooks vs CI — and when each runs
- **Decide** commit-to-main vs ship-via-PR vs infographics-sync vs skip
- **Implement** first-time setup (PAT, `gh`, quality checks) and recover from auth/CI failures

Every artifact must help someone **learn deeply and ship safely** — not duplicate README tables without judgment or traps.

---

## Repo structure (target)

```text
agentic-workflows/
├── AGENT-infographics.md          # this file
├── learning-hub.html              # single entry hub
├── infographics-folder-map.yaml   # mapped main folders
├── infographics-sync.md           # pre-commit sync workflow
├── sources/*.mmd + *.svg          # workflow diagrams
├── study-notes/
│   ├── 00-brief.md
│   ├── 00-coverage-map.md
│   └── NN-<concept>.md
├── README.md                      # index (source)
├── git-commit-push.md             # source
├── git-feature-pr.md              # source
├── architecture.md                # source
├── workflow-picker.md             # source
├── prerequisites.md               # source
└── local-quality-checks.md        # source
```

**Browse:** `learning-hub.html` · Map: [infographics-folder-map.yaml](infographics-folder-map.yaml)

---

## Source inputs

| Source doc | Infographic focus |
|------------|-------------------|
| [README.md](README.md) | Quick start decision: which path? |
| [architecture.md](architecture.md) | Layers diagram; skills vs rules vs hooks |
| [git-commit-push.md](git-commit-push.md) | Commit flow incl. infographics Step 2.5 |
| [git-feature-pr.md](git-feature-pr.md) | PR path; solo vs team merge gates |
| [workflow-picker.md](workflow-picker.md) | Discovery menu flow |
| [infographics-sync.md](infographics-sync.md) | Pre-commit learning artifact sync |
| [prerequisites.md](prerequisites.md) | One-time setup checklist |
| [local-quality-checks.md](local-quality-checks.md) | CI-equivalent checks before commit |
| [branch-naming.md](branch-naming.md) | `feature/` naming rules |

Cross-links (not owned here): [gh-docs/git-push-authentication.md](../gh-docs/git-push-authentication.md)

---

## Three-layer model

```text
agentic-workflows/*.md → sources/*.mmd + study-notes/
                       → learning-hub.html
```

---

## Phases A–E (folder root)

### Phase A — Parse

1. Read changed workflow `.md` files end-to-end.
2. **`study-notes/00-brief.md`**: 3–5 objectives, key triggers (*"commit and push"*, *"ship via PR"*), failure modes to memorize, diagram candidates.
3. **`study-notes/00-coverage-map.md`**: each workflow doc section → ✅ diagram/note/hub panel or ❌ gap.

### Phase B — Diagrams

Priority diagrams (create or refresh when source changes):

| # | Concept | Type |
|---|---------|------|
| 01 | Which shipping path? | Decision tree: main vs PR vs PR-only |
| 02 | Cursor layers | Flow: rule → skill → doc → hook → CI |
| 03 | Commit pipeline | Flow: inspect → secrets → infographics → quality → commit → push |
| 04 | PR pipeline | Flow: branch → commit → `gh pr create` → review → merge |
| 05 | Workflow picker | Discovery: show workflows → pick → run skill |
| 06 | Infographics sync | Pre-commit: detect → bootstrap/incremental → SVG → stage |

- Header:

  ```text
  %% Agentic workflows — <title>
  %% Source: agentic-workflows/<file>.md
  %% Hub panel: #<panel-slug>
  ```

- Colors: navy `#0B1F3A`; green `#2E7D5B`; amber `#E8A317`; red `#C0392B`.
- Export SVG: `npx @mermaid-js/mermaid-cli -i sources/NN-<concept>.mmd -o sources/NN-<concept>.svg`

### Phase C — Study notes

Per `study-notes/NN-<concept>.md`:

- In one minute
- From the workflow doc (paraphrased)
- Must know before you ask the agent to ship
- Common traps (401, Auto-review, workflow PAT scope, amend after hook fail)
- Commands to remember
- Teach it in 2 minutes

### Phase D — Implementation guides

For setup-heavy topics (prerequisites, quality checks), include **numbered implementation paths** in study notes or hub panels — not just “see prerequisites.md”.

Example traps to always cover:

- Commit only when asked (no auto-commit)
- Never commit `token.md` / credentials
- Auto-review on push to `main` ≠ auth failure
- Quality checks run **after** infographics sync, **before** commit

### Phase E — Hub sync

**`learning-hub.html`** (reuse shared UI from cert prep when bootstrapping):

- Link `../get-cert-gear-prof-de-gcp/docs/shared/learning-hub.{css,js}` or copy pattern from [udemy/dataform/learning-hub.html](../udemy/dataform/learning-hub.html)
- Sidebar: How to use · Workflows · Diagrams · Retain · Troubleshooting · Source docs
- Retain panels `#note-<concept>` synced with study notes
- Link every `agentic-workflows/*.md` source from hub

---

## Incremental vs bootstrap

| Mode | Agent action |
|------|--------------|
| **Bootstrap** | Full diagram set (01–06), coverage map, all core study notes, hub |
| **Incremental** | Match changed `.md` to diagram + note + hub panel; update `00-coverage-map.md` |

When `infographics-sync.md` or `infographics-folder-map.yaml` changes, refresh diagram **06** and commit-flow note.

---

## Quality checklist

- [ ] Decision trees include **when not to** use a path (e.g. when PR is required)
- [ ] Failure modes from git-commit-push / git-feature-pr appear in retain panels
- [ ] Every `.mmd` has sibling `.svg`
- [ ] `00-coverage-map.md` covers all workflow docs listed in README map
- [ ] Hub is navigable with Live Server — learner does not hunt scattered `.md` files
- [ ] No secrets or PAT examples with real values

---

## Anti-patterns

- Do not copy README quick-start tables into hub without adding judgment and traps
- Do not create diagrams that only list skill filenames (use decision flows)
- Do not document infographics sync without linking folder map and quality bar
- Do not mark workflow “done” with sidebar-only hub updates

---

*Agent instructions for agentic-workflows learning infographics.*

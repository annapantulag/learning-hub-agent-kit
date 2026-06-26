---
name: workflow-picker
description: >-
  List available agent workflows and skills in this repo so the user can choose
  what to do without remembering trigger phrases. Use when the user asks what
  workflows are available, what they can do, to show options, pick a workflow,
  workflow menu, or help getting started with agentic workflows.
---

# Workflow picker

Help the user **discover and choose** a workflow — do not run a git or content workflow until they pick one.

Full doc: [agentic-workflows/workflow-picker.md](../../../agentic-workflows/workflow-picker.md)

## Step 1 — Discover (parallel)

Scan repo-local skills and reference docs:

```bash
find .cursor/skills -name SKILL.md 2>/dev/null | sort
find . -path './.git' -prune -o -path '*/.cursor/skills/*/SKILL.md' -print 2>/dev/null | grep -v '^\./\.cursor/' | sort
ls -1 agentic-workflows/*.md 2>/dev/null
```

For each `SKILL.md`, read the YAML frontmatter (`name`, `description`) only — do not load full procedure yet.

**Categorize:**

| Category | Path pattern | Examples |
|----------|--------------|----------|
| **Repo-wide workflows** | `.cursor/skills/*/SKILL.md` | git-commit-push, git-feature-pr |
| **Topic-scoped workflows** | `*/.cursor/skills/*/SKILL.md` (not under repo-root `.cursor/`) | gcp-pde-infographics |
| **Reference docs** | `agentic-workflows/*.md` (no matching skill) | prerequisites, architecture |

Skip `workflow-picker` itself from the runnable list (you are already in it). Include it in a footnote as *"show workflows again"*.

## Step 2 — Present menu

Group options under short headings. For each **skill**, show:

- **Label:** human title from skill `name` (title case, hyphens → spaces)
- **One line:** first sentence of `description`
- **Say this:** shortest natural trigger (from skill doc or README quick start)

Prefer the **AskQuestion** tool when available — one question, `allow_multiple: false`, options = runnable skills only (not reference-only docs).

If AskQuestion is unavailable, use a numbered markdown list the user can reply to with a number or name.

Always add a final option: **"Something else / I'll describe it"** — then ask in plain language what they want.

## Step 3 — Run chosen workflow

When the user picks (or names) an option:

1. Read the full `SKILL.md` for that workflow
2. Follow it step by step
3. If they picked a **reference doc** only (e.g. prerequisites), open/summarize that doc and ask whether they want to run a related skill next

Do not commit, push, branch, or merge unless the chosen workflow's skill instructs it **and** the user has confirmed through that workflow's normal gates.

## Quick fallback (if discovery fails)

Offer these repo-wide defaults from [agentic-workflows/README.md](../../../agentic-workflows/README.md):

| # | Workflow | Trigger |
|---|----------|---------|
| 1 | Commit & push to `main` | *"Commit and push"* |
| 2 | Ship via PR (`feature/` branch) | *"Ship via PR"* |
| 3 | Create PR only | *"Create a pull request"* |
| 4 | Show setup / prerequisites | *"Help me set up git for this repo"* |

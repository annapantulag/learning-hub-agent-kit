# Commit message examples

Style guide for `learning-hub-gcp` — derived from recent `git log` on `main`.

The agent should read this (or `git log -5`) before drafting a message.

## Conventions

| Aspect | This repo |
|--------|-----------|
| Format | Full sentences — **not** required to use Conventional Commits (`feat:`, `fix:`) |
| Length | 1–2 sentences in the subject; optional body for context |
| Focus | **Why** the change matters, not a file list |
| Tone | Clear, descriptive — like a short changelog entry |
| HEREDOC | Always pass the message via HEREDOC in shell (see [git-commit-push.md](git-commit-push.md)) |
| PR path | Larger or reviewable changes → `feature/...` branch via [git-feature-pr.md](git-feature-pr.md) |

## Real examples from this repo

### Rename / restructure

```text
Rename cert hub to get-cert-gear-prof-de-gcp and add Cursor agent workflows.

Aligns the PDE cert folder with repo naming conventions, updates cross-links
in Udemy Dataform and gh-docs, and documents commit/push rules and skills
for the learning hub.
```

**Why it works:** Subject states the main action; body explains impact without listing every file.

### Large docs / content addition

```text
Enhance learning hub with new Dataform resources and GitHub documentation.
```

Single sentence is fine when the diff is broad but thematically one change (Dataform + gh-docs in one pass).

### Initial / milestone

```text
Initial learning hub: cert prep, courses, Udemy Dataform checklist
```

Short label-style subject works for bootstrap commits.

## Templates by change type

### Documentation only

```text
Add agentic-workflows docs and Phase 2 commit/PR skills.

Documents branch naming, commit style, and GitHub PR workflow for Cursor agents.
```

### Infographic / study notes (PR path: `feature/...` branch)

```text
Add mod-05 ETL study notes and Dataflow Beam diagram for cert prep.

Covers transcript sections on batch pipelines and Apache Beam model for PDE exam review.
```

### Cross-link / fix

```text
Fix broken links to cert hub after folder rename.

Updates udemy/dataform learning-hub.html paths to get-cert-gear-prof-de-gcp.
```

### Agent workflow / tooling

```text
Add secret-commit hook and docs CI workflow.

Blocks agent git commit when staged files match token or credential patterns.
```

## Anti-patterns (avoid)

| Bad | Why |
|-----|-----|
| `update files` | No context |
| `fix stuff` | Not actionable |
| `WIP` | Not descriptive |
| `feat: add README` | Conventional prefix not used in this repo |
| Listing 20 filenames in the subject | Use body or rely on git diff |

## Agent checklist

Before committing:

1. Run `git log -5 --format='%s'`
2. Match sentence style and length of recent commits
3. Subject ≤ ~72 characters when possible (soft limit)
4. Omit `Co-authored-by` unless the user requests it

---
name: infographics-sync
description: >-
  Sync learning infographics for mapped main folders before commit. Detects changed
  folders from git diff, bootstraps or updates hubs, diagrams, and study notes.
  Use when user commits, asks to sync infographics, or mapped folders changed.
---

# Infographics sync

## Quick reference

| User says | Do |
|-----------|-----|
| *(part of commit)* | Run Steps 1–6 when mapped/candidate folders in diff |
| *"Sync infographics"* | Steps 1–6 only |
| *"Skip infographics this commit"* | Skip — hand off to quality checks |

Full doc: [agentic-workflows/infographics-sync.md](../../../agentic-workflows/infographics-sync.md)  
Folder map: [agentic-workflows/infographics-folder-map.yaml](../../../agentic-workflows/infographics-folder-map.yaml)

## Purpose (non-negotiable)

Infographics must support **deep learning** and **implementation** — decision trees, study notes with traps, labs with *why*, coverage maps, and a go-to `learning-hub.html`. Do not create artifacts for their own sake.

## Step 1 — Detect

```bash
bash .github/scripts/detect-infographics-folders.sh
```

Parse JSON: if `skip_sync` is `true`, hand off to quality checks. Otherwise process `affected[]` and prompt on `candidates[]`. Report `placeholder_touched[]` once without syncing.

**Always read `folder_registry[]`** for hub_status and agent_note before deciding scope — even when only infra paths changed.

## Step 2 — New unmapped folders

If candidates exist → **AskQuestion**:

- **Add and bootstrap** — update map, scaffold AGENT doc, full infographics, stage
- **Skip this commit** — continue without map change

Adding to map **must** include bootstrap infographics in the same session.

## Step 3 — Per affected folder

Read `agent_doc` (and `skill` if set) from [infographics-folder-map.yaml](../../../agentic-workflows/infographics-folder-map.yaml).

Each `affected[]` entry has `mode`:

| Mode | Action |
|------|--------|
| `bootstrap` | Entire folder per AGENT doc |
| `incremental` | Changed subpaths only |

Placeholder folders never appear in `affected[]` — they are listed under `placeholder_touched[]`. Report those once and do not sync.

## Step 4 — Export SVGs

```bash
npx @mermaid-js/mermaid-cli -i <file>.mmd -o <file>.svg
```

## Step 5 — Quality check (infographics)

Before staging, verify: coverage map updated, retain panels match notes, every `.mmd` has `.svg`, content grounded in source material.

## Step 6 — Stage and update state

```bash
git add <generated paths>
```

Update [infographics-folder-state.yaml](../../../agentic-workflows/infographics-folder-state.yaml) (`diagram_count`, `expected_sync_mode`, `last_sync_commit`). If bootstrap finished, set `hub_status: complete` in [infographics-folder-map.yaml](../../../agentic-workflows/infographics-folder-map.yaml).

Hand off to [git-commit-push](../git-commit-push/SKILL.md) Step 3 (quality checks).

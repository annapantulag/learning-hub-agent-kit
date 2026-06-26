# learning-hub-agent-kit

Shared Cursor agentic workflows — git safety, commit/push, feature-PR, secrets, and optional learning infographics.

Single source of truth extracted from [learning-hub-gcp](https://github.com/annapantulag/learning-hub-gcp). Install into any repo with `install.sh`.

**GitHub:** [annapantulag/learning-hub-agent-kit](https://github.com/annapantulag/learning-hub-agent-kit)

## Modules

| Module | Purpose |
|--------|---------|
| `core-git` | Rules + skills: git-safety, commit/push, feature-PR, PR, workflow-picker |
| `secrets` | Commit-blocking hook + secret-scan CI |
| `docs` | Generic `agentic-workflows/` + `gh-docs/` reference |
| `infographics` | Optional pre-commit learning artifacts (learning repos only) |

## Quick start

```bash
git clone https://github.com/annapantulag/learning-hub-agent-kit.git
cd learning-hub-agent-kit

# Code repo
./install.sh --repo /path/to/repo --modules core-git,secrets,docs

# Learning repo (adds infographics + presync.yaml)
./install.sh --repo /path/to/repo --modules core-git,secrets,docs,infographics
```

After install, commit the copied files in the target repo. Learning repos must customize `infographics-folder-map.yaml` (copy from `infographics-folder-map.example.yaml`).

**Adoption guide:** [modules/docs/agentic-workflows/adopt-learning-hub-agent-kit.md](modules/docs/agentic-workflows/adopt-learning-hub-agent-kit.md) — step-by-step for any repo (solo, team, code, learning).

## Commands

```bash
./install.sh --repo <path> --modules core-git,secrets,docs
./install.sh --repo <path> --modules core-git,secrets,docs,infographics
./install.sh --check --repo <path>
./install.sh --update --repo <path> --modules core-git,secrets,docs
./install.sh --global   # core-git skills/rules/hooks → ~/.cursor (docs links not rewritten yet)
```

## Version

See [VERSION](VERSION). Consumers get `.learning-hub-agent-kit-version` after install.

## Status

- **0.1.2** — Add [adopt-learning-hub-agent-kit.md](modules/docs/agentic-workflows/adopt-learning-hub-agent-kit.md) adoption guide (Phase 7 team setup included).
- **0.1.1** — Fix `--global` install paths (`~/.cursor/skills`, `rules`, `hooks`); hook command rewritten for global layout.
- **0.1.0** — Phase 2 scaffold: modules populated from learning-hub-gcp; `install.sh` supports `--repo`, `--check`, `--update`, `--global` (basic).

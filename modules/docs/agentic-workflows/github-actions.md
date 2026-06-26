# GitHub Actions (CI)

Server-side checks on push and pull requests. Complements Cursor agent workflows — does **not** replace commit/push from chat.

**Run the same checks locally before commit:** [local-quality-checks.md](local-quality-checks.md) · `bash .github/scripts/run-quality-checks.sh`

## What runs today

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Secret scan | [`.github/workflows/secret-scan.yml`](../.github/workflows/secret-scan.yml) | `push`, `pull_request` | Fail if forbidden secret filenames are tracked in git |
| Quality checks | [`.github/workflows/quality-checks.yml`](../.github/workflows/quality-checks.yml) | `push`, `pull_request` | HTML link check, Mermaid/SVG pairing, scoped markdown lint |

### Quality checks (detail)

| Job | Script / tool | What it enforces |
|-----|---------------|------------------|
| **html-links** | [`.github/scripts/check-html-links.py`](../.github/scripts/check-html-links.py) | Relative `href` in tracked `learning-hub.html` files resolve to real files |
| **mermaid-svg** | [`.github/scripts/check-mermaid-svg.sh`](../.github/scripts/check-mermaid-svg.sh) | Every tracked `.mmd` has sibling `.svg`; if `.mmd` changes in a PR, `.svg` must change too |
| **infographics-integrity** | [`.github/scripts/check-infographics-integrity.py`](../.github/scripts/check-infographics-integrity.py) | Folder map ↔ state ↔ filesystem aligned (`agent_doc`, `hub_status`, placeholder rules) |
| **markdown-lint** | [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) + [`.markdownlint-cli2.yaml`](../.markdownlint-cli2.yaml) | Lint `agentic-workflows/`, `gh-docs/`, `.cursor/skills/`, root `README.md` |

All three jobs call [`.github/scripts/run-quality-checks.sh`](../.github/scripts/run-quality-checks.sh) — the same script agents and humans run locally before commit.

### Local (before commit)

```bash
bash .github/scripts/run-quality-checks.sh
```

See [local-quality-checks.md](local-quality-checks.md). Agent commit/PR skills require this **after** infographics sync (when applicable), **after** `git add`, **before** `git commit`.

### Infographics sync + Mermaid CI

When [infographics-sync](infographics-sync.md) adds or updates `.mmd` files, export sibling `.svg` before commit:

```bash
npx @mermaid-js/mermaid-cli -i path/to/diagram.mmd -o path/to/diagram.svg
```

The **mermaid-svg** CI job **fails** the PR if a tracked `.mmd` changed without a matching `.svg` update in the same change. That is the hard gate — run `bash .github/scripts/run-quality-checks.sh mermaid-svg` locally after infographics work to avoid a failed PR.

| Layer | Behavior |
|-------|----------|
| Agent (pre-commit) | infographics-sync exports SVG + stages both files |
| Local script | `check-mermaid-svg.sh` — error if missing pair or stale SVG on changed `.mmd` |
| GitHub Actions | Same script on `pull_request` — blocks merge until fixed |

Regenerate SVG locally after editing Mermaid:

```bash
npx -p @mermaid-js/mermaid-cli mmdc -i path/to/diagram.mmd -o path/to/diagram.svg
```

## Secret scan workflow

Blocks commits that accidentally add files matching `.gitignore` secret patterns:

- `token.md`, `*token*.md`
- `.env`, `.env.*`
- `*credentials*.json`, `*service-account*.json`
- `*.pem`, `*.key`

This mirrors the Cursor hook [`.cursor/hooks/block-secret-commit.sh`](../.cursor/hooks/block-secret-commit.sh) at CI time.

## Backlog — optional later

| Workflow | Status | Revisit when |
|----------|--------|--------------|
| Markdown lint on all study notes | 📋 Optional | Multiple contributors or frequent doc PRs |
| Lychee external URL check | 📋 Optional | GitHub Pages live with external links |

## Enabling GitHub Actions

1. Push `.github/workflows/` to `main`
2. Repo → **Actions** tab → enable workflows if prompted
3. Private repos: Actions minutes apply on free tier

Pushing workflow files requires **Workflows: Read and write** on your fine-grained PAT — see [prerequisites.md](prerequisites.md).

## Agent interaction

- The Cursor agent can **read** workflow results via `gh run list` / `gh pr checks`
- Fixing CI failures: user asks in chat; agent fixes files and commits (commit skill)

## Related

- [git-commit-push.md](git-commit-push.md)
- [git-feature-pr.md](git-feature-pr.md) — PRs run CI on `pull_request`
- [phases.md](phases.md) — Phase 3c

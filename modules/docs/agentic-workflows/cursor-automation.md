# Cursor Automations (optional)

Scheduled or event-driven agent runs **without** you in chat. Separate from the commit/push **skill** used in day-to-day work.

## Status — deferred (Phase 3b)

| Item | Status |
|------|--------|
| Automations in this repo | **Not configured** — ideas documented below only |
| Why deferred | Chat + skills cover daily commit/push and PR; automations add ops overhead without a current need |
| When to revisit | You want scheduled audits (e.g. weekly uncommitted notes) or Slack-triggered summaries without opening Cursor |

No action required until you explicitly ask to create an automation (e.g. *"Create a Cursor automation for …"*).

---

## Learn now (documentation map — no implementation required)

Read in this order to understand how Automations fit this repo **before** you create one.

| Step | Doc | What you learn |
|------|-----|----------------|
| 1 | [architecture.md § Layers](architecture.md#layers) | Automations = layer 5; how they differ from skills, rules, hooks, GitHub Actions |
| 2 | [architecture.md § Cursor Automations](architecture.md#cursor-automations) | File format (editor UI, not repo YAML); when **not** to use for daily git |
| 3 | **This file** — [Example ideas](#example-ideas-for-this-repo) | Concrete prompts for *this* learning hub |
| 4 | [Cursor Automations product docs](https://cursor.com/docs/agent/automations) | Triggers (cron, git, Slack), cloud vs local runtime |
| 5 | Personal skill `~/.cursor/skills-cursor/automate/SKILL.md` | Step-by-step **creation** flow when you are ready (Agents Window required) |

### How Automations compare to what you already have

| Mechanism | Runs when | Best for |
|-----------|-----------|----------|
| **Chat + skill** | You ask in Cursor | Commit, push, PR — [git-commit-push.md](git-commit-push.md), [git-feature-pr.md](git-feature-pr.md) |
| **Rule** | Every agent session | Safety — [git-safety.mdc](../.cursor/rules/git-safety.mdc) |
| **Hook** | Before agent shell commands | Block secret commits — [block-secret-commit.sh](../.cursor/hooks/block-secret-commit.sh) |
| **GitHub Actions** | Push / PR on GitHub | CI — [github-actions.md](github-actions.md) |
| **Cursor Automation** | Schedule or event (no chat) | Weekly audits, post-push summaries, Slack triggers |

### When you are ready to implement (checklist)

Use this later — **not needed today**.

1. **Prerequisites**
   - [Cloud Agents](https://cursor.com/dashboard?tab=cloud-agents) if using cloud runtime
   - `gh` CLI or GitHub MCP for git/PR triggers
   - Files referenced in prompts must be **committed** on the branch the automation checks out

2. **Open the editor**
   - Cursor → **Automations** (requires Agents Window)
   - Or in chat: *"Create a Cursor automation for …"* (loads the automate skill)

3. **Define four fields**
   - **Trigger** — cron, git push, PR opened, Slack message, etc.
   - **Tools** — repo read, `gh`, optional MCP (Slack, Linear, …)
   - **Prompt** — plain-language instructions; include *"Do not commit unless I reply commit and push"*
   - **Name** — short label in the Automations list

4. **Test**
   - Run once manually from the editor
   - Confirm it does not auto-commit (align with [git-safety.mdc](../.cursor/rules/git-safety.mdc))

5. **Document** (optional)
   - Add a row to the [Example ideas](#example-ideas-for-this-repo) table below with what you created

---

## When to use

| Use Automations | Use chat + skill instead |
|-----------------|--------------------------|
| Weekly reminder to review uncommitted study notes | "Commit and push" after a session |
| On PR opened: summarize diff for review | Creating the PR yourself |
| Slack: "summarize mod-05 progress" on demand | One-off questions in Cursor |

## When not to use

- Routine commits to `main` — use [git-commit-push skill](../.cursor/skills/git-commit-push/SKILL.md)
- Anything requiring your approval on every file — chat is safer

## Example ideas for this repo

### 1. Weekly study-notes audit (cron)

**Trigger:** Every Sunday 9:00  
**Prompt:** List uncommitted changes under `get-cert-gear-prof-de-gcp/` and `udemy/dataform/`. Summarize what topics were touched. Do not commit unless I reply "commit and push".

### 2. Post-push link sanity (git push to main)

**Trigger:** Git push on `learning-hub-gcp`  
**Prompt:** For any `learning-hub.html` changed in the last commit, list internal `href` targets and flag paths that do not exist in the repo.

### 3. Slack study ping (slackTrigger)

**Trigger:** Message in `#learning-hub` containing "weekly recap"  
**Prompt:** Read latest commits on `main` and summarize cert prep progress.

## How to create (when ready)

1. Open **Cursor → Automations** (Agents Window required)
2. In chat: *"Create a Cursor automation for …"* — follows the **automate** skill (`~/.cursor/skills-cursor/automate/SKILL.md`)
3. Or configure manually in the editor: trigger → tools (`gh`, read repo) → prompt

Automations YAML is internal; you describe behavior in plain language in the editor.

## Prerequisites

See [Learn now § When you are ready to implement](#when-you-are-ready-to-implement-checklist) above.

## Related

- [architecture.md](architecture.md) — layer 5 (Automations vs skills)
- [phases.md](phases.md) — Phase 3b status

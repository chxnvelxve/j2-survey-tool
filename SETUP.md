# Codex QA kit — one-time setup (LOG-AI-01, Windows)

## What this does
At the end of each phase you push as normal. The push runs lint + build, then
Codex reviews the diff and writes `QA-REPORT.md`. Small stuff Codex fixes itself;
anything it disagrees with or that's big gets escalated to you, and the push is
blocked until you look. Your next action is always the last line of the report.

## 0. Prereqs (once per machine)
- Codex CLI installed and signed in with your ChatGPT Pro account
  (this uses your plan, not a per-token API key).
  Verify: `codex --version` and `codex login` if needed.
- Node + pnpm available in the same shell.

## 1. Drop these files into the repo root
```
AGENTS.md
QA-REPORT.md            <- created automatically on first run; safe to gitignore
.codex/config.toml
scripts/codex-qa.sh
.githooks/pre-push
PASTE-PROMPT.md
```

## 2. Point git at the hooks folder + make scripts executable
Run once inside the repo:
```
git config core.hooksPath .githooks
git add scripts/codex-qa.sh .githooks/pre-push
git update-index --chmod=+x scripts/codex-qa.sh
git update-index --chmod=+x .githooks/pre-push
```
On Windows, run the hook via Git Bash (installed with Git for Windows). The
shebang lines make it work there. If you push from PowerShell and the hook
doesn't fire, do your end-of-phase push from the Git Bash shell.

## 3. Gitignore the report (optional but recommended)
Add to `.gitignore`:
```
QA-REPORT.md
```
It's a scratch artifact for you, not something main needs.

## 4. Normal workflow from now on
1. Cursor builds the phase.
2. You tell Cursor to add/commit as you already do.
3. `git push`  ← hook fires here.
   - 🟢 PASS  → push goes through. Done.
   - 🔧 FIXED → push blocked once; commit Codex's small fixes, push again.
   - 🟡 NEEDS-HUMAN → push blocked; open QA-REPORT.md, answer the questions,
     paste the "If you agree, tell Codex" line back to Codex, re-run.

Emergency bypass (skips QA): `git push --no-verify`.

## 5. Reusing this as a master across projects
Copy `AGENTS.md`, `.codex/`, `scripts/`, `.githooks/`, `PASTE-PROMPT.md` into any
new repo, then re-run the two commands in step 2. Nothing in the kit is
survey-app-specific. Tweak the `pnpm` commands in `codex-qa.sh` only if a repo
uses npm or yarn instead.

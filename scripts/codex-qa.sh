#!/usr/bin/env bash
# codex-qa.sh — run local gates, then hand the diff to Codex for review.
# Exit 0 = safe to push. Exit 1 = stop and read QA-REPORT.md.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT" || exit 1

echo "──────────────────────────────────────────"
echo " QA gate: pytest before Codex review"
echo "──────────────────────────────────────────"

FAILED=0

# lint/build: no pnpm or ruff script in this Python repo — skip (not fail)
echo "lint: skip (no pnpm/ruff configured)"
echo "build: skip (no frontend build step)"

# Prefer `python`, fall back to Windows `py` launcher (Git Bash on Windows).
if command -v python >/dev/null 2>&1 && python -c "import sys" >/dev/null 2>&1; then
  python -m pytest -q || FAILED=1
elif command -v py >/dev/null 2>&1; then
  py -m pytest -q || FAILED=1
else
  echo "❌ Neither usable python nor py found for pytest."
  FAILED=1
fi

if [ "$FAILED" -ne 0 ]; then
  echo "❌ Local gates failed. Fix in Cursor first — not sending to Codex yet."
  echo "   (Push blocked. Nothing was sent to Codex.)"
  exit 1
fi

echo "✅ Local gates passed. Sending diff to Codex for QA review..."

# What Codex reviews: everything since the last pushed commit on this branch.
# Falls back to last commit if no upstream is set yet.
RANGE="@{push}..HEAD"
git rev-parse "@{push}" >/dev/null 2>&1 || RANGE="HEAD~1..HEAD"

PROMPT="Review the changes in this range: ${RANGE}.
Follow AGENTS.md exactly. Run the checks, classify findings into Category A
(fix silently) or Category B (stop and escalate), and write QA-REPORT.md at the
repo root using the required structure. Do not push, commit, or touch main."

# Non-interactive Codex run (codex-cli 0.142+).
# approval_policy via -c: --ask-for-approval was removed from newer CLIs.
# Project .codex/config.toml also sets these; -c makes the hook self-contained.
# Close stdin so non-interactive/hook runs don't hang on "Reading additional input…".
# Fail closed if Codex itself errors (do not fall through to a stale QA-REPORT.md).
codex exec \
  -c approval_policy=never \
  --sandbox workspace-write \
  "$PROMPT" </dev/null
if [ $? -ne 0 ]; then
  echo "⚠️  Codex review failed. Blocking push so you can look."
  exit 1
fi

# Decide pass/block from the verdict Codex wrote.
if [ ! -f QA-REPORT.md ]; then
  echo "⚠️  Codex did not produce QA-REPORT.md. Blocking push so you can look."
  exit 1
fi

echo ""
echo "──────── QA-REPORT.md (top) ────────"
head -n 20 QA-REPORT.md
echo "────────────────────────────────────"

if grep -q "VERDICT: NEEDS-HUMAN" QA-REPORT.md; then
  echo "🟡 Codex needs a decision from you. Push BLOCKED."
  echo "   Open QA-REPORT.md — your next action is at the bottom."
  exit 1
fi

if grep -q "VERDICT: FIXED" QA-REPORT.md; then
  echo "🔧 Codex made small fixes. Review + 'git add -A && git commit --amend' or a new commit,"
  echo "   then push again. Push BLOCKED once so the fixes get committed."
  exit 1
fi

echo "🟢 VERDICT: PASS — push allowed."
exit 0

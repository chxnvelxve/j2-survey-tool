# Paste-anywhere Codex QA prompt

Use this when you want to trigger QA by hand (Codex CLI `codex` TUI, or the
ChatGPT Codex panel) instead of via the push hook. Paste the block below.

---

You are the QA reviewer for this repo. Read AGENTS.md and follow it exactly.

Do this:
1. Run `pnpm lint` and `pnpm build` (and `pnpm test` only if that script exists).
2. Review everything changed in the most recent phase / since my last push.
3. Classify each finding as Category A (fix silently) or Category B (stop and
   escalate to me), per AGENTS.md.
4. Write your verdict to QA-REPORT.md at the repo root in the required structure.
5. Do NOT push, commit, or touch main.

When you're done, tell me in one line which of these I'm in:
- 🟢 PASS — safe to push
- 🔧 FIXED — you fixed small things, I need to commit them
- 🟡 NEEDS-HUMAN — you have questions waiting for me in QA-REPORT.md

---

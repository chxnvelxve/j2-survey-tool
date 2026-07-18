---
project: j2-survey-tool
artifact: engineering_artifacts_map
status: implemented
last_updated: 2026-07-18
sensitivity: internal_log
---

# Engineering Artifacts — J2 Survey Tool

Thin contract map for builders and QA. This is **not** the operator handoff.

## Canonical pointers

| Role | Path |
|---|---|
| Status index | `docs/PROJECT_STATUS.md` |
| Live operator / build truth | `docs/handoff.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Decisions / blockers | `docs/DECISIONS.md` |
| Build-phase history (`needs_review`) | `docs/PHASES.md` — prefer handoff for current truth |
| This map | `docs/ENGINEERING_ARTIFACTS.md` |
| Agent entry | `CLAUDE.md` |
| Prior QA artifact (root) | `QA-REPORT.md` (latest on file: PASS 2026-07-12) |

## Work packet / completion / QA

**Project-local paths** (J2):

| Artifact | Path | Naming |
|---|---|---|
| Work packets | `docs/work-packets/` | `WP-YYYY-NNN-*.md` |
| Completion summaries | `docs/completions/` | `CS-YYYY-NNN-*.md` |
| QA reports | `docs/qa/` | `QA-YYYY-NNN-*.md` |

**Field / shape authority** (do not fork templates casually):

- `C:\LOG\00_Command\ai-organization\organization\shared\templates\WORK_PACKET.md`
- `C:\LOG\00_Command\ai-organization\organization\shared\templates\COMPLETION_SUMMARY.md`
- `C:\LOG\00_Command\ai-organization\organization\shared\templates\QA_REPORT.md`
- `C:\LOG\00_Command\ai-organization\organization\shared\standards\ARTIFACT_CONTRACT.md`

Same required fields as org templates; paths are project-local.

New formal QA reports go under `docs/qa/`. Keep root `QA-REPORT.md` as historical latest unless/until founder consolidates.

## Tool lanes

| Lane | Role on J2 |
|---|---|
| Cursor | Primary builder |
| Claude Code | Architecture / complex work as needed |
| Codex | QA (`QA-REPORT` pattern); CI runs `ruff` + `pytest` on `main` |

## Branch and human approval

- Default engineering branch: **`main`**.
- Confirm working branch before commit (topic branches such as `meeting-prep` may be active).
- Human approval required for merge/push/deploy/destructive actions.
- Product activation (Phases 8/9/10) stays blocked on Josh assets — do not invent client inputs.

## Fresh-builder read order

1. `docs/PROJECT_STATUS.md`
2. `docs/ENGINEERING_ARTIFACTS.md` (this file)
3. `docs/handoff.md` — live post-UAT truth
4. Approved work packet under `docs/work-packets/` when assigned
5. `CLAUDE.md` for stack, design rules, and Cursor workflow

## Fresh-QA read order

1. Approved work packet (`docs/work-packets/`)
2. Completion summary (`docs/completions/`)
3. Diff / commit range named in the completion summary
4. `docs/handoff.md` + `CLAUDE.md` non-negotiables
5. Write `docs/qa/QA-YYYY-NNN-*.md` when a formal report is required (root `QA-REPORT.md` remains prior evidence)

---
project: j2-survey-tool
status: partially_implemented
last_updated: 2026-07-18
sensitivity: internal_log
inventory: observed_path_not_fully_reverified_2026-07-18
cos_baseline: PR-2026-001 accepted
engineering_artifacts: docs/ENGINEERING_ARTIFACTS.md
---

# Project Status — J2 Survey Tool

## Purpose

Automate field AP photo capture → Ekahau `.esx` ingestion → client-ready Word report for J2 Communications; engine kept brandable for re-license.

## Current Phase

**v1 build + operator handoff largely done** (UAT PASS 2026-07-08 on sample fixtures). Phases **8 / 9 / 10 are shells** waiting on Josh assets for live activation.  
`docs/PHASES.md` marked `needs_review` for next-step planning — prefer `docs/handoff.md` + this status.

## Last Completed Milestone

- **P4-J2-1 / WP-2026-002** — J2 engineering artifact foothold (status/artifact map, WP/CS/QA paths, light `CLAUDE.md` / `PHASES.md` reconcile).
- Phase 7 UAT against sample fixtures — **PASS** (2026-07-08); Tailscale URL + local prod-like compose.
- Operator handoff docs for Josh (branding, template swap, Nextcloud, Phase 8/9/10 activation runbooks).
- Latest root QA report on file: **PASS** (2026-07-12).

## Active Work

None. WP-2026-002 implemented (docs-only). Activation work remains **blocked on external assets**.

## Next Milestone

When Josh delivers assets: activate Phase 8 (real `.esx`), 9 (template/brand polish), 10 (Nextcloud) per handoff runbooks — one phase at a time.

## Blockers

Locked on Josh / J2:

- Real `.esx` export  
- Gold-standard Word sample deliverable  
- Nextcloud URL + app password  
- (Related) real brand logo/hex  

## Decisions Needed

- Billing fork: second 50% on deploy + UAT (sample data) vs waiting on Phase 8/9/10 — open in `docs/DECISIONS.md` / handoff; **business confirm with Josh**.

## Primary Builder

Cursor (Claude for architecture / complex work as needed).

## QA Lane

Codex / `QA-REPORT.md` pattern + `docs/qa/` going forward; CI runs `ruff` + `pytest` on `main`.

## Canonical Files

| Role | Path |
|---|---|
| Operator handoff | `docs/handoff.md` |
| Decisions / blockers | `docs/DECISIONS.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Phase plan (history; `needs_review`) | `docs/PHASES.md` |
| This status | `docs/PROJECT_STATUS.md` |
| Engineering artifacts | `docs/ENGINEERING_ARTIFACTS.md` |
| Work packets | `docs/work-packets/` |
| Completions | `docs/completions/` |
| QA reports | `docs/qa/` (root `QA-REPORT.md` = prior latest) |
| Agent entry | `CLAUDE.md` |

## Risks

- Residual drift risk until `PHASES.md` is fully rewritten or formally superseded (banner + status pointers mitigate for now).
- Silent assumptions in `.esx` schema until real file arrives (Phase 8).
- Do not ingest day-job / NDA material into LOG or Command Vault.

## Next Human Action

1. Confirm billing split with Josh when convenient (business).  
2. Park product engineering until Josh assets arrive.  
3. Merge/cherry-pick WP-2026-002 docs onto `main` when ready (landed on active topic branch if not on `main`).

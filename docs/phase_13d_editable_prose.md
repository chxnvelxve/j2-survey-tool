# Phase 13d — Editable DRAFTED prose  ⚙️(change-order — post-v1 polish)

Continues Phase 12 / [`STATUS_FOR_NEXT_PHASES.md`](STATUS_FOR_NEXT_PHASES.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) · [`DECISIONS.md`](DECISIONS.md) win.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Optional polish — build only on an explicit change-order.** Not required for v1
acceptance: the v1 assumption is that DRAFTED sections are human-written *after*
download (edit the `.docx` directly — zero code). This phase moves that editing
**into the app** so the human prose is captured per-Job before generation.

## Included vs change-order ⚙️
**Recommend: change-order.** v1's DRAFTED contract already ships (fixed placeholder
prose in `context.py`, editable in Word post-download). In-app editable fields are a
convenience upgrade, not a gap in the fixed-fee scope. Small (~one migration + one
HTMX form), but out-of-scope until J2 asks. Do **not** build speculatively.

## Goal
Let the Drafter edit the three DRAFTED sections — `exec_summary`,
`scope_methodology`, `findings` — on a Job before generation, persist them, and feed
them into the rendered `.docx`. Empty falls back to the current placeholder. **No
change to the frozen context keys.**

## Scope
- Add three nullable text columns to `Job` (`exec_summary`, `scope_methodology`,
  `findings`) via a new Alembic migration (0008).
- HTMX edit form on the Job detail view (three textareas; save without full reload),
  available to the Drafter hat before the generate gate.
- `context.py` prefers the Job value when non-empty, else the existing placeholder —
  so the **top-level key inventory in [`template_map.md`](template_map.md) is
  unchanged** and the contract test keeps passing.
- No RF math, no auto-authoring. This is human prose capture only (Findings stays
  DRAFTED — machine-graded findings are the parked RF-math item).

## Non-negotiables honored
Merge/parse/generate contracts untouched; frozen `docxtpl` keys unchanged; branding
stays in config. Phone remains capture-only (this is a Drafter-side desktop edit).

## Done when
- Drafter can edit the three prose sections on a Job and save (HTMX, no full reload).
- Saved values render into the generated `.docx`; empty falls back to placeholder.
- Migration 0008 applies cleanly up/down; contract test + CI green.

## Depends on
Nothing external. ⚙️ Change-order approval only. Reads best after
[Phase 13b](phase_13b_template_brand_activation.md) so the editable voice matches the
gold template — but not a hard dependency.

## Blockers
- ⚙️ Change-order sign-off (out of fixed-fee scope).
- None technical.

## Files likely touched
- `app/models/` (Job columns) · `alembic/versions/0008_*.py`
- `app/api/jobs.py` (save endpoint) · `app/templates/` (Job detail edit partial)
- `app/services/generator/context.py` (prefer Job value over placeholder)
- `tests/` (fallback + persistence tests)

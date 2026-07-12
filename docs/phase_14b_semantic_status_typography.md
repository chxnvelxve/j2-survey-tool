# Phase 14b — Semantic status colors + AP identifier typography  (unblocked)

Continues [Phase 14](phase_14_ui_tokens.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) wins. Legend: 🔒 Josh · 🟡 placeholder · ⚙️ decision.

**Unblocked. Depends on Phase 14 tokens existing.** Component-level visual pass —
still **no layout/IA restructuring**. Applies the design system to the two highest
impact-per-line recommendations from the review: semantic status signaling on the
jobs list, and monospace AP identifiers app-wide.

## Goal
Make job status scannable at a glance and make AP names read as machine identifiers,
using only the Phase 14 tokens plus a small status→color mapping in the templates.

## Scope — in
- **AP-identifier mono treatment:** define `.ap-id { font-family: var(--font-mono);
  font-weight: var(--weight-medium); letter-spacing: 0.02em; }` and apply the class
  wherever an AP name renders — parsed AP list, photos list, merged results, override
  audit, flag detail, capture AP-name display.
- **Jobs list semantic status (on cards, not a table):** map each `job.status` to a
  `--status-*` pair via a Jinja macro or dict, then:
  - add `border-left: 4px solid var(--status-*)` to each `.item-card`
    ([list.html:12](../app/templates/pages/jobs/list.html));
  - restyle the plain `.badge` into a tinted semantic chip (`--status-*` text on
    `--status-*-bg`). Keep the existing `job_status_label()` text — **color only**.
- **Button hierarchy (tokens, restrained):** primary = `var(--brand-primary)`;
  the single terminal CTA per page (Generate / Approve) and sun-critical capture
  buttons may use `var(--brand-accent)` with explicit `color: var(--text-on-accent)`;
  secondary/override buttons use `--surface-raised` + `--border-default`. One accent
  element per page maximum.
- `tabular-nums` on timestamp/count text for column alignment.

## Scope — out
- No change to the card **layout** or list IA — only rails, chip colors, type.
- No sticky bars, no two-column, no capture restructure (→ 14c / 14d).
- No new status states or status logic — consume the existing enum only.

## Non-negotiables honored
- Semantic colors are additive; every colored chip keeps its **text label**
  (color is never the only signal). Branding stays config-driven. No engine/route
  changes. Exact-AP-name join and server-side hard-fail untouched.

## Files likely touched
- `app/static/css/app.css` (`.ap-id`, status chip + rail classes, button tiers)
- `app/templates/pages/jobs/list.html` (rail + chip, status→color mapping)
- `app/templates/partials/jobs/*` (add `.ap-id` on AP names; button classes)
- Optionally a small `app/templates/partials/_status.html` macro for status→token
  mapping (presentation helper only — no route/model change)

## Done when
- A reviewer scanning the jobs list can locate approved vs in-review vs flagged jobs
  by color rail without reading each label.
- Every AP identifier across the app renders in mono and is visually distinct from prose.
- At most one amber accent element appears per page; all other primaries are navy.
- Status→color mapping is centralized (one macro/dict), not copy-pasted per template.

## Depends on / unblockers
[Phase 14](phase_14_ui_tokens.md) tokens must exist. Otherwise fully unblocked.

## Do NOT change
- `job_status_label()` output text, the status enum, or any status server logic.
- Any `hx-*` attribute / target id (see Phase 14 list), form actions, routes.
- `app/models/*`, `app/services/*`, `app/api/*` logic.

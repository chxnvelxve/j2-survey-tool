# Phase 14d — Login card + optional desktop two-column detail  (optional / higher-risk)

Continues [Phase 14c](phase_14c_mobile_capture_readiness.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) wins. Legend: 🔒 Josh · 🟡 placeholder · ⚙️ decision.

**Optional layout/IA pass — ship 14–14c first.** Split into a safe half (login card)
and a higher-risk half (desktop two-column job detail). The two-column restructure is
the **only** change in this refresh that reflows HTMX-wired layout, so it is isolated
here and can be deferred or dropped without affecting the token/visual work.

## Goal
Polish the login surface into a centered card, and — **optionally** — give the desktop
job-detail page a two-column workflow/readiness layout, without touching any HTMX
target, route, or service.

## Scope — in
### Part 1 — Login card (low risk, recommended)
- Centered `max-width: 400px` card on `--surface-base`, `--surface-card` fill,
  `--radius-lg`, `--shadow-md`.
- Suppress the logged-out **Jobs nav** on the login page (it's unusable pre-auth) —
  via a `base.html` block toggle or a login-specific header variant.
- Full-width submit button; focus ring using `--border-focus`.

### Part 2 — Desktop two-column job detail (optional, higher-risk) ⚙️
- At `≥1024px`, arrange [detail.html](../app/templates/pages/jobs/detail.html) as
  ~60% workflow column (survey files, parsed APs, photos, merge, attachments) + ~40%
  **sticky** readiness/generate/review column.
- **Reflow by wrapping existing `.upload-section`s in two column containers** — do
  **not** move, rename, or split any `hx-target` element. Below 1024px it collapses to
  the current single-column stack (14c's sticky mobile bar still applies).

## Scope — out
- No new content, fields, or endpoints — pure reflow + login styling.
- Part 2 is **not required** for the refresh to be "done"; treat as opt-in.

## Non-negotiables honored
- Branding config-driven; no engine/route/model/HTMX changes. Phone unaffected
  (single-column collapse preserved).

## Files likely touched
- `app/templates/login.html` (card markup, nav suppression)
- `app/templates/base.html` (optional `nav` block toggle for logged-out state)
- `app/templates/pages/jobs/detail.html` (Part 2: column wrappers only)
- `app/static/css/app.css` (login card, two-column grid + sticky column)

## Done when
- **Part 1:** login renders as a centered card with no logged-out Jobs nav; submit is
  full-width; behavior identical.
- **Part 2 (if taken):** on ≥1024px the detail page shows workflow left / sticky
  readiness right; below 1024px it is the current stack; **all HTMX swaps still target
  their original ids** and every phase action works end-to-end.

## Depends on / unblockers
[Phase 14](phase_14_ui_tokens.md) tokens. Part 2 reads best after
[14c](phase_14c_mobile_capture_readiness.md) (shares the readiness styling). No
external blockers. ⚙️ Part 2 is optional scope — confirm before building.

## Do NOT change
- Any `hx-target` id or `hx-*` attribute in `detail.html` (`#survey-files-list`,
  `#parsed-aps`, `#photos-list`, `#merged-results`, `#attachments-list`,
  `#drafted-prose`, `#job-status`) — wrap, never rename or relocate.
- `/login` form `action`, the `next` hidden field, or `app/api/auth.py` logic.
- Routes, models, services.

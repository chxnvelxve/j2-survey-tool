# Phase 14c — Mobile capture polish + readiness action bar  (unblocked, isolated)

Continues [Phase 14b](phase_14b_semantic_status_typography.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) wins. Legend: 🔒 Josh · 🟡 placeholder · ⚙️ decision.

**Unblocked. Isolated mobile CSS + light markup.** Refines the field-capture surface
(most of which [Phase 11](phase_11_field_capture_ux.md) already built) and adds a
glanceable readiness stepper with a mobile sticky action bar. Self-contained: it
touches capture + the readiness/generate area only, so it can ship on its own.

## Goal
Make the phone capture flow unmistakable in the field and keep the terminal CTA
(Generate / Approve) always reachable, using CSS + Jinja conditionals — **no JS**
beyond what already exists.

## Scope — in
- **Capture refinements** (build on existing `.capture-page` / `.touch-target`):
  - AP-name display in `.ap-id` mono at `--text-xl`.
  - Camera / upload buttons to `min-height: var(--touch-field)` (56px); the primary
    capture action may use `--brand-accent` for sun-readability.
  - Optional lightweight "AP n of m" progress text if the parsed AP count is already
    available in context — **display only**, no new server data.
  - Keep the datalist picker, soft mismatch hint, and inline JS **exactly as-is**.
- **Readiness indicators:** restyle the existing `.checklist` markers into semantic
  states driven by tokens — ✅ ready (`--status-success`), 🟡 pending
  (`--status-warning`), ⬛ blocked (`--status-error`). CSS + existing Jinja
  conditionals; no new logic.
- **Mobile sticky action bar:** on `max-width: 640px`, pin the terminal CTA
  (Generate / Approve) via `position: sticky; bottom: 0; z-index: var(--z-sticky)`
  with the current readiness count, so it never scrolls out of reach.

## Scope — out
- No change to capture upload endpoints, `hx-post` targets, or the AP-name JS logic.
- No desktop two-column detail (→ 14d).
- No new readiness rules or gate logic — style the existing checklist only.
- No on-device processing of any kind (non-negotiable #3).

## Non-negotiables honored
- **Phone = capture-and-upload only.** All refinements are presentation; hard-fail on
  AP-name mismatch stays server-side at merge. Branding config-driven; no route/engine
  changes.

## Files likely touched
- `app/static/css/app.css` (capture mobile rules, readiness states, sticky bar)
- `app/templates/pages/jobs/capture.html` (mono AP name, button classes; **JS untouched**)
- `app/templates/partials/jobs/capture_photos.html` (`.ap-id`, touch sizing)
- `app/templates/partials/jobs/generate_section.html` / `review_section.html`
  (sticky CTA wrapper, readiness marker classes)
- Readiness checklist partial(s) consuming the `.checklist` styles

## Done when
- On a phone-width viewport a tech sees a mono AP name, 56px accent camera buttons,
  and (if available) "AP n of m" — with the datalist picker + soft hint still working.
- Readiness items show ✅/🟡/⬛ semantic states from tokens.
- The Generate/Approve CTA stays visible via a sticky bottom bar on mobile without
  scrolling; desktop behavior unchanged.

## Depends on / unblockers
[Phase 14](phase_14_ui_tokens.md) tokens + [14b](phase_14b_semantic_status_typography.md)
`.ap-id`. Otherwise fully unblocked.

## Do NOT change
- The capture JS block ([capture.html:98–121](../app/templates/pages/jobs/capture.html))
  or the `#ap-name-input` / `#ap-names` / `#ap-mismatch-hint` / `#ap-names-json` ids.
- Any `hx-post` / `hx-target` / `hx-include` on the capture or generate forms.
- Merge/parse/generate services, routes, models. Server-side hard-fail stays.

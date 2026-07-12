# Phase 14 — UI design tokens + base styles  (unblocked, foundation)

Continues Phase 13 / [`phase_13_overview.md`](phase_13_overview.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) win.
Legend: 🔒 blocked on Josh · 🟡 sample/placeholder config now · ⚙️ business decision.

**Fully unblocked — run first.** This is the visual **token pass** only: extract the
inline CSS into a tokenised stylesheet and adopt a design-system `:root`. **No
per-page layout or IA restructuring** (that is 14b–14d). Derived from the Perplexity
"UI Refresh Design Spec" with two hard corrections carried in from the design review:
`--brand-primary` stays **config-driven**, and external CDNs are **vendored**.

## Goal
Move all styling out of the `base.html` inline `<style>` block into a single
`app/static/css/app.css` built on CSS custom properties (color, type, spacing,
radius, shadow, touch, z-index). Every existing screen renders **structurally
identical** — same markup, same HTMX, same behavior — just on tokens instead of
scattered hexes. Refresh the header into a filled brand strip with a config-driven
environment badge.

## Scope — in
- **Serve `/static` first (required enabling step).** `app/main.py` currently exempts
  `/static` from the Mode B auth gate ([main.py:18](../app/main.py)) but **never mounts
  it** — nothing serves `app/static/`, so `app.css`/vendored htmx would 404. Add, inside
  `create_app()`:
  ```python
  from fastapi.staticfiles import StaticFiles
  app.mount("/static", StaticFiles(directory="app/static"), name="static")
  ```
  This is enabling infrastructure, not a routing/pipeline change. Verify `/static/…`
  serves before doing CSS work. `app/static/.gitkeep` already exists; add `css/` + `js/`.
- New `app/static/css/app.css`: the full `:root` token set from the spec's §6 block,
  **with these changes**:
  - `--brand-primary` is **not** in the static file — it stays injected from config
    (`{{ brand_primary_color }}`) in `base.html`, as today ([base.html:9](../app/templates/base.html)).
  - `--brand-primary-dark` / `--brand-primary-light` **derive** from it via
    `color-mix(in srgb, var(--brand-primary), black/white …)` so Josh's final hex
    propagates automatically — no second hardcoded navy.
  - `--brand-accent` (amber) ships as a **static swappable token** 🟡, pending Josh's
    brand confirmation. Do **not** repoint every primary button to amber in this phase.
- Port every current rule from `base.html`'s `<style>` (lines 8–371) into `app.css`
  verbatim in **the same source order**, swapping literal hexes for the new tokens.
- Vendor htmx locally: download `htmx.min.js` → `app/static/js/`, replace the unpkg
  `<script>` ([base.html:372](../app/templates/base.html)) with a `/static/js/…` ref.
- `base.html`: replace the `<style>` block with `<link rel="stylesheet" href="/static/css/app.css">`;
  keep the small inline `:root { --brand-primary: {{ brand_primary_color }}; }` injection.
- Header strip: fill the header with `var(--brand-primary)`, company name (from config)
  + optional env badge driven by an **existing env/config value** (not literal "PRODUCTION").
- Apply base type/background to `body` (`--font-sans` with `system-ui` fallback,
  `--surface-base`, `--text-primary`).

## Scope — out
- No status-rail / semantic badge work (→ 14b).
- No AP-identifier mono class (→ 14b).
- No capture / readiness / mobile-bar work (→ 14c).
- No two-column detail or login card (→ 14d).
- No IBM Plex web font in this phase — `system-ui` / system-mono fallbacks only.
  Self-hosted Plex is an **optional** later enhancement, never a CDN link.

## Non-negotiables honored
- **Branding stays in config (#6):** `--brand-primary` remains `{{ brand_primary_color }}`;
  the same hex still feeds the docx generator. Accent is a swappable token.
- No engine/pipeline/route/model/HTMX changes — presentation only.
- Phone stays capture-and-upload only (untouched here).

## Files likely touched
- `app/main.py` (**add the `StaticFiles` mount** — enabling step above)
- `app/templates/base.html` (swap `<style>` → `<link>`; header strip; vendored htmx)
- `app/static/css/app.css` (new)
- `app/static/js/htmx.min.js` (new, vendored)

## Done when
- Every page (jobs list, job detail, capture, login, health) renders visually
  equivalent to before, sourced from `app.css`.
- No `<style>` block remains in `base.html` except the one-line brand-var injection.
- No network call to `unpkg` or Google Fonts (grep clean); htmx served from `/static`.
- Changing `BRAND_PRIMARY_COLOR` in `.env` still re-skins the whole UI (and shades
  track it via `color-mix`).

## Depends on / unblockers
Nothing external. **Fully unblocked.** Reads well before [Phase 13b](phase_13b_template_brand_activation.md)
brand activation — when Josh's hex lands it drops into the existing token with zero
component edits.

## Do NOT change
- The Mode B auth gate, `SessionMiddleware`, or router wiring in `main.py` — **only add
  the `StaticFiles` mount**; leave `_is_exempt`, the middleware, and `include_router`
  calls exactly as they are.
- Any `hx-*` attribute, `hx-target` id, form `action`, or route handler.
- HTMX swap-target ids that live in templates: `#survey-files-list`, `#parsed-aps`,
  `#photos-list`, `#merged-results`, `#attachments-list`, `#drafted-prose`,
  `#capture-photos-list`, `#job-status`, `#ap-name-input`, `#ap-names`,
  `#ap-mismatch-hint`, `#ap-names-json`.
- `app/api/*` route logic, `app/models/*`, `app/services/*`.
- The capture-page JS block ([capture.html:98–121](../app/templates/pages/jobs/capture.html)).

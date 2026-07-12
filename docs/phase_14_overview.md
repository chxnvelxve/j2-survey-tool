# Phase 14 batch — Operator UI refresh  (index)

Continues [Phase 13](phase_13_overview.md).
Canon: [`CLAUDE.md`](../CLAUDE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) win.
Legend: 🔒 blocked on Josh · 🟡 placeholder config now · ⚙️ business decision.

**Visual refresh only — not a pipeline or IA rebuild.** Adopts the Perplexity "UI
Refresh Design Spec" **with the corrections from the design review**: `--brand-primary`
stays config-driven (never hardcoded), CDNs are vendored (Tailscale/VPS has no assured
egress), the desktop dense-table jobs list is dropped (this app is correctly mobile-first
card IA), and the only layout-reflow change (desktop two-column detail) is isolated as
optional. Sequential, each slice independently shippable.

## The batch

| Phase | Topic | Type | Gate |
|---|---|---|---|
| [**14**](phase_14_ui_tokens.md) | Design tokens + base styles + header strip + vendored htmx | Foundation | none — **start here** |
| [**14b**](phase_14b_semantic_status_typography.md) | Semantic status rail/badges + AP-identifier mono + button tiers | Visual | needs 14 |
| [**14c**](phase_14c_mobile_capture_readiness.md) | Mobile capture polish + readiness stepper + sticky mobile CTA | Visual | needs 14/14b |
| [**14d**](phase_14d_layout_login_optional.md) | Login card (safe) + **optional** desktop two-column detail ⚙️ | Layout/IA | needs 14; Part 2 opt-in |

## Sequencing
Do them one at a time (Cursor Ask→Plan→Build), in order. 14 is the only one that
touches app wiring (it adds the missing `/static` mount); 14b–14c are CSS + light
template markup; 14d Part 2 is optional and the only higher-risk reflow.

## Relationship to Josh's blockers
Fully unblocked — none of 14–14d wait on Josh. The token layer is built so that when
[Phase 13b](phase_13b_template_brand_activation.md) lands (real logo/hex/thresholds),
the brand hex drops into `BRAND_PRIMARY_COLOR` and re-skins the whole UI via one
variable — no component edits.

## Explicitly not in this batch
- Desktop dense data table for jobs (**dropped** — wrong for mobile-first field techs).
- IBM Plex web fonts via CDN (**reshaped** — system fonts ship first; self-hosted Plex
  is an optional later enhancement, never a CDN link).
- `BRAND_ACCENT_COLOR` promoted to config (deferred until Josh confirms the accent;
  ships as a swappable CSS token so this batch stays route-free apart from the mount).

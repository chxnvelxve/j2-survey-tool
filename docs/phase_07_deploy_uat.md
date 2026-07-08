# Phase 7 — Production deploy + UAT + label isolation  ⚙️(auth fork)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Run first.** Fully unblocked (you have VPS access).

## Goal
Get v1 running on the VPS, smoke-test the full workflow end to end, lock the handoff
acceptance checklist, and close the one bit of canon drift from the last batch: isolate
Job-status / readiness-gate **display labels** from enum values so a later Josh
confirmation is a config edit, not a migration.

## Scope
- Deploy to VPS per `docs/deploy.md`: Docker Compose up, healthchecks green, migrations run.
- Reverse proxy in front of the app (**Caddy** preferred — auto-TLS, tiny config). Commit a
  sample `Caddyfile`; real domain is a 🟡 placeholder (`survey.example.com`).
- Access gating: **Tailscale-only** for v1 (see auth fork). Document the tailnet ACL
  assumption in `docs/deploy.md`.
- **Label isolation refactor (closes canon drift):** add a single `app/core/labels.py`
  mapping stable enum values → human display strings for Job status and readiness gates.
  Templates render *display* strings via this map, never the raw enum name. No enum value
  changes, no migration. When Josh confirms terminology, only `labels.py` changes.
- UAT acceptance checklist (`docs/uat_checklist.md`): create Job → upload sample `.esx` +
  photos + one attachment → parse → merge → resolve flags → generate → download → approve,
  with expected result at each step.

## Auth fork ⚙️ — resolve before building the gating layer
Pick one; don't build both:
- **A (default for v1): Tailscale-only, no app auth.** Anyone on the tailnet can do
  anything. Zero maintenance, matches the ~$2,500 no-post-handoff-cost constraint.
- **B: minimal single-shared-password gate** (one env var, session cookie). Only if J2
  needs someone off-tailnet to reach it.

Full RBAC / multi-user stays **out of v1** (parked). This file assumes **A** unless Josh
says otherwise.

## Sample config used now (🟡 swap later)
- `PUBLIC_HOSTNAME=survey.example.com`
- `ACCESS_MODE=tailscale`  *(A)* — reserved value `shared_password` for (B)
- No secrets committed; `.env.example` documents both modes.

## Done when
VPS serves the app over the reverse proxy with TLS; the full UAT checklist passes on the
deployed instance against sample data; status/gate display strings all route through
`labels.py`; `docs/uat_checklist.md` committed and checked off once.

## Depends on
VPS access (you have this). **Not blocked on Josh.**

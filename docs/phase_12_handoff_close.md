# Phase 12 — Handoff hardening + v1 acceptance close  ⚙️(billing fork)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Run last.** Technical scope is unblocked; the billing trigger is a decision, not code.

## Goal
Make the fixed-fee handoff defensible and low-maintenance. Decide what counts as "v1 done"
for billing.

## Scope
- **Minimal CI** (GitHub Actions): run the ~55-test suite + a lint pass on push. One
  workflow file; no deploy automation (keeps post-handoff cost at zero).
- **Backup note** in `docs/deploy.md`: how to snapshot the Postgres volume + storage dir on
  the VPS — a documented procedure, not a running service (no maintenance cost).
- `docs/handoff.md`: what Josh owns, how to change branding config, how to swap the template,
  how to point at Nextcloud when creds exist, how to promote the Phase 8/9/10 stubs.
- Final acceptance checklist tie-off referencing the Phase 7 UAT.

## Billing fork ⚙️ — resolve, don't code around
Is v1 "done for billing" once **deployed + UAT-passed against sample data**, with
real-`.esx` validation (8), template polish (9), and Nextcloud (10) treated as **included
activations** (not new change orders)?

Recommendation: bill the second 50% on **deploy + UAT acceptance**, and treat 8/9/10
activations as already-scoped work that completes when Josh delivers assets — since the
shells are built in this batch. Confirm the split with Josh; this is the open billing
question from `03_DOMAIN_AND_DECISIONS.md`.

## Done when
CI green on push; backup + handoff docs committed; acceptance checklist signed; billing
trigger agreed.

## Depends on
Billing-split decision (business). Technical scope is unblocked.

# Phase 11 — Field capture UX polish  (unblocked, high value)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Fully unblocked — run early.** Directly attacks the highest-leverage real-world failure
point (a mistyped AP name breaking the exact-name join).

## Goal
Make field capture harder to get wrong. Phone stays **capture-and-upload only**
(non-negotiable #3); this is UX, not on-device processing.

## Scope
- Mobile-friendly capture view: large touch targets, close/far photo slots per AP,
  minimal typing.
- **AP-name picker from the parsed survey model:** once a Job has a parsed `.esx`, the
  capture form offers the real AP-name list as a typeahead/dropdown so the Tech selects
  rather than types. Free-text stays allowed (a Tech may capture before the `.esx` is
  uploaded), but a selected name is guaranteed to match — directly reducing name-contract
  friction.
- Capture-side warning (**not** a block): if a typed name matches no parsed AP, show a soft
  "no match yet — will flag at merge" hint. Still uploads; hard-fail stays at merge per canon.
- Per-job settings on the same view (survey type, location vertical, band plan, site
  metadata) so the readiness gate's required fields get populated at capture time.

## Non-negotiables honored
Phone does no merging/processing — capture and upload only. Hard-fail on mismatch still
happens **server-side at merge**, not on the phone.

## Done when
On a phone-width viewport, a Tech can pick an AP name from the parsed list, attach close+far
photos, fill per-job settings, and upload — with a soft mismatch hint for unparsed/typed
names. No change to merge's server-side hard-fail.

## Depends on
Nothing external. **Fully unblocked.**

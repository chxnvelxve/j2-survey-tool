# Phase 8 — Real `.esx` alignment  🔒(real J2 `.esx`)  🟡(sample schema stub now)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Build the shell now; activate when the real file arrives.** Do not wait on Josh to start.

## Goal
Replace the provisional parser mapping with one verified against a real J2 Ekahau export.
Build the shell and test harness now against a documented sample schema so activation is fast.

## Scope — shell (buildable now)
- [`docs/esx_schema.md`](esx_schema.md): write down the **assumed** JSON schema the current parser targets
  (`project.json`, `floorPlans.json`, `accessPoints.json`, radio JSON) — field by field,
  each marked **ASSUMED** vs **CONFIRMED**. This is the diff surface for when the real file lands.
- Parser **schema-version guard**: detect and record the Ekahau schema version/shape; if an
  unexpected shape appears, **hard-fail loudly** with the offending keys (consistent with the
  project's hard-fail philosophy) rather than silently mis-mapping.
- Expand `tests/fixtures/build_sample_survey.py` to emit **two** fixture variants — a "clean"
  one and one with intentional edge cases (unicode AP names, missing radio block, duplicate
  AP name across files). Tests assert exact-name preservation across both.
- Heatmap-image question 🟡: assume `.esx` **contains rendered heatmap PNGs** as image assets
  and wire the parser to surface image refs. Mark this **ASSUMED** in `docs/esx_schema.md`.
  If Josh confirms a manual export step is needed instead, that becomes a capture-side change,
  not a parser rewrite.

## Scope — activation (on real file 🔒)
- Diff the real file against `docs/esx_schema.md`; correct field mappings; flip
  ASSUMED→CONFIRMED.
- Replace fixture-derived assumptions with real-shape fixtures (scrub any client-identifying
  data before committing).
- Remove the "provisional/unverified" header comment in `parser.py`.

## Done when
- **Shell:** schema doc committed with every field marked ASSUMED/CONFIRMED; version guard
  hard-fails on unknown shapes with a clear message; edge-case fixtures pass.
- **Activated:** parser round-trips a real J2 `.esx`; no ASSUMED fields remain for the
  mainline path; provisional comment removed.

## Depends on
🔒 Real `.esx` from Josh **for activation**. Shell is unblocked.

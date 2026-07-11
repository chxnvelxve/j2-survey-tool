# Phase 9 — Deliverable template polish  🔒(sample Word report)  🟡(placeholder template now)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Build the shell now; activate when Josh's sample report arrives.**

## Goal
Turn the placeholder `.docx` template into one that matches J2's real client-facing report.
Build the mapping scaffold now so the real template drops into a known set of context vars.

## Scope — shell (buildable now)
- `docs/template_map.md`: the section→data-source map from the canonical eight-section
  structure (Cover, Exec Summary, Scope/Methodology, Success Criteria, Findings, AP
  Inventory, Issues & Gaps, Appendices) → the exact `docxtpl` context keys the generator
  already produces. Mark each section **AUTO** (machine-fed) vs **DRAFTED** (human-written).
- **Freeze the generator context contract:** document every key `context.py` emits so the
  template binds against a stable surface. Add a contract test that fails if a documented
  key disappears.
- 🟡 **Sample branding config** so the placeholder looks real end to end:
  - `BRAND_COMPANY_NAME="J2 Communications"`
  - `BRAND_PRIMARY_COLOR="#1F4E79"`  *(placeholder navy — confirm J2 brand hex)*
  - `BRAND_LOGO_PATH="branding/j2_logo_placeholder.png"`  *(commit a neutral placeholder
    logo; swap real asset later)*
- 🟡 **Success-criteria profiles** stubbed as a lookup table with sample thresholds so the
  "Success Criteria" section renders (see below).
- Improve the placeholder template's structure (all 8 sections present, headings, photo grid
  for AP Inventory, appendix tables) so it's a credible dry-run before the real format arrives.

## Scope — activation (on sample deliverable 🔒)
- Reverse-engineer Josh's "gold standard" doc: identify AUTO vs DRAFTED regions, headers,
  spacing, voice.
- Rebuild `templates_docx/survey_report.docx` to match; bind to the frozen context contract.
- Replace placeholder branding with real J2 assets/hex.

## Requirement profiles 🟡 (open question — sample now)
Canon/briefing leaves open whether success thresholds (e.g., −67 dBm RSSI) are a **built-in
per-vertical lookup table** or a **per-job manual input**. Build it as a **lookup table with a
per-job override field** — the superset that satisfies either answer. Seed sample profiles so
the section renders. Table lives in `app/services/generator/profiles.py`; per-job override
wins when set.

| Profile (vertical) | Min RSSI | Min SNR | Min data rate | Max co-channel overlap |
|---|---|---|---|---|
| `warehouse`    | −67 dBm | 25 dB | 144 Mbps | 3 APs |
| `office`       | −65 dBm | 25 dB | 300 Mbps | 3 APs |
| `hospital`     | −62 dBm | 30 dB | 300 Mbps | 2 APs |
| `outdoor_yard` | −72 dBm | 20 dB | 54 Mbps  | 4 APs |

*(All values PLACEHOLDER — confirm real J2 thresholds.)*

## Done when
- **Shell:** `docs/template_map.md` + frozen context contract + contract test committed;
  placeholder template renders all 8 sections with sample branding and a sample profile
  end to end.
- **Activated:** rendered `.docx` visually matches J2's sample; real branding + real
  thresholds in place.

## Depends on
🔒 Sample Word deliverable from Josh **for activation**; real brand hex/logo; confirmed
thresholds. Shell is unblocked.

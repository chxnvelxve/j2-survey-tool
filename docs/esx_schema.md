# Ekahau `.esx` JSON schema — parser target

Canonical diff surface for Phase 8 activation. When a real J2 Ekahau export arrives,
diff it against this document field-by-field and flip **ASSUMED** → **CONFIRMED**.

**Status legend**

| Status | Meaning |
|--------|---------|
| **CONFIRMED** | Exercised by committed fixtures + parser unit tests, and treated as stable for `fixture_v1` |
| **ASSUMED** | Parser accepts or documents the field, but shape/presence is not verified against a real J2 `.esx` (may still appear in fixtures — e.g. heatmaps) |

Parser profile: **`fixture_v1`** (see [Schema fingerprint](#schema-fingerprint)).

---

## Overview

An `.esx` file is a **ZIP archive** containing JSON manifests and image assets.
The parser unzips to a temp directory, validates shape via `schema_guard.py`, then
maps into `SurveyModel`. No Ekahau API required.

One `.esx` → one `SurveyModel`. A Job with N survey files parses N times.

**AP name is sacred** — preserved exactly (no trim, no case change). It is the merge
join key.

---

## ZIP inventory

| Path | Required | Status | Notes |
|------|----------|--------|-------|
| `project.json` | yes | CONFIRMED | Project metadata |
| `floorPlans.json` | yes | CONFIRMED | Floor list |
| `accessPoints.json` | yes | CONFIRMED | AP list |
| `simulatedRadios.json` | no | CONFIRMED | RF data (fixture uses this) |
| `measuredRadios.json` | no | ASSUMED | Alternate radio source; same record shape |
| `*.png` (floor plans) | no | CONFIRMED | Referenced by `floorPlans[].image` |
| `*.png` (heatmaps) | no | ASSUMED | Referenced by `floorPlans[].heatmap` — see [Heatmaps](#heatmaps) |
| Other JSON files | — | ASSUMED | Unknown files are ignored today; activation may add profiles |

---

## `project.json`

**Root type:** object

| Field | Type | Maps to | Status | Notes |
|-------|------|---------|--------|-------|
| `name` | string (required) | `SurveyProject.name` | CONFIRMED | |
| `version` | string | *(not mapped)* | ASSUMED | Allowed in whitelist for fingerprint; Ekahau version metadata |
| `created` | string | *(not mapped)* | ASSUMED | ISO timestamp metadata |
| `modified` | string | *(not mapped)* | ASSUMED | ISO timestamp metadata |

---

## `floorPlans.json`

**Root type:** array of objects

| Field | Type | Maps to | Status | Notes |
|-------|------|---------|--------|-------|
| `id` | string (required) | `SurveyFloor.id` | CONFIRMED | |
| `name` | string (required) | `SurveyFloor.name` | CONFIRMED | |
| `image` | string | `SurveyFloor.image_ref` | CONFIRMED | Path to floor-plan PNG inside ZIP |
| `imageRef` | string | `SurveyFloor.image_ref` | ASSUMED | Alias for `image`; parser accepts either |
| `heatmap` | string | `SurveyFloor.heatmap_ref` | ASSUMED | Path to heatmap PNG inside ZIP |
| `heatmapRef` | string | `SurveyFloor.heatmap_ref` | ASSUMED | Alias for `heatmap` |

---

## `accessPoints.json`

**Root type:** array of objects

| Field | Type | Maps to | Status | Notes |
|-------|------|---------|--------|-------|
| `id` | string | *(join key for radios)* | CONFIRMED | Links to `accessPointId` in radio JSON |
| `name` | string (required) | `SurveyAP.name` | CONFIRMED | Exact preservation required |
| `model` | string | `SurveyAP.model` | CONFIRMED | |
| `vendor` | string | `SurveyAP.vendor` | CONFIRMED | |
| `floorId` | string | `SurveyAP.floor_id` | CONFIRMED | |
| `floor_id` | string | `SurveyAP.floor_id` | ASSUMED | Alias for `floorId` |
| `x` | number | `SurveyAP.x` | CONFIRMED | Plan coordinates |
| `y` | number | `SurveyAP.y` | CONFIRMED | Plan coordinates |

APs with no matching radio record parse with `radios: []` (CONFIRMED via edge-case fixture).

---

## `simulatedRadios.json` / `measuredRadios.json`

**Root type:** array of objects (both files optional; same record shape)

| Field | Type | Maps to | Status | Notes |
|-------|------|---------|--------|-------|
| `accessPointId` | string (required) | *(join to AP `id`)* | CONFIRMED | |
| `apId` | string | *(join to AP `id`)* | ASSUMED | Alias for `accessPointId` |
| `band` | string (required) | `SurveyRadio.band` | CONFIRMED | e.g. `5GHz`, `2.4GHz` |
| `channel` | integer | `SurveyRadio.channel` | CONFIRMED | |
| `txPower` | number | `SurveyRadio.tx_power` | CONFIRMED | |
| `tx_power` | number | `SurveyRadio.tx_power` | ASSUMED | Alias for `txPower` |

Parser reads both files if present and merges radios by AP id.

---

## Image assets

### Floor-plan PNGs

| Aspect | Status | Notes |
|--------|--------|-------|
| PNG bytes in ZIP root | CONFIRMED | Fixture includes `floor1.png` |
| Referenced via `floorPlans[].image` | CONFIRMED | Stored as `SurveyFloor.image_ref` |
| Subfolder layout | ASSUMED | Real exports may nest images; activation must confirm paths |

### Heatmaps

| Aspect | Status | Notes |
|--------|--------|-------|
| Heatmap PNGs inside `.esx` ZIP | ASSUMED | Not verified against real J2 export |
| Per-floor JSON ref (`heatmap` / `heatmapRef`) | ASSUMED | Wired to `SurveyFloor.heatmap_ref` |
| Per-AP heatmap refs | ASSUMED | Not implemented — gap if real file uses this layout |
| ZIP inventory inference (no JSON ref) | ASSUMED | Not implemented — document gap if needed at activation |

**Fallback if Josh confirms manual heatmap export:** heatmaps become a Job attachment
or separate upload step instead of in-ZIP refs. `SurveyFloor.heatmap_ref` stays optional;
the generator would pull heatmaps from attachments. This is a capture/UX change, not a
parser rewrite.

---

## Schema fingerprint

Profile **`fixture_v1`** is detected when:

1. Required JSON files exist: `project.json`, `floorPlans.json`, `accessPoints.json`
2. Root types match: `project.json` = object; others = arrays
3. All keys in each file/record are within the allowed whitelist (see `schema_guard.py`)
4. Optional JSON (`simulatedRadios.json`, `measuredRadios.json`) may be absent

If shape does not match any known profile, the parser **hard-fails** with `ParseError`
naming the offending file and unknown keys. Never silently mis-map.

Fingerprint is logged at INFO during parse; not stored on `SurveyModel` (no consumer yet).

---

## Fixture variants

Regenerate: `python tests/fixtures/build_sample_survey.py`

| File | Purpose |
|------|---------|
| `sample_survey_clean.esx` | Minimal happy path; tidy AP names |
| `sample_survey_edge_cases.esx` | Whitespace/unicode names, missing radio AP, heatmap ref |
| `sample_survey_dup_a.esx` / `sample_survey_dup_b.esx` | Duplicate AP name across files (future merge tests) |
| `sample_survey.esx` | Backward-compat alias → `edge_cases` |

---

## Activation checklist

When a real J2 `.esx` arrives from Josh:

1. **Inventory:** `unzip -l real.esx`; pretty-print each JSON file's top-level keys.
2. **Diff this doc:** for every field, mark ASSUMED → CONFIRMED or add new rows.
3. **Update `schema_guard.py`:** add/replace profile (e.g. `j2_ekahau_2024`); do not
   loosen guards without documenting new allowed keys here.
4. **Adjust `parser.py`:** change `_parse_*` mappings only where real keys differ.
5. **Commit scrubbed real-shape fixture(s)** (no client-identifying data).
6. **Heatmaps:** confirm in-ZIP refs vs manual export; update [Heatmaps](#heatmaps) section.
7. **Remove provisional header** in `parser.py`; ensure mainline path has no ASSUMED gaps.

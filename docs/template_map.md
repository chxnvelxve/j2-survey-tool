# Template map — section → docxtpl context

Frozen contract for `templates_docx/survey_report.docx`. Generator emits these
keys from `app/services/generator/context.py`. The contract test
(`tests/test_context_contract.py`) fails if a documented key disappears.

**AUTO** = machine-fed from Job / MergedJob / branding.
**DRAFTED** = human-written placeholder string until Josh's sample deliverable
arrives (🔒 activation).

Legend: 🟡 sample / placeholder · 🔒 blocked on Josh

---

## 1. Cover — AUTO

| Context key | Source |
|-------------|--------|
| `logo` | `BrandingConfig.logo_path` → InlineImage or null |
| `company_name` | `BRAND_COMPANY_NAME` |
| `primary_color` | `BRAND_PRIMARY_COLOR` 🟡 |
| `job_name` | Job.name |
| `project_name` | First parsed survey project name |

## 2. Executive Summary — DRAFTED

| Context key | Source |
|-------------|--------|
| `exec_summary` | Placeholder prose from context.py 🟡 |

## 3. Scope / Methodology — DRAFTED (+ AUTO crumbs)

| Context key | Source |
|-------------|--------|
| `scope_methodology` | Placeholder prose 🟡 |
| `survey_type` | Job.survey_type (or "—") |
| `location_vertical` | Job.location_vertical (or "—") |
| `band_plan` | Job.band_plan (or "—") |
| `site_metadata` | Job.site_metadata (or "—") |

## 4. Success Criteria — AUTO

| Context key | Source |
|-------------|--------|
| `success_criteria.profile_key` | Resolved profile id |
| `success_criteria.label` | Display label |
| `success_criteria.min_rssi_dbm` | Threshold 🟡 PLACEHOLDER |
| `success_criteria.min_snr_db` | Threshold 🟡 |
| `success_criteria.min_data_rate_mbps` | Threshold 🟡 |
| `success_criteria.max_co_channel_aps` | Threshold 🟡 |
| `success_criteria.is_override` | True when Job.success_criteria_override applied |

Lookup: `app/services/generator/profiles.py` via `Job.location_vertical`.
Per-job `success_criteria_override` JSON wins field-by-field when set.

## 5. Findings — DRAFTED (+ AUTO counts)

| Context key | Source |
|-------------|--------|
| `findings` | Placeholder prose 🟡 (no RF pass/fail math in shell) |
| `ap_count` | `len(aps)` |
| `override_count` | `len(overrides)` |

## 6. AP Inventory — AUTO

| Context key | Source |
|-------------|--------|
| `aps[]` | MergedJob APs (sorted by name) |

Per AP:

| Key | Notes |
|-----|-------|
| `name`, `model`, `vendor`, `floor`, `x`, `y` | Survey fields |
| `radios[]` | `{band, channel, tx_power}` |
| `radios_summary` | Human-readable radio line |
| `status` | MergedAPStatus value |
| `photo_close`, `photo_far` | InlineImage or null |
| `photo_close_label`, `photo_far_label` | Filename or "Not provided" |

## 7. Issues & Gaps — AUTO

| Context key | Source |
|-------------|--------|
| `overrides[]` | Flags with non-empty override_reason |
| `has_overrides` | bool |

Per override: `ap_name`, `type_label`, `detail`, `reason`.

## 8. Appendices — AUTO

| Context key | Source |
|-------------|--------|
| `attachments[]` | Job attachments (sorted by filename) |

Per attachment: `filename`, `image` (InlineImage if image), `is_image`.

---

## Top-level key inventory (frozen)

```
company_name, primary_color, logo,
job_name, project_name,
survey_type, location_vertical, band_plan, site_metadata,
success_criteria,
exec_summary, scope_methodology, findings,
ap_count, override_count,
aps, attachments, overrides, has_overrides
```

Do not remove keys without updating this doc and the contract test together.

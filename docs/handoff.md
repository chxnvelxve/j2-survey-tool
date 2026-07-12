# Operator handoff — J2 Survey Tool v1

Day-2 notes for Josh / J2 after the fixed-fee build. Deploy steps live in
[`deploy.md`](deploy.md). This doc covers ownership, re-skinning, and how to
activate the Phase 8/9/10 shells when assets arrive.

## What Josh owns

| Area | Notes |
|---|---|
| VPS + Docker | Host, disk, `docker compose` prod stack |
| Tailscale | Node, Serve enablement, tailnet ACL |
| Secrets | `.env` — `SECRET_KEY`, DB passwords, never commit real values |
| Real field assets | J2 `.esx`, gold-standard Word sample, brand logo/hex, Nextcloud URL + app password |
| Backups | Follow the Backup section in [`deploy.md`](deploy.md) before upgrades |

Builder-owned engine stays brandable via config — no hardcoded client names in
pipeline stages.

## Change branding

Edit `.env` (see [`.env.example`](../.env.example)):

```bash
BRAND_COMPANY_NAME=J2 Communications
BRAND_PRIMARY_COLOR=#1F4E79          # placeholder navy — swap real hex
BRAND_LOGO_PATH=branding/j2_logo_placeholder.png
```

Replace the logo file under `branding/` (or point `BRAND_LOGO_PATH` at a new path
inside the container). Restart `web` after changes. Branding must stay out of
`app/services/` engine logic.

## Swap the Word template

1. Keep the frozen `docxtpl` context keys documented in [`template_map.md`](template_map.md)
   (contract test in `tests/test_context_contract.py` guards removals).
2. Replace [`templates_docx/survey_report.docx`](../templates_docx/survey_report.docx)
   with the real layout, or set `DOCX_TEMPLATE_PATH` to another mounted `.docx`.
3. Generate a Job and open the download — sections should still bind to the same keys.

Placeholder structure and sample success-criteria profiles are Phase 9 shell;
activation = match Josh’s real client report (see below).

## Point storage at Nextcloud

Shell is implemented (`NextcloudStorage` over WebDAV). Local remains the default.

```bash
STORAGE_BACKEND=nextcloud
NEXTCLOUD_URL=https://nextcloud.example.com
NEXTCLOUD_USERNAME=survey-bot
NEXTCLOUD_PASSWORD=app-password-from-nextcloud
NEXTCLOUD_WEBDAV_ROOT=j2-survey
```

Missing URL/user/password raises `StorageNotConfiguredError` — **no silent fallback
to local**. Smoke after flip: upload → download → confirm `url_for` works. Details:
[`phase_10_nextcloud.md`](phase_10_nextcloud.md).

## Promote Phase 8 / 9 / 10 stubs (activation)

Shells are built; live activation waits on Josh’s assets. Use these as the runbooks:

| Phase | Stub today | When assets arrive |
|---|---|---|
| **8** Real `.esx` | Assumed schema in [`esx_schema.md`](esx_schema.md); sample fixtures | Diff real export → flip ASSUMED→CONFIRMED; fix parser mappings ([`phase_08_real_esx.md`](phase_08_real_esx.md)) |
| **9** Template polish | Placeholder `.docx`, sample brand hex/logo, profile thresholds | Rebuild template from gold-standard Word; real branding ([`phase_09_template_polish.md`](phase_09_template_polish.md)) |
| **10** Nextcloud | Mocked WebDAV tests; `STORAGE_BACKEND=local` | Set creds as above; live round-trip ([`phase_10_nextcloud.md`](phase_10_nextcloud.md)) |

## v1 acceptance (tie-off)

Phase 7 UAT against sample fixtures is the acceptance evidence:

- Checklist: [`uat_checklist.md`](uat_checklist.md)
- Sign-off: **PASS** — 2026-07-08 — Tailscale URL + local prod-like compose

No re-sign required for this handoff slice. Re-run the checklist after major
activation changes (real `.esx` / template) if Josh wants a second pass.

## Billing fork (open — business, not code)

From [`phase_12_handoff_close.md`](phase_12_handoff_close.md) and the open item in
[`DECISIONS.md`](DECISIONS.md):

**Recommendation:** bill the second 50% on **deploy + UAT acceptance** (sample data).
Treat Phase 8/9/10 activations as **already-scoped** work that completes when Josh
delivers assets — not new change orders.

Confirm the split with Josh. Shipping this handoff does **not** require that
agreement first.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs `ruff check` (narrow rule set) and
`pytest` on push/PR to `main`. No deploy automation — keeps post-handoff maintenance
near zero.

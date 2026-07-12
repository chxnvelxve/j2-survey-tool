# Phase 10 — Nextcloud storage  🔒(WebDAV creds)  🟡(stub + local now)

Continues `04_BUILD_PHASES.md`. Canon: `03_DOMAIN_AND_DECISIONS.md` wins.
Legend: 🔒 blocked on Josh · 🟡 sample config now · ⚙️ business decision.

**Build the shell now; activate when Josh provides creds.** Least urgent blocker (local
stub already unblocks dev).

## Goal
Implement `NextcloudStorage` behind the existing `Storage` interface so nothing upstream
changes. Everything is buildable now except the live credential test.

## Scope — buildable now
- Implement `NextcloudStorage.save / open / url_for` against **WebDAV** using a documented
  sample endpoint (🟡 `https://nextcloud.example.com/remote.php/dav/files/USER/`).
- Config in `.env.example` (values placeholder; real ones never committed):
  `STORAGE_BACKEND`, `NEXTCLOUD_URL`, `NEXTCLOUD_USERNAME`, `NEXTCLOUD_PASSWORD`,
  `NEXTCLOUD_WEBDAV_ROOT`.
- Tests against a **mocked WebDAV** (respx/responses) so the impl is verified without live
  creds: upload path, fetch, `url_for` shape, error on missing file.
- Keep `LocalStorage` as default; `STORAGE_BACKEND=local` stays the dev/CI default.
- **Graceful failure:** if `STORAGE_BACKEND=nextcloud` but creds absent, raise the existing
  `StorageNotConfiguredError` with an actionable message. **Do not silently fall back to
  local** — that would hide a production misconfiguration.

## Scope — activation (on creds 🔒)
- Point env at the real Nextcloud; run the smoke path (upload a report, download it back,
  resolve a `url_for`).
- Confirm WebDAV auth style (app password vs basic); adjust if Josh's instance differs.

## Done when
- **Shell:** `NextcloudStorage` passes the mocked-WebDAV suite; local stays default;
  missing-creds path raises cleanly.
- **Activated:** a generated report round-trips through the real Nextcloud instance;
  `url_for` yields a working link.

## Depends on
🔒 Nextcloud URL + app password from Josh **for activation**. Shell is unblocked.

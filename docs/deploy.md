# Production deployment (VPS handoff)

Minimal notes for running the J2 Survey Tool on a VPS with Docker Compose.

## Prerequisites

- Docker and Docker Compose v2
- Tailscale on the VPS (for ACCESS_MODE A — v1 default)
- Copy `.env.example` to `.env` and set production values

## Required environment variables

| Variable | Notes |
|---|---|
| `APP_ENV` | Set to `production` (disables uvicorn `--reload`) |
| `SECRET_KEY` | Change from default (strong random string) |
| `DATABASE_URL` | Postgres connection string |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Used by the `db` service |
| `STORAGE_LOCAL_ROOT` | `/app/storage` inside container |
| `STORAGE_BACKEND` | `local` (default); `nextcloud` WebDAV shell is ready — needs Josh’s creds to activate |
| Branding vars | `BRAND_*`, `DOCX_TEMPLATE_PATH` |
| `PUBLIC_HOSTNAME` | Placeholder `survey.example.com` — used by Caddy when serving a real domain |
| `ACCESS_MODE` | `tailscale` (v1 default) or `shared_password` (MODE B — not implemented yet) |

## Development vs production compose

**Development** (hot reload):

```bash
docker compose up --build
```

The bundled [`docker-compose.yml`](../docker-compose.yml) bind-mounts `./:/app` for local hot reload and exposes port `8050` on all interfaces.

**Production** (baked image, localhost-only port):

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

[`docker-compose.prod.yml`](../docker-compose.prod.yml) uses Compose `!override` on `ports` and `volumes` so the prod file **replaces** (not appends) the base mappings: no code bind-mount, `127.0.0.1:8050` only, and `restart: unless-stopped`. Requires Docker Compose v2.24+ (`!override` / `!reset`). Migrations run automatically via [`scripts/entrypoint.sh`](../scripts/entrypoint.sh) on web container start.

Before first start, create the storage dirs if missing:

```bash
mkdir -p storage/uploads storage/output storage/jobs
```

## Volumes

- `pgdata` — Postgres data (compose named volume)
- `./storage:/app/storage` — uploaded files and generated reports

Persist `./storage` on the host or map to a dedicated data path.

## Backup

Documented procedure only — no backup daemon. Run before upgrades or VPS moves.

Compose files for these commands:

```bash
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
```

**1. Postgres (logical dump — preferred)**

```bash
mkdir -p backups
$COMPOSE exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "backups/pg_$(date +%Y%m%d_%H%M%S).sql"
```

**2. Postgres (volume copy — alternative)**

Stop the stack briefly, then copy the named volume `pgdata` (exact path depends on Docker root; e.g. `docker volume inspect <project>_pgdata`). Prefer `pg_dump` when possible.

**3. File storage**

```bash
tar -czf "backups/storage_$(date +%Y%m%d_%H%M%S).tar.gz" storage
```

Or `rsync -a storage/ /path/to/offbox/storage/`.

**Restore sketch**

1. Restore SQL: `$COMPOSE exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB" < backups/pg_….sql` (into an empty/fresh DB), **or** restore the `pgdata` volume from the copy.
2. Unpack `storage` onto the host path mounted as `./storage`.
3. `$COMPOSE up -d` and confirm `GET /health`.

## Health check

- JSON: `GET /health` → `{"status":"ok","env":"production"}`
- Compose healthchecks are configured for `web` and `db`

Verify after deploy:

```bash
# Containers healthy
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# App responds (direct — bypasses proxy)
curl -s http://127.0.0.1:8050/health

# Through Tailscale Serve (after setup below)
curl -s https://<machine-name>.<tailnet>.ts.net/health
```

## Access model (ACCESS_MODE)

### A — Tailscale-only (v1 default)

`ACCESS_MODE=tailscale` — **no app-level authentication**. Authorization is the tailnet ACL: anyone on the J2 tailnet who can reach the VPS can use the app (create Jobs, approve, etc.). Roles in the UI are workflow hats, not enforced permissions.

Assumptions:

- The VPS runs Tailscale and is only reachable by tailnet members for app access.
- Docker binds the web port to `127.0.0.1:8050` so the app is not exposed on the public NIC.
- Full RBAC / multi-user auth is **parked** for post-v1.

### B — Shared password (parked)

`ACCESS_MODE=shared_password` requires `SHARED_ACCESS_PASSWORD`. The app will **refuse to start** if the password is missing. The login gate itself is **not implemented in v1** — this documents the env contract for a small follow-up if J2 needs off-tailnet access. Do not set `ACCESS_MODE=shared_password` until MODE B is built.

There is **no silent fallback** between modes.

## TLS and reverse proxy

TLS terminates at **one** edge layer — Tailscale Serve **or** Caddy, not both.

### Primary for ACCESS_MODE A: Tailscale Serve

Zero public DNS; HTTPS on the tailnet; forwards to the app on localhost.

```bash
# On the VPS (after prod compose is up and /health returns ok)
tailscale serve --bg --https=443 http://127.0.0.1:8050

# Verify in a browser on the tailnet
# https://<machine-name>.<tailnet>.ts.net/
```

If the CLI prints **Serve is not enabled on your tailnet**, a tailnet admin must open the
URL Tailscale prints (or Admin console → DNS / Serve) and enable Serve for the node, then
re-run the `tailscale serve` command.

To remove: `tailscale serve reset`

### Alternative: Caddy (public domain or MODE B)

Use when J2 has a real domain and wants Let's Encrypt, or when MODE B is implemented.

Sample config: [`deploy/Caddyfile`](../deploy/Caddyfile)

```bash
sudo apt install caddy
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
# Set PUBLIC_HOSTNAME in /etc/caddy/caddy.env or export before reload
sudo systemctl reload caddy
```

Caddy reverse-proxies to `127.0.0.1:8050` where Docker exposes the web container.

## First-deploy checklist

1. Clone the repo on the VPS.
2. `cp .env.example .env` — set `APP_ENV=production`, strong `SECRET_KEY`, DB passwords, `ACCESS_MODE=tailscale`.
3. Ensure `tests/fixtures/sample_survey.esx` exists (committed alias of `edge_cases`) or run `python tests/fixtures/build_sample_survey.py`.
4. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`
5. `curl -s http://127.0.0.1:8050/health` — expect `{"status":"ok","env":"production"}`.
6. `tailscale serve --bg --https=443 http://127.0.0.1:8050`
7. Open `https://<tailnet-hostname>/` from a tailnet device.
8. Walk [`docs/uat_checklist.md`](uat_checklist.md) and sign off.

## Nextcloud storage (activation blocked)

The WebDAV client is implemented. `STORAGE_BACKEND=nextcloud` still requires
`NEXTCLOUD_URL`, `NEXTCLOUD_USERNAME`, and `NEXTCLOUD_PASSWORD` — missing creds raise
loudly (no silent fallback to local). Use `STORAGE_BACKEND=local` until Josh provides
access. See [`handoff.md`](handoff.md).

## Operator handoff

Day-2 ownership, branding/template swap, stub activation, and billing note:
[`handoff.md`](handoff.md).

## Troubleshooting

| Symptom | Check |
|---|---|
| `web` container unhealthy | `docker compose logs web` — migration errors, missing `.env` |
| `connection refused` on 8050 | `docker compose ps` — is `web` up? Prod compose binds `127.0.0.1` only |
| App won't start, ACCESS_MODE error | `.env` has valid `ACCESS_MODE`; don't use `shared_password` until MODE B exists |
| 502 from Tailscale Serve | App not listening on `127.0.0.1:8050`; verify health curl locally first |
| `Serve is not enabled on your tailnet` | Admin must enable Serve in the Tailscale console (URL printed by CLI), then re-run `tailscale serve` |
| Port 8050 already in use / web Created exit 128 | Prod override must use `ports: !override` (not append); see `docker-compose.prod.yml` |
| `web` has no Docker network / can't resolve `db` | Port bind failed on first start (e.g. Windows Docker + `127.0.0.1:8050`); `docker compose rm -sf web` then `up -d` again when port is free |
| Uploads/deliverables missing after restart | Ensure `./storage` host directory exists and is mounted |

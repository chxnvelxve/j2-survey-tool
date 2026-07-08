# Production deployment (VPS handoff)

Minimal notes for running the J2 Survey Tool on a VPS with Docker Compose.

## Prerequisites

- Docker and Docker Compose v2
- Copy `.env.example` to `.env` and set production values

## Required environment variables

| Variable | Notes |
|---|---|
| `APP_ENV` | Set to `production` (disables uvicorn `--reload`) |
| `SECRET_KEY` | Change from default |
| `DATABASE_URL` | Postgres connection string |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Used by the `db` service |
| `STORAGE_LOCAL_ROOT` | `/app/storage` inside container |
| `STORAGE_BACKEND` | `local` for now; `nextcloud` is stubbed until Josh provides access |
| Branding vars | `BRAND_*`, `DOCX_TEMPLATE_PATH` |

## Start

```bash
docker compose up --build -d
```

Migrations run automatically via `scripts/entrypoint.sh` on web container start.

## Volumes

- `pgdata` — Postgres data (compose named volume)
- `./storage:/app/storage` — uploaded files and generated reports

Persist `./storage` on the host or map to a dedicated data path.

## Development vs production compose

The bundled `docker-compose.yml` bind-mounts `./:/app` for local hot reload. For production, **remove that volume** so the image runs the baked-in code:

```yaml
volumes:
  - ./storage:/app/storage   # keep storage only
```

## Health check

- JSON: `GET /health` → `{"status":"ok","env":"production"}`
- Compose healthchecks are configured for `web` and `db`

## Reverse proxy / access

Point your reverse proxy (nginx, Caddy) or Tailscale funnel at host port **8050** (maps to container port 8000). TLS termination is out of scope for this handoff — configure on the proxy.

## Nextcloud storage (blocked)

`STORAGE_BACKEND=nextcloud` will fail at startup with a clear error until WebDAV credentials are provided by Josh. Use `local` until then.

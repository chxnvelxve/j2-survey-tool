# J2 Wireless Site Survey Automation Tool

Automates: **field AP photo capture → Ekahau `.esx` ingestion → client-ready Word
report**. Built for J2 Communications; engine designed to re-license to other survey
shops via branding config.

## Quick start
```bash
cp .env.example .env        # fill in values
docker compose up --build   # web + postgres (runs alembic upgrade head on start)
# open http://localhost:8050/        — HTML health page
# open http://localhost:8050/health  — JSON health check
```

Local dev without Docker: `alembic upgrade head` then `uvicorn app.main:app --reload`.

## Architecture
Three swappable stages — `parser → merge → generator` — wrapped in a FastAPI +
HTMX web app. See `docs/ARCHITECTURE.md`.

## For AI agents (Cursor / Claude)
Start with `CLAUDE.md`, then `docs/PHASES.md`. Cursor rules are in `.cursor/rules/`,
reusable skills in `.cursor/skills/`. Work one phase at a time; don't jump ahead.

## Docs
- `docs/ARCHITECTURE.md` — pipeline & stage contracts
- `docs/DOMAIN.md` — entities, roles, glossary
- `docs/PHASES.md` — build phasing (Phase 0 → 6)
- `docs/DECISIONS.md` — decision log + open questions + blockers

## Blocked on Josh / J2
Real `.esx` · sample Word deliverable · Nextcloud access.

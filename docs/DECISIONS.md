# Decision Log

Confirmed decisions from design conversations. Append new ones; don't rewrite history.

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Stack: FastAPI + Jinja2 + HTMX, Postgres, docxtpl, Docker Compose | Single language, no JS build step, cheap to maintain post-handoff |
| 2 | Phone = capture-and-upload only | No on-device processing; keeps phone side trivial |
| 3 | Merge fires on manual push by Drafter | Drafter controls when photos + survey combine |
| 4 | Join key = exact AP name; hard-fail on mismatch | No silent/fuzzy merging; correctness over convenience |
| 5 | Two photos per AP (close + far) | Documentation standard |
| 6 | Override reasons are bulk-applyable w/ autocomplete | Handles 30-AP same-cause case in one action |
| 7 | Multiple `.esx` per Job, parsed per-file | Multi-floor/building sites (warehouses, hospitals) |
| 8 | Attachments modeled as lists | Multiple IDF/LLD fall out for free |
| 9 | Output format = Word `.docx` via repeatable template | J2 hands Word docs to its clients |
| 10 | Branding in config, not engine | Engine re-licensable to other survey shops |
| 11 | Postgres over SQLite | Multi-tenant future without migration pain |
| 12 | Local storage stub now, Nextcloud later | Unblocks dev; real storage waits on Josh |
| 13 | Roles are hats, not people | One person may be Tech + Drafter + Approver |

## Open / unconfirmed (flag inline where relevant)
- Exact Job status/phase names (partly NotebookLM synthesis — confirm w/ Josh).
- Definition of the four readiness gates.
- Billing-phase split & billable-troubleshooting definition (business, not code).

## Blockers on Josh / J2
- Real `.esx` file · Sample deliverable (Word) · Nextcloud access.

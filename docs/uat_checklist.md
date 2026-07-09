# UAT acceptance checklist — J2 Survey Tool v1

One-time manual sign-off that the full pipeline works end-to-end. Use sample fixtures
from `tests/fixtures/` — not a real J2 `.esx` (Phase 8).

## Environments

| Environment | Base URL | How to start |
|---|---|---|
| Local prod-like | `http://127.0.0.1:8050` | `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d` |
| VPS deployed | `https://<tailnet-hostname>/` | Prod compose + Tailscale Serve per [`deploy.md`](deploy.md) |

Set `APP_ENV=production` in `.env` for both.

## Fixture prep (run once if missing)

```bash
python tests/fixtures/build_sample_survey.py
```

Produces `tests/fixtures/sample_survey_clean.esx`, `sample_survey_edge_cases.esx`,
and related variants. `sample_survey.esx` is an alias of `edge_cases` (APs include
**AP-01-NE**, ** AP-02-SW ** with surrounding spaces).

Photos (already in repo):

- `tests/fixtures/gen_photo_close.png`
- `tests/fixtures/gen_photo_far.png`

For step 6, any small file works as an attachment (e.g. a PNG or PDF).

---

## Checklist

### Preamble

- [x] `GET /health` returns `{"status":"ok","env":"production"}`
- [x] Fixture `tests/fixtures/sample_survey.esx` exists

### Workflow

| # | Step | Action | Expected result | Pass |
|---|---|---|---|:---:|
| 1 | Create Job | Jobs → New → name **UAT Sample Job** | Job detail opens; status badge **Awaiting inputs** | [x] |
| 2 | Upload `.esx` | Upload `tests/fixtures/sample_survey.esx` | File listed under Survey files; status → **Inputs uploaded** | [x] |
| 3 | Parse | View parsed survey / AP list | **AP-01-NE** and **AP-02-SW** visible | [x] |
| 4 | Upload photos | Close + far for **AP-01-NE** (use sample PNGs) | Two photos listed with AP name and shot type | [x] |
| 5 | Upload attachment | Upload one attachment file | Attachment count ≥ 1 | [x] |
| 6 | Push merge | Click **Push merge** | Status → **Merged**; flags for **AP-02-SW** (missing photos) | [x] |
| 7 | Resolve flags | Multi-select AP-02 flags; override reason e.g. **Not surveyed this visit** | Status → **Flags resolved**; generate readiness checklist greens | [x] |
| 8 | Generate | Click **Generate report** | Status → **Draft in review**; download link appears | [x] |
| 9 | Download | Click **Download report (.docx)** | File downloads and opens without error | [x] |
| 10 | Approve | Optional approver name; click **Approve** | Status → **Approved**; job locked; approval timestamp shown | [x] |

### Label spot-check (optional)

- [x] Status badges match strings in `app/core/labels.py` (not raw enum values like `draft_in_review`)
- [x] Readiness checklist rows match `GENERATION_GATE_LABELS` / `APPROVAL_GATE_LABELS` in `labels.py`

---

## Sign-off

| Field | Value |
|---|---|
| Date | 2026-07-08 |
| Operator | Cursor agent (HTTP UAT) |
| Environment URL | `https://log-ai-01.tail25aa6a.ts.net/` (also verified `http://127.0.0.1:8050`; UAT job 6) |
| Result | [x] PASS  [ ] FAIL |
| Notes | Prod compose on LOG-AI-01. Tailscale Serve enabled; `/health` returns `{"status":"ok","env":"production"}` over HTTPS. Full pipeline UAT passed via HTTP on job 6. |

If any step fails, note the step number, what you saw, and check `docker compose logs web`.

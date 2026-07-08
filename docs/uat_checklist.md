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

Produces `tests/fixtures/sample_survey.esx` (APs: **AP-01-NE**, **AP-02-SW**).

Photos (already in repo):

- `tests/fixtures/gen_photo_close.png`
- `tests/fixtures/gen_photo_far.png`

For step 6, any small file works as an attachment (e.g. a PNG or PDF).

---

## Checklist

### Preamble

- [ ] `GET /health` returns `{"status":"ok","env":"production"}`
- [ ] Fixture `tests/fixtures/sample_survey.esx` exists

### Workflow

| # | Step | Action | Expected result | Pass |
|---|---|---|---|:---:|
| 1 | Create Job | Jobs → New → name **UAT Sample Job** | Job detail opens; status badge **Awaiting inputs** | [ ] |
| 2 | Upload `.esx` | Upload `tests/fixtures/sample_survey.esx` | File listed under Survey files; status → **Inputs uploaded** | [ ] |
| 3 | Parse | View parsed survey / AP list | **AP-01-NE** and **AP-02-SW** visible | [ ] |
| 4 | Upload photos | Close + far for **AP-01-NE** (use sample PNGs) | Two photos listed with AP name and shot type | [ ] |
| 5 | Upload attachment | Upload one attachment file | Attachment count ≥ 1 | [ ] |
| 6 | Push merge | Click **Push merge** | Status → **Merged**; flags for **AP-02-SW** (missing photos) | [ ] |
| 7 | Resolve flags | Multi-select AP-02 flags; override reason e.g. **Not surveyed this visit** | Status → **Flags resolved**; generate readiness checklist greens | [ ] |
| 8 | Generate | Click **Generate report** | Status → **Draft in review**; download link appears | [ ] |
| 9 | Download | Click **Download report (.docx)** | File downloads and opens without error | [ ] |
| 10 | Approve | Optional approver name; click **Approve** | Status → **Approved**; job locked; approval timestamp shown | [ ] |

### Label spot-check (optional)

- [ ] Status badges match strings in `app/core/labels.py` (not raw enum values like `draft_in_review`)
- [ ] Readiness checklist rows match `GENERATION_GATE_LABELS` / `APPROVAL_GATE_LABELS` in `labels.py`

---

## Sign-off

| Field | Value |
|---|---|
| Date | |
| Operator | |
| Environment URL | |
| Result | [ ] PASS  [ ] FAIL |
| Notes | |

If any step fails, note the step number, what you saw, and check `docker compose logs web`.

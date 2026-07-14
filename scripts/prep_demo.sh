#!/usr/bin/env bash
# Prep fixtures + print demo URLs for the J2 owner meeting.
# Usage: ./scripts/prep_demo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8050}"

echo "==> Building sample .esx fixtures"
"$PYTHON" tests/fixtures/build_sample_survey.py

if [[ ! -f tests/fixtures/gen_photo_close.png || ! -f tests/fixtures/gen_photo_far.png ]]; then
  echo "==> Building sample close/far photos"
  "$PYTHON" tests/fixtures/build_gen_photos.py
else
  echo "==> Sample photos already present"
fi

echo "==> Ensuring Word template + placeholder logo"
"$PYTHON" templates_docx/build_placeholder_template.py
"$PYTHON" scripts/build_placeholder_logo.py

echo
echo "==> Health check: ${BASE_URL}/health"
if curl -fsS -m 5 "${BASE_URL}/health"; then
  echo
  echo "OK — app is up"
else
  echo
  echo "WARN — app not reachable at ${BASE_URL}"
  echo "Start with one of:"
  echo "  docker compose up --build"
  echo "  # or local:"
  echo "  export DATABASE_URL=postgresql+psycopg://j2:changeme@127.0.0.1:5432/j2survey"
  echo "  export STORAGE_LOCAL_ROOT=${ROOT}/storage"
  echo "  export DOCX_TEMPLATE_PATH=${ROOT}/templates_docx/survey_report.docx"
  echo "  export BRAND_LOGO_PATH=${ROOT}/branding/j2_logo_placeholder.png"
  echo "  alembic upgrade head && uvicorn app.main:app --host 127.0.0.1 --port 8050"
fi

echo
echo "==> Demo assets"
echo "  Survey:  ${ROOT}/tests/fixtures/sample_survey.esx"
echo "  Close:   ${ROOT}/tests/fixtures/gen_photo_close.png"
echo "  Far:     ${ROOT}/tests/fixtures/gen_photo_far.png"
echo "  Template:${ROOT}/templates_docx/survey_report.docx"
echo
echo "==> URLs (after you create the staged Job)"
echo "  Jobs list:  ${BASE_URL}/jobs"
echo "  Job detail: ${BASE_URL}/jobs/<JOB_ID>"
echo "  Capture:    ${BASE_URL}/jobs/<JOB_ID>/capture"
echo
echo "Pre-stage checklist:"
echo "  1. Create Job: Acme Warehouse — Jul 2026"
echo "  2. Upload sample_survey.esx; confirm AP-01-NE / AP-02-SW parsed"
echo "  3. Open capture on phone (or DevTools phone width)"
echo "  4. Keep Close/Far PNGs ready; leave AP-02-SW without photos for hard-fail beat"
echo "  5. Save a fallback .docx from rehearsal to Desktop"
echo
echo "Script: docs/meeting_demo_script.md"
echo "Index:  docs/meeting_prep_index.md"
echo "Asks:   docs/meeting_josh_asks.md"
echo
echo "After a cold rehearsal, copy the fallback .docx to Desktop:"
echo "  demo_fallback/Acme_Warehouse_demo_fallback.docx"

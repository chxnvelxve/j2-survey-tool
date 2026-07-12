"""Phase 14b — regression test for the job_status_badge() macro.

Guards against a real bug this phase introduced: job_status_badge() is a
Jinja macro imported into page/partial templates, and it calls
job_status_label(), which is injected per-request via _base_context() in
app/api/jobs.py (a context variable), not registered as a Jinja environment
global. Imported macros only see request context if imported `with context`
— without it, rendering raises UndefinedError as soon as a job exists.

This renders the real template files directly (no DB, no TestClient) so it
stays fast and independent of the Postgres-only DATABASE_URL used elsewhere.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

from app.core.labels import job_status_label
from app.models.enums import JobStatus

_env = Environment(loader=FileSystemLoader("app/templates"))

_STATUS_TOKEN = {
    JobStatus.AWAITING_INPUTS: "warning",
    JobStatus.INPUTS_UPLOADED: "info",
    JobStatus.MERGED: "error",
    JobStatus.FLAGS_RESOLVED: "neutral",
    JobStatus.DRAFT_IN_REVIEW: "info",
    JobStatus.APPROVED: "success",
}


def _fake_job(status: JobStatus) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        name="Test job",
        status=status,
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )


def test_jobs_list_renders_status_chip_for_every_status() -> None:
    template = _env.get_template("pages/jobs/list.html")
    for status, token in _STATUS_TOKEN.items():
        html = template.render(
            jobs=[_fake_job(status)],
            job_status_label=job_status_label,
        )
        assert job_status_label(status) in html
        assert f"badge--status-{token}" in html
        assert f"item-card--status-{token}" in html


def test_jobs_list_renders_with_no_jobs() -> None:
    template = _env.get_template("pages/jobs/list.html")
    html = template.render(jobs=[], job_status_label=job_status_label)
    assert "No jobs yet" in html

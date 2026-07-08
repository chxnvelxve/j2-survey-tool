"""Job CRUD and upload routes."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.storage import Storage, get_storage
from app.models.enums import PhotoShotType
from app.schemas.job import JobCreate, JobListItem, JobRead, job_status_label
from app.schemas.merge import FLAG_TYPE_LABELS
from app.schemas.survey import ParsedSurveyFile, floor_name_for
from app.services.generator.errors import GeneratorError
from app.services.job_flag_resolution import (
    FlagResolutionError,
    NoMergeSnapshotError,
    all_flags_resolved,
    list_past_override_reasons,
    resolve_job_flags,
)
from app.services.job_generate import (
    GenerateNotAllowedError,
    generate_job_report,
    generation_readiness,
)
from app.services.job_merge import merged_job_from_snapshot, push_job_merge
from app.services.jobs import (
    InvalidSurveyFileError,
    JobFileNotFoundError,
    create_job,
    delete_attachment,
    delete_photo,
    delete_survey_file,
    get_job,
    list_jobs,
    upload_attachment,
    upload_photo,
    upload_survey_file,
)
from app.services.survey_parse import parse_job_surveys

router = APIRouter(prefix="/jobs", tags=["jobs"])
templates = Jinja2Templates(directory="app/templates")


def _base_context(**extra: object) -> dict[str, object]:
    return {
        "brand_company_name": settings.BRAND_COMPANY_NAME,
        "brand_primary_color": settings.BRAND_PRIMARY_COLOR,
        "job_status_label": job_status_label,
        "floor_name_for": floor_name_for,
        "flag_type_label": lambda t: FLAG_TYPE_LABELS.get(t, t.value),
        **extra,
    }


def _merged_floor_for(parsed_surveys: list[ParsedSurveyFile], ap_name: str) -> str:
    for pf in parsed_surveys:
        if pf.survey is None:
            continue
        for ap in pf.survey.aps:
            if ap.name == ap_name:
                return floor_name_for(pf.survey, ap.floor_id)
    return "—"


def _job_detail_context(
    db: Session,
    storage: Storage,
    job_id: int,
) -> dict[str, object]:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    job_read = JobRead.model_validate(job)
    parsed_surveys = parse_job_surveys(db, storage, job)
    merged_job = merged_job_from_snapshot(job)
    generate_ready, generate_block_reason = generation_readiness(job, merged_job)
    return _base_context(
        job=job_read,
        parsed_surveys=parsed_surveys,
        merged_job=merged_job,
        merged_floor_for=lambda name: _merged_floor_for(parsed_surveys, name),
        past_override_reasons=list_past_override_reasons(db),
        generate_ready=generate_ready,
        generate_block_reason=generate_block_reason,
        flags_all_resolved=all_flags_resolved(merged_job) if merged_job else False,
    )


@router.get("", response_class=HTMLResponse)
def jobs_list(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    jobs = [JobListItem.model_validate(j) for j in list_jobs(db)]
    return templates.TemplateResponse(
        request,
        "pages/jobs/list.html",
        _base_context(jobs=jobs),
    )


@router.get("/new", response_class=HTMLResponse)
def jobs_new_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/jobs/new.html",
        _base_context(),
    )


@router.post("")
def jobs_create(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    payload = JobCreate(name=name)
    job = create_job(db, payload.name)
    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


@router.get("/{job_id}", response_class=HTMLResponse)
def jobs_detail(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "pages/jobs/detail.html",
        ctx,
    )


@router.post("/{job_id}/parse-surveys", response_class=HTMLResponse)
def jobs_parse_surveys(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/parsed_aps.html",
        ctx,
    )


@router.post("/{job_id}/merge", response_class=HTMLResponse)
def jobs_push_merge(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    push_job_merge(db, storage, job)
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/merged_results.html",
        ctx,
    )


@router.post("/{job_id}/generate", response_class=HTMLResponse)
def jobs_generate_report(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    ctx = _job_detail_context(db, storage, job_id)
    try:
        generate_job_report(db, storage, job)
        ctx = _job_detail_context(db, storage, job_id)
    except (NoMergeSnapshotError, GenerateNotAllowedError, GeneratorError) as exc:
        ctx["generate_error"] = str(exc)
    return templates.TemplateResponse(
        request,
        "partials/jobs/generate_section.html",
        ctx,
    )


@router.get("/{job_id}/download")
def jobs_download_report(
    job_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> StreamingResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.deliverable_path:
        raise HTTPException(status_code=404, detail="No deliverable for this job")
    try:
        file_handle = storage.open(job.deliverable_path)
    except OSError as exc:
        raise HTTPException(status_code=404, detail="Deliverable file not found") from exc
    safe_name = job.name.replace('"', "'")
    return StreamingResponse(
        file_handle,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_report.docx"'},
    )


@router.post("/{job_id}/resolve-flags", response_class=HTMLResponse)
def jobs_resolve_flags(
    request: Request,
    job_id: int,
    flag_indices: list[int] = Form(default=[]),
    override_reason: str = Form(default=""),
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    ctx = _job_detail_context(db, storage, job_id)
    try:
        resolve_job_flags(db, job, flag_indices, override_reason)
        ctx = _job_detail_context(db, storage, job_id)
    except (NoMergeSnapshotError, FlagResolutionError) as exc:
        ctx["flag_resolve_error"] = str(exc)
    return templates.TemplateResponse(
        request,
        "partials/jobs/merged_results.html",
        ctx,
    )


@router.post("/{job_id}/survey-files", response_class=HTMLResponse)
async def jobs_upload_survey_file(
    request: Request,
    job_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        upload_survey_file(db, storage, job, file)
    except InvalidSurveyFileError as exc:
        ctx = _job_detail_context(db, storage, job_id)
        ctx["survey_upload_error"] = str(exc)
        return templates.TemplateResponse(
            request,
            "partials/jobs/survey_files.html",
            ctx,
        )
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/survey_files.html",
        ctx,
    )


@router.post("/{job_id}/photos", response_class=HTMLResponse)
async def jobs_upload_photo(
    request: Request,
    job_id: int,
    file: UploadFile,
    ap_name: str = Form(...),
    shot_type: PhotoShotType = Form(...),
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    upload_photo(db, storage, job, file, ap_name, shot_type)
    job = get_job(db, job_id)
    assert job is not None
    job_read = JobRead.model_validate(job)
    return templates.TemplateResponse(
        request,
        "partials/jobs/photos.html",
        _base_context(job=job_read),
    )


@router.post("/{job_id}/attachments", response_class=HTMLResponse)
async def jobs_upload_attachment(
    request: Request,
    job_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    upload_attachment(db, storage, job, file)
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/attachments.html",
        ctx,
    )


@router.delete("/{job_id}/survey-files/{survey_file_id}", response_class=HTMLResponse)
def jobs_delete_survey_file(
    request: Request,
    job_id: int,
    survey_file_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        delete_survey_file(db, storage, job, survey_file_id)
    except JobFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/survey_files.html",
        ctx,
    )


@router.delete("/{job_id}/photos/{photo_id}", response_class=HTMLResponse)
def jobs_delete_photo(
    request: Request,
    job_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        delete_photo(db, storage, job, photo_id)
    except JobFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/photos.html",
        ctx,
    )


@router.delete("/{job_id}/attachments/{attachment_id}", response_class=HTMLResponse)
def jobs_delete_attachment(
    request: Request,
    job_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    storage: Storage = Depends(get_storage),
) -> HTMLResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        delete_attachment(db, storage, job, attachment_id)
    except JobFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ctx = _job_detail_context(db, storage, job_id)
    return templates.TemplateResponse(
        request,
        "partials/jobs/attachments.html",
        ctx,
    )

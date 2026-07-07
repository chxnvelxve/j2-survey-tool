"""Job CRUD and upload routes."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.storage import Storage, get_storage
from app.models.enums import PhotoShotType
from app.schemas.job import JobCreate, JobListItem, JobRead, job_status_label
from app.schemas.survey import floor_name_for
from app.services.jobs import (
    DuplicatePhotoError,
    create_job,
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
        **extra,
    }


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
    return _base_context(job=job_read, parsed_surveys=parsed_surveys)


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
    upload_survey_file(db, storage, job, file)
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
    try:
        upload_photo(db, storage, job, file, ap_name, shot_type)
    except DuplicatePhotoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
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
    job = get_job(db, job_id)
    assert job is not None
    job_read = JobRead.model_validate(job)
    return templates.TemplateResponse(
        request,
        "partials/jobs/attachments.html",
        _base_context(job=job_read),
    )

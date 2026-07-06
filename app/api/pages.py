"""HTML page routes."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def health_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/health.html",
        {
            "brand_company_name": settings.BRAND_COMPANY_NAME,
            "brand_primary_color": settings.BRAND_PRIMARY_COLOR,
            "app_env": settings.APP_ENV,
        },
    )

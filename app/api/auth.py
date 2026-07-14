"""Shared-password login/logout routes (ACCESS_MODE=shared_password)."""
from __future__ import annotations

import secrets
from urllib.parse import urlparse

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SESSION_AUTH_KEY = "authenticated"


def _safe_next(next_url: str | None) -> str:
    """Allow only same-origin relative paths (no scheme/host open redirects)."""
    if not next_url:
        return "/"
    parsed = urlparse(next_url)
    if parsed.scheme or parsed.netloc:
        return "/"
    if not next_url.startswith("/") or next_url.startswith("//"):
        return "/"
    return next_url


def _password_matches(submitted: str, expected: str) -> bool:
    if not expected:
        return False
    # compare_digest requires equal length; reject length mismatch without raising.
    if len(submitted) != len(expected):
        secrets.compare_digest(expected, expected)
        return False
    return secrets.compare_digest(submitted, expected)


def _login_context(
    *,
    error: str | None = None,
    next_url: str = "/",
) -> dict:
    return {
        "brand_company_name": settings.BRAND_COMPANY_NAME,
        "brand_primary_color": settings.BRAND_PRIMARY_COLOR,
        "error": error,
        "next_url": next_url,
    }


@router.get("/login", response_class=HTMLResponse, response_model=None)
def login_get(request: Request, next: str | None = None):
    # Mode A has no SessionMiddleware — never touch request.session there.
    if settings.ACCESS_MODE != "shared_password":
        return RedirectResponse(url="/", status_code=303)
    if request.session.get(SESSION_AUTH_KEY):
        return RedirectResponse(url=_safe_next(next), status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        _login_context(next_url=_safe_next(next)),
    )


@router.post("/login", response_class=HTMLResponse, response_model=None)
def login_post(
    request: Request,
    password: str = Form(...),
    next: str = Form("/"),
):
    if settings.ACCESS_MODE != "shared_password":
        return RedirectResponse(url="/", status_code=303)
    if not _password_matches(password, settings.SHARED_ACCESS_PASSWORD):
        return templates.TemplateResponse(
            request,
            "login.html",
            _login_context(
                error="Incorrect password.",
                next_url=_safe_next(next),
            ),
            status_code=200,
        )

    request.session[SESSION_AUTH_KEY] = True
    return RedirectResponse(url=_safe_next(next), status_code=303)


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    if settings.ACCESS_MODE == "shared_password":
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/", status_code=303)

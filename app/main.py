"""FastAPI app factory + entrypoint. Phase 0 scaffold."""
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import SESSION_AUTH_KEY, router as auth_router
from app.api.jobs import router as jobs_router
from app.api.pages import router as pages_router
from app.core.config import settings

_EXEMPT_EXACT = frozenset({"/health", "/login", "/logout"})


def _is_exempt(path: str) -> bool:
    if path in _EXEMPT_EXACT:
        return True
    return path.startswith("/static")


def _login_redirect_for(request: Request) -> str:
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"
    return f"/login?next={quote(path, safe='')}"


def create_app() -> FastAPI:
    app = FastAPI(title="J2 Survey Tool")

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "env": settings.APP_ENV})

    app.include_router(auth_router)
    app.include_router(pages_router)
    app.include_router(jobs_router)

    if settings.ACCESS_MODE == "shared_password":
        # Import only for Mode B (itsdangerous / SessionMiddleware).
        from starlette.middleware.sessions import SessionMiddleware

        # Gate runs inside the stack; SessionMiddleware must wrap it (added last = outermost).
        @app.middleware("http")
        async def shared_password_gate(request: Request, call_next):
            if settings.ACCESS_MODE != "shared_password":
                return await call_next(request)
            if _is_exempt(request.url.path):
                return await call_next(request)
            if request.session.get(SESSION_AUTH_KEY):
                return await call_next(request)
            return RedirectResponse(url=_login_redirect_for(request), status_code=303)

        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.SECRET_KEY,
            same_site="lax",
            https_only=settings.APP_ENV == "production",
        )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app


app = create_app()

"""FastAPI app factory + entrypoint. Phase 0 scaffold."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.jobs import router as jobs_router
from app.api.pages import router as pages_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="J2 Survey Tool")

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "env": settings.APP_ENV})

    app.include_router(pages_router)
    app.include_router(jobs_router)
    return app


app = create_app()

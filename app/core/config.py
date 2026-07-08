"""Central settings. Everything env-driven — no literals for paths/secrets/branding."""
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AccessMode = Literal["tailscale", "shared_password"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "postgresql+psycopg://j2:changeme@db:5432/j2survey"

    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_ROOT: str = "/app/storage"

    # Nextcloud — blocked on Josh (#12); stub raises if STORAGE_BACKEND=nextcloud.
    NEXTCLOUD_URL: str = ""
    NEXTCLOUD_USERNAME: str = ""
    NEXTCLOUD_PASSWORD: str = ""
    NEXTCLOUD_WEBDAV_ROOT: str = ""

    # Branding — kept OUT of engine code so the tool re-skins per client.
    BRAND_COMPANY_NAME: str = "J2 Communications"
    BRAND_LOGO_PATH: str = ""
    BRAND_PRIMARY_COLOR: str = "#0B3D91"

    DOCX_TEMPLATE_PATH: str = "/app/templates_docx/survey_report.docx"

    # Deploy / access (Phase 7)
    PUBLIC_HOSTNAME: str = "survey.example.com"
    ACCESS_MODE: AccessMode = "tailscale"
    SHARED_ACCESS_PASSWORD: str = ""

    @model_validator(mode="after")
    def validate_access_mode(self) -> "Settings":
        if self.ACCESS_MODE == "shared_password" and not self.SHARED_ACCESS_PASSWORD.strip():
            raise ValueError(
                "ACCESS_MODE=shared_password requires SHARED_ACCESS_PASSWORD to be set. "
                "Shared-password gate is not implemented in v1 — use ACCESS_MODE=tailscale "
                "or set the password when MODE B is enabled.",
            )
        return self


settings = Settings()

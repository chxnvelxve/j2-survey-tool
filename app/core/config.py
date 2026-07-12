"""Central settings. Everything env-driven — no literals for paths/secrets/branding."""
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AccessMode = Literal["tailscale", "shared_password"]

# Default placeholder — Mode B refuses to start if SECRET_KEY is still this value.
_DEFAULT_SECRET_KEY = "changeme"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    DATABASE_URL: str = "postgresql+psycopg://j2:changeme@db:5432/j2survey"

    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_ROOT: str = "/app/storage"

    # Nextcloud WebDAV — shell implemented; live activation blocked on Josh (#12).
    # STORAGE_BACKEND=nextcloud requires URL + USERNAME + PASSWORD (no silent local fallback).
    NEXTCLOUD_URL: str = ""
    NEXTCLOUD_USERNAME: str = ""
    NEXTCLOUD_PASSWORD: str = ""
    NEXTCLOUD_WEBDAV_ROOT: str = ""

    # Branding — kept OUT of engine code so the tool re-skins per client.
    # 🟡 Phase 9 sample defaults — swap real J2 assets/hex on activation.
    BRAND_COMPANY_NAME: str = "J2 Communications"
    BRAND_LOGO_PATH: str = "branding/j2_logo_placeholder.png"
    BRAND_PRIMARY_COLOR: str = "#1F4E79"

    DOCX_TEMPLATE_PATH: str = "/app/templates_docx/survey_report.docx"

    # Deploy / access (Phase 7)
    PUBLIC_HOSTNAME: str = "survey.example.com"
    ACCESS_MODE: AccessMode = "tailscale"
    SHARED_ACCESS_PASSWORD: str = ""

    @model_validator(mode="after")
    def validate_access_mode(self) -> "Settings":
        if self.ACCESS_MODE != "shared_password":
            return self
        if not self.SHARED_ACCESS_PASSWORD.strip():
            raise ValueError(
                "ACCESS_MODE=shared_password requires SHARED_ACCESS_PASSWORD to be set. "
                "Use ACCESS_MODE=tailscale (v1 default) or set SHARED_ACCESS_PASSWORD.",
            )
        secret = self.SECRET_KEY.strip()
        if not secret or secret == _DEFAULT_SECRET_KEY:
            raise ValueError(
                "ACCESS_MODE=shared_password requires SECRET_KEY to be set to a "
                "non-default value (not blank or 'changeme'). "
                "The session cookie is signed with SECRET_KEY.",
            )
        return self


settings = Settings()

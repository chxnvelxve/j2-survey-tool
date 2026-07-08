"""Central settings. Everything env-driven — no literals for paths/secrets/branding."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "postgresql+psycopg://j2:changeme@db:5432/j2survey"

    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_ROOT: str = "/app/storage"

    # Branding — kept OUT of engine code so the tool re-skins per client.
    BRAND_COMPANY_NAME: str = "J2 Communications"
    BRAND_LOGO_PATH: str = ""
    BRAND_PRIMARY_COLOR: str = "#0B3D91"

    DOCX_TEMPLATE_PATH: str = "/app/templates_docx/survey_report.docx"


settings = Settings()

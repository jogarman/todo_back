from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
import os


class Settings(BaseSettings):
    app_env: str = Field(default="development")
    app_port: int = Field(default=8000)
    gcp_project_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("TODO_GCP_PROJECT_ID", "GCP_PROJECT_ID"),
    )
    google_application_credentials: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "TODO_GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS"
        ),
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# Ensure GOOGLE_APPLICATION_CREDENTIALS is set for Google SDK if only TODO_* is provided
if (
    settings.google_application_credentials
    and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials

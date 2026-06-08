from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    PROJECT_DIR,
)


class Settings(BaseSettings):
    secret_key: SecretStr
    database_url: str
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    debug: bool = False
    environment: str = "development"
    redis_url: str = "redis://127.0.0.1:6379/0"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"  # noqa: S105
    postgres_db: str = "learn_fastapi"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: SecretStr | None = None
    cloudinary_api_secret: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()  # ty:ignore[missing-argument]

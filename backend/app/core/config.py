from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://brokeros:brokeros_dev@localhost:5432/brokeros"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Security
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_STRING"
    access_token_expire_minutes: int = 480  # 8 hours
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # Development secret (used to detect unsafe production config)
    _DEV_SECRET: str = "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_STRING"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate_production_config(self) -> None:
        """Validate that production configuration is safe.

        Raises:
            RuntimeError: If production is running with development secrets.
        """
        if self.is_production and self.secret_key == self._DEV_SECRET:
            raise RuntimeError(
                "Production environment cannot use the default development SECRET_KEY. "
                "Set a secure SECRET_KEY environment variable."
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_config()
    return settings

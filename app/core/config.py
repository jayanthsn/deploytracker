import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/deploytracker"

    @property
    def async_database_url(self) -> str:
        raise NotImplementedError

    @property
    def is_production(self) -> bool:
        return False


class DevelopmentSettings(BaseAppSettings):
    APP_ENV: Literal["development"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    DB_PATH: str = "./deploytracker.db"

    @property
    def async_database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.DB_PATH}"


class TestingSettings(BaseAppSettings):
    # Isolated from .env — all values are hardcoded defaults for test runs
    model_config = SettingsConfigDict(env_file=None)

    APP_ENV: Literal["testing"] = "testing"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    DB_PATH: str = "./deploytracker_test.db"

    @property
    def async_database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.DB_PATH}"


class ProductionSettings(BaseAppSettings):
    # TODO: Set APP_ENV=production in the production environment
    # TODO: Set DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db> pointing to the PostgreSQL server
    APP_ENV: Literal["production"] = "production"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @property
    def async_database_url(self) -> str:
        # TODO: Ensure DATABASE_URL is configured in the production environment before deploying
        return self.DATABASE_URL

    @property
    def is_production(self) -> bool:
        return True


def get_settings() -> BaseAppSettings:
    match os.getenv("APP_ENV", "development"):
        case "testing":
            return TestingSettings()
        case "production":
            return ProductionSettings()
        case _:
            return DevelopmentSettings()


settings: BaseAppSettings = get_settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: Literal["development", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # SQLite (development)
    DB_PATH: str = "./deploytracker.db"

    # PostgreSQL (production)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/deploytracker"

    @property
    def async_database_url(self) -> str:
        if self.APP_ENV == "production":
            return self.DATABASE_URL
        return f"sqlite+aiosqlite:///{self.DB_PATH}"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()

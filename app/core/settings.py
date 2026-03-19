from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinGuard"
    app_version: str = "1.1.0"
    debug: bool = False
    api_prefix: str = "/api"
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    database_url: str | None = None
    vercel: str | None = Field(default=None, alias="VERCEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def templates_dir(self) -> Path:
        return self.project_root / "templates"

    @property
    def static_dir(self) -> Path:
        return self.project_root / "static"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            if self.database_url.startswith("postgres://"):
                return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
            if self.database_url.startswith("postgresql://"):
                return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
            return self.database_url
        if self.vercel:
            return "sqlite:////tmp/finguard.db"
        return f"sqlite:///{self.project_root / 'finguard.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

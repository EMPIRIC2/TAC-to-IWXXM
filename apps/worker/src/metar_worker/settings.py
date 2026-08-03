"""Worker settings from environment (ADR-018 amend / ADR-033 / F30)."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Runtime configuration for the F8 ingest worker."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(default="", validation_alias="DATABASE_URL")
    ingest_poller_url: str = Field(default="", validation_alias="INGEST_POLLER_URL")
    ingest_poll_interval_sec: float = Field(
        default=30.0,
        validation_alias="INGEST_POLL_INTERVAL_SEC",
    )
    ingest_profile: str = Field(default="annex3", validation_alias="INGEST_PROFILE")
    iwxxm_version: str = Field(default="2025-2", validation_alias="IWXXM_VERSION")
    once: bool = Field(
        default=False,
        validation_alias="INGEST_ONCE",
        description="When true, poll once and exit (tests / smoke).",
    )


__all__ = ["WorkerSettings"]

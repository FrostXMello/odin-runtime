"""Typed environment configuration — kernel reads runtime behavior from here only."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files() -> list[str]:
    """Search project roots for .env."""
    candidates = [
        Path(".env"),
        Path("odin/.env"),
        Path("odin/backend/.env"),
    ]
    return [str(p) for p in candidates if p.exists()]


class OdinEnvironmentConfig(BaseSettings):
    """
    Centralized runtime control via environment variables.

    Safe defaults: VALKYRIE off, desktop control off, autonomy level 1.
    """

    model_config = SettingsConfigDict(
        env_file=_env_files() or ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    runtime_mode: Literal["development", "staging", "production"] = Field(
        default="development", validation_alias="ODIN_RUNTIME_MODE"
    )
    kernel_enabled: bool = Field(default=True, validation_alias="ODIN_KERNEL_ENABLED")

    model_primary: str = Field(default="gemini", validation_alias="ODIN_MODEL_PRIMARY")
    model_fallback: str = Field(default="deepseek-r1", validation_alias="ODIN_MODEL_FALLBACK")
    model_coder: str = Field(default="deepseek-coder", validation_alias="ODIN_MODEL_CODER")

    local_models_enabled: bool = Field(default=True, validation_alias="ODIN_LOCAL_MODELS_ENABLED")
    ollama_url: str = Field(default="http://localhost:11434", validation_alias="ODIN_OLLAMA_URL")

    live_loop_enabled: bool = Field(default=False, validation_alias="ODIN_LIVE_LOOP_ENABLED")
    live_loop_interval_seconds: float = Field(
        default=5.0, validation_alias="ODIN_LIVE_LOOP_INTERVAL_SECONDS"
    )
    conscious_loop_enabled: bool = Field(default=False, validation_alias="ODIN_CONSCIOUS_LOOP_ENABLED")

    autonomy_level: int = Field(default=1, validation_alias="ODIN_AUTONOMY_LEVEL")
    desktop_control_enabled: bool = Field(
        default=False, validation_alias="ODIN_DESKTOP_CONTROL_ENABLED"
    )

    signal_bus_enabled: bool = Field(default=True, validation_alias="ODIN_SIGNAL_BUS_ENABLED")
    stability_loop_enabled: bool = Field(default=True, validation_alias="ODIN_STABILITY_LOOP_ENABLED")

    valkyrie_enabled: bool = Field(default=False, validation_alias="ODIN_VALKYRIE_ENABLED")

    @field_validator("autonomy_level")
    @classmethod
    def clamp_autonomy(cls, v: int) -> int:
        return max(0, min(4, v))

    @field_validator("runtime_mode", mode="before")
    @classmethod
    def normalize_mode(cls, v: str) -> str:
        return str(v).lower() if v else "development"

    def snapshot(self) -> dict:
        return {
            "runtime_mode": self.runtime_mode,
            "kernel_enabled": self.kernel_enabled,
            "model_primary": self.model_primary,
            "model_fallback": self.model_fallback,
            "model_coder": self.model_coder,
            "local_models_enabled": self.local_models_enabled,
            "live_loop_enabled": self.live_loop_enabled,
            "autonomy_level": self.autonomy_level,
            "desktop_control_enabled": self.desktop_control_enabled,
            "signal_bus_enabled": self.signal_bus_enabled,
            "stability_loop_enabled": self.stability_loop_enabled,
            "valkyrie_enabled": self.valkyrie_enabled,
            "gemini_configured": bool(self.gemini_api_key),
        }

    def allows_desktop_execution(self) -> bool:
        return self.valkyrie_enabled and self.desktop_control_enabled

    def allows_os_mutation(self) -> bool:
        return self.allows_desktop_execution()


@lru_cache
def get_environment_config() -> OdinEnvironmentConfig:
    return OdinEnvironmentConfig()

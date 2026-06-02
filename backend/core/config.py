from contextvars import ContextVar
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_kubectl_context: ContextVar[str | None] = ContextVar("kubectl_context", default=None)


def set_kubectl_context(context: str | None):
    """Set the active kubectl context for the current execution scope."""
    return _kubectl_context.set(context)


def reset_kubectl_context(token) -> None:
    """Reset kubectl context variable."""
    _kubectl_context.reset(token)


def get_kubectl_context() -> str | None:
    """Return the active kubectl context, if any."""
    return _kubectl_context.get()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ai-kubernetes-agent"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]

    openrouter_api_key: str = ""
    openrouter_model: str = ""
    kubeconfig_path: str = ""

    auth_enabled: bool = True
    insforge_url: str = ""
    insforge_service_key: str = ""

    investigation_history_table: str = "investigation_history"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

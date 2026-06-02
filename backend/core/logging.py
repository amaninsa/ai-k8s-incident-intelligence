import os
import sys
from pathlib import Path

from loguru import logger

from core.config import settings


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )


def log_startup() -> None:
    api_key_loaded = "yes" if settings.openrouter_api_key else "no"
    cwd = os.getcwd()
    backend_env = Path(__file__).resolve().parent.parent / ".env"
    backend_env_loaded = backend_env.is_file() and Path(cwd, ".env").resolve() == backend_env.resolve()

    logger.info(f"Application name: {settings.app_name}")
    logger.info(f"Environment loaded: {settings.environment}")
    logger.info(f"AUTH_ENABLED={str(settings.auth_enabled).lower()}")
    logger.info(f"INSFORGE_URL={settings.insforge_url or '(not set)'}")
    logger.info(f"cwd={cwd}")
    logger.info(f"backend/.env loaded={'yes' if backend_env_loaded else 'no'}")
    logger.info(f"OPENROUTER_API_KEY loaded: {api_key_loaded}")
    logger.info(f"OPENROUTER_MODEL value: {settings.openrouter_model or '(not set)'}")
    logger.info(f"KUBECONFIG_PATH value: {settings.kubeconfig_path or '(not set)'}")

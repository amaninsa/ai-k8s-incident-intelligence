"""OpenRouter LLM client for Kubernetes diagnosis generation."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx
from loguru import logger

from ai.exceptions import OpenRouterAPIError, OpenRouterConfigError, OpenRouterTimeoutError
from core.config import settings

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.0


def _validate_config() -> None:
    if not settings.openrouter_api_key:
        raise OpenRouterConfigError("OpenRouter API key is not configured")
    if not settings.openrouter_model:
        raise OpenRouterConfigError("OpenRouter model is not configured")


def _build_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ai-kubernetes-agent",
        "X-Title": settings.app_name,
    }


def _extract_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise OpenRouterAPIError("OpenRouter returned no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise OpenRouterAPIError("OpenRouter returned empty content")

    return content.strip()


def generate_completion(messages: list[dict[str, str]]) -> str:
    """
    Send a chat completion request to OpenRouter.

    Raises:
        OpenRouterConfigError: Missing API key or model.
        OpenRouterTimeoutError: Request timed out.
        OpenRouterAPIError: Non-success HTTP response or malformed payload.
    """
    _validate_config()

    request_body = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    timeout = DEFAULT_TIMEOUT_SECONDS
    max_retries = DEFAULT_MAX_RETRIES
    last_error: Exception | None = None

    logger.info("OpenRouter request started for model: {}", settings.openrouter_model)

    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    OPENROUTER_CHAT_URL,
                    headers=_build_headers(),
                    json=request_body,
                )
        except httpx.TimeoutException as exc:
            last_error = OpenRouterTimeoutError("OpenRouter request timed out")
            logger.warning(
                "OpenRouter request timed out (attempt {}/{})",
                attempt + 1,
                max_retries + 1,
            )
            if attempt >= max_retries:
                raise last_error from exc
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue
        except httpx.HTTPError as exc:
            last_error = OpenRouterAPIError(f"OpenRouter request failed: {exc}")
            logger.warning(
                "OpenRouter HTTP error (attempt {}/{}): {}",
                attempt + 1,
                max_retries + 1,
                exc,
            )
            if attempt >= max_retries:
                raise last_error from exc
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue

        if response.status_code in {401, 403}:
            logger.error("OpenRouter authentication failed with status {}", response.status_code)
            raise OpenRouterAPIError("OpenRouter authentication failed. Check your API key.")

        if response.status_code == 429:
            logger.warning("OpenRouter rate limit hit (attempt {}/{})", attempt + 1, max_retries + 1)
            last_error = OpenRouterAPIError("OpenRouter rate limit exceeded")
            if attempt >= max_retries:
                raise last_error
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue

        if response.status_code >= 500:
            logger.warning(
                "OpenRouter server error {} (attempt {}/{})",
                response.status_code,
                attempt + 1,
                max_retries + 1,
            )
            last_error = OpenRouterAPIError(f"OpenRouter server error: {response.status_code}")
            if attempt >= max_retries:
                raise last_error
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue

        if response.status_code >= 400:
            detail = _safe_error_detail(response)
            logger.error("OpenRouter request failed with status {}: {}", response.status_code, detail)
            raise OpenRouterAPIError(detail)

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise OpenRouterAPIError("OpenRouter returned invalid JSON") from exc

        content = _extract_content(payload)
        logger.info("OpenRouter request succeeded")
        return content

    if last_error:
        raise last_error
    raise OpenRouterAPIError("OpenRouter request failed after retries")


def _safe_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except json.JSONDecodeError:
        text = response.text.strip()
        return text[:300] if text else f"OpenRouter request failed with status {response.status_code}"

    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if message:
            return str(message)[:300]
    if isinstance(error, str):
        return error[:300]

    return f"OpenRouter request failed with status {response.status_code}"

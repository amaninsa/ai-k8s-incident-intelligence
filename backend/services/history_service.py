"""Persist and retrieve investigation history via InsForge database."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from loguru import logger

from core.config import settings


LOCAL_DEV_TOKEN = "local-dev-token"


def _records_url() -> str:
    return (
        f"{settings.insforge_url.rstrip('/')}/api/database/records/"
        f"{settings.investigation_history_table}"
    )


def _headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _extract_namespace(investigation: dict[str, Any]) -> str | None:
    pods = investigation.get("pods", {}).get("problematic_pods") or []
    if pods:
        return pods[0].get("namespace")
    events = investigation.get("events", {}).get("critical_events") or []
    if events:
        return events[0].get("namespace")
    return None


async def save_investigation_history(
    *,
    user_id: str,
    access_token: str,
    cluster: str,
    status: str,
    diagnosis: dict[str, Any],
    investigation: dict[str, Any],
) -> dict[str, Any] | None:
    """Store an investigation record in InsForge."""
    if not settings.insforge_url:
        logger.warning("InsForge URL not configured; skipping history persistence")
        return None

    if not access_token or access_token == LOCAL_DEV_TOKEN:
        logger.warning(
            "Skipping history persistence: a valid InsForge user JWT is required "
            "(sign in on the frontend and restart the backend after updating auth settings)"
        )
        return None

    record = {
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cluster": cluster,
        "namespace": _extract_namespace(investigation),
        "root_cause": diagnosis.get("root_cause", ""),
        "confidence": diagnosis.get("confidence", 0),
        "status": status,
        "diagnosis": diagnosis,
        "investigation": investigation,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _records_url(),
                headers=_headers(access_token),
                json=[record],
            )
    except httpx.HTTPError as exc:
        logger.error("Failed to save investigation history: {}", exc)
        return None

    if response.status_code >= 400:
        logger.error(
            "InsForge history insert failed with status {}: {}",
            response.status_code,
            response.text[:300],
        )
        return None

    payload = response.json()
    if isinstance(payload, list) and payload:
        return payload[0]
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list) and data:
            return data[0]
    return record


async def list_investigation_history(access_token: str, limit: int = 20) -> list[dict[str, Any]]:
    """Return recent investigations for the authenticated user."""
    if not settings.insforge_url:
        return []

    if not access_token or access_token == LOCAL_DEV_TOKEN:
        logger.warning(
            "Skipping history query: a valid InsForge user JWT is required "
            "(sign in on the frontend and restart the backend after updating auth settings)"
        )
        return []

    params = {
        "order": "timestamp.desc",
        "limit": str(limit),
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                _records_url(),
                headers=_headers(access_token),
                params=params,
            )
    except httpx.HTTPError as exc:
        logger.error("Failed to list investigation history: {}", exc)
        return []

    if response.status_code >= 400:
        logger.error(
            "InsForge history query failed with status {}: {}",
            response.status_code,
            response.text[:300],
        )
        return []

    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return data
    return []


async def get_investigation_history_record(
    record_id: str,
    access_token: str,
) -> dict[str, Any] | None:
    """Fetch a single investigation record by id."""
    if not settings.insforge_url:
        return None

    url = f"{_records_url()}/{record_id}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=_headers(access_token))
    except httpx.HTTPError:
        return None

    if response.status_code >= 400:
        return None

    payload = response.json()
    if isinstance(payload, dict):
        return payload.get("data") or payload
    return None

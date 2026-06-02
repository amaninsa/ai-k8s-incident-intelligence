"""InsForge authentication helpers for protected API routes."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

security = HTTPBearer(auto_error=False)

LOCAL_DEV_TOKEN = "local-dev-token"
LOCAL_DEV_USER = {"id": "local-dev-user", "email": "dev@local"}


def _extract_user(payload: dict[str, Any]) -> dict[str, Any] | None:
    user = payload.get("user") or payload.get("data", {}).get("user") or payload
    if isinstance(user, dict) and user.get("id"):
        return user
    return None


async def verify_insforge_token(token: str) -> dict[str, Any] | None:
    """Validate a user access token against InsForge."""
    if not settings.insforge_url or not token or token == LOCAL_DEV_TOKEN:
        return None

    url = f"{settings.insforge_url.rstrip('/')}/api/auth/sessions/current"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None

    return _extract_user(response.json())


async def resolve_insforge_session(
    credentials: HTTPAuthorizationCredentials | None = None,
    *,
    query_token: str | None = None,
) -> tuple[dict[str, Any], str] | None:
    """Return verified InsForge user and JWT for database API calls."""
    token: str | None = None
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    elif query_token:
        token = query_token

    if not token or token == LOCAL_DEV_TOKEN:
        return None

    user = await verify_insforge_token(token)
    if user is None:
        return None

    return user, token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Require a valid InsForge session for protected routes."""
    session = await resolve_insforge_session(credentials)
    if session:
        return session[0]

    if not settings.auth_enabled:
        return LOCAL_DEV_USER.copy()

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")

    raise HTTPException(status_code=401, detail="Invalid or expired session")


def get_access_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Return the InsForge JWT used for database API calls."""
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        if token and token != LOCAL_DEV_TOKEN:
            return token

    if not settings.auth_enabled:
        return LOCAL_DEV_TOKEN

    raise HTTPException(status_code=401, detail="Authentication required")


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any] | None:
    """Return the current user when authenticated, otherwise None."""
    session = await resolve_insforge_session(credentials)
    if session:
        return session[0]

    if not settings.auth_enabled:
        return LOCAL_DEV_USER.copy()

    return None

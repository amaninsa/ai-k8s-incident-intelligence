from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.auth import get_current_user, resolve_insforge_session
from services.history_service import list_investigation_history

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/history")
async def get_history(
    _user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Return recent investigations for the authenticated user."""
    session = await resolve_insforge_session(credentials)
    if not session:
        return {"history": []}

    _history_user, access_token = session
    records = await list_investigation_history(access_token)
    summaries = [
        {
            "id": record.get("id"),
            "timestamp": record.get("timestamp"),
            "cluster": record.get("cluster"),
            "namespace": record.get("namespace"),
            "root_cause": record.get("root_cause"),
            "confidence": record.get("confidence"),
            "status": record.get("status"),
        }
        for record in records
    ]
    return {"history": summaries}

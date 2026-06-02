from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.auth import get_current_user, resolve_insforge_session
from services.export_service import export_as_json, export_as_markdown, export_as_pdf_bytes
from services.history_service import get_investigation_history_record

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/export/{record_id}")
async def export_investigation(
    record_id: str,
    format: str = Query("json", pattern="^(json|markdown|pdf)$"),
    _user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Response:
    """Export a stored investigation in JSON, Markdown, or PDF format."""
    session = await resolve_insforge_session(credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Valid InsForge session required")

    _history_user, access_token = session
    record = await get_investigation_history_record(record_id, access_token)
    if record is None:
        raise HTTPException(status_code=404, detail="Investigation record not found")

    if format == "json":
        content = export_as_json(record)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="rca-{record_id}.json"'},
        )

    if format == "markdown":
        content = export_as_markdown(record)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="rca-{record_id}.md"'},
        )

    pdf_bytes = export_as_pdf_bytes(record)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="rca-{record_id}.pdf"'},
    )

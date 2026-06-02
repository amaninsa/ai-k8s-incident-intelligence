import asyncio
import json
from queue import Empty, Queue

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ai.root_cause_analyzer import analyze_root_cause
from core.auth import get_current_user, resolve_insforge_session
from kubernetes.exceptions import (
    ClusterAccessError,
    InvalidContextError,
    KubeconfigNotFoundError,
    KubectlNotFoundError,
)
from models.investigation import InvestigateRequest
from services.history_service import save_investigation_history
from services.investigation_service import run_investigation

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def _resolve_stream_user(
    credentials: HTTPAuthorizationCredentials | None,
    access_token: str | None,
) -> tuple[dict, str]:
    from core.auth import LOCAL_DEV_TOKEN, LOCAL_DEV_USER
    from core.config import settings

    session = await resolve_insforge_session(credentials, query_token=access_token)
    if session:
        return session

    if not settings.auth_enabled:
        return LOCAL_DEV_USER.copy(), LOCAL_DEV_TOKEN

    raise HTTPException(status_code=401, detail="Authentication required")


def _build_response(investigation: dict, diagnosis, history_id: str | None = None) -> dict:
    evidence = {
        "cluster": investigation.get("cluster", {}),
        "pods": investigation.get("pods", {}),
        "logs": investigation.get("logs", {}),
        "events": investigation.get("events", {}),
        "deployments": investigation.get("deployments", {}),
        "network": investigation.get("network", {}),
    }

    critical_events = evidence.get("events", {}).get("critical_events") or []
    response_status = "warning" if critical_events else "success"

    payload = {
        "status": response_status,
        "investigation": evidence,
        "diagnosis": diagnosis.model_dump(),
    }
    if history_id:
        payload["history_id"] = history_id
    return payload


def _map_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, KubectlNotFoundError):
        return HTTPException(status_code=503, detail="kubectl not found")
    if isinstance(exc, KubeconfigNotFoundError):
        return HTTPException(status_code=503, detail="kubeconfig not found")
    if isinstance(exc, InvalidContextError):
        return HTTPException(status_code=400, detail="invalid context selected")
    if isinstance(exc, ClusterAccessError):
        return HTTPException(status_code=503, detail="cluster access failed")
    return HTTPException(status_code=500, detail="investigation failed")


@router.post("/investigate")
async def investigate_cluster(
    request: InvestigateRequest | None = None,
    _user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Collect Kubernetes evidence and generate an AI diagnosis."""
    context = request.context if request else None

    try:
        investigation = run_investigation(context=context)
    except (KubectlNotFoundError, KubeconfigNotFoundError, InvalidContextError, ClusterAccessError) as exc:
        raise _map_exception(exc) from None

    evidence = {
        "cluster": investigation.get("cluster", {}),
        "pods": investigation.get("pods", {}),
        "logs": investigation.get("logs", {}),
        "events": investigation.get("events", {}),
        "deployments": investigation.get("deployments", {}),
        "network": investigation.get("network", {}),
    }

    diagnosis = analyze_root_cause(evidence)
    response = _build_response(investigation, diagnosis)

    session = await resolve_insforge_session(credentials)
    if session:
        history_user, history_token = session
        saved = await save_investigation_history(
            user_id=history_user["id"],
            access_token=history_token,
            cluster=investigation.get("cluster", {}).get("current_context", context or "unknown"),
            status=response["status"],
            diagnosis=diagnosis.model_dump(),
            investigation=response["investigation"],
        )
        if saved and saved.get("id"):
            response["history_id"] = saved["id"]

    return response


@router.get("/investigate/stream")
async def investigate_stream(
    context: str = Query(..., description="kubectl context to investigate"),
    access_token: str | None = Query(None, description="Bearer token for EventSource clients"),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """Stream real investigation progress using Server-Sent Events."""
    user, token = await _resolve_stream_user(credentials, access_token)

    async def event_generator():
        queue: Queue = Queue()

        def on_progress(step: str, status: str) -> None:
            queue.put(
                {
                    "type": "progress",
                    "step": step,
                    "status": status,
                }
            )

        def run_pipeline() -> None:
            try:
                investigation = run_investigation(context=context, on_progress=on_progress)
                evidence = {
                    "cluster": investigation.get("cluster", {}),
                    "pods": investigation.get("pods", {}),
                    "logs": investigation.get("logs", {}),
                    "events": investigation.get("events", {}),
                    "deployments": investigation.get("deployments", {}),
                    "network": investigation.get("network", {}),
                }

                on_progress("AI Reasoning", "active")
                diagnosis = analyze_root_cause(evidence)
                on_progress("AI Reasoning", "complete")
                on_progress("Root Cause Found", "complete")

                response = _build_response(investigation, diagnosis)
                queue.put({"type": "complete", "data": response, "needs_save": True})
            except (
                KubectlNotFoundError,
                KubeconfigNotFoundError,
                InvalidContextError,
                ClusterAccessError,
            ) as exc:
                http_exc = _map_exception(exc)
                queue.put({"type": "error", "detail": http_exc.detail, "status": http_exc.status_code})
            except Exception:
                queue.put({"type": "error", "detail": "investigation failed", "status": 500})
            finally:
                queue.put(None)

        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, run_pipeline)

        saved_response: dict | None = None

        while True:
            await asyncio.sleep(0.2)
            try:
                item = queue.get_nowait()
            except Empty:
                continue

            if item is None:
                break

            if item.get("type") == "complete" and item.get("needs_save"):
                data = item["data"]
                saved = await save_investigation_history(
                    user_id=user["id"],
                    access_token=token,
                    cluster=data.get("investigation", {})
                    .get("cluster", {})
                    .get("current_context", context),
                    status=data.get("status", "success"),
                    diagnosis=data.get("diagnosis", {}),
                    investigation=data.get("investigation", {}),
                )
                if saved and saved.get("id"):
                    data["history_id"] = saved["id"]
                saved_response = data
                item = {"type": "complete", "data": data}
                yield f"data: {json.dumps(item)}\n\n"
                continue

            yield f"data: {json.dumps(item)}\n\n"

        if saved_response is None:
            return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

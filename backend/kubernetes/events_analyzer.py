"""Analyze Kubernetes events for critical failure signals."""

from __future__ import annotations

import json
from typing import Any

from kubernetes.kubectl_executor import run_kubectl

CRITICAL_REASONS = {
    "FailedScheduling",
    "BackOff",
    "FailedMount",
    "FailedPull",
    "ErrImagePull",
    "Unhealthy",
}


def analyze_events() -> dict[str, Any]:
    """Return critical events detected across all namespaces."""
    result = run_kubectl("get", "events", "-A", "-o", "json")

    if not result["success"]:
        return {
            "critical_events": [],
            "error": result["stderr"].strip() or "failed to list events",
        }

    try:
        payload = json.loads(result["stdout"] or "{}")
    except json.JSONDecodeError:
        return {
            "critical_events": [],
            "error": "invalid events JSON response",
        }

    items = payload.get("items") or []
    critical_events: list[dict[str, str]] = []
    seen_events: set[tuple[str, str, str, str]] = set()

    for event in items:
        reason = (event.get("reason") or "").strip()
        if reason not in CRITICAL_REASONS:
            continue

        metadata = event.get("metadata") or {}
        involved = event.get("involvedObject") or {}

        namespace = metadata.get("namespace") or involved.get("namespace") or "unknown"
        name = involved.get("name") or metadata.get("name") or "unknown"
        message = (event.get("message") or "")[:300]

        dedupe_key = (namespace, name, reason, message)
        if dedupe_key in seen_events:
            continue
        seen_events.add(dedupe_key)

        critical_events.append(
            {
                "namespace": namespace,
                "name": name,
                "reason": reason,
                "message": message,
                "type": event.get("type") or "Unknown",
            }
        )

    return {"critical_events": critical_events}

"""Inspect pod health across all namespaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from kubernetes.kubectl_executor import run_kubectl

PROBLEMATIC_WAITING_REASONS = {
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "CreateContainerConfigError",
    "InvalidImageName",
}

PROBLEMATIC_TERMINATED_REASONS = {
    "Error",
    "OOMKilled",
}

CONTAINER_CREATING_STUCK_MINUTES = 5


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _minutes_since(timestamp: datetime | None) -> float | None:
    if timestamp is None:
        return None
    delta = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
    return delta.total_seconds() / 60


def _container_issues(
    namespace: str,
    pod_name: str,
    container_statuses: list[dict[str, Any]] | None,
    pod_start_time: datetime | None,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    for container in container_statuses or []:
        state = container.get("state") or {}
        waiting = state.get("waiting") or {}
        terminated = state.get("terminated") or {}

        waiting_reason = waiting.get("reason", "")
        if waiting_reason in PROBLEMATIC_WAITING_REASONS:
            issues.append(
                {
                    "namespace": namespace,
                    "name": pod_name,
                    "status": waiting_reason,
                }
            )
            continue

        if waiting_reason == "ContainerCreating":
            started_at = _parse_timestamp(container.get("state", {}).get("waiting", {}).get("startedAt"))
            reference_time = started_at or pod_start_time
            age_minutes = _minutes_since(reference_time)
            if age_minutes is not None and age_minutes > CONTAINER_CREATING_STUCK_MINUTES:
                issues.append(
                    {
                        "namespace": namespace,
                        "name": pod_name,
                        "status": "ContainerCreatingStuck",
                    }
                )
            continue

        terminated_reason = terminated.get("reason", "")
        if terminated_reason in PROBLEMATIC_TERMINATED_REASONS:
            issues.append(
                {
                    "namespace": namespace,
                    "name": pod_name,
                    "status": terminated_reason,
                }
            )

    return issues


def _pod_phase_issues(namespace: str, pod_name: str, phase: str) -> dict[str, str] | None:
    if phase in {"Pending", "Failed", "Unknown"}:
        return {
            "namespace": namespace,
            "name": pod_name,
            "status": phase,
        }
    return None


def inspect_pods() -> dict[str, Any]:
    """Return pod health summary with problematic pods listed."""
    result = run_kubectl("get", "pods", "-A", "-o", "json")

    if not result["success"]:
        return {
            "healthy": False,
            "error": result["stderr"].strip() or "failed to list pods",
            "problematic_pods": [],
        }

    try:
        payload = json.loads(result["stdout"] or "{}")
    except json.JSONDecodeError:
        return {
            "healthy": False,
            "error": "invalid pod JSON response",
            "problematic_pods": [],
        }

    items = payload.get("items") or []
    problematic_pods: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for pod in items:
        metadata = pod.get("metadata") or {}
        status = pod.get("status") or {}

        namespace = metadata.get("namespace", "unknown")
        pod_name = metadata.get("name", "unknown")
        phase = status.get("phase", "Unknown")
        pod_start_time = _parse_timestamp(status.get("startTime"))

        phase_issue = _pod_phase_issues(namespace, pod_name, phase)
        if phase_issue:
            key = (namespace, pod_name, phase_issue["status"])
            if key not in seen:
                seen.add(key)
                problematic_pods.append(phase_issue)

        container_statuses = status.get("containerStatuses") or status.get("initContainerStatuses")
        for issue in _container_issues(namespace, pod_name, container_statuses, pod_start_time):
            key = (issue["namespace"], issue["name"], issue["status"])
            if key not in seen:
                seen.add(key)
                problematic_pods.append(issue)

    return {
        "healthy": len(problematic_pods) == 0,
        "problematic_pods": problematic_pods,
    }

"""Inspect deployment health across all namespaces."""

from __future__ import annotations

import json
from typing import Any

from kubernetes.kubectl_executor import run_kubectl


def _condition_issue(
    namespace: str,
    name: str,
    condition: dict[str, Any],
) -> dict[str, str] | None:
    condition_type = condition.get("type", "")
    status = condition.get("status", "")
    reason = condition.get("reason", "")
    message = (condition.get("message") or "")[:300]

    if condition_type == "Progressing" and status == "False":
        return {
            "namespace": namespace,
            "name": name,
            "issue": "rollout not progressing",
            "detail": message or reason or "Progressing=False",
        }

    if condition_type == "Available" and status == "False":
        return {
            "namespace": namespace,
            "name": name,
            "issue": "deployment unavailable",
            "detail": message or reason or "Available=False",
        }

    if reason in {"ReplicaSetCreateError", "FailedCreate", "ProgressDeadlineExceeded"}:
        return {
            "namespace": namespace,
            "name": name,
            "issue": "rollout failure",
            "detail": message or reason,
        }

    return None


def inspect_deployments() -> dict[str, Any]:
    """Return deployment health summary with detected issues."""
    result = run_kubectl("get", "deployments", "-A", "-o", "json")

    if not result["success"]:
        return {
            "healthy": False,
            "issues": [],
            "error": result["stderr"].strip() or "failed to list deployments",
        }

    try:
        payload = json.loads(result["stdout"] or "{}")
    except json.JSONDecodeError:
        return {
            "healthy": False,
            "issues": [],
            "error": "invalid deployments JSON response",
        }

    items = payload.get("items") or []
    issues: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for deployment in items:
        metadata = deployment.get("metadata") or {}
        spec = deployment.get("spec") or {}
        status = deployment.get("status") or {}

        namespace = metadata.get("namespace", "unknown")
        name = metadata.get("name", "unknown")

        desired_replicas = spec.get("replicas")
        available_replicas = status.get("availableReplicas") or 0
        unavailable_replicas = status.get("unavailableReplicas") or 0

        if isinstance(desired_replicas, int) and available_replicas < desired_replicas:
            issue = {
                "namespace": namespace,
                "name": name,
                "issue": "insufficient available replicas",
                "detail": f"available={available_replicas}, desired={desired_replicas}",
            }
            key = (namespace, name, issue["issue"])
            if key not in seen:
                seen.add(key)
                issues.append(issue)

        if unavailable_replicas:
            issue = {
                "namespace": namespace,
                "name": name,
                "issue": "unavailable replicas",
                "detail": f"unavailable={unavailable_replicas}",
            }
            key = (namespace, name, issue["issue"])
            if key not in seen:
                seen.add(key)
                issues.append(issue)

        for condition in status.get("conditions") or []:
            condition_issue = _condition_issue(namespace, name, condition)
            if condition_issue is None:
                continue
            key = (namespace, name, condition_issue["issue"])
            if key not in seen:
                seen.add(key)
                issues.append(condition_issue)

    return {
        "healthy": len(issues) == 0,
        "issues": issues,
    }

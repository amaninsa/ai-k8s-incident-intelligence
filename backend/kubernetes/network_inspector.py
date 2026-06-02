"""Inspect service and endpoint networking health."""

from __future__ import annotations

import json
from typing import Any

from kubernetes.kubectl_executor import run_kubectl

IGNORED_SERVICES = {("default", "kubernetes")}


def _load_json_command(*args: str) -> tuple[dict[str, Any] | None, str | None]:
    result = run_kubectl(*args)
    if not result["success"]:
        return None, result["stderr"].strip() or f"failed to run kubectl {' '.join(args)}"

    try:
        return json.loads(result["stdout"] or "{}"), None
    except json.JSONDecodeError:
        return None, "invalid JSON response"


def _endpoint_has_addresses(endpoint: dict[str, Any]) -> bool:
    subsets = endpoint.get("subsets") or []
    for subset in subsets:
        addresses = subset.get("addresses") or []
        if addresses:
            return True
    return False


def _labels_match_selector(labels: dict[str, str] | None, selector: dict[str, str] | None) -> bool:
    if not selector:
        return True
    if not labels:
        return False
    return all(labels.get(key) == value for key, value in selector.items())


def _pods_by_namespace(pods_payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for pod in pods_payload.get("items") or []:
        metadata = pod.get("metadata") or {}
        namespace = metadata.get("namespace")
        if namespace:
            grouped.setdefault(namespace, []).append(pod)
    return grouped


def inspect_networking() -> dict[str, Any]:
    """Detect service networking issues such as missing endpoints or selector mismatches."""
    services_payload, services_error = _load_json_command("get", "svc", "-A", "-o", "json")
    endpoints_payload, endpoints_error = _load_json_command("get", "endpoints", "-A", "-o", "json")
    pods_payload, _ = _load_json_command("get", "pods", "-A", "-o", "json")

    if services_payload is None:
        return {
            "healthy": False,
            "issues": [],
            "error": services_error or "failed to list services",
        }

    if endpoints_payload is None:
        return {
            "healthy": False,
            "issues": [],
            "error": endpoints_error or "failed to list endpoints",
        }

    pods_by_namespace = _pods_by_namespace(pods_payload or {})

    endpoints_index: dict[tuple[str, str], dict[str, Any]] = {}
    for endpoint in endpoints_payload.get("items") or []:
        metadata = endpoint.get("metadata") or {}
        namespace = metadata.get("namespace")
        name = metadata.get("name")
        if namespace and name:
            endpoints_index[(namespace, name)] = endpoint

    issues: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for service in services_payload.get("items") or []:
        metadata = service.get("metadata") or {}
        spec = service.get("spec") or {}

        namespace = metadata.get("namespace", "unknown")
        name = metadata.get("name", "unknown")

        if (namespace, name) in IGNORED_SERVICES:
            continue

        selector = spec.get("selector") or {}
        endpoint = endpoints_index.get((namespace, name))

        if selector:
            namespace_pods = pods_by_namespace.get(namespace, [])
            matching_pods = [
                pod
                for pod in namespace_pods
                if _labels_match_selector((pod.get("metadata") or {}).get("labels"), selector)
            ]

            if not matching_pods:
                issue = {
                    "namespace": namespace,
                    "name": name,
                    "issue": "selector mismatch",
                    "detail": "no pods match service selector",
                }
                key = (namespace, name, issue["issue"])
                if key not in seen:
                    seen.add(key)
                    issues.append(issue)
                continue

        if endpoint is None:
            issue = {
                "namespace": namespace,
                "name": name,
                "issue": "missing endpoints",
                "detail": "endpoints object not found",
            }
            key = (namespace, name, issue["issue"])
            if key not in seen:
                seen.add(key)
                issues.append(issue)
            continue

        if not _endpoint_has_addresses(endpoint):
            issue = {
                "namespace": namespace,
                "name": name,
                "issue": "service without backing pods",
                "detail": "endpoints exist but no ready addresses",
            }
            key = (namespace, name, issue["issue"])
            if key not in seen:
                seen.add(key)
                issues.append(issue)

    return {
        "healthy": len(issues) == 0,
        "issues": issues,
    }

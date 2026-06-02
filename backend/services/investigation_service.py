"""Orchestrate the Kubernetes investigation workflow."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.config import reset_kubectl_context, set_kubectl_context
from kubernetes.cluster_verifier import ensure_cluster_access
from kubernetes.deployment_inspector import inspect_deployments
from kubernetes.events_analyzer import analyze_events
from kubernetes.logs_collector import collect_logs
from kubernetes.network_inspector import inspect_networking
from kubernetes.pod_inspector import inspect_pods

ProgressCallback = Callable[[str, str], None]

INVESTIGATION_STEPS = [
    ("Checking Pods", "cluster_and_pods"),
    ("Collecting Logs", "logs"),
    ("Reading Events", "events"),
    ("Inspecting Deployments", "deployments"),
    ("Checking Networking", "network"),
]


def _emit(on_progress: ProgressCallback | None, step: str, status: str) -> None:
    if on_progress:
        on_progress(step, status)


def run_investigation(
    context: str | None = None,
    on_progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    """
    Collect Kubernetes troubleshooting evidence in sequence.

    Raises typed exceptions from cluster verification when access fails.
    """
    context_token = set_kubectl_context(context)

    try:
        _emit(on_progress, "Checking Pods", "active")
        cluster = ensure_cluster_access()
        pods = inspect_pods()
        _emit(on_progress, "Checking Pods", "complete")

        _emit(on_progress, "Collecting Logs", "active")
        logs = collect_logs(pods.get("problematic_pods"))
        _emit(on_progress, "Collecting Logs", "complete")

        _emit(on_progress, "Reading Events", "active")
        events = analyze_events()
        _emit(on_progress, "Reading Events", "complete")

        _emit(on_progress, "Inspecting Deployments", "active")
        deployments = inspect_deployments()
        _emit(on_progress, "Inspecting Deployments", "complete")

        _emit(on_progress, "Checking Networking", "active")
        network = inspect_networking()
        _emit(on_progress, "Checking Networking", "complete")

        return {
            "cluster": cluster,
            "pods": pods,
            "logs": logs,
            "events": events,
            "deployments": deployments,
            "network": network,
        }
    finally:
        reset_kubectl_context(context_token)

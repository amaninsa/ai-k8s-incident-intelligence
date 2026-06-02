"""List available Kubernetes contexts from kubeconfig."""

from __future__ import annotations

from typing import Any

from kubernetes.kubectl_executor import run_kubectl


def list_cluster_contexts() -> dict[str, Any]:
    """Return kubectl contexts configured in kubeconfig."""
    result = run_kubectl("config", "get-contexts", "-o", "name")

    if not result["success"]:
        return {
            "contexts": [],
            "error": result["stderr"].strip() or "failed to list cluster contexts",
        }

    contexts = [
        line.strip()
        for line in (result["stdout"] or "").splitlines()
        if line.strip()
    ]

    return {"contexts": contexts}

"""Verify kubectl access and cluster connectivity."""

from __future__ import annotations

import os
from typing import Any

from loguru import logger

from core.config import get_kubectl_context
from kubernetes.exceptions import (
    ClusterAccessError,
    InvalidContextError,
    KubeconfigNotFoundError,
    KubectlNotFoundError,
)
from kubernetes.kubectl_executor import get_kubectl_path, run_kubectl


def _resolve_kubeconfig_path() -> str | None:
    if settings_kubeconfig := _get_settings_kubeconfig():
        return settings_kubeconfig

    env_kubeconfig = os.environ.get("KUBECONFIG")
    if env_kubeconfig:
        paths = env_kubeconfig.split(os.pathsep)
        for path in paths:
            if os.path.isfile(path):
                return path
        return None

    default_path = os.path.expanduser("~/.kube/config")
    if os.path.isfile(default_path):
        return default_path

    return None


def _get_settings_kubeconfig() -> str | None:
    from core.config import settings

    if settings.kubeconfig_path and os.path.isfile(settings.kubeconfig_path):
        return settings.kubeconfig_path
    return None


def verify_cluster_access() -> dict[str, Any]:
    """
    Verify kubectl is installed, kubeconfig exists, context is set, and cluster responds.

    Returns:
        {"connected": True, "current_context": "..."} on success
        {"connected": False, "error": "..."} on failure
    """
    kubectl_path = get_kubectl_path()
    logger.info("[DEBUG] verify_cluster_access: kubectl path = {}", kubectl_path)
    logger.info("[DEBUG] verify_cluster_access: current PATH = {}", os.environ.get("PATH", ""))

    if kubectl_path is None:
        logger.info("[DEBUG] verify_cluster_access failed: kubectl not found")
        return {"connected": False, "error": "kubectl not found"}

    kubeconfig_path = _resolve_kubeconfig_path()
    logger.info("[DEBUG] verify_cluster_access: current kubeconfig path = {}", kubeconfig_path)

    if kubeconfig_path is None:
        logger.info("[DEBUG] verify_cluster_access failed: kubeconfig not found")
        return {"connected": False, "error": "kubeconfig not found"}

    selected_context = get_kubectl_context()

    version_result = run_kubectl("version", "--client")
    if not version_result["success"]:
        logger.info(
            "[DEBUG] verify_cluster_access failed at 'kubectl version --client': "
            "returncode={} stderr={}",
            version_result["returncode"],
            version_result["stderr"].strip() or "(empty)",
        )
        return {
            "connected": False,
            "error": version_result["stderr"].strip() or "kubectl client check failed",
        }

    if selected_context:
        current_context = selected_context
    else:
        context_result = run_kubectl("config", "current-context")
        if not context_result["success"]:
            logger.info(
                "[DEBUG] verify_cluster_access failed at 'kubectl config current-context': "
                "returncode={} stderr={}",
                context_result["returncode"],
                context_result["stderr"].strip() or "(empty)",
            )
            return {
                "connected": False,
                "error": context_result["stderr"].strip() or "no current context configured",
            }
        current_context = context_result["stdout"].strip()

    if not current_context:
        logger.info("[DEBUG] verify_cluster_access failed: current context is empty")
        return {"connected": False, "error": "no current context configured"}

    ns_result = run_kubectl("get", "ns")
    if not ns_result["success"]:
        stderr = ns_result["stderr"].strip() or "(empty)"
        logger.info(
            "[DEBUG] verify_cluster_access failed at 'kubectl get ns': "
            "returncode={} stdout={} stderr={}",
            ns_result["returncode"],
            ns_result["stdout"].strip() or "(empty)",
            stderr,
        )
        if selected_context and ("not found" in stderr.lower() or "does not exist" in stderr.lower()):
            return {
                "connected": False,
                "error": "invalid context selected",
            }
        return {
            "connected": False,
            "error": "Cluster unreachable",
        }

    return {
        "connected": True,
        "current_context": current_context,
    }


def ensure_cluster_access() -> dict[str, Any]:
    """
    Verify cluster access and raise typed exceptions for API error handling.

    Raises:
        KubectlNotFoundError
        KubeconfigNotFoundError
        InvalidContextError
        ClusterAccessError
    """
    result = verify_cluster_access()

    if result.get("connected"):
        return result

    error = result.get("error", "cluster access failed")
    logger.info("[DEBUG] ensure_cluster_access failed: underlying error = {}", error)

    if error == "kubectl not found":
        raise KubectlNotFoundError(error)
    if error == "kubeconfig not found":
        raise KubeconfigNotFoundError(error)
    if error == "invalid context selected":
        raise InvalidContextError(error)
    raise ClusterAccessError("cluster access failed")

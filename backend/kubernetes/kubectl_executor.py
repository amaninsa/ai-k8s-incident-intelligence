"""Low-level kubectl command execution."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from loguru import logger

from core.config import get_kubectl_context, settings

DEFAULT_TIMEOUT_SECONDS = 30


def get_kubectl_path() -> str | None:
    """Return the absolute path to kubectl, or None if not installed."""
    return shutil.which("kubectl")


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    if settings.kubeconfig_path:
        env["KUBECONFIG"] = settings.kubeconfig_path
    return env


def _resolve_kubeconfig_for_debug(env: dict[str, str]) -> str:
    kubeconfig = env.get("KUBECONFIG")
    if kubeconfig:
        return kubeconfig
    default_path = os.path.expanduser("~/.kube/config")
    return default_path if os.path.isfile(default_path) else "(not found)"


def _log_kubectl_debug(
    *,
    kubectl_path: str | None,
    command: list[str],
    env: dict[str, str],
    stdout: str,
    stderr: str,
    returncode: int,
) -> None:
    logger.info("[DEBUG] kubectl path: {}", kubectl_path)
    logger.info("[DEBUG] current PATH: {}", env.get("PATH", ""))
    logger.info("[DEBUG] current kubeconfig path: {}", _resolve_kubeconfig_for_debug(env))
    logger.info("[DEBUG] command executed: {}", " ".join(command))
    logger.info("[DEBUG] stdout: {}", stdout.strip() if stdout else "(empty)")
    logger.info("[DEBUG] stderr: {}", stderr.strip() if stderr else "(empty)")
    logger.info("[DEBUG] return code: {}", returncode)


def run_kubectl(
    *args: str,
    timeout: int | None = None,
) -> dict[str, Any]:
    """
    Run a kubectl command and return structured output.

    Never raises uncaught exceptions — failures are returned in the result dict.
    """
    kubectl_path = get_kubectl_path()
    env = _build_env()

    if kubectl_path is None:
        logger.warning("kubectl binary not found on PATH")
        _log_kubectl_debug(
            kubectl_path=None,
            command=["kubectl", *args],
            env=env,
            stdout="",
            stderr="kubectl binary not found",
            returncode=-1,
        )
        return {
            "success": False,
            "stdout": "",
            "stderr": "kubectl binary not found",
            "returncode": -1,
        }

    command = [kubectl_path]
    active_context = get_kubectl_context()
    if active_context:
        command.extend(["--context", active_context])
    command.extend(args)
    command_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT_SECONDS

    logger.info("Executing kubectl command: kubectl {}", " ".join(args))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=command_timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.error("kubectl command timed out after {}s: {}", command_timeout, " ".join(args))
        _log_kubectl_debug(
            kubectl_path=kubectl_path,
            command=command,
            env=env,
            stdout="",
            stderr=f"kubectl command timed out after {command_timeout}s",
            returncode=-1,
        )
        return {
            "success": False,
            "stdout": "",
            "stderr": f"kubectl command timed out after {command_timeout}s",
            "returncode": -1,
        }
    except OSError as exc:
        logger.error("kubectl command failed to start: {}", exc)
        _log_kubectl_debug(
            kubectl_path=kubectl_path,
            command=command,
            env=env,
            stdout="",
            stderr=str(exc),
            returncode=-1,
        )
        return {
            "success": False,
            "stdout": "",
            "stderr": str(exc),
            "returncode": -1,
        }

    success = result.returncode == 0
    logger.info("kubectl return code: {}", result.returncode)
    _log_kubectl_debug(
        kubectl_path=kubectl_path,
        command=command,
        env=env,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )

    if not success and result.stderr:
        logger.warning("kubectl stderr: {}", result.stderr.strip())

    return {
        "success": success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }

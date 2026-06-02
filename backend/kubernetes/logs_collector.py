"""Collect and summarize logs for problematic pods."""

from __future__ import annotations

import re
from typing import Any

from kubernetes.kubectl_executor import run_kubectl

MAX_LOG_LINES = 50

SUMMARY_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)(traceback|exception|panic|fatal error)", "exception detected"),
    (r"(?i)(connection refused|connection reset|connection timed out|dial tcp)", "connection failure"),
    (r"(?i)(failed to start|startup error|could not start|exit code)", "startup error"),
    (r"(?i)(required environment variable|missing env|env.*not set|undefined env)", "missing environment variable"),
    (r"(?i)(imagepullbackoff|failed to pull|pull access denied|manifest unknown|invalid image)", "image error"),
    (r"(?i)(permission denied|forbidden|unauthorized)", "permission error"),
    (r"(?i)(no such file|file not found)", "missing file"),
]


def _summarize_log_lines(lines: list[str]) -> list[str]:
    summaries: list[str] = []
    seen: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        for pattern, label in SUMMARY_PATTERNS:
            if re.search(pattern, stripped):
                summary = f"{label}: {stripped[:200]}"
                if summary not in seen:
                    seen.add(summary)
                    summaries.append(summary)
                break

    if not summaries and lines:
        non_empty = [line.strip() for line in lines if line.strip()]
        if non_empty:
            summaries.append(f"recent log activity: {non_empty[-1][:200]}")

    return summaries[:10]


def _pod_log_key(namespace: str, name: str) -> str:
    return f"{namespace}/{name}"


def collect_logs(problematic_pods: list[dict[str, str]] | None) -> dict[str, Any]:
    """Collect concise log summaries for problematic pods only."""
    if not problematic_pods:
        return {"pods": {}}

    log_summaries: dict[str, Any] = {}

    for pod in problematic_pods:
        namespace = pod.get("namespace")
        name = pod.get("name")
        if not namespace or not name:
            continue

        result = run_kubectl(
            "logs",
            name,
            "-n",
            namespace,
            "--tail",
            str(MAX_LOG_LINES),
            "--all-containers=true",
        )

        key = _pod_log_key(namespace, name)

        if not result["success"]:
            stderr = (result["stderr"] or "").strip()
            log_summaries[key] = {
                "summaries": [f"log collection failed: {stderr[:200]}" if stderr else "log collection failed"],
                "lines_collected": 0,
            }
            continue

        lines = (result["stdout"] or "").splitlines()
        log_summaries[key] = {
            "summaries": _summarize_log_lines(lines),
            "lines_collected": min(len(lines), MAX_LOG_LINES),
        }

    return {"pods": log_summaries}

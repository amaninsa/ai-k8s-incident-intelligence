"""Build structured prompts for Kubernetes troubleshooting LLM calls."""

from __future__ import annotations

import json
from typing import Any

SYSTEM_PROMPT = """You are a Senior Kubernetes SRE.

Analyze the provided Kubernetes investigation evidence and identify the most likely root cause.
Be precise, practical, and beginner-friendly.

Respond with JSON only. Do not include markdown fences or extra text.

Use this exact JSON schema:
{
  "root_cause": "short summary of the primary root cause",
  "explanation": "clear explanation of why this is happening",
  "fix": "step-by-step remediation guidance",
  "kubectl_command": "one useful kubectl command to investigate or verify the fix",
  "prevention_recommendation": "how to prevent this issue in the future",
  "confidence": 0
}

Rules:
- confidence must be an integer from 0 to 100
- prioritize the most critical and correlated findings
- if evidence is insufficient, state that clearly and lower confidence
- do not invent resources that are not present in the evidence
"""


def build_diagnosis_prompt(investigation: dict[str, Any]) -> str:
    """Convert investigation evidence into a structured troubleshooting prompt."""
    cluster = investigation.get("cluster") or {}
    pods = investigation.get("pods") or {}
    logs = investigation.get("logs") or {}
    events = investigation.get("events") or {}
    deployments = investigation.get("deployments") or {}
    network = investigation.get("network") or {}

    sections = [
        "## Cluster",
        _format_section(cluster),
        "## Pod Findings",
        _format_section(pods),
        "## Log Findings",
        _format_section(logs),
        "## Event Findings",
        _format_section(events),
        "## Deployment Findings",
        _format_section(deployments),
        "## Network Findings",
        _format_section(network),
        "## Task",
        "Based on the evidence above, produce the required JSON diagnosis.",
    ]

    return "\n\n".join(sections)


def build_messages(investigation: dict[str, Any]) -> list[dict[str, str]]:
    """Build OpenRouter chat messages for diagnosis generation."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_diagnosis_prompt(investigation)},
    ]


def _format_section(data: Any) -> str:
    if not data:
        return "No data collected."
    return json.dumps(data, indent=2, default=str)

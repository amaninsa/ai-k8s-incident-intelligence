"""Analyze investigation evidence for diagnosis quality scoring."""

from __future__ import annotations

from typing import Any


def collect_evidence_metadata(investigation: dict[str, Any]) -> dict[str, Any]:
    """Extract affected resources, evidence counts, and correlation signals."""
    pods = investigation.get("pods") or {}
    logs = investigation.get("logs") or {}
    events = investigation.get("events") or {}
    deployments = investigation.get("deployments") or {}
    network = investigation.get("network") or {}

    affected_resources: set[str] = set()
    evidence_count = 0

    problematic_pods = pods.get("problematic_pods") or []
    for pod in problematic_pods:
        namespace = pod.get("namespace")
        name = pod.get("name")
        if namespace and name:
            affected_resources.add(f"{namespace}/{name}")
    evidence_count += len(problematic_pods)

    log_pods = logs.get("pods") or {}
    log_resources: set[str] = set()
    for resource_key, log_data in log_pods.items():
        log_resources.add(resource_key)
        affected_resources.add(resource_key)
        summaries = (log_data or {}).get("summaries") or []
        evidence_count += len(summaries)

    critical_events = events.get("critical_events") or []
    event_resources: set[str] = set()
    for event in critical_events:
        namespace = event.get("namespace")
        name = event.get("name")
        if namespace and name:
            resource = f"{namespace}/{name}"
            event_resources.add(resource)
            affected_resources.add(resource)
    evidence_count += len(critical_events)

    deployment_issues = deployments.get("issues") or []
    for issue in deployment_issues:
        namespace = issue.get("namespace")
        name = issue.get("name")
        if namespace and name:
            affected_resources.add(f"{namespace}/{name}")
    evidence_count += len(deployment_issues)

    network_issues = network.get("issues") or []
    for issue in network_issues:
        namespace = issue.get("namespace")
        name = issue.get("name")
        if namespace and name:
            affected_resources.add(f"{namespace}/{name}")
    evidence_count += len(network_issues)

    pod_resources = {
        f"{pod.get('namespace')}/{pod.get('name')}"
        for pod in problematic_pods
        if pod.get("namespace") and pod.get("name")
    }

    logs_with_content = {
        key
        for key, data in log_pods.items()
        if (data or {}).get("summaries")
    }

    overlap_targets = event_resources | pod_resources
    logs_and_events_agree = bool(logs_with_content & overlap_targets)
    has_critical_events = len(critical_events) > 0
    has_log_evidence = bool(logs_with_content)
    pods_marked_healthy = pods.get("healthy") is True

    signal_inconsistencies: list[str] = []
    backoff_events = [
        event for event in critical_events if event.get("reason") in {"BackOff", "CrashLoopBackOff"}
    ]
    if backoff_events and pods_marked_healthy:
        signal_inconsistencies.append(
            "Critical BackOff events were detected while pod inspection reported healthy pods."
        )
    if has_critical_events and not has_log_evidence and not pod_resources:
        signal_inconsistencies.append(
            "Events indicate problems, but no matching pod or log evidence was collected."
        )
    if has_log_evidence and not has_critical_events and not pod_resources:
        signal_inconsistencies.append(
            "Logs contain errors, but no supporting pod failures or critical events were found."
        )

    return {
        "affected_resources": sorted(affected_resources),
        "evidence_count": evidence_count,
        "has_critical_events": has_critical_events,
        "has_log_evidence": has_log_evidence,
        "logs_and_events_agree": logs_and_events_agree,
        "signal_inconsistencies": signal_inconsistencies,
        "pods_marked_healthy": pods_marked_healthy,
    }


def calculate_confidence(
    metadata: dict[str, Any],
    *,
    is_fallback: bool,
    llm_confidence: int | None = None,
) -> int:
    """Calculate confidence score from evidence strength."""
    if is_fallback:
        return min(49, llm_confidence if llm_confidence is not None else 25)

    inconsistencies = metadata.get("signal_inconsistencies") or []
    penalty = min(20, len(inconsistencies) * 8)

    if metadata.get("logs_and_events_agree"):
        base = 92
        score = max(base, llm_confidence or 0, 90) - penalty
        return max(75, score)

    if metadata.get("has_critical_events"):
        base = 82
        score = min(max(base, llm_confidence or 0, 75), 89) - penalty
        return max(50, score)

    if metadata.get("evidence_count", 0) > 0:
        base = 62
        score = min(max(base, llm_confidence or 0, 50), 74) - penalty
        return max(40, score)

    return min(max((llm_confidence or 0) - penalty, 50), 74)


def enrich_diagnosis_with_resources(
    diagnosis: Any,
    affected_resources: list[str],
) -> Any:
    """Include namespace/resource names in diagnosis text fields."""
    if not affected_resources:
        return diagnosis

    resource_summary = ", ".join(affected_resources[:8])
    if len(affected_resources) > 8:
        resource_summary += f" (+{len(affected_resources) - 8} more)"

    resource_prefix = f"Affected resources: {resource_summary}."

    if resource_prefix not in diagnosis.explanation:
        diagnosis.explanation = f"{resource_prefix} {diagnosis.explanation}".strip()

    if affected_resources and not any(
        resource in diagnosis.root_cause for resource in affected_resources[:3]
    ):
        primary = affected_resources[0]
        diagnosis.root_cause = f"[{primary}] {diagnosis.root_cause}".strip()

    if affected_resources and "namespace" not in diagnosis.fix.lower():
        sample = affected_resources[0]
        if "/" in sample:
            namespace, name = sample.split("/", 1)
            diagnosis.fix = (
                f"Focus on namespace '{namespace}' and resource '{name}'. {diagnosis.fix}"
            ).strip()

    if not diagnosis.kubectl_command or diagnosis.kubectl_command == "kubectl get pods -A":
        primary = affected_resources[0]
        if "/" in primary:
            namespace, name = primary.split("/", 1)
            diagnosis.kubectl_command = f"kubectl describe pod {name} -n {namespace}"

    return diagnosis

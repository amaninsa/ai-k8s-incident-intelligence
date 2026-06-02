"""Pydantic models for AI-generated Kubernetes diagnoses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DiagnosisResponse(BaseModel):
    root_cause: str = ""
    explanation: str = ""
    fix: str = ""
    kubectl_command: str = ""
    prevention_recommendation: str = ""
    confidence: int = Field(default=0, ge=0, le=100)
    affected_resources: list[str] = Field(default_factory=list)
    evidence_count: int = Field(default=0, ge=0)


def fallback_diagnosis(reason: str) -> DiagnosisResponse:
    """Return a safe fallback diagnosis when AI reasoning is unavailable."""
    return DiagnosisResponse(
        root_cause="Unable to determine root cause automatically",
        explanation=reason,
        fix="Review the investigation evidence and address the highest-severity findings first.",
        kubectl_command="kubectl get pods -A",
        prevention_recommendation=(
            "Configure monitoring alerts for pod restarts, failed deployments, and critical events."
        ),
        confidence=25,
        affected_resources=[],
        evidence_count=0,
    )

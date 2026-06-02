"""Generate Kubernetes root cause diagnoses using LLM reasoning."""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger

from ai.diagnosis_models import DiagnosisResponse, fallback_diagnosis
from ai.evidence_analyzer import (
    calculate_confidence,
    collect_evidence_metadata,
    enrich_diagnosis_with_resources,
)
from ai.exceptions import (
    DiagnosisParseError,
    OpenRouterAPIError,
    OpenRouterConfigError,
    OpenRouterTimeoutError,
)
from ai.llm_client import generate_completion
from ai.prompt_builder import build_messages


def analyze_root_cause(investigation: dict[str, Any]) -> DiagnosisResponse:
    """
    Generate an AI diagnosis from investigation evidence.

    Never raises to callers — returns a graceful fallback diagnosis on failure.
    """
    metadata = collect_evidence_metadata(investigation)

    try:
        messages = build_messages(investigation)
        content = generate_completion(messages)
        diagnosis = _parse_diagnosis(content)
        diagnosis = _apply_diagnosis_quality(
            diagnosis,
            metadata,
            is_fallback=False,
        )
        logger.info("Diagnosis generated with confidence {}", diagnosis.confidence)
        return diagnosis
    except OpenRouterConfigError as exc:
        logger.error("OpenRouter configuration error: {}", exc)
        return _apply_diagnosis_quality(fallback_diagnosis(str(exc)), metadata, is_fallback=True)
    except OpenRouterTimeoutError as exc:
        logger.error("OpenRouter failure: {}", exc)
        return _apply_diagnosis_quality(
            fallback_diagnosis("AI diagnosis timed out. Review the investigation evidence manually."),
            metadata,
            is_fallback=True,
        )
    except OpenRouterAPIError as exc:
        logger.error("OpenRouter failure: {}", exc)
        return _apply_diagnosis_quality(
            fallback_diagnosis(f"AI diagnosis unavailable: {exc}"),
            metadata,
            is_fallback=True,
        )
    except DiagnosisParseError as exc:
        logger.error("Diagnosis parsing failed: {}", exc)
        return _apply_diagnosis_quality(
            fallback_diagnosis("AI diagnosis could not be parsed. Review the investigation evidence manually."),
            metadata,
            is_fallback=True,
        )
    except Exception as exc:
        logger.error("Unexpected diagnosis failure: {}", exc)
        return _apply_diagnosis_quality(
            fallback_diagnosis("AI diagnosis encountered an unexpected error."),
            metadata,
            is_fallback=True,
        )


def _apply_diagnosis_quality(
    diagnosis: DiagnosisResponse,
    metadata: dict[str, Any],
    *,
    is_fallback: bool,
) -> DiagnosisResponse:
    affected_resources = metadata.get("affected_resources") or []
    diagnosis.affected_resources = affected_resources
    diagnosis.evidence_count = metadata.get("evidence_count", 0)
    inconsistencies = metadata.get("signal_inconsistencies") or []
    diagnosis.confidence = calculate_confidence(
        metadata,
        is_fallback=is_fallback,
        llm_confidence=diagnosis.confidence,
    )
    enriched = enrich_diagnosis_with_resources(diagnosis, affected_resources)
    if inconsistencies and inconsistencies[0] not in enriched.explanation:
        enriched.explanation = (
            f"{enriched.explanation} Signal note: {inconsistencies[0]}"
        ).strip()
    return enriched


def _parse_diagnosis(content: str) -> DiagnosisResponse:
    parsed = _extract_json_object(content)
    if parsed is None:
        raise DiagnosisParseError("LLM response did not contain valid JSON")

    try:
        return DiagnosisResponse.model_validate(parsed)
    except Exception as exc:
        raise DiagnosisParseError(f"LLM response did not match diagnosis schema: {exc}") from exc


def _extract_json_object(content: str) -> dict[str, Any] | None:
    stripped = content.strip()

    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)

    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    return data if isinstance(data, dict) else None

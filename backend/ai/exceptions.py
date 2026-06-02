"""Custom exceptions for the AI reasoning layer."""

from __future__ import annotations


class OpenRouterConfigError(Exception):
    """Raised when OpenRouter configuration is missing or invalid."""


class OpenRouterAPIError(Exception):
    """Raised when the OpenRouter API returns an error response."""


class OpenRouterTimeoutError(Exception):
    """Raised when an OpenRouter request times out."""


class DiagnosisParseError(Exception):
    """Raised when the LLM response cannot be parsed into a diagnosis."""

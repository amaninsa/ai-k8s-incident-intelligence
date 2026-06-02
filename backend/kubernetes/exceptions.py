"""Shared exceptions for the Kubernetes investigation layer."""

from __future__ import annotations


class KubectlNotFoundError(Exception):
    """Raised when the kubectl binary is not available on PATH."""


class KubeconfigNotFoundError(Exception):
    """Raised when no kubeconfig file can be found."""


class ClusterAccessError(Exception):
    """Raised when the cluster cannot be reached or verified."""

    def __init__(self, message: str = "cluster access failed") -> None:
        self.message = message
        super().__init__(message)


class InvalidContextError(Exception):
    """Raised when the selected kubectl context is invalid."""

"""Validation errors for local loaders."""

from __future__ import annotations


class LoaderValidationError(ValueError):
    """Raised when dataset or config input does not satisfy schema requirements."""

"""Artifact store interface."""

from __future__ import annotations

from typing import Protocol


class ArtifactStore(Protocol):
    def put_text(self, relative_path: str, payload: str) -> str:
        """Store text and return absolute path."""

    def get_text(self, relative_path: str) -> str:
        """Read text artifact."""

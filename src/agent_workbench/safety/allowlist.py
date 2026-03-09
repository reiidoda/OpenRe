"""Allowlist checks."""

from __future__ import annotations

from urllib.parse import urlparse


def is_allowlisted(url: str, allowed_domains: list[str]) -> bool:
    domain = urlparse(url).netloc
    return domain in allowed_domains

"""Project naming helpers."""

from __future__ import annotations

import keyword
import re


_SEPARATORS_RE = re.compile(r"[^a-zA-Z0-9]+")
_DUPLICATE_UNDERSCORE_RE = re.compile(r"_+")


def slugify(value: str) -> str:
    """Normalize text into a filesystem-safe kebab-case slug."""
    value = value.strip().lower()
    value = _SEPARATORS_RE.sub("-", value)
    return value.strip("-")


def module_name(value: str) -> str:
    """Normalize text into a valid Python module/package name."""
    normalized = _SEPARATORS_RE.sub("_", value.strip().lower())
    normalized = _DUPLICATE_UNDERSCORE_RE.sub("_", normalized).strip("_")
    if normalized and normalized[0].isdigit():
        normalized = f"project_{normalized}"
    if keyword.iskeyword(normalized):
        normalized = f"{normalized}_app"
    return normalized


def title_from_slug(slug: str) -> str:
    """Create a human-friendly title from a normalized slug."""
    return " ".join(part.capitalize() for part in slug.split("-") if part)

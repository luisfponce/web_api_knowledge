"""Static sanity checks for generated projects."""

from __future__ import annotations

import json
import py_compile
from pathlib import Path

import yaml

from .errors import SanityCheckError
from .manifest import required_paths
from .models import ProjectConfig


def run_sanity_checks(config: ProjectConfig) -> None:
    destination = config.destination
    missing = [path for path in required_paths(config) if not (destination / path).exists()]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        raise SanityCheckError(f"Missing generated files: {joined}")

    _check_json(destination)
    _check_yaml(destination)
    _check_python_syntax(destination)
    _check_no_source_branding(destination)


def _check_json(destination: Path) -> None:
    for path in destination.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SanityCheckError(f"Invalid JSON in {path.relative_to(destination)}: {exc}") from exc


def _check_yaml(destination: Path) -> None:
    for pattern in ("*.yml", "*.yaml"):
        for path in destination.rglob(pattern):
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                raise SanityCheckError(f"Invalid YAML in {path.relative_to(destination)}: {exc}") from exc


def _check_python_syntax(destination: Path) -> None:
    for path in destination.rglob("*.py"):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            raise SanityCheckError(f"Invalid Python in {path.relative_to(destination)}: {exc.msg}") from exc


def _check_no_source_branding(destination: Path) -> None:
    forbidden = ("web_api_knowledge", "iPrompt", "prompt-catalog-token")
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for value in forbidden:
            if value in text:
                raise SanityCheckError(f"Forbidden source branding found in {path.relative_to(destination)}")

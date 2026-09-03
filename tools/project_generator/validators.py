"""Validation and compatibility rules for project generation."""

from __future__ import annotations

import re
from pathlib import Path

from .errors import ValidationError
from .models import Backend, Database, Frontend, ProjectConfig, Structure


_PACKAGE_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def validate_project_name(name: str) -> None:
    if not name.strip():
        raise ValidationError("Project name is required.")


def validate_slug(slug: str) -> None:
    if not slug:
        raise ValidationError("Project slug could not be derived.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValidationError("Project slug must be kebab-case alphanumeric text.")


def validate_package_name(package_name: str) -> None:
    if not _PACKAGE_RE.fullmatch(package_name):
        raise ValidationError("Package name must be a valid Python identifier.")


def validate_destination(destination: Path, *, allow_existing_empty: bool = True) -> None:
    if destination.exists() and not destination.is_dir():
        raise ValidationError(f"Destination exists and is not a directory: {destination}")
    if destination.exists() and any(destination.iterdir()) and not allow_existing_empty:
        raise ValidationError(f"Destination must be empty or absent: {destination}")


def validate_config(config: ProjectConfig, *, allow_existing_empty: bool = True) -> None:
    validate_project_name(config.name)
    validate_slug(config.slug)
    validate_package_name(config.package_name)
    validate_destination(config.destination, allow_existing_empty=allow_existing_empty)

    if config.structure != Structure.MONOREPO:
        raise ValidationError("Only monorepo output is implemented in this version.")
    if config.backend == Backend.NONE and config.frontend == Frontend.NONE:
        raise ValidationError("Select at least one of backend or frontend.")
    if config.database != Database.NONE and config.backend == Backend.NONE:
        raise ValidationError("A database requires a backend in this version.")
    if config.backend_options.auth and config.backend == Backend.NONE:
        raise ValidationError("Auth scaffold requires the FastAPI backend.")
    if config.backend_options.auth and config.database == Database.NONE:
        raise ValidationError("Auth scaffold requires a SQL database.")
    if config.backend_options.alembic and config.database == Database.NONE:
        raise ValidationError("Alembic requires a SQL database.")
    if config.infra.caddy and not config.infra.docker:
        raise ValidationError("Caddy generation requires Docker Compose files.")
    if config.infra.caddy and not (config.has_frontend or config.has_backend):
        raise ValidationError("Caddy requires at least one HTTP service.")
    if config.frontend_options.api_client.value == "axios":
        raise ValidationError("Axios is reserved for a future generator plugin; use Fetch.")

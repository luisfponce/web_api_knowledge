"""YAML configuration loading for rapid project generation."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Any

import yaml

from .errors import ValidationError
from .models import (
    ApiClient,
    Backend,
    BackendOptions,
    Database,
    Frontend,
    FrontendOptions,
    InfraOptions,
    ProjectConfig,
    Structure,
)
from .naming import module_name, slugify, title_from_slug
from .validators import validate_config


_TOP_LEVEL_KEYS = {"project", "stack", "backend_options", "frontend_options", "infra"}
_PROJECT_KEYS = {
    "name",
    "slug",
    "package_name",
    "description",
    "destination",
    "structure",
    "init_git",
    "agents_md",
}
_STACK_KEYS = {"backend", "frontend", "database"}


def load_config_file(path: Path) -> ProjectConfig:
    """Load, validate, and normalize a YAML generator configuration file."""
    if not path.exists():
        raise ValidationError(f"Config file does not exist: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(f"Invalid YAML in config file {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError("Config file must contain a top-level mapping.")
    _reject_unknown_keys(raw, _TOP_LEVEL_KEYS, "top-level config")

    project = _mapping(raw.get("project", {}), "project")
    stack = _mapping(raw.get("stack", {}), "stack")
    backend_options = _mapping(raw.get("backend_options", {}), "backend_options")
    frontend_options = _mapping(raw.get("frontend_options", {}), "frontend_options")
    infra = _mapping(raw.get("infra", {}), "infra")

    _reject_unknown_keys(project, _PROJECT_KEYS, "project")
    _reject_unknown_keys(stack, _STACK_KEYS, "stack")
    _reject_unknown_keys(backend_options, _dataclass_keys(BackendOptions), "backend_options")
    _reject_unknown_keys(frontend_options, _dataclass_keys(FrontendOptions), "frontend_options")
    _reject_unknown_keys(infra, _dataclass_keys(InfraOptions), "infra")

    name = _required_str(project, "name")
    slug = _optional_str(project, "slug") or slugify(name)
    package_name = _optional_str(project, "package_name") or module_name(slug)
    description = _optional_str(project, "description") or f"{title_from_slug(slug)} application"
    destination_value = _optional_str(project, "destination") or str(Path.cwd() / slug)

    config = ProjectConfig(
        name=name,
        slug=slug,
        package_name=package_name,
        description=description,
        destination=Path(destination_value).expanduser().resolve(),
        structure=_enum(project.get("structure", Structure.MONOREPO.value), Structure, "project.structure"),
        init_git=_bool(project.get("init_git", True), "project.init_git"),
        agents_md=_bool(project.get("agents_md", True), "project.agents_md"),
        backend=_enum(stack.get("backend", Backend.FASTAPI.value), Backend, "stack.backend"),
        frontend=_enum(stack.get("frontend", Frontend.REACT_VITE.value), Frontend, "stack.frontend"),
        database=_enum(stack.get("database", Database.POSTGRESQL.value), Database, "stack.database"),
        backend_options=BackendOptions(**_coerce_dataclass_options(backend_options, BackendOptions, "backend_options")),
        frontend_options=FrontendOptions(
            **_coerce_dataclass_options(frontend_options, FrontendOptions, "frontend_options")
        ),
        infra=InfraOptions(**_coerce_dataclass_options(infra, InfraOptions, "infra")),
    )
    validate_config(config, allow_existing_empty=True)
    return config


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"Config section '{field_name}' must be a mapping.")
    return value


def _reject_unknown_keys(value: dict[str, Any], allowed: set[str], field_name: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        keys = ", ".join(unknown)
        allowed_keys = ", ".join(sorted(allowed))
        raise ValidationError(f"Unknown key(s) in {field_name}: {keys}. Allowed keys: {allowed_keys}.")


def _dataclass_keys(dataclass_type: type) -> set[str]:
    return {field.name for field in fields(dataclass_type)}


def _required_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Config field 'project.{key}' is required and must be a non-empty string.")
    return value.strip()


def _optional_str(mapping: dict[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Config field 'project.{key}' must be a non-empty string when provided.")
    return value.strip()


def _bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"Config field '{field_name}' must be true or false.")
    return value


def _enum(value: Any, enum_type: type, field_name: str):
    if not isinstance(value, str):
        raise ValidationError(f"Config field '{field_name}' must be a string.")
    try:
        return enum_type(value)
    except ValueError as exc:
        accepted = ", ".join(item.value for item in enum_type)
        raise ValidationError(f"Invalid value for '{field_name}': {value}. Accepted values: {accepted}.") from exc


def _coerce_dataclass_options(mapping: dict[str, Any], dataclass_type: type, section: str) -> dict[str, Any]:
    defaults = dataclass_type()
    values: dict[str, Any] = {}
    for field in fields(dataclass_type):
        raw_value = mapping.get(field.name, getattr(defaults, field.name))
        field_name = f"{section}.{field.name}"
        if field.type in {bool, "bool"}:
            values[field.name] = _bool(raw_value, field_name)
        elif field.name == "api_client":
            values[field.name] = _enum(raw_value, ApiClient, field_name)
        else:
            values[field.name] = raw_value
    return values

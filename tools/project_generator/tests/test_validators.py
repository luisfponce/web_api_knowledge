from pathlib import Path

import pytest

from tools.project_generator.errors import ValidationError
from tools.project_generator.models import Backend, BackendOptions, Database, Frontend, InfraOptions, ProjectConfig, Structure
from tools.project_generator.naming import module_name, slugify
from tools.project_generator.validators import validate_config, validate_package_name


def config_for(tmp_path: Path, **overrides) -> ProjectConfig:
    values = {
        "name": "Acme Task Board",
        "slug": "acme-task-board",
        "package_name": "acme_task_board",
        "description": "Task tracking app",
        "destination": tmp_path / "acme-task-board",
        "backend": Backend.FASTAPI,
        "frontend": Frontend.REACT_VITE,
        "database": Database.POSTGRESQL,
        "backend_options": BackendOptions(auth=True, alembic=True),
        "infra": InfraOptions(docker=True, caddy=True, github_actions=True),
    }
    values.update(overrides)
    return ProjectConfig(**values)


def test_naming_helpers_normalize_text() -> None:
    assert slugify("Acme Task Board!") == "acme-task-board"
    assert module_name("123 Acme Task Board") == "project_123_acme_task_board"
    assert module_name("class") == "class_app"


def test_package_name_must_be_identifier() -> None:
    with pytest.raises(ValidationError):
        validate_package_name("not-valid")


def test_requires_backend_or_frontend(tmp_path: Path) -> None:
    config = config_for(
        tmp_path,
        backend=Backend.NONE,
        frontend=Frontend.NONE,
        database=Database.NONE,
        backend_options=BackendOptions(auth=False, alembic=False),
        infra=InfraOptions(docker=False, caddy=False),
    )
    with pytest.raises(ValidationError, match="at least one"):
        validate_config(config)


def test_auth_requires_database(tmp_path: Path) -> None:
    config = config_for(
        tmp_path,
        database=Database.NONE,
        backend_options=BackendOptions(auth=True, alembic=False),
    )
    with pytest.raises(ValidationError, match="Auth scaffold requires"):
        validate_config(config)


def test_polyrepo_is_reserved_for_later(tmp_path: Path) -> None:
    config = config_for(tmp_path, structure=Structure.POLYREPO)
    with pytest.raises(ValidationError, match="Only monorepo"):
        validate_config(config)

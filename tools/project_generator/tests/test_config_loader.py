from pathlib import Path

import pytest

from tools.project_generator.config_loader import load_config_file
from tools.project_generator.errors import ValidationError
from tools.project_generator.models import Backend, Database, Frontend


def write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_full_stack_populated_yaml(tmp_path: Path) -> None:
    destination = tmp_path / "generated"
    path = write_config(
        tmp_path,
        f"""
project:
  name: Acme Task Board
  slug: acme-task-board
  package_name: acme_task_board
  description: Team task tracking API and web app
  destination: {destination}
  structure: monorepo
  init_git: false
  agents_md: true
stack:
  backend: fastapi
  frontend: react-vite
  database: postgresql
backend_options:
  orm: true
  alembic: true
  pydantic_settings: true
  auth: true
  websockets: false
  background_tasks: false
  ruff: true
  mypy: true
  pytest: true
frontend_options:
  typescript: true
  react_router: true
  api_client: fetch
  tailwind: false
  vitest: true
  testing_library: false
infra:
  docker: true
  redis: true
  caddy: true
  github_actions: true
""",
    )

    config = load_config_file(path)

    assert config.name == "Acme Task Board"
    assert config.backend == Backend.FASTAPI
    assert config.frontend == Frontend.REACT_VITE
    assert config.database == Database.POSTGRESQL
    assert config.backend_options.mypy is True
    assert config.infra.redis is True
    assert config.destination == destination.resolve()


def test_derives_slug_and_package_name(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        f"""
project:
  name: Reporting Portal
  destination: {tmp_path / "reporting"}
stack:
  backend: none
  frontend: react-vite
  database: none
backend_options:
  auth: false
  alembic: false
infra:
  docker: false
  caddy: false
""",
    )

    config = load_config_file(path)

    assert config.slug == "reporting-portal"
    assert config.package_name == "reporting_portal"


def test_rejects_unknown_top_level_key(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
project:
  name: Bad Config
unexpected: true
""",
    )

    with pytest.raises(ValidationError, match="Unknown key"):
        load_config_file(path)


def test_rejects_unknown_nested_key(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
project:
  name: Bad Config
  package: wrong
""",
    )

    with pytest.raises(ValidationError, match="project"):
        load_config_file(path)


def test_rejects_invalid_enum_value(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
project:
  name: Bad Config
stack:
  backend: flask
""",
    )

    with pytest.raises(ValidationError, match="Accepted values"):
        load_config_file(path)


def test_rejects_empty_yaml_file(tmp_path: Path) -> None:
    path = write_config(tmp_path, "")

    with pytest.raises(ValidationError, match="top-level mapping"):
        load_config_file(path)

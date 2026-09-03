from pathlib import Path

import pytest

from tools.project_generator.cli import main


def test_cli_generates_project_from_config(tmp_path: Path) -> None:
    destination = tmp_path / "generated"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
project:
  name: Configured API
  destination: {destination}
  init_git: false
stack:
  backend: fastapi
  frontend: none
  database: sqlite
backend_options:
  auth: false
  alembic: false
infra:
  docker: false
  caddy: false
  github_actions: false
""",
        encoding="utf-8",
    )

    assert main(["--config", str(config_path), "--yes"]) == 0
    assert (destination / "backend/app/main.py").exists()
    assert not (destination / "frontend").exists()


def test_cli_config_values_are_not_replaced_by_parser_defaults(tmp_path: Path) -> None:
    destination = tmp_path / "frontend-only"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
project:
  name: Frontend Only
  destination: {destination}
  init_git: false
stack:
  backend: none
  frontend: react-vite
  database: none
backend_options:
  auth: false
  alembic: false
  pytest: false
infra:
  docker: false
  caddy: false
  github_actions: false
""",
        encoding="utf-8",
    )

    assert main(["--config", str(config_path), "--yes"]) == 0
    assert (destination / "frontend/src/main.tsx").exists()
    assert not (destination / "backend").exists()
    assert not (destination / ".github").exists()


def test_cli_config_allows_destination_override(tmp_path: Path) -> None:
    original_destination = tmp_path / "original"
    override_destination = tmp_path / "override"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
project:
  name: Override Demo
  destination: {original_destination}
  init_git: false
stack:
  backend: none
  frontend: react-vite
  database: none
backend_options:
  auth: false
  alembic: false
  pytest: false
infra:
  docker: false
  caddy: false
  github_actions: false
""",
        encoding="utf-8",
    )

    assert main(["--config", str(config_path), "--destination", str(override_destination), "--yes"]) == 0
    assert not original_destination.exists()
    assert (override_destination / "frontend/src/main.tsx").exists()


def test_cli_config_requires_yes_for_non_interactive_write(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
project:
  name: Needs Confirmation
  destination: {tmp_path / "generated"}
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
        encoding="utf-8",
    )

    with pytest.raises(SystemExit):
        main(["--config", str(config_path)])

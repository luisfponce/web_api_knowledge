from pathlib import Path

import pytest

from tools.project_generator.errors import SanityCheckError
from tools.project_generator.models import Backend, BackendOptions, Database, Frontend, InfraOptions, ProjectConfig
from tools.project_generator.renderer import render_to_directory
from tools.project_generator.sanity import run_sanity_checks


def frontend_only_config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        name="Frontend Only",
        slug="frontend-only",
        package_name="frontend_only",
        description="Frontend app",
        destination=tmp_path / "frontend-only",
        backend=Backend.NONE,
        frontend=Frontend.REACT_VITE,
        database=Database.NONE,
        backend_options=BackendOptions(auth=False, alembic=False, pytest=False),
        infra=InfraOptions(docker=False, caddy=False, github_actions=False),
    )


def test_sanity_rejects_invalid_json(tmp_path: Path) -> None:
    config = frontend_only_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)
    (config.destination / "frontend/package.json").write_text("{invalid", encoding="utf-8")

    with pytest.raises(SanityCheckError, match="Invalid JSON"):
        run_sanity_checks(config)


def test_sanity_rejects_source_branding(tmp_path: Path) -> None:
    config = frontend_only_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)
    (config.destination / "README.md").write_text("web_api_knowledge", encoding="utf-8")

    with pytest.raises(SanityCheckError, match="Forbidden source branding"):
        run_sanity_checks(config)

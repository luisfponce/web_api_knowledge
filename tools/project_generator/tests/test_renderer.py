from pathlib import Path
import json
import tomllib

import pytest
from jinja2 import UndefinedError

from tools.project_generator.errors import RenderError, ValidationError
from tools.project_generator.models import Backend, BackendOptions, Database, Frontend, InfraOptions, ProjectConfig
from tools.project_generator.renderer import create_environment, render_project, render_to_directory
from tools.project_generator.sanity import run_sanity_checks


def backend_only_config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        name="API Only",
        slug="api-only",
        package_name="api_only",
        description="Backend only app",
        destination=tmp_path / "api-only",
        backend=Backend.FASTAPI,
        frontend=Frontend.NONE,
        database=Database.SQLITE,
        backend_options=BackendOptions(auth=False, alembic=False, pytest=True),
        infra=InfraOptions(docker=False, caddy=False, github_actions=False),
    )


def full_stack_config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        name="Acme Task Board",
        slug="acme-task-board",
        package_name="acme_task_board",
        description="Task tracking app",
        destination=tmp_path / "acme-task-board",
        backend=Backend.FASTAPI,
        frontend=Frontend.REACT_VITE,
        database=Database.POSTGRESQL,
        backend_options=BackendOptions(auth=True, alembic=True, pytest=True),
        infra=InfraOptions(docker=True, redis=True, caddy=True, github_actions=True),
    )


def test_strict_undefined_fails_loudly() -> None:
    env = create_environment()
    with pytest.raises(UndefinedError):
        env.from_string("{{ missing.value }}").render({})


def test_render_backend_only_project_passes_static_sanity(tmp_path: Path) -> None:
    config = backend_only_config(tmp_path)
    config.destination.mkdir()
    written = render_to_directory(config, config.destination)

    assert config.destination / "backend/app/main.py" in written
    assert (config.destination / "backend/app/main.py").exists()
    run_sanity_checks(config)


def test_render_full_stack_project_passes_static_sanity(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    assert (config.destination / "frontend/src/main.tsx").exists()
    assert (config.destination / "docker-compose.yml").exists()
    run_sanity_checks(config)


def test_backend_pyproject_limits_setuptools_package_discovery(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    pyproject = tomllib.loads((config.destination / "backend/pyproject.toml").read_text(encoding="utf-8"))

    package_find = pyproject["tool"]["setuptools"]["packages"]["find"]
    assert package_find["include"] == ["app*"]
    assert "alembic*" in package_find["exclude"]
    assert "tests*" in package_find["exclude"]


def test_auth_backend_pyproject_includes_email_validation_dependency(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    pyproject = tomllib.loads((config.destination / "backend/pyproject.toml").read_text(encoding="utf-8"))

    assert any(dependency.startswith("pydantic[email]") for dependency in pyproject["project"]["dependencies"])


def test_db_tests_override_database_url_before_app_imports(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    conftest = (config.destination / "backend/tests/conftest.py").read_text(encoding="utf-8")

    assert conftest.index("os.environ.setdefault") < conftest.index("from app.db.session import get_session")


def test_generated_makefile_uses_explicit_env_file_for_compose_up(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    makefile = (config.destination / "Makefile").read_text(encoding="utf-8")

    assert "--env-file .env up --build" in makefile


def test_frontend_docker_and_ci_are_lockfile_tolerant(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    dockerfile = (config.destination / "frontend/Dockerfile").read_text(encoding="utf-8")
    ci = (config.destination / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "if [ -f package-lock.json ]; then npm ci; else npm install; fi" in dockerfile
    assert "if [ -f package-lock.json ]; then npm ci; else npm install; fi" in ci


def test_generated_gitignore_covers_common_local_artifacts(tmp_path: Path) -> None:
    config = full_stack_config(tmp_path)
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    gitignore = (config.destination / ".gitignore").read_text(encoding="utf-8")

    for entry in ("*.egg-info/", "*.sqlite", "*.sqlite3", "*.tsbuildinfo", "coverage/", ".kilo/plans/"):
        assert entry in gitignore


def test_special_character_metadata_renders_valid_manifests(tmp_path: Path) -> None:
    config = ProjectConfig(
        name="Bob's \"Portal\"",
        slug="bobs-portal",
        package_name="bobs_portal",
        description="Tracks \"quoted\" <things> & users' work",
        destination=tmp_path / "bobs-portal",
        backend=Backend.FASTAPI,
        frontend=Frontend.REACT_VITE,
        database=Database.SQLITE,
        backend_options=BackendOptions(auth=False, alembic=False, pytest=True),
        infra=InfraOptions(docker=False, caddy=False, github_actions=False),
    )
    config.destination.mkdir()
    render_to_directory(config, config.destination)

    pyproject = tomllib.loads((config.destination / "backend/pyproject.toml").read_text(encoding="utf-8"))
    package_json = json.loads((config.destination / "frontend/package.json").read_text(encoding="utf-8"))
    home_page = (config.destination / "frontend/src/pages/home-page.tsx").read_text(encoding="utf-8")

    assert pyproject["project"]["description"] == "Tracks \"quoted\" <things> & users' work backend"
    assert package_json["name"] == "bobs-portal-frontend"
    assert "Bob's \\\"Portal\\\"" in home_page
    run_sanity_checks(config)


def test_render_project_prevents_overwrite(tmp_path: Path) -> None:
    config = backend_only_config(tmp_path)
    config.destination.mkdir()
    (config.destination / "existing.txt").write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(ValidationError, match="empty or absent"):
        render_project(config)


def test_render_project_rejects_destination_that_changes_mid_render(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = backend_only_config(tmp_path)
    original_mkdir = Path.mkdir

    def mkdir_and_dirty(self: Path, *args, **kwargs):
        original_mkdir(self, *args, **kwargs)
        if self == config.destination.parent:
            config.destination.mkdir(exist_ok=True)
            (config.destination / "race.txt").write_text("dirty", encoding="utf-8")

    monkeypatch.setattr(Path, "mkdir", mkdir_and_dirty)
    with pytest.raises(RenderError, match="became non-empty"):
        render_project(config)

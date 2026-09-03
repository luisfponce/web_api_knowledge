from pathlib import Path

from tools.project_generator.manifest import build_manifest
from tools.project_generator.models import Backend, BackendOptions, Database, Frontend, InfraOptions, ProjectConfig


def test_full_stack_manifest_includes_selected_capabilities(tmp_path: Path) -> None:
    config = ProjectConfig(
        name="Acme Task Board",
        slug="acme-task-board",
        package_name="acme_task_board",
        description="Task app",
        destination=tmp_path / "acme-task-board",
        backend=Backend.FASTAPI,
        frontend=Frontend.REACT_VITE,
        database=Database.POSTGRESQL,
        backend_options=BackendOptions(auth=True, alembic=True, pytest=True),
        infra=InfraOptions(docker=True, redis=True, caddy=True, github_actions=True),
    )

    destinations = {spec.destination for spec in build_manifest(config)}

    assert "AGENTS.md" in destinations
    assert "backend/app/main.py" in destinations
    assert "backend/alembic/env.py" in destinations
    assert "backend/app/api/v1/auth.py" in destinations
    assert "backend/.dockerignore" in destinations
    assert "frontend/src/lib/http/api-client.ts" in destinations
    assert "frontend/src/vite-env.d.ts" in destinations
    assert "frontend/.dockerignore" in destinations
    assert "docker-compose.yml" in destinations
    assert "Caddyfile.example" in destinations
    assert ".github/workflows/ci.yml" in destinations


def test_backend_only_sqlite_manifest_omits_frontend_and_alembic(tmp_path: Path) -> None:
    config = ProjectConfig(
        name="API Only",
        slug="api-only",
        package_name="api_only",
        description="API app",
        destination=tmp_path / "api-only",
        backend=Backend.FASTAPI,
        frontend=Frontend.NONE,
        database=Database.SQLITE,
        backend_options=BackendOptions(auth=False, alembic=False, pytest=True),
        infra=InfraOptions(docker=False, caddy=False, github_actions=False),
    )

    destinations = {spec.destination for spec in build_manifest(config)}

    assert "backend/app/main.py" in destinations
    assert "backend/app/api/v1/items.py" in destinations
    assert "backend/alembic/env.py" not in destinations
    assert "backend/.dockerignore" not in destinations
    assert not any(path.startswith("frontend/") for path in destinations)

"""Manifest construction for selected generator capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from .models import Database, ProjectConfig


@dataclass(frozen=True)
class TemplateSpec:
    template: str
    destination: str


def build_manifest(config: ProjectConfig) -> list[TemplateSpec]:
    """Return the exact templates to render for a project configuration."""
    specs: list[TemplateSpec] = [
        TemplateSpec("common/gitignore.j2", ".gitignore"),
        TemplateSpec("common/env.example.j2", ".env.example"),
        TemplateSpec("common/README.md.j2", "README.md"),
        TemplateSpec("common/Makefile.j2", "Makefile"),
    ]
    if config.agents_md:
        specs.append(TemplateSpec("agents/AGENTS.md.j2", "AGENTS.md"))

    if config.has_backend:
        specs.extend(_backend_specs(config))
    if config.has_frontend:
        specs.extend(_frontend_specs(config))
    if config.infra.docker:
        specs.extend(_docker_specs(config))
    if config.infra.caddy:
        specs.append(TemplateSpec("infra_caddy/Caddyfile.example.j2", "Caddyfile.example"))
    if config.infra.github_actions:
        specs.append(TemplateSpec("infra_github_actions/ci.yml.j2", ".github/workflows/ci.yml"))

    return specs


def required_paths(config: ProjectConfig) -> list[Path]:
    """Return files that must exist after rendering."""
    return [Path(spec.destination) for spec in build_manifest(config)]


def _backend_specs(config: ProjectConfig) -> list[TemplateSpec]:
    specs = [
        TemplateSpec("backend_fastapi/pyproject.toml.j2", "backend/pyproject.toml"),
        TemplateSpec("backend_fastapi/app/__init__.py.j2", "backend/app/__init__.py"),
        TemplateSpec("backend_fastapi/app/main.py.j2", "backend/app/main.py"),
        TemplateSpec("backend_fastapi/app/api/__init__.py.j2", "backend/app/api/__init__.py"),
        TemplateSpec("backend_fastapi/app/api/router.py.j2", "backend/app/api/router.py"),
        TemplateSpec("backend_fastapi/app/api/v1/__init__.py.j2", "backend/app/api/v1/__init__.py"),
        TemplateSpec("backend_fastapi/app/api/v1/health.py.j2", "backend/app/api/v1/health.py"),
        TemplateSpec("backend_fastapi/app/core/__init__.py.j2", "backend/app/core/__init__.py"),
        TemplateSpec("backend_fastapi/app/core/config.py.j2", "backend/app/core/config.py"),
        TemplateSpec("backend_fastapi/app/core/errors.py.j2", "backend/app/core/errors.py"),
    ]
    if config.has_database:
        specs.extend(
            [
                TemplateSpec("backend_fastapi/app/db/__init__.py.j2", "backend/app/db/__init__.py"),
                TemplateSpec("backend_fastapi/app/db/base.py.j2", "backend/app/db/base.py"),
                TemplateSpec("backend_fastapi/app/db/session.py.j2", "backend/app/db/session.py"),
                TemplateSpec("backend_fastapi/app/models/__init__.py.j2", "backend/app/models/__init__.py"),
                TemplateSpec("backend_fastapi/app/models/item.py.j2", "backend/app/models/item.py"),
                TemplateSpec("backend_fastapi/app/repositories/__init__.py.j2", "backend/app/repositories/__init__.py"),
                TemplateSpec("backend_fastapi/app/repositories/items.py.j2", "backend/app/repositories/items.py"),
                TemplateSpec("backend_fastapi/app/schemas/__init__.py.j2", "backend/app/schemas/__init__.py"),
                TemplateSpec("backend_fastapi/app/schemas/item.py.j2", "backend/app/schemas/item.py"),
                TemplateSpec("backend_fastapi/app/services/__init__.py.j2", "backend/app/services/__init__.py"),
                TemplateSpec("backend_fastapi/app/services/items.py.j2", "backend/app/services/items.py"),
                TemplateSpec("backend_fastapi/app/api/v1/items.py.j2", "backend/app/api/v1/items.py"),
            ]
        )
    if config.backend_options.auth:
        specs.extend(
            [
                TemplateSpec("backend_fastapi/app/core/security.py.j2", "backend/app/core/security.py"),
                TemplateSpec("backend_fastapi/app/models/user.py.j2", "backend/app/models/user.py"),
                TemplateSpec("backend_fastapi/app/repositories/users.py.j2", "backend/app/repositories/users.py"),
                TemplateSpec("backend_fastapi/app/schemas/auth.py.j2", "backend/app/schemas/auth.py"),
                TemplateSpec("backend_fastapi/app/schemas/user.py.j2", "backend/app/schemas/user.py"),
                TemplateSpec("backend_fastapi/app/services/auth.py.j2", "backend/app/services/auth.py"),
                TemplateSpec("backend_fastapi/app/api/v1/auth.py.j2", "backend/app/api/v1/auth.py"),
            ]
        )
    if config.backend_options.alembic:
        specs.extend(
            [
                TemplateSpec("backend_fastapi/alembic.ini.j2", "backend/alembic.ini"),
                TemplateSpec("backend_fastapi/alembic/env.py.j2", "backend/alembic/env.py"),
                TemplateSpec("backend_fastapi/alembic/versions/gitkeep.j2", "backend/alembic/versions/.gitkeep"),
            ]
        )
    if config.infra.docker:
        specs.extend(
            [
                TemplateSpec("backend_fastapi/Dockerfile.j2", "backend/Dockerfile"),
                TemplateSpec("backend_fastapi/dockerignore.j2", "backend/.dockerignore"),
            ]
        )
    if config.backend_options.pytest:
        specs.extend(
            [
                TemplateSpec("backend_fastapi/tests/conftest.py.j2", "backend/tests/conftest.py"),
                TemplateSpec("backend_fastapi/tests/test_health.py.j2", "backend/tests/test_health.py"),
            ]
        )
        if config.has_database:
            specs.append(TemplateSpec("backend_fastapi/tests/test_items.py.j2", "backend/tests/test_items.py"))
        if config.backend_options.auth:
            specs.append(TemplateSpec("backend_fastapi/tests/test_auth.py.j2", "backend/tests/test_auth.py"))
    if config.database == Database.NONE:
        specs.append(TemplateSpec("backend_fastapi/app/schemas/__init__.py.j2", "backend/app/schemas/__init__.py"))
    return specs


def _frontend_specs(config: ProjectConfig) -> list[TemplateSpec]:
    specs = [
        TemplateSpec("frontend_react_vite/package.json.j2", "frontend/package.json"),
        TemplateSpec("frontend_react_vite/index.html.j2", "frontend/index.html"),
        TemplateSpec("frontend_react_vite/vite.config.ts.j2", "frontend/vite.config.ts"),
        TemplateSpec("frontend_react_vite/tsconfig.json.j2", "frontend/tsconfig.json"),
        TemplateSpec("frontend_react_vite/tsconfig.app.json.j2", "frontend/tsconfig.app.json"),
        TemplateSpec("frontend_react_vite/eslint.config.js.j2", "frontend/eslint.config.js"),
        TemplateSpec("frontend_react_vite/src/main.tsx.j2", "frontend/src/main.tsx"),
        TemplateSpec("frontend_react_vite/src/vite-env.d.ts.j2", "frontend/src/vite-env.d.ts"),
        TemplateSpec("frontend_react_vite/src/app/providers.tsx.j2", "frontend/src/app/providers.tsx"),
        TemplateSpec("frontend_react_vite/src/app/router.tsx.j2", "frontend/src/app/router.tsx"),
        TemplateSpec("frontend_react_vite/src/components/ui/button.tsx.j2", "frontend/src/components/ui/button.tsx"),
        TemplateSpec("frontend_react_vite/src/components/ui/card.tsx.j2", "frontend/src/components/ui/card.tsx"),
        TemplateSpec("frontend_react_vite/src/components/ui/input.tsx.j2", "frontend/src/components/ui/input.tsx"),
        TemplateSpec("frontend_react_vite/src/pages/home-page.tsx.j2", "frontend/src/pages/home-page.tsx"),
        TemplateSpec("frontend_react_vite/src/pages/items-page.tsx.j2", "frontend/src/pages/items-page.tsx"),
        TemplateSpec("frontend_react_vite/src/styles/base.css.j2", "frontend/src/styles/base.css"),
    ]
    if config.has_backend:
        specs.extend(
            [
                TemplateSpec("frontend_react_vite/src/lib/http/api-error.ts.j2", "frontend/src/lib/http/api-error.ts"),
                TemplateSpec("frontend_react_vite/src/lib/http/api-client.ts.j2", "frontend/src/lib/http/api-client.ts"),
                TemplateSpec("frontend_react_vite/src/features/items/items-types.ts.j2", "frontend/src/features/items/items-types.ts"),
                TemplateSpec("frontend_react_vite/src/features/items/items-service.ts.j2", "frontend/src/features/items/items-service.ts"),
            ]
        )
    if config.infra.docker:
        specs.extend(
            [
                TemplateSpec("frontend_react_vite/Dockerfile.j2", "frontend/Dockerfile"),
                TemplateSpec("frontend_react_vite/dockerignore.j2", "frontend/.dockerignore"),
                TemplateSpec("frontend_react_vite/nginx.conf.j2", "frontend/nginx.conf"),
            ]
        )
    if config.frontend_options.vitest:
        specs.append(TemplateSpec("frontend_react_vite/src/pages/home-page.test.tsx.j2", "frontend/src/pages/home-page.test.tsx"))
    return specs


def _docker_specs(config: ProjectConfig) -> list[TemplateSpec]:
    return [
        TemplateSpec("infra_docker/docker-compose.yml.j2", "docker-compose.yml"),
        TemplateSpec("infra_docker/docker-compose.local.yml.j2", "docker-compose.local.yml"),
        TemplateSpec("infra_docker/docker-compose.prod.yml.j2", "docker-compose.prod.yml"),
    ]

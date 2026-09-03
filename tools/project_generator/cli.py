"""Command line entrypoint for the project generator."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .config_loader import load_config_file
from .errors import GeneratorError
from .git_ops import init_repository
from .models import Backend, BackendOptions, Database, Frontend, FrontendOptions, InfraOptions, ProjectConfig, Structure
from .naming import module_name, slugify, title_from_slug
from .prompts import format_summary, run_wizard
from .renderer import render_project
from .sanity import run_sanity_checks
from .validators import validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a modular FastAPI/React project.")
    parser.add_argument("--config", type=Path, help="YAML config file for rapid non-interactive setup.")
    parser.add_argument("--name", help="Project display name. If omitted, run the interactive wizard.")
    parser.add_argument("--destination", type=Path, help="Destination directory.")
    parser.add_argument("--package-name", help="Python package/module name.")
    parser.add_argument("--description", help="Project description.")
    parser.add_argument("--backend", choices=[item.value for item in Backend], default=None)
    parser.add_argument("--frontend", choices=[item.value for item in Frontend], default=None)
    parser.add_argument("--database", choices=[item.value for item in Database], default=None)
    parser.add_argument("--no-auth", action="store_true", default=None, help="Skip JWT/OAuth2 auth scaffold.")
    parser.add_argument("--no-alembic", action="store_true", default=None, help="Skip Alembic migrations.")
    parser.add_argument("--mypy", action="store_true", default=None, help="Enable generated mypy config and CI step.")
    parser.add_argument("--no-pytest", action="store_true", default=None, help="Skip backend pytest scaffold.")
    parser.add_argument("--no-docker", action="store_true", default=None, help="Skip Docker and Compose files.")
    parser.add_argument("--redis", action="store_true", default=None, help="Include Redis service and env contract.")
    parser.add_argument("--caddy", action="store_true", default=None, help="Include Caddy production proxy overlay.")
    parser.add_argument("--no-github-actions", action="store_true", default=None, help="Skip GitHub Actions CI.")
    parser.add_argument("--no-agents", action="store_true", default=None, help="Skip generated AGENTS.md.")
    parser.add_argument("--no-git", action="store_true", default=None, help="Skip git init.")
    parser.add_argument("--yes", action="store_true", help="Do not ask for final confirmation in non-interactive mode.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.config:
            config = _apply_arg_overrides(load_config_file(args.config), args)
        elif args.name:
            config = _config_from_args(args)
        else:
            config = run_wizard()
        validate_config(config, allow_existing_empty=False)
        if (args.name or args.config) and not args.yes:
            print(format_summary(config))
            parser.error("Pass --yes to write files in non-interactive mode.")
        render_project(config)
        run_sanity_checks(config)
        git_initialized = init_repository(config.destination) if config.init_git else False
    except GeneratorError as exc:
        parser.exit(2, f"error: {exc}\n")

    print(format_next_steps(config, git_initialized=git_initialized))
    return 0


def _config_from_args(args: argparse.Namespace) -> ProjectConfig:
    slug = slugify(args.name)
    destination = args.destination or (Path.cwd() / slug)
    database = Database(args.database or Database.POSTGRESQL.value)
    backend = Backend(args.backend or Backend.FASTAPI.value)
    frontend = Frontend(args.frontend or Frontend.REACT_VITE.value)
    docker = not bool(args.no_docker)
    auth = not bool(args.no_auth) and backend != Backend.NONE and database != Database.NONE
    alembic = not bool(args.no_alembic) and database in {Database.POSTGRESQL, Database.MARIADB}
    return ProjectConfig(
        name=args.name,
        slug=slug,
        package_name=args.package_name or module_name(slug),
        description=args.description or f"{title_from_slug(slug)} application",
        destination=destination.expanduser().resolve(),
        structure=Structure.MONOREPO,
        init_git=not bool(args.no_git),
        agents_md=not bool(args.no_agents),
        backend=backend,
        frontend=frontend,
        database=database,
        backend_options=BackendOptions(auth=auth, alembic=alembic, mypy=bool(args.mypy), pytest=not bool(args.no_pytest)),
        frontend_options=FrontendOptions(),
        infra=InfraOptions(
            docker=docker,
            redis=bool(args.redis),
            caddy=bool(args.caddy),
            github_actions=not bool(args.no_github_actions),
        ),
    )


def _apply_arg_overrides(config: ProjectConfig, args: argparse.Namespace) -> ProjectConfig:
    """Apply only explicitly supplied CLI flags over a YAML configuration."""
    project_updates = {}
    if args.name:
        project_updates["name"] = args.name
        project_updates["slug"] = slugify(args.name)
        if args.package_name is None:
            project_updates["package_name"] = module_name(project_updates["slug"])
    if args.destination is not None:
        project_updates["destination"] = args.destination.expanduser().resolve()
    if args.package_name is not None:
        project_updates["package_name"] = args.package_name
    if args.description is not None:
        project_updates["description"] = args.description
    if args.backend is not None:
        project_updates["backend"] = Backend(args.backend)
    if args.frontend is not None:
        project_updates["frontend"] = Frontend(args.frontend)
    if args.database is not None:
        project_updates["database"] = Database(args.database)
    if args.no_git is not None:
        project_updates["init_git"] = False
    if args.no_agents is not None:
        project_updates["agents_md"] = False

    backend_options = config.backend_options
    backend_option_updates = {}
    if args.no_auth is not None:
        backend_option_updates["auth"] = False
    if args.no_alembic is not None:
        backend_option_updates["alembic"] = False
    if args.mypy is not None:
        backend_option_updates["mypy"] = True
    if args.no_pytest is not None:
        backend_option_updates["pytest"] = False
    if backend_option_updates:
        backend_options = replace(backend_options, **backend_option_updates)

    infra = config.infra
    infra_updates = {}
    if args.no_docker is not None:
        infra_updates["docker"] = False
    if args.redis is not None:
        infra_updates["redis"] = True
    if args.caddy is not None:
        infra_updates["caddy"] = True
    if args.no_github_actions is not None:
        infra_updates["github_actions"] = False
    if infra_updates:
        infra = replace(infra, **infra_updates)

    return replace(config, backend_options=backend_options, infra=infra, **project_updates)


def format_next_steps(config: ProjectConfig, *, git_initialized: bool) -> str:
    lines = [
        f"Generated {config.name} at {config.destination}",
        f"Services: {', '.join(config.generated_services) or 'none'}",
        f"Git repository: {'initialized' if git_initialized else 'not initialized'}",
        "Next steps:",
    ]
    if config.has_backend:
        lines.append("  cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'")
    if config.has_frontend:
        lines.append("  cd frontend && npm install")
    lines.append("  cp .env.example .env")
    lines.append("  make test")
    if config.infra.docker:
        lines.append("  make up")
    return "\n".join(lines)

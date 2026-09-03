"""Terminal wizard prompts with safe defaults."""

from __future__ import annotations

from pathlib import Path


from .models import Backend, BackendOptions, Database, Frontend, FrontendOptions, InfraOptions, ProjectConfig, Structure
from .naming import module_name, slugify, title_from_slug


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or (default or "")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    marker = "Y/n" if default else "y/N"
    answer = input(f"{prompt} [{marker}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def run_wizard() -> ProjectConfig:
    name = ask("Project name", "Acme Task Board")
    slug = ask("Project slug", slugify(name))
    package_name = ask("Python package/module name", module_name(slug))
    description = ask("Description", f"{title_from_slug(slug)} full-stack application")
    destination = Path(ask("Destination directory", str(Path.cwd() / slug))).expanduser().resolve()

    frontend_enabled = ask_yes_no("Generate React + Vite frontend", True)
    backend_enabled = ask_yes_no("Generate FastAPI backend", True)
    database = Database.NONE
    if backend_enabled and ask_yes_no("Use PostgreSQL database", True):
        database = Database.POSTGRESQL
    elif backend_enabled and ask_yes_no("Use SQLite database", False):
        database = Database.SQLITE

    docker = ask_yes_no("Generate Docker Compose files", True)
    redis = docker and ask_yes_no("Include Redis service", False)
    caddy = docker and ask_yes_no("Include Caddy production proxy", frontend_enabled)
    github_actions = ask_yes_no("Generate GitHub Actions CI", True)
    auth = backend_enabled and database != Database.NONE and ask_yes_no("Generate JWT/OAuth2 auth scaffold", True)
    alembic = database in {Database.POSTGRESQL, Database.MARIADB} and ask_yes_no("Generate Alembic migrations", True)

    config = ProjectConfig(
        name=name,
        slug=slug,
        package_name=package_name,
        description=description,
        destination=destination,
        structure=Structure.MONOREPO,
        init_git=ask_yes_no("Initialize Git repository", True),
        agents_md=ask_yes_no("Generate AGENTS.md", True),
        backend=Backend.FASTAPI if backend_enabled else Backend.NONE,
        frontend=Frontend.REACT_VITE if frontend_enabled else Frontend.NONE,
        database=database,
        backend_options=BackendOptions(auth=auth, alembic=alembic),
        frontend_options=FrontendOptions(),
        infra=InfraOptions(docker=docker, redis=redis, caddy=caddy, github_actions=github_actions),
    )

    print("\nConfiguration summary:")
    print(format_summary(config))
    if not ask_yes_no("Write these files", False):
        raise SystemExit(1)
    return config


def format_summary(config: ProjectConfig) -> str:
    lines = [
        f"Project: {config.name}",
        f"Package: {config.package_name}",
        f"Description: {config.description}",
        f"Destination: {config.destination}",
        f"Structure: {config.structure.value}",
        f"Backend: {config.backend.value}",
        f"Frontend: {config.frontend.value}",
        f"Database: {config.database.value}",
        f"Services: {', '.join(config.generated_services) or 'none'}",
        f"Git: {'initialize' if config.init_git else 'skip'}",
        f"AGENTS.md: {'yes' if config.agents_md else 'no'}",
    ]
    return "\n".join(lines)

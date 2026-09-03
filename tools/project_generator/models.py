"""Configuration models for generated projects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Structure(StrEnum):
    MONOREPO = "monorepo"
    POLYREPO = "polyrepo"


class Backend(StrEnum):
    NONE = "none"
    FASTAPI = "fastapi"


class Frontend(StrEnum):
    NONE = "none"
    REACT_VITE = "react-vite"


class Database(StrEnum):
    NONE = "none"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MARIADB = "mariadb"


class ApiClient(StrEnum):
    FETCH = "fetch"
    AXIOS = "axios"


@dataclass(frozen=True)
class BackendOptions:
    orm: bool = True
    alembic: bool = True
    pydantic_settings: bool = True
    auth: bool = True
    websockets: bool = False
    background_tasks: bool = False
    ruff: bool = True
    mypy: bool = False
    pytest: bool = True


@dataclass(frozen=True)
class FrontendOptions:
    typescript: bool = True
    react_router: bool = True
    api_client: ApiClient = ApiClient.FETCH
    tailwind: bool = False
    vitest: bool = True
    testing_library: bool = False


@dataclass(frozen=True)
class InfraOptions:
    docker: bool = True
    redis: bool = False
    caddy: bool = False
    github_actions: bool = True


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    slug: str
    package_name: str
    description: str
    destination: Path
    structure: Structure = Structure.MONOREPO
    init_git: bool = True
    agents_md: bool = True
    backend: Backend = Backend.FASTAPI
    frontend: Frontend = Frontend.REACT_VITE
    database: Database = Database.POSTGRESQL
    backend_options: BackendOptions = BackendOptions()
    frontend_options: FrontendOptions = FrontendOptions()
    infra: InfraOptions = InfraOptions()

    @property
    def has_backend(self) -> bool:
        return self.backend != Backend.NONE

    @property
    def has_frontend(self) -> bool:
        return self.frontend != Frontend.NONE

    @property
    def has_database(self) -> bool:
        return self.database != Database.NONE

    @property
    def has_persistent_database(self) -> bool:
        return self.database in {Database.POSTGRESQL, Database.MARIADB}

    @property
    def db_service_name(self) -> str:
        if self.database == Database.POSTGRESQL:
            return "postgres"
        if self.database == Database.MARIADB:
            return "mariadb"
        return ""

    @property
    def database_url_placeholder(self) -> str:
        if self.database == Database.SQLITE:
            return "sqlite+pysqlite:///./app.db"
        if self.database == Database.POSTGRESQL:
            return "postgresql+psycopg://app:change-me@postgres:5432/app"
        if self.database == Database.MARIADB:
            return "mysql+pymysql://app:change-me@mariadb:3306/app"
        return ""

    @property
    def generated_services(self) -> list[str]:
        services: list[str] = []
        if self.has_backend:
            services.append("backend")
        if self.has_frontend:
            services.append("frontend")
        if self.has_persistent_database:
            services.append(self.db_service_name)
        if self.infra.redis:
            services.append("redis")
        if self.infra.caddy:
            services.append("caddy")
        return services

# web_api_knowledge

## Summary

`web_api_knowledge` is a full-stack learning project for Web API concepts using FastAPI, MariaDB, and React/Vite. The app includes authentication plus prompt CRUD flows backed by a SQLModel data model.

## Quick Start

The startup script deploys the frontend, backend, and MariaDB with Docker Compose, waits for service readiness, and verifies basic connectivity.

```bash
./scripts/run-compose-stack.sh
```

Primary URLs:

- Frontend: `http://127.0.0.1:8080`
- Backend direct: `http://127.0.0.1:8000`
- API through frontend proxy: `http://127.0.0.1:8080/api/v1/...`

Stop the stack from the repository root:

```bash
docker compose down
```

Use `docker-compose down` if your environment only has the legacy Compose command.

## Documentation

- [`frontend/README.md`](frontend/README.md): frontend local development, production build, Docker, nginx proxying, and environment notes.
- [`webapi/README.md`](webapi/README.md): backend deployment, MariaDB operations, API checks, configuration, and troubleshooting.
- [`webapi/tests/README.md`](webapi/tests/README.md): backend test commands and CI/CD test mapping.
- [`plans/dbdiagram.md`](plans/dbdiagram.md): database and ORM diagram details for dbdiagram.io.

## Repository Layout

- `frontend/`: React, TypeScript, and Vite frontend served by nginx in Docker.
- `webapi/`: FastAPI backend application, API routes, models, configuration, and database connections.
- `webapi/tests/`: pytest suites for functional route tests and nonfunctional CI checks.
- `scripts/`: local automation, including the full-stack Compose startup script.
- `docker-compose.yml`: MariaDB, backend, and frontend service definitions for local full-stack runs.

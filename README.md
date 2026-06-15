# web_api_knowledge

## Summary

`web_api_knowledge` is a full-stack learning project for Web API concepts using FastAPI, MariaDB, and React/Vite. The app includes authentication plus prompt CRUD flows backed by a SQLModel data model.

## Quick Start

The startup script deploys the frontend, backend, MariaDB, and Redis with Docker Compose, waits for service readiness, and verifies basic connectivity.

For local development, copy the placeholder environment template and replace the values with local-only secrets before starting the stack:

```bash
cp .env.example .env
```

The startup script treats `.env` as a non-blocking shared configuration file. If values are missing, it prints warnings and Compose falls back to local placeholders so developers can still bring up the stack for basic testing.

```bash
./scripts/run-compose-stack.sh
```

Primary URLs:

- Frontend: `http://127.0.0.1:8080`
- Backend direct: `http://127.0.0.1:8000/docs`
- API through frontend proxy: `http://127.0.0.1:8080/api/v1/...`

Stop the stack from the repository root:

```bash
docker compose down
```

Use `docker-compose down` if your environment only has the legacy Compose command.

## Environment Variables

Use environment variables as the configuration boundary for the application. Keep `.env` for local development only; `.gitignore` excludes it, and `.env.example` is the committed configuration contract for Python, Docker Compose, and CI/CD documentation.

Local Compose reads values such as `MARIADB_USER`, `MARIADB_PASSWORD`, `DB_URL`, `REDIS_HOST`, `REDIS_PORT`, `ENV_MAIL_USERNAME`, `ENV_MAIL_PASSWORD`, `ENV_MAIL_FROM`, and `ENV_SECRET_KEY` from your shell or `.env`. The backend also calls `load_dotenv()` in `webapi/core/config.py`, so direct Python runs can read the same root `.env` file. Do not put real email passwords, database passwords, JWT secrets, API keys, or tokens in source files, scripts, docs, or workflow YAML.

Recommended architecture:

- Keep `.env.example` as the canonical list of supported configuration keys.
- Use `.env` for local developer defaults only; it should be generated from `.env.example` and ignored by git.
- Let `docker-compose.yml` reference environment variables with local/test-safe fallbacks so basic development remains non-blocking.
- Let `webapi/core/config.py` read from process environment variables after `load_dotenv()` so the backend works the same when launched with `uvicorn` or in a container.
- Use real secret stores in shared environments instead of copying local `.env` files.

Production deployments should inject secrets from the hosting platform, such as a cloud secret manager, Kubernetes/external secrets, Docker secrets, or PaaS environment variables. Do not deploy a repository-local `.env` file to production.

GitHub Actions should use repository or environment `secrets` for sensitive values and `vars` or workflow `env` for non-sensitive constants. The current Python test jobs already read `ENV_MAIL_USERNAME`, `ENV_MAIL_PASSWORD`, and `ENV_SECRET_KEY` from GitHub Secrets; keep test credentials fake or isolated unless a workflow intentionally sends real email.

CI/CD variable guide:

| Name | Store as | Used by | Notes |
| --- | --- | --- | --- |
| `ENV_SECRET_KEY` | Secret | Backend tests, backend runtime | JWT signing key. Use a strong, environment-specific value. |
| `ENV_MAIL_PASSWORD` | Secret | SMTP/password recovery flows | Use a provider app password or transactional email API credential. |
| `ENV_MAIL_USERNAME` | Secret or variable | SMTP config | Store as a secret if it identifies a private mailbox. Fake value is enough for tests that do not send email. |
| `ENV_MAIL_FROM` | Variable or secret | SMTP sender identity | Usually non-sensitive, but keep environment-specific. |
| `DB_URL` | Secret | Backend runtime, integration tests | Required when CI/prod uses MariaDB or another external DB. Unit tests can omit it and use SQLite fallback. |
| `MARIADB_ROOT_PASSWORD` | Secret | Compose/integration environments | Needed when CI/CD starts MariaDB with Compose. |
| `MARIADB_PASSWORD` | Secret | Compose/integration environments | Must match the password embedded in `DB_URL` when Compose starts MariaDB. |
| `MARIADB_DATABASE` | Variable | Compose/integration environments | Defaults to `crud_data` locally. |
| `MARIADB_USER` | Variable or secret | Compose/integration environments | Defaults to `webapi_user` locally. |
| `REDIS_HOST` | Variable | Backend runtime | Use `redis` in Compose, service hostname in production, or `127.0.0.1` for direct local runs. |
| `REDIS_PORT` | Variable | Backend runtime | Defaults to `6379`. |
| `REDIS_PSW` | Secret | Backend runtime | Only needed when Redis requires auth. |
| `MARIADB_HOST_PORT` | Variable | Local/CI Compose | Optional published host port override. |
| `REDIS_HOST_PORT` | Variable | Local/CI Compose | Optional published host port override. |

If Gmail SMTP is used, use an app password rather than an account password. Scope and rotate credentials separately for local, CI, staging, and production.

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
- `docker-compose.yml`: MariaDB, Redis, backend, and frontend service definitions for local full-stack runs.

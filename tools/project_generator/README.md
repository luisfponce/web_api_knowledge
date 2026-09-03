# Project Generator

The Project Generator creates a clean Python 3.12+ full-stack starter project from a small set of stack choices. It is designed for monorepo applications that may include a FastAPI backend, a React + Vite frontend, SQL database support, Docker Compose infrastructure, optional Caddy reverse proxying, GitHub Actions CI, and generated `AGENTS.md` guidance.

The generator uses templates and a manifest system rather than copying an existing application wholesale. Generated projects avoid known starter-project debt such as stale Vite files, ORM models as request bodies, import-time schema creation for persistent databases, missing Python tool config, and secret-bearing environment files.

## What It Generates

- Root files: `README.md`, `Makefile`, `.env.example`, `.gitignore`, and optional `AGENTS.md`.
- Backend: FastAPI app under `backend/app`, `/api/v1` routing, Pydantic Settings, structured API errors, SQLAlchemy 2.0 models, repositories, schemas, services, tests, and optional Alembic migrations.
- Frontend: React + Vite + TypeScript under `frontend/src`, React Router, React Query provider, Fetch API client, shared UI primitives, CSS base styles, and Vitest tests.
- Infrastructure: Dockerfiles, Compose overlays, service DNS, named database volumes, optional Redis, optional Caddy, and GitHub Actions jobs matching the selected modules.
- Safety checks: required-file checks, JSON/YAML syntax validation, Python syntax validation, and generated-content checks for source-project branding.

## Requirements

- Python 3.12 or newer.
- `pip` for installing generator dependencies.
- Optional: Git, if using generated repository initialization.
- Optional: Docker, Node.js, and npm for running generated projects after creation.

## Installation

From the repository root, install the generator-only dependencies:

```bash
python -m pip install -r tools/project_generator/requirements.txt
```

The dependencies are intentionally isolated from application runtime dependencies:

- `jinja2`: strict template rendering.
- `pyyaml`: YAML config loading and generated YAML sanity checks.

## Basic Usage

Run the interactive wizard from the repository root:

```bash
python -m tools.project_generator
```

Run non-interactively with flags:

```bash
python -m tools.project_generator \
  --name "Acme Task Board" \
  --destination /tmp/kilo/acme-task-board \
  --backend fastapi \
  --frontend react-vite \
  --database postgresql \
  --redis \
  --caddy \
  --yes
```

Run from a YAML config file:

```bash
python -m tools.project_generator \
  --config tools/project_generator/config.yaml \
  --yes
```

Override selected config values from the command line:

```bash
python -m tools.project_generator \
  --config tools/project_generator/config.example.yaml \
  --destination /tmp/kilo/my-generated-app \
  --no-git \
  --yes
```

Non-interactive generation requires `--yes`. Without it, the tool prints the normalized configuration summary and exits before writing files.

## Configuration Files

Use `tools/project_generator/config.yaml` for rapid setup. Use `tools/project_generator/config.example.yaml` as the fully populated template showing every supported field. For real project runs with absolute local paths, copy either file to `tools/project_generator/config.local.yaml` and edit the copy; that local config filename is ignored by Git.

Top-level sections:

- `project`: identity, destination, repository options, and generated agent instructions.
- `stack`: backend, frontend, and database choices.
- `backend_options`: FastAPI-related optional scaffolding and Python tools.
- `frontend_options`: React/Vite-related optional scaffolding and frontend tools.
- `infra`: Docker, Redis, Caddy, and GitHub Actions choices.

Supported values:

- `project.structure`: `monorepo`. `polyrepo` is reserved for a future version.
- `stack.backend`: `fastapi`, `none`.
- `stack.frontend`: `react-vite`, `none`.
- `stack.database`: `postgresql`, `mariadb`, `sqlite`, `none`.
- `frontend_options.api_client`: `fetch`. `axios` is reserved for a future plugin.

Minimal config:

```yaml
project:
  name: Task Board Starter
  destination: /tmp/kilo/task-board-starter

stack:
  backend: fastapi
  frontend: react-vite
  database: postgresql
```

The loader derives `project.slug` and `project.package_name` from `project.name` when omitted. It fails fast on unknown keys, invalid enum values, malformed YAML, and incompatible options.

## CLI Reference

- `--config PATH`: load a YAML configuration file.
- `--name TEXT`: project display name. If omitted and no config is supplied, starts the wizard.
- `--destination PATH`: output directory. Must be absent or empty.
- `--package-name TEXT`: Python package/module name.
- `--description TEXT`: generated project description.
- `--backend {fastapi,none}`: backend stack.
- `--frontend {react-vite,none}`: frontend stack.
- `--database {postgresql,mariadb,sqlite,none}`: database stack.
- `--no-auth`: skip JWT/OAuth2 auth scaffold.
- `--no-alembic`: skip Alembic migrations.
- `--mypy`: enable generated Mypy config and CI step.
- `--no-pytest`: skip backend pytest scaffold.
- `--no-docker`: skip Docker and Compose files.
- `--redis`: include Redis service and environment contract.
- `--caddy`: include Caddy production proxy overlay.
- `--no-github-actions`: skip GitHub Actions CI.
- `--no-agents`: skip generated `AGENTS.md`.
- `--no-git`: skip `git init`.
- `--yes`: confirm non-interactive writes.

## Recipes

Backend-only SQLite API:

```bash
python -m tools.project_generator \
  --name "Inventory API" \
  --destination /tmp/kilo/inventory-api \
  --backend fastapi \
  --frontend none \
  --database sqlite \
  --no-auth \
  --no-alembic \
  --no-docker \
  --no-github-actions \
  --no-git \
  --yes
```

Frontend-only React app:

```bash
python -m tools.project_generator \
  --name "Marketing Site" \
  --destination /tmp/kilo/marketing-site \
  --backend none \
  --frontend react-vite \
  --database none \
  --no-docker \
  --no-github-actions \
  --no-git \
  --yes
```

Full-stack app with PostgreSQL, Redis, Docker, Caddy, and CI:

```bash
python -m tools.project_generator \
  --name "Operations Console" \
  --destination /tmp/kilo/operations-console \
  --backend fastapi \
  --frontend react-vite \
  --database postgresql \
  --redis \
  --caddy \
  --yes
```

## Generated Project Workflow

After generation, follow the printed next steps. Typical setup:

```bash
cp .env.example .env
make test
make lint
make up
```

For backend work:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

For frontend work:

```bash
cd frontend
npm install
npm run dev
```

After the first frontend `npm install`, commit the generated `package-lock.json` if the generated project will use CI or Docker. Generated Docker and CI commands are lockfile-tolerant: they run `npm ci` when `package-lock.json` exists and fall back to `npm install` otherwise.

## Validation And Safety

- The destination directory must be absent or empty. Existing non-empty directories are never overwritten.
- Real secrets are never read from `.env`; generated projects receive safe placeholders in `.env.example`.
- Generated `.env` files are intentionally not created. Copy `.env.example` yourself and fill local values.
- Static sanity checks do not require Docker, network access, Node dependencies, or installed generated backend dependencies.
- Persistent databases use Alembic by default. SQLite without Alembic uses an explicit startup-time `init_db()` path instead of import-time schema creation.
- Collection endpoints return `200 []` when empty.

## Troubleshooting

If `pip install -e '.[dev]'` fails with `Multiple top-level packages discovered in a flat-layout: ['app', 'alembic']`, regenerate with the current tool or add this section to the generated `backend/pyproject.toml`:

```toml
[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["alembic*", "tests*"]
```

If auth-enabled backend imports fail around `EmailStr` or email validation, make sure the generated backend dependencies include `pydantic[email]` and reinstall the backend environment.

If frontend Docker or CI fails before a lockfile exists, run `npm install` in `frontend/` once, or keep the generated lockfile-tolerant install command that falls back from `npm ci` to `npm install`.

## Development

Run the generator test suite from the repository root:

```bash
python -m pytest tools/project_generator/tests
```

Run Python syntax compilation:

```bash
python -m compileall tools/project_generator
```

Render a sample into `/tmp/kilo`:

```bash
python -m tools.project_generator \
  --config tools/project_generator/config.yaml \
  --destination /tmp/kilo/project-generator-readme-sample \
  --no-git \
  --yes
```

When adding new generator options, update the config model, validation rules, manifest selection, templates, README, example config, and tests together.

# WebAPI Backend

## Overview

The backend is a FastAPI app with users, auth, prompts, SQLModel persistence, MariaDB support, and a SQLite fallback. The ASGI app object is `myapp` in [`main.py`](main.py), and API routes are mounted under `/api/v1`.

## Requirements

- Python 3.12.
- MariaDB client/build system packages when installing the backend dependencies locally.
- Redis for password recovery endpoints.
- Python dependencies from the root [`requirements.txt`](../requirements.txt).

## Local Development Without Docker

Use this flow when developing the FastAPI backend directly on your machine.

Create and activate a virtual environment from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run the backend from `webapi/`:

```bash
cd webapi
uvicorn main:myapp --reload --host 127.0.0.1 --port 8000
```

By default, the app uses SQLite because `DB_URL` is unset. This creates `webapi/crud_data.db`, which is convenient for local development.

Password recovery endpoints require Redis. Start a local Redis container when working with `/api/v1/auth/generate` or `/api/v1/auth/recover`:

```bash
docker run -d --name webapi-redis -p 6379:6379 redis:7-alpine
```

Verify Redis is reachable:

```bash
docker exec webapi-redis redis-cli ping
```

Expected output:

```text
PONG
```

The backend defaults to `REDIS_HOST=127.0.0.1` and `REDIS_PORT=6379`, so no Redis environment variables are needed for this default container.

If host port `6379` is unavailable, publish Redis on another local port and export the matching backend setting before starting Uvicorn:

```bash
docker run -d --name webapi-redis -p 6380:6379 redis:7-alpine
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6380
```

Remove the local Redis container when done:

```bash
docker rm -f webapi-redis
```

To use a local MariaDB server instead, create the database and user first, then export `DB_URL` before starting Uvicorn:

```bash
export DB_URL="mariadb+mariadbconnector://webapi_user:replace_with_local_database_password@127.0.0.1:3306/crud_data"
uvicorn main:myapp --reload --host 127.0.0.1 --port 8000
```

The local backend is available at `http://127.0.0.1:8000`, with API routes under `http://127.0.0.1:8000/api/v1`. Most auth, users, and prompts development can run without Redis; only password recovery storage and retrieval require it.

## Run With Docker Compose

The recommended workflow is the full-stack Compose script from the repository root:

```bash
./scripts/run-compose-stack.sh
```

Compose starts MariaDB, Redis, the FastAPI backend, and the nginx frontend. Inside the Compose network, the backend connects to the database host `mariadb` and Redis host `redis`, and frontend nginx proxies API requests to the backend service name `backend`.

For local secret values, copy the root environment template and edit `.env` before starting Compose:

```bash
cp .env.example .env
```

Docker Compose reads the root `.env` file automatically for variable interpolation. The startup script also loads the same file into the shell environment before running Compose, and the backend loads it through `python-dotenv` when started directly with Python. Missing values produce warnings in the startup script, not hard failures, so basic local/test runs can continue with Compose fallbacks.

Backend URLs:

- Direct backend: `http://127.0.0.1:8000`
- API through frontend proxy: `http://127.0.0.1:8080/api/v1/...`
- MariaDB host port: `127.0.0.1:3306` by default
- Redis host port: `127.0.0.1:6379` by default

Manual Compose startup from the repository root:

```bash
docker compose up --build -d
docker compose ps
docker compose logs backend
```

Use `docker-compose` instead of `docker compose` if your environment only has the legacy command.

Override the published MariaDB or Redis host ports for local inspection when needed:

```bash
MARIADB_HOST_PORT=3307 docker compose up --build -d
REDIS_HOST_PORT=6380 docker compose up --build -d
MARIADB_HOST_PORT=3307 REDIS_HOST_PORT=6380 docker compose up --build -d
```

Stop or reset the Compose stack:

```bash
docker compose down
docker compose down -v
```

`docker compose down -v` removes the database volume too.

## Backend Docker Image

Build the backend image from the repository root because the root [`Dockerfile`](../Dockerfile) copies both [`requirements.txt`](../requirements.txt) and `webapi/`:

```bash
docker build -t webapi:dev .
```

Run a standalone SQLite smoke test:

```bash
docker run --rm -p 8000:8000 webapi:dev
```

The backend uses `DB_URL` for MariaDB. If `DB_URL` is unset, it falls back to SQLite at `sqlite:///./crud_data.db`.

## Manual MariaDB And Backend Docker Flow

Use this advanced reference flow only when you need to run backend and MariaDB outside Compose.

Build the backend image from the repository root:

```bash
docker build -t webapi:dev .
```

Create a Docker network for the backend and database:

```bash
docker network create webapi-net || true
```

Start MariaDB:

```bash
docker run -d --name webapi-mariadb --network webapi-net -p 3306:3306 -e MARIADB_ROOT_PASSWORD=replace_with_local_root_password -e MARIADB_DATABASE=crud_data -e MARIADB_USER=webapi_user -e MARIADB_PASSWORD=replace_with_local_database_password -v webapi-mariadb-data:/var/lib/mysql mariadb:11
```

Wait until MariaDB is ready:

```bash
docker exec webapi-mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb-admin ping -h 127.0.0.1 -u "$MARIADB_USER"'
```

Start the backend with `DB_URL` pointed at the MariaDB container hostname:

```bash
docker run --rm --name webapi-backend --network webapi-net -p 8000:8000 -e DB_URL="mariadb+mariadbconnector://webapi_user:replace_with_local_database_password@webapi-mariadb:3306/crud_data" webapi:dev
```

Inside this Docker network, the database host is `webapi-mariadb`, not `127.0.0.1`.

All-in-one manual startup after building the image:

```bash
docker network create webapi-net || true
docker run -d --name webapi-mariadb --network webapi-net -p 3306:3306 -e MARIADB_ROOT_PASSWORD=replace_with_local_root_password -e MARIADB_DATABASE=crud_data -e MARIADB_USER=webapi_user -e MARIADB_PASSWORD=replace_with_local_database_password -v webapi-mariadb-data:/var/lib/mysql mariadb:11
docker exec webapi-mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb-admin ping -h 127.0.0.1 -u "$MARIADB_USER"'
docker run --rm --name webapi-backend --network webapi-net -p 8000:8000 -e DB_URL="mariadb+mariadbconnector://webapi_user:replace_with_local_database_password@webapi-mariadb:3306/crud_data" webapi:dev
```

## API Verification

Use `http://127.0.0.1:8080/api/v1` when the full Compose stack is running and you want to verify frontend nginx proxying. Use `http://127.0.0.1:8000/api/v1` when checking the backend port directly.

Check the frontend proxy with an intentionally invalid login request:

```bash
curl -i -X POST http://127.0.0.1:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{}'
```

HTTP `422` confirms nginx forwarded the request to FastAPI and FastAPI returned validation errors.

Check the backend root endpoint directly:

```bash
curl http://127.0.0.1:8000/
```

Create a user through the frontend proxy. Change `username`, `phone`, or `email` before rerunning because those fields must be unique:

```bash
curl -X POST http://127.0.0.1:8080/api/v1/auth/signup -H "Content-Type: application/json" -d '{"username":"demo_user_001","name":"Demo","last_name":"User","phone":"5550000001","email":"demo001@example.com","hashed_password":"demo-password"}'
```

Login and store the token without requiring `jq`:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"demo_user_001","password":"demo-password"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

Create a prompt using the token. The `rate` field must be a string because the API schema defines it as text:

```bash
curl -X POST http://127.0.0.1:8080/api/v1/prompts -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"model_name":"gpt-demo","prompt_text":"Explain FastAPI in one sentence.","category":"demo","rate":"5"}'
```

Confirm prompts are readable through the API:

```bash
curl http://127.0.0.1:8080/api/v1/prompts -H "Authorization: Bearer $TOKEN"
```

For direct backend checks, replace `http://127.0.0.1:8080/api/v1` with `http://127.0.0.1:8000/api/v1` in the same API commands.

## Database Access

Open a MariaDB shell inside the Compose database service:

```bash
docker compose exec mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb "$MARIADB_DATABASE" -u "$MARIADB_USER"'
```

Use `docker-compose exec mariadb ...` if your environment only has the legacy Compose command.

The startup script also prints the matching Compose command for entering the database container:

```bash
docker compose exec mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb "$MARIADB_DATABASE" -u "$MARIADB_USER"'
```

If you are using the manual backend flow, use the named manual container instead:

```bash
docker exec -it webapi-mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb "$MARIADB_DATABASE" -u "$MARIADB_USER"'
```

Useful SQL checks:

```sql
SHOW TABLES;
SELECT id, username, email FROM `user`;
SELECT id, user_id, model_name, category, rate FROM prompts;
```

## Configuration

- `DB_URL` controls the MariaDB connection. If unset, the backend defaults to SQLite at `sqlite:///./crud_data.db`.
- Docker Compose passes `DB_URL` to the backend. Keep `DB_URL` aligned with `MARIADB_USER`, `MARIADB_PASSWORD`, and `MARIADB_DATABASE` when changing local database credentials.
- JWT and mail settings are read in [`core/config.py`](core/config.py).
- `ENV_MAIL_USERNAME`, `ENV_MAIL_PASSWORD`, `ENV_MAIL_FROM`, and `ENV_SECRET_KEY` should come from local `.env`, shell exports, CI secrets, or production secret management. Do not commit real values.
- Redis is configured through `REDIS_HOST`, `REDIS_PORT`, and optional `REDIS_PSW` in [`core/config.py`](core/config.py). Local defaults are `127.0.0.1:6379`; Compose sets `REDIS_HOST=redis` for backend containers.
- The backend Docker image includes a deterministic `fastapi_mail/config.py` dependency patch after installing pinned requirements.

Scalable configuration approach:

- Maintain `.env.example` as the single source of truth for supported keys and comments.
- Use `.env` for direct local Python runs and local Compose runs.
- Use CI/CD secrets and deployment-platform secrets for real environments instead of distributing `.env` files.
- Prefer adding new configuration keys to `.env.example`, `docker-compose.yml`, and `webapi/core/config.py` together so all runtimes stay consistent.

## Troubleshooting

If Compose startup fails with `Bind for :::3306 failed: port is already allocated`, another container or local database is already using MariaDB's host port. The startup script automatically chooses a fallback MariaDB port when the conflict is another Docker container. For manual Compose startup, set `MARIADB_HOST_PORT=3307` or another free port.

Check running Docker containers:

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

If old manual backend workflow containers are running, remove them before starting Compose:

```bash
docker rm -f webapi-mariadb webapi-redis webapi-backend
```

If a previous Compose stack is running, stop it from the repository root:

```bash
docker compose down
```

Use `docker-compose down` if your environment only has the legacy Compose command.

If port `8000` or `8080` is already allocated, stop the service using that port or edit `docker-compose.yml` to publish a different host port.

If Compose startup fails because Redis host port `6379` is already allocated, use another host port:

```bash
REDIS_HOST_PORT=6380 docker compose up --build -d
```

Check Redis readiness in Compose:

```bash
docker compose exec redis redis-cli ping
```

If an old manual Redis container is running, remove it before starting Compose:

```bash
docker rm -f webapi-redis
```

If the backend logs show SQLite during the manual backend flow, confirm the backend `docker run` command includes a `DB_URL` value such as `mariadb+mariadbconnector://webapi_user:replace_with_local_database_password@webapi-mariadb:3306/crud_data`.

If the backend fails during manual startup, MariaDB may not be ready yet. Run the readiness check again, then restart the backend container.

To reset manual database data too, remove the named volume:

```bash
docker volume rm webapi-mariadb-data
```

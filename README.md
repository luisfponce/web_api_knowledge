# web_api_knowledge
This is a simple app is aimed to solidify and escalate web api knowledge.

## Full Stack With Docker Compose

The recommended local workflow is Docker Compose. It runs MariaDB, the FastAPI backend, and a production nginx frontend container from one command.

### One-Command Startup

Run this from the repository root:

```bash
./scripts/run-compose-stack.sh
```

The script:

- Detects `docker compose` and falls back to `docker-compose` if the plugin is unavailable
- Runs `up --build -d` from the repository root
- Waits for healthy `mariadb` and `backend` services
- Checks the frontend at `http://127.0.0.1:8080/`
- Checks the backend direct endpoint at `http://127.0.0.1:8000/`
- Checks nginx API proxying through `http://127.0.0.1:8080/api/v1/auth/login`
- Checks MariaDB connectivity with `mariadb-admin ping`
- Publishes MariaDB on host port `3306` by default, or automatically uses the next available Docker port from `3307` to `3319` when `3306` is already used by another Docker container

Use existing images without rebuilding:

```bash
./scripts/run-compose-stack.sh --no-build
```

Increase the readiness timeout when running the first database initialization on a slow machine:

```bash
./scripts/run-compose-stack.sh --timeout 180
```

### Manual Compose Startup

If you prefer to run Compose manually, use:

```bash
docker compose up --build -d
```

If your Docker CLI does not have the Compose plugin, use the legacy command:

```bash
docker-compose up --build -d
```

The frontend serves the built React app and proxies same-origin `/api/*` requests to the backend service.

URLs:

- Frontend: `http://127.0.0.1:8080`
- Backend through frontend proxy: `http://127.0.0.1:8080/api/v1/...`
- Backend direct developer port: `http://127.0.0.1:8000`
- MariaDB direct developer port: `127.0.0.1:3306` by default

Override the published MariaDB host port for local inspection when needed:

```bash
MARIADB_HOST_PORT=3307 docker compose up --build -d
```

Legacy fallback:

```bash
MARIADB_HOST_PORT=3307 docker-compose up --build -d
```

Stop the stack:

```bash
docker compose down
```

Reset the database volume too:

```bash
docker compose down -v
```

Check service health and logs:

```bash
docker compose ps
docker compose logs backend
docker compose logs frontend
docker compose logs mariadb
```

Legacy fallback:

```bash
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mariadb
```

The backend receives `DB_URL=mariadb+mariadbconnector://webapi_user:webapi_password@mariadb:3306/crud_data` from Compose. Inside containers, service names such as `mariadb` and `backend` are used instead of `127.0.0.1`.

## Verify The Docker Compose Stack

After running `./scripts/run-compose-stack.sh` or manual Compose startup, use these commands for additional checks.

Check the frontend and proxied API:

```bash
curl http://127.0.0.1:8080/
curl -i -X POST http://127.0.0.1:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{}'
```

The invalid login request should return HTTP `422`, which confirms nginx forwarded the API request to FastAPI.

Check the backend direct developer port:

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

Confirm the prompt is readable through the API:

```bash
curl http://127.0.0.1:8080/api/v1/prompts -H "Authorization: Bearer $TOKEN"
```

Open a MariaDB shell inside the database container:

```bash
docker compose exec mariadb mariadb -u webapi_user -pwebapi_password crud_data
```

Run these SQL commands:

```sql
SHOW TABLES;
SELECT id, username, email FROM `user`;
SELECT id, user_id, model_name, category, rate FROM prompts;
```

## Manual Backend With MariaDB

Run these commands from the repository root.

Build the backend image:

```bash
docker build -t webapi:dev .
```

Create a Docker network for the backend and database:

```bash
docker network create webapi-net || true
```

Start MariaDB in one copy-paste command:

```bash
docker run -d --name webapi-mariadb --network webapi-net -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root_password -e MARIADB_DATABASE=crud_data -e MARIADB_USER=webapi_user -e MARIADB_PASSWORD=webapi_password -v webapi-mariadb-data:/var/lib/mysql mariadb:11
```

This starts a MariaDB container named `webapi-mariadb`, creates database `crud_data`, creates user `webapi_user` with password `webapi_password`, stores data in the `webapi-mariadb-data` volume, and exposes MariaDB on host port `3306` for local inspection.

Wait until MariaDB is ready before starting the backend:

```bash
docker exec webapi-mariadb mariadb-admin ping -h 127.0.0.1 -u webapi_user -pwebapi_password
```

Start the backend with `DB_URL` pointed at the MariaDB container hostname:

```bash
docker run --rm --name webapi-backend --network webapi-net -p 8000:8000 -e DB_URL="mariadb+mariadbconnector://webapi_user:webapi_password@webapi-mariadb:3306/crud_data" webapi:dev
```

Inside the Docker network, the database host is `webapi-mariadb`, not `127.0.0.1`.

### All-In-One Startup

After building the image, this block starts the network, MariaDB, checks readiness, and runs the backend:

```bash
docker network create webapi-net || true
docker run -d --name webapi-mariadb --network webapi-net -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root_password -e MARIADB_DATABASE=crud_data -e MARIADB_USER=webapi_user -e MARIADB_PASSWORD=webapi_password -v webapi-mariadb-data:/var/lib/mysql mariadb:11
docker exec webapi-mariadb mariadb-admin ping -h 127.0.0.1 -u webapi_user -pwebapi_password
docker run --rm --name webapi-backend --network webapi-net -p 8000:8000 -e DB_URL="mariadb+mariadbconnector://webapi_user:webapi_password@webapi-mariadb:3306/crud_data" webapi:dev
```

## Verify The Manual API

Keep the backend container running in one terminal, then run these commands from another terminal.

Check the root endpoint:

```bash
curl http://127.0.0.1:8000/
```

Create a user. Change `username`, `phone`, or `email` before rerunning because those fields must be unique:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/signup -H "Content-Type: application/json" -d '{"username":"demo_user_001","name":"Demo","last_name":"User","phone":"5550000001","email":"demo001@example.com","hashed_password":"demo-password"}'
```

Login and store the token without requiring `jq`:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"demo_user_001","password":"demo-password"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

Create a prompt using the token. The `rate` field must be a string because the API schema defines it as text:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/prompts -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"model_name":"gpt-demo","prompt_text":"Explain FastAPI in one sentence.","category":"demo","rate":"5"}'
```

Confirm the prompt is readable through the API:

```bash
curl http://127.0.0.1:8000/api/v1/prompts -H "Authorization: Bearer $TOKEN"
```

## Verify Manual MariaDB Data

Open a MariaDB shell inside the database container:

```bash
docker exec -it webapi-mariadb mariadb -u webapi_user -pwebapi_password crud_data
```

Run these SQL commands:

```sql
SHOW TABLES;
SELECT id, username, email FROM `user`;
SELECT id, user_id, model_name, category, rate FROM prompts;
```

## Standalone SQLite Smoke Test

This quick command runs the backend without `DB_URL`, so the app falls back to SQLite inside the container:

```bash
docker build -t webapi:dev . && docker run --rm -p 8000:8000 webapi:dev
```

## Troubleshooting

If Compose startup fails with `Bind for :::3306 failed: port is already allocated`, another container or local database is already using MariaDB's host port. The startup script automatically chooses a fallback MariaDB port when the conflict is another Docker container. For manual Compose startup, set `MARIADB_HOST_PORT=3307` or another free port.

Check running Docker containers:

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

If the old manual backend workflow containers are running, remove them before starting Compose:

```bash
docker rm -f webapi-mariadb webapi-backend
```

If a previous Compose stack is running, stop it from the repository root:

```bash
docker compose down
```

Use `docker-compose down` if your environment only has the legacy Compose command.

If port `8000` or `8080` is already allocated, stop the service using that port or edit `docker-compose.yml` to publish a different host port.

If the backend logs show SQLite, confirm the backend `docker run` command includes `-e DB_URL="mariadb+mariadbconnector://webapi_user:webapi_password@webapi-mariadb:3306/crud_data"`.

If the backend fails during startup, MariaDB may not be ready yet. Run the readiness check again, then restart the backend container.

If container names already exist, remove the old containers:

```bash
docker rm -f webapi-mariadb webapi-backend
```

To reset database data too, remove the named volume:

```bash
docker volume rm webapi-mariadb-data
```

## Database diagram documentation

The ORM model and relational mapping documentation for dbdiagram.io is available at [`plans/dbdiagram.md`](plans/dbdiagram.md).

## Frontend v1

A minimal frontend scaffold is available in [`frontend/`](frontend/).

Run it locally:

```bash
cd frontend
npm install
npm run dev
```

Detailed frontend docs are in [`frontend/README.md`](frontend/README.md).

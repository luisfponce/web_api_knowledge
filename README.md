# web_api_knowledge
This is a simple app is aimed to solidify and escalate web api knowledge.

## Backend With MariaDB

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

## Verify The API

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

## Verify MariaDB Data

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

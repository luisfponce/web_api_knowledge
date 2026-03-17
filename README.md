# web_api_knowledge
This is a simple app is aimed to solidify and escalate web api knowledge

Build and run the app:
```bash
docker build -t webapi:dev .; docker run --rm -p 8000:8000 webapi:dev
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

# Backend Tests

## Overview

Backend tests use pytest and FastAPI `TestClient`. [`conftest.py`](conftest.py) overrides database and Redis dependencies with in-memory SQLite and fake Redis for most route tests, so route tests do not require a real Redis server.

## Run From The Backend Directory

Run backend test commands from `webapi/`:

```bash
cd webapi
```

## Main Test Commands

Run the CI wrapper, which executes `tests/nonfunctional`:

```bash
pytest tests/test_ci.py -v
```

Run the CD/release wrapper, which executes `tests/functional`:

```bash
rm -f crud_data.db
pytest tests/test_release.py -v
```

Run the functional suite directly:

```bash
pytest tests/functional -v
```

Run the nonfunctional suite directly:

```bash
pytest tests/nonfunctional -v
```

Run one targeted test:

```bash
pytest tests/functional/test_prompts_routes.py::test_create_prompt_user_not_found_returns_404 -v
```

## Local SQLite Data

Some wrapper tests can create `webapi/crud_data.db` through the app's default SQLite fallback. Remove it before release-suite runs to match GitHub Actions' clean workspace behavior:

```bash
rm -f crud_data.db
```

## GitHub Actions Mapping

- CI runs `pytest tests/test_ci.py -v` from `webapi/`.
- CD runs `pytest tests/test_release.py -v` from `webapi/` after removing `crud_data.db`.

## Tips

- Keep route tests isolated through fixtures and dependency overrides.
- Use targeted tests before full suites when debugging route behavior.
- Fix dependency or import failures before investigating route assertions.

# web_api_knowledge
This is a simple app is aimed to solidify and escalate web api knowledge

Build and run the app:
```bash
docker build -t webapi:dev .; docker run --rm -p 8000:8000 webapi:dev
```

## Development tooling and quality gates

This project now includes recruiter-relevant backend tooling practices:

- **Formatter:** Black (configured in [`pyproject.toml`](pyproject.toml))
- **Linter:** Pylint (configured in [`.pylintrc`](.pylintrc))
- **Git hooks:** pre-commit (configured in [`.pre-commit-config.yaml`](.pre-commit-config.yaml))
- **Validation:** Pydantic constraints in schemas under [`webapi/schemas`](webapi/schemas)
- **CI quality gates:** formatting and lint checks in [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml) and [`.github/workflows/cd.yml`](.github/workflows/cd.yml)

### Local setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Install git hooks:

```bash
pre-commit install
```

### Run tooling locally

Run Black formatting:

```bash
black webapi
```

Run Pylint checks:

```bash
pylint webapi/schemas
```

Run pre-commit on all files:

```bash
pre-commit run --all-files
```

Run validation-focused tests:

```bash
pytest webapi/tests/functional/test_auth_routes.py -k validation
```

## Database diagram documentation

The ORM model and relational mapping documentation for dbdiagram.io is available at [`plans/dbdiagram.md`](plans/dbdiagram.md).

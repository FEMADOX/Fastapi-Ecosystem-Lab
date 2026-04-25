# AGENTS.md - AI Development Guidelines

## Overview

This is a monorepo workspace containing three main projects:
- **learn_fastapi/** — Backend API built with FastAPI, SQLAlchemy, PostgreSQL, and async patterns
- **learn_streamlit/** — Data dashboards and prototyping frontend with Streamlit
- **learn_nextjs/** — Production-grade Next.js web frontend with TypeScript and Tailwind CSS

AI agents should focus on the **learn_fastapi** project for backend development unless otherwise specified.

## Package Management

- Run `uv add <package_name>` to add a dependency to the workspace.
- Run `uv sync` to install all dependencies including dev tools.
- Update `pyproject.toml` directly when managing complex dependency groups (see `dev` and `streamlit-deps` groups).

## Code Quality & Formatting

After moving files or changing imports, always validate the codebase:

- **Linting**: `ruff check learn_fastapi` to check for style violations.
- **Auto-fix**: `ruff check --fix learn_fastapi` to automatically fix linting issues.
- **Formatting**: `ruff format --check learn_fastapi` to check formatting; `ruff format --fix learn_fastapi` to auto-fix.
- **Type checking**: `ty check learn_fastapi` to validate type hints (note: some rules are commented out in CI).
- **Code comments**: When replacing code, always add a comment explaining *why* you made the change. This helps reviewers understand intent and aids maintenance.

## FastAPI Backend Architecture

### Module Structure

Each module in `learn_fastapi/src/` (auth, users, items) follows a consistent structure:

```
module/
├── annotations.py      # Annotated type aliases for the module
├── config.py           # Module-specific settings (if needed)
├── dependencies.py     # FastAPI dependency injection
├── exceptions.py       # Custom exceptions for the module
├── models.py           # SQLAlchemy ORM models
├── repository.py       # Data access layer (queries, transactions)
├── router.py           # API endpoints
├── schema.py           # Pydantic request/response models
├── service.py          # Business logic layer
└── utils.py            # Helper functions (non-business logic)
```

**Key patterns:**
- Keep business logic in `service.py`, database access in `repository.py`, and validation in `schema.py`.
- Use `dependencies.py` to wire services and manage dependency injection.
- Exceptions are module-specific (e.g., `ItemNotFound`, `DuplicateEmail`).

### Database & Async Patterns

- **Session management**: Use `AsyncSessionDep` (defined in `database.py`) for automatic session handling. The `get_session()` dependency provides rollback on `DBAPIError`.
- **Models**: All SQLAlchemy models inherit from `Base` (in `database.py`); model imports are explicitly listed in `alembic/env.py` for migration auto-detection.
- **Transactions**: Session is automatically committed on successful route completion; rollback happens on exceptions.
- **SQLite vs PostgreSQL**: The app auto-detects SQLite and enables `check_same_thread=False` and batch mode in migrations.

### Alembic Migrations

- **Generate migrations**: Run `alembic revision --autogenerate -m "description"` from `learn_fastapi/` folder.
- **Apply migrations**: Automatically checked and applied at app startup via `lifespan()` in `config.py`.
- **Model detection**: All models must be imported in `alembic/env.py` for autogenerate to detect schema changes.
- **Downgrade**: Use `alembic downgrade -1` to rollback the last migration (rarely needed).

### API Versioning

- The app uses **fastapi-versionizer** to automatically version endpoints under `/v1`, `/v2`, etc.
- Current active version routes are available at `/latest/`.
- New endpoints default to the current major version; use `@api_version(N)` decorator to target specific versions.

### Environment Configuration

Create a `.env` file in the project root (see `.env.example`):
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db
DEBUG=True
ALLOWED_HOSTS=["localhost", "127.0.0.1", "localhost:3000"]
# ... additional vars as needed
```

For **local PostgreSQL** development, use Docker Compose (see below) or configure your own PostgreSQL instance.

### Running the FastAPI App

- **Development with hot reload**: `uv run python -m learn_fastapi.src.main`
  - The app auto-detects `.env` file in the project root.
  - File watcher monitors changes and triggers Swagger UI refresh.
  - Migrations are checked on startup.
- **Production**: Set `DEBUG=False`, use a production-grade ASGI server (Gunicorn + Uvicorn), and configure PostgreSQL.

### Docker & Local Services

- **docker-compose.yaml** defines local PostgreSQL and the FastAPI app.
- **To start locally**: `docker-compose up -d`
- **To stop**: `docker-compose down`
- **Dockerfile** is used for production deployment (e.g., Koyeb).

## Testing Instructions

- **Run all tests**: `pytest` from the `learn_fastapi/` folder (or `uv run pytest --config-file=pyproject.toml` from project root).
- **Run a specific test file**: `pytest tests/v1/test_auth.py`
- **Run a specific test function**: `pytest tests/v1/test_auth.py::TestAuthRouter::test_login`
- **Run tests matching a pattern**: `pytest -k "test_login"`.
- **Run tests with a marker**: `pytest -m "integration"`.
- **Run tests in parallel**: `pytest -n auto` (uses all available CPUs; requires `pytest-xdist[psutil]`).
- **Test database**: Uses in-memory SQLite (`sqlite+aiosqlite:///:memory:`) for fast, isolated tests.
- **AsyncClient**: The test suite provides `PrefixedAsyncClient` that auto-prefixes routes with `/v1` (test API version).
- **Async tests**: All tests are async; use `pytest-asyncio` for proper event loop handling.
- **CI Pipeline**: The workflow (`.github/workflows/fastapi.yaml`) runs Python 3.14, pytest, ruff checks on every push/PR.
- Fix any test or type errors until the whole suite is green.
- Add or update tests for the code you change, even if nobody asked.

## PR Instructions

- **Title format**: `[learn_fastapi] <description>` or `[learn_nextjs] <description>` depending on the project.
- **Before committing**: Run linting, formatting, and tests: `uv run ruff check learn_fastapi && uv run ruff format --check learn_fastapi && uv run pytest`.
- **Test coverage**: Add or update tests for any code changes, even if not explicitly requested.
- **The commit should pass all tests before you merge.**

## Commit Message Guidelines

Follow the **Conventional Commits** specification (see `.github/copilot-instructions.md` for details).

**Format**: `<type>(<scope>): <description>`

**Examples**:
- `feat(auth): add JWT token refresh endpoint`
- `fix(items): prevent duplicate item names for the same user`
- `test(auth): add test for token expiration`

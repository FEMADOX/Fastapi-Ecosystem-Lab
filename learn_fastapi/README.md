# learn_fastapi

A personal learning module for exploring FastAPI concepts, patterns, and best practices.

## Structure

```text
learn_fastapi/
├── alembic/
|   ├── versions/        # Auto-generated migration scripts
|   ├── env.py           # Alembic configuration and setup
|   ├── README.md        # Alembic usage instructions
|   └── script.py.mako   # Template for generating migration scripts
├── docs/
|   ├── fastapi-best-practices.md
|   ├── awesome-fastapi.md
|   └── fastapi-new.md
├── src/
│   ├── auth/           # Authentication module
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── config.py       # Auth-specific settings (JWT, cookies)
│   │   ├── dependencies.py # Auth dependencies (get_current_user)
│   │   ├── exceptions.py   # Auth-specific exceptions
│   │   ├── models.py       # SQLAlchemy models (User, RefreshToken)
│   │   ├── router.py       # Auth endpoints (login, register, etc.)
│   │   ├── schema.py       # Auth Pydantic models
│   │   └── utils.py        # Utility functions (hashing, token creation, etc.)
│   ├── items/          # Items module (example domain)
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schema.py       # Item Pydantic model
│   │   ├── router.py       # CRUD endpoints for /items
│   │   └── validators.py   # Custom validation logic (Not used in this example, but good for complex business rules)
|   ├── media/images/   # Media storage (e.g. uploaded images)
|   ├── static/js/      # Static files (e.g. CSS, JS)
│   ├── utils/          # Shared utilities
│   │   ├── alembic.py      # Alembic integration helpers
│   │   ├── annotations.py  # Shared type annotations
│   │   └── hot_reload.py   # Development hot-reload WebSocket
│   ├── config.py       # Global configuration and lifespan
│   ├── constants.py    # Project paths and constants
│   ├── database.py     # SQLAlchemy engine and session setup
│   ├── main.py         # uvicorn runner (__main__)
│   └── middleware.py   # Custom middleware (e.g. Swagger hot reload, CORS, etc.)
├── tests/
|   |-- auth/
|   |   ├── conftest.py     # Auth fixtures
|   |   └── test_router.py  # Authentication tests
│   ├── items/
│   |   ├── conftest.py     # TestClient fixture
│   |   └── test_router.py  # Full CRUD test suite
|   ├── conftest.py     # Global test fixtures (e.g. TestClient)
|   └── test_main.py    # Basic smoke test for app startup
├── .env.example
├── alembic.ini
├── docker-compose.yaml
└── README.md
```

## Topics Covered

### `items` App

| Concept                                  | Where                                                                  |
|------------------------------------------|------------------------------------------------------------------------|
| `APIRouter` with prefix & tags           | [`router.py`](src/items/router.py)                                     |
| Pydantic model with `Field` validation   | [`schema.py`](src/items/schema.py)                                     |
| `Annotated` aliases                      | [`annotations.py`](src/items/annotations.py)                           |
| Cross-field business rule validation     | [`validators.py`](src/items/validators.py)                             |
| JSON file as persistent in-memory store  | [`database.py`](src/database.py)                                       |
| Full CRUD: GET / POST / PUT / DELETE     | [`router.py`](src/items/router.py)                                     |
| HTTP status codes via `starlette.status` | [`router.py`](src/items/router.py)                                     |
| `HTTPException` for 404 responses        | [`router.py`](src/items/router.py)                                     |
| Integration tests with `TestClient`      | [`tests/first_steps/test_router.py`](tests/items/test_router.py)       |

#### `items` Endpoints

Base prefix: `/items`

| Method   | Path                | Description                            |                           Body Params                           |
|:---------|:--------------------|:---------------------------------------|:---------------------------------------------------------------:|
| `GET`    | `/hello-world/`     | Health-check / hello world             |                                                                 |
| `GET`    | `/`                 | List all items                         |                                                                 |
| `GET`    | `/{id_param}`       | Get item by `UUID`                     |                                                                 |
| `POST`   | `/`                 | Create a new item                      |                             `Item`                              |
| `PUT`    | `/{id_param}`       | Replace fields of an existing item     |                          `ItemUpdate`                           |
| `PATCH`  | `/{id_param}`       | Partially update an existing item      |                          `ItemUpdate`                           |
| `DELETE` | `/{id_param}`       | Delete an item                         |                                                                 |
| `POST`   | `/image/{id_param}` | Upload/update image for an item        |             `image_file` (`UploadFile`), `caption`              |
| `GET`    | `/image/`           | Get image file by filename             |                                                                 |
| `POST`   | `/with-image/`      | Create item with optional image upload | `name`, `description`, `price`, `tax`, `image_file?`, `caption` |

### `auth` App

| Concept                                  | Where                                                                  |
|------------------------------------------|------------------------------------------------------------------------|
| JWT authentication with refresh tokens   | [`router.py`](src/auth/router.py), [`utils.py`](src/auth/utils.py)     |
| Password hashing with Argon2             | [`utils.py`](src/auth/utils.py)                                        |
| OAuth2 Password Flow with Bearer tokens  | [`dependencies.py`](src/auth/dependencies.py)                          |
| CSRF token protection                    | [`router.py`](src/auth/router.py)                                      |
| Refresh token rotation                   | [`router.py`](src/auth/router.py), [`models.py`](src/auth/models.py)   |
| Secure cookie handling                   | [`utils.py`](src/auth/utils.py), [`config.py`](src/auth/config.py)     |
| Custom exceptions for auth errors        | [`exceptions.py`](src/auth/exceptions.py)                              |
| User model with SQLAlchemy ORM           | [`models.py`](src/auth/models.py)                                      |
| Dependency injection for current user    | [`dependencies.py`](src/auth/dependencies.py)                          |

#### `auth` Endpoints

Base prefix: `/auth`

| Method | Path        | Description                          | Body Params                                            | Headers/Cookies                                           |
|:-------|:------------|:-------------------------------------|:-------------------------------------------------------|:----------------------------------------------------------|
| `POST` | `/register` | Register a new user account          | `UserCreate` (email, password)                         | —                                                         |
| `POST` | `/token`    | Login and receive JWT access token   | `OAuth2PasswordRequestForm` (username/email, password) | —                                                         |
| `POST` | `/refresh`  | Refresh access token                 | —                                                      | `X-CSRF-Token`, `refresh_token` + `csrf_token` (cookies)  |
| `POST` | `/logout`   | Logout and revoke refresh token      | —                                                      | `X-CSRF-Token`, `refresh_token` + `csrf_token` (cookies)  |
| `GET`  | `/me`       | Get current user profile             | —                                                      | `Authorization: Bearer <token>`                           |

**Authentication Flow:**

1. **Register** → Create account with email/password
2. **Login** → Get `access_token` (JWT), `refresh_token` (cookie), `csrf_token` (cookie + response body)
3. **Use APIs** → Include `Authorization: Bearer <access_token>` header
4. **Refresh** → Exchange expired access token for new one using refresh token
5. **Logout** → Revoke refresh token and clear cookies

## Running

```bash
uv run learn_fastapi/src/main.py
```

## Local PostgreSQL with Docker Compose

This project includes `docker-compose.yaml` to run PostgreSQL locally.

From `learn_fastapi/`:

```bash
docker compose up -d
```

Stop and remove the container:

```bash
docker compose down
```

The configured database settings are:

- Host: `localhost`
- Port: `5432`
- Database: `learn_fastapi`
- User: `postgres`
- Password: `postgres`

Connection URL example:

```text
postgresql://postgres:postgres@localhost:5432/learn_fastapi
```

## Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema version control and migrations.

### How It Works

- Models are defined in `src/auth/models.py` and `src/items/models.py`
- Migrations are generated automatically from model changes
- Migrations are applied when the FastAPI app starts (via `lifespan`)
- Each migration is tracked with a revision ID in `alembic/versions/`

### Common Migration Commands

#### Generate a new migration after updating models

```bash
uv run alembic revision --autogenerate -m "description of changes"
```

Example:

```bash
uv run alembic revision --autogenerate -m "add status field to items"
```

#### Apply all pending migrations

```bash
uv run alembic upgrade head
```

#### Check the current migration version

```bash
uv run alembic current
```

#### View all migration revisions

```bash
uv run alembic heads
```

#### Downgrade to the previous migration

```bash
uv run alembic downgrade -1
```

#### Downgrade all the way to the start

```bash
uv run alembic downgrade base
```

### How Migrations Run at Startup

When the FastAPI app starts:

1. The `lifespan` function in `src/config.py` is called
2. It checks for pending migrations using `check_pending_migrations()` from `src/utils/alembic.py`
3. If migrations are pending, a warning is logged (manual migration required)
4. The app then starts normally

**Note:** Migrations are **checked** at startup, but not automatically applied. You must run `alembic upgrade head` manually to apply pending migrations.

### Best Practices

- **Always review generated migrations** before committing them
- **Never manually edit migration files** after they've been applied to production
- **Test migrations locally** before deploying to production
- **Keep models and migrations in sync** — always regenerate migrations after model changes
- **Use descriptive revision messages** to document what changed
- **Import all models in `alembic/env.py`** — ensures Alembic can detect all table changes
- **Commit migrations to version control** — essential for team collaboration and production deployments

### Alembic Configuration Details

The project includes several Alembic enhancements in `alembic/env.py`:

- **Explicit model imports** — All SQLAlchemy models are imported directly to ensure Alembic detects schema changes
- **Logger preservation** — `disable_existing_loggers=False` keeps uvicorn and app loggers active during migrations
- **SQLite compatibility** — Automatic configuration for SQLite-specific features:
  - `render_as_batch=True` — enables batch mode for better ALTER TABLE support
  - `check_same_thread=False` — allows SQLite access from multiple threads
- **Server default comparison** — Detects changes in column default values

### Environment Configuration

Alembic and the application use environment variables defined in `.env` (see `.env.example` for reference).

**Required environment variables:**

```bash
# Auth
SECRET_KEY=your-secret-key-here
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=fastapi_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security
COOKIE_SECURE=false        # true in production (HTTPS only)
COOKIE_SAMESITE=lax        # strict/lax/none
COOKIE_DOMAIN=             # empty for localhost, set domain in production
```

**For SQLite (development):**

```bash
DATABASE_URL=sqlite+aiosqlite:///./learn_fastapi/test.db
```

**Note:** Alembic automatically reads `DATABASE_URL` from the environment. The `alembic.ini` file is only used as a fallback.

## Testing

```bash
pytest
```

Tests use an **in-memory SQLite database** (`sqlite+aiosqlite:///:memory:`) which:

- Is fast and isolated per test
- Doesn't require PostgreSQL to be running
- Automatically creates/drops all tables from models
- Doesn't use Alembic (migrations are only for production PostgreSQL)

## Docs

### Reference Materials

- [`docs/fastapi-best-practices.md`](docs/fastapi-best-practices.md) — Opinionated best practices: project structure, async routes, Pydantic, dependency injection.
- [`docs/awesome-fastapi.md`](docs/awesome-fastapi.md) — Curated list of FastAPI third-party extensions, resources, and open source projects.
- [`docs/fastapi-new.md`](docs/fastapi-new.md) — Additional FastAPI patterns and modern approaches.

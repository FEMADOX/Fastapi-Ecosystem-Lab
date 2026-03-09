# learn_fastapi

A personal learning module for exploring FastAPI concepts, patterns, and best practices.

## Structure

```text
learn_fastapi/
├── docs/
|   ├── fastapi-best-practices.md
|   ├── awesome-fastapi.md
|   └── fastapi-new.md
├── src/
│   ├── items/          # Items module (example domain)
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schema.py       # Item Pydantic model
│   │   ├── router.py       # CRUD endpoints for /items
│   │   └── validators.py   # Custom validation logic (Not used in this example, but good for complex business rules)
│   ├── auth/           # Authentication module
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── router.py       # Auth endpoints (login, register, etc.)
│   │   ├── schema.py       # Auth Pydantic models
│   │   └── utils.py        # Utility functions (hashing, token creation, etc.)
│   ├── config.py       # Global configuration (e.g. DB path)
│   ├── constants.py    # In-memory DB constant
│   ├── database.py     # JSON persistence helpers
│   |-- main.py         # uvicorn runner (__main__)
│   └── middleware.py   # Custom middleware (e.g. logging, CORS, etc.)
├── tests/
|   |-- conftest.py     # Global test fixtures (e.g. TestClient)
|   |-- test_main.py    # Basic smoke test for app startup
|   |-- auth/
|   |   ├── conftest.py     # Auth fixtures
|   |   └── test_auth.py    # Authentication tests
│   └── items/
│       ├── conftest.py     # TestClient fixture
│       └── test_router.py  # Full CRUD test suite
|-- .env.example
|-- docker-compose.yaml
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

## API Endpoints

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

### `auth` App (planned)

<!-- TODO (FENYXZ): Implement auth tests -->

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
2. It runs `alembic upgrade head` to apply any pending migrations
3. If no migrations are pending, nothing happens (idempotent)
4. The app then starts normally

### Best Practices

- **Always review generated migrations** before committing them
- **Never manually edit migration files** after they've been applied to production
- **Test migrations locally** before deploying to production
- **Keep models and migrations in sync** — always regenerate migrations after model changes
- **Use descriptive revision messages** to document what changed

### Environment Configuration

Alembic uses the `DATABASE_URL` environment variable (if set) or falls back to `alembic.ini`:

**Via environment variable (recommended for production):**

```bash
export DATABASE_URL=postgresql+asyncpg://postgres:password@host:5432/learn_fastapi
```

**Or update `alembic.ini`:**

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/learn_fastapi
```

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

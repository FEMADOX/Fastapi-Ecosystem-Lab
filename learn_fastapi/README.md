# learn_fastapi

A personal learning module for exploring FastAPI concepts, patterns, and best practices.

## Structure

```text
learn_fastapi/
├── src/
│   ├── first_steps/
│   │   ├── router.py       # CRUD endpoints for /items
│   │   ├── schema.py       # Item Pydantic model
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── validators.py   # Custom validation logic
│   │   └── my_app.py       # App entry point (uvicorn)
│   ├── config.py       # Global configuration (e.g. DB path)
│   ├── constants.py    # In-memory DB constant
│   ├── database.py     # JSON persistence helpers
│   └── main.py         # uvicorn runner (__main__)
├── tests/
|   |-- conftest.py     # Global test fixtures (e.g. TestClient)
|   |-- auth/
|   |   ├── conftest.py     # Auth fixtures
|   |   └── test_auth.py    # Authentication tests
│   └── items/
│       ├── conftest.py     # TestClient fixture
│       └── test_router.py  # Full CRUD test suite
└── docs/
    ├── fastapi-best-practices.md
    ├── awesome-fastapi.md
    └── fastapi-new.md
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

## Testing

```bash
pytest
```

## Docs

### Reference Materials

- [`docs/fastapi-best-practices.md`](docs/fastapi-best-practices.md) — Opinionated best practices: project structure, async routes, Pydantic, dependency injection.
- [`docs/awesome-fastapi.md`](docs/awesome-fastapi.md) — Curated list of FastAPI third-party extensions, resources, and open source projects.
- [`docs/fastapi-new.md`](docs/fastapi-new.md) — Additional FastAPI patterns and modern approaches.

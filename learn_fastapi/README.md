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
│   └── first_steps/
│       ├── conftest.py     # TestClient fixture
│       └── test_router.py  # Full CRUD test suite
└── docs/
    ├── fastapi-best-practices.md
    ├── awesome-fastapi.md
    └── fastapi-new.md
```

## Topics Covered

### `first_steps`

| Concept                                  | Where                                                                  |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| `APIRouter` with prefix & tags           | [`router.py`](src/first_steps/router.py)                               |
| Pydantic model with `Field` validation   | [`schema.py`](src/first_steps/schema.py)                               |
| `Annotated` + `AfterValidator` aliases   | [`annotations.py`](src/first_steps/annotations.py)                     |
| Cross-field business rule validation     | [`validators.py`](src/first_steps/validators.py)                       |
| JSON file as persistent in-memory store  | [`database.py`](src/database.py)                                       |
| Full CRUD: GET / POST / PUT / DELETE     | [`router.py`](src/first_steps/router.py)                               |
| `int \| uuid.UUID` path parameter union  | [`router.py`](src/first_steps/router.py)                               |
| HTTP status codes via `starlette.status` | [`router.py`](src/first_steps/router.py)                               |
| `HTTPException` for 404 responses        | [`router.py`](src/first_steps/router.py)                               |
| Integration tests with `TestClient`      | [`tests/first_steps/test_router.py`](tests/first_steps/test_router.py) |

## API Endpoints

Base prefix: `/items`

| Method   | Path            | Description                 | Body Params  |
| -------- | --------------- | --------------------------- | ------------ |
| `GET`    | `/hello-world/` | Health-check / hello world  |              |
| `GET`    | `/`             | List all items              |              |
| `GET`    | `/{id_param}`   | Get item by `int` or `UUID` |              |
| `POST`   | `/`             | Create a new item           | `Item`       |
| `PUT`    | `/{id_param}`   | Replace an item             | `Item`       |
| `DELETE` | `/{id_param}`   | Delete an item              |              |

## Running

```bash
uv run learn_fastapi/src/main.py
```

## Testing

```bash
pytest
```

## Docs

- [`docs/fastapi-notes.md`](docs/fastapi-notes.md) — Personal notes from the FastAPI learning process (CRUD, ORM, JWT, Alembic, CORS, deployment).
- [`docs/fastapi-best-practices.md`](docs/fastapi-best-practices.md) — Opinionated best practices: project structure, async routes, Pydantic, dependency injection.
- [`docs/awesome-fastapi.md`](docs/awesome-fastapi.md) — Curated list of FastAPI third-party extensions, resources, and open source projects.

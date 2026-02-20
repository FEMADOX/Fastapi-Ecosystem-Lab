# FastAPI Best Practices

> Source: <https://github.com/zhanymkanov/fastapi-best-practices>

Opinionated list of best practices and conventions used at a startup.

---

## Contents

- [Project Structure](#project-structure)
- [Async Routes](#async-routes)
- [Pydantic](#pydantic)
- [Dependencies](#dependencies)
- [Miscellaneous](#miscellaneous)
- [Bonus Section](#bonus-section)

---

## Project Structure

There are many ways to structure a project, but the best structure is one that is consistent, straightforward, and free of surprises.

Many example projects organize by file type (crud, routers, models), which works for microservices or small projects. However, this doesn't scale well for monoliths with many domains.

The recommended scalable structure is inspired by Netflix's [Dispatch](https://github.com/Netflix/dispatch):

```text
fastapi-project
├── alembic/
├── src
│   ├── auth
│   │   ├── router.py
│   │   ├── schemas.py  # pydantic models
│   │   ├── models.py   # db models
│   │   ├── dependencies.py
│   │   ├── config.py   # local configs
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── aws
│   │   ├── client.py   # client model for external service communication
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   ├── posts
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py       # global configs
│   ├── models.py       # global models
│   ├── exceptions.py   # global exceptions
│   ├── pagination.py   # global module e.g. pagination
│   ├── database.py     # db connection related stuff
│   └── main.py
├── tests/
│   ├── auth
│   ├── aws
│   └── posts
├── templates/
│   └── index.html
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
├── logging.ini
└── alembic.ini
```

### Rules

1. Store all domain directories inside `src/`
   - `src/` — highest level, contains common models, configs, constants
   - `src/main.py` — root of the project, inits the FastAPI app
2. Each package has its own router, schemas, models, etc.
   - `router.py` — core of each module with all endpoints
   - `schemas.py` — pydantic models
   - `models.py` — db models
   - `service.py` — module-specific business logic
   - `dependencies.py` — router dependencies
   - `constants.py` — module-specific constants and error codes
   - `config.py` — env vars
   - `utils.py` — non-business logic functions (response normalization, data enrichment, etc.)
   - `exceptions.py` — module-specific exceptions e.g. `PostNotFound`, `InvalidUserData`
3. When a package requires services or dependencies from other packages, import with explicit module name:

```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
from src.posts.constants import ErrorCode as PostsErrorCode
```

---

## Async Routes

FastAPI is async-first. However, `sync` and `async` routes behave differently.

### I/O Intensive Tasks

```python
import asyncio
import time
from fastapi import APIRouter

router = APIRouter()

@router.get("/terrible-ping")
async def terrible_ping():
    time.sleep(10)  # BLOCKS the entire event loop
    return {"pong": True}

@router.get("/good-ping")
def good_ping():
    time.sleep(10)  # runs in threadpool, event loop stays free
    return {"pong": True}

@router.get("/perfect-ping")
async def perfect_ping():
    await asyncio.sleep(10)  # non-blocking
    return {"pong": True}
```

**Summary:**

- `async` route with `time.sleep()` → blocks the whole server
- `sync` route → FastAPI offloads to threadpool automatically
- `async` route with `await asyncio.sleep()` → correct async

> ⚠️ Threads have overhead. Don't overuse sync routes.

### CPU Intensive Tasks

For CPU-bound work (heavy calculations, video transcoding, data processing):

- Awaiting them provides **no benefit** — CPU must actively work
- Running in threads is **also ineffective** due to Python's GIL
- Solution: offload to worker processes (`multiprocessing`, Celery, etc.)

---

## Pydantic

### Use Pydantic extensively

```python
from enum import StrEnum
from pydantic import AnyUrl, BaseModel, EmailStr, Field

class MusicBand(StrEnum):
    AEROSMITH = "AEROSMITH"
    QUEEN = "QUEEN"
    ACDC = "AC/DC"

class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128, pattern="^[A-Za-z0-9-_]+$")
    email: EmailStr
    age: int = Field(ge=18, default=None)
    favorite_band: MusicBand | None = None
    website: AnyUrl | None = None
```

### Custom Base Model

Create a global base model for consistent behavior across all models:

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict

def datetime_to_gmt_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)
```

### Decouple Pydantic BaseSettings

Don't put everything in one `BaseSettings`. Split by domain:

```python
# src/auth/config.py
from pydantic_settings import BaseSettings

class AuthConfig(BaseSettings):
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 5  # minutes

auth_settings = AuthConfig()

# src/config.py
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    ENVIRONMENT: str = "production"

settings = Config()
```

---

## Dependencies

### Use dependencies for request validation

Dependencies can validate data against DB constraints (e.g., checking if an email exists):

```python
# dependencies.py
async def valid_post_id(post_id: UUID4) -> dict:
    post = await service.get_by_id(post_id)
    if not post:
        raise PostNotFound()
    return post

# router.py
@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_by_id(post: dict = Depends(valid_post_id)):
    return post
```

### Chain Dependencies

```python
async def valid_owned_post(
    post: dict = Depends(valid_post_id),
    token_data: dict = Depends(parse_jwt_data),
) -> dict:
    if post["creator_id"] != token_data["user_id"]:
        raise UserNotOwner()
    return post
```

### Dependency calls are cached

FastAPI caches dependency results within a request's scope. If `valid_post_id` is used by 3 dependencies in the same route, it runs only **once**.

### Prefer `async` dependencies

Sync dependencies run in a threadpool (unnecessary overhead for small non-I/O operations).

---

## Miscellaneous

### Follow REST conventions

Use consistent URL naming so dependencies can be reused:

- `GET /courses/:course_id`
- `GET /courses/:course_id/chapters/:chapter_id/lessons`

### FastAPI response serialization note

FastAPI creates your Pydantic model **twice**: once when you return it, once to validate the response. Be aware of side effects in validators.

### Run sync SDKs in a thread pool

```python
from fastapi.concurrency import run_in_threadpool

@app.get("/")
async def call_sync_lib():
    client = SyncAPIClient()
    await run_in_threadpool(client.make_request, data=my_data)
```

### Hide docs in production

```python
from starlette.config import Config

config = Config(".env")
ENVIRONMENT = config("ENVIRONMENT")
SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_configs = {"title": "My API"}
if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)
```

### Set async test client from day 0

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_create_post(client: AsyncClient):
    resp = await client.post("/posts")
    assert resp.status_code == 201
```

### Use Ruff

Ruff replaces black, autoflake, isort and supports 600+ lint rules:

```sh
ruff check --fix src
ruff format src
```

---

## Bonus Section

See the [issues section](https://github.com/zhanymkanov/fastapi-best-practices/issues) of the project for community-shared best practices on:

- Permissions & auth
- Class-based services & views
- Task queues
- Custom response serializers
- Configuration with dynaconf

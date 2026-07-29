# learn_fastapi

A FastAPI learning backend that now applies Clean Architecture to the `auth`,
`users`, and `items` features while preserving the existing versioned HTTP API.

## Table of Contents

- [learn\_fastapi](#learn_fastapi)
  - [Table of Contents](#table-of-contents)
  - [Architecture](#architecture)
    - [Dependency rule](#dependency-rule)
    - [Project structure](#project-structure)
    - [Layer responsibilities](#layer-responsibilities)
    - [Request flow](#request-flow)
  - [Features](#features)
    - [`items`](#items)
      - [Cloudinary media](#cloudinary-media)
      - [Redis cache](#redis-cache)
    - [`auth`](#auth)
    - [`users`](#users)
    - [Server-Sent Events](#server-sent-events)
  - [Running](#running)
  - [Local Services with Docker Compose](#local-services-with-docker-compose)
  - [Database Migrations with Alembic](#database-migrations-with-alembic)
  - [Testing and Quality Checks](#testing-and-quality-checks)
  - [Documentation](#documentation)

## Architecture

The backend is organized by feature. The core features use four explicit
layers rather than a repository/service structure:

```text
presentation -> application -> domain
infrastructure -> application -> domain
```

### Dependency rule

- `domain` contains business entities, value objects, domain errors, and
  persistence contracts. It does not import FastAPI, Pydantic, SQLAlchemy,
  Redis, Cloudinary, or SSE.
- `application` coordinates commands, queries, and use cases. It depends on
  domain abstractions and declares ports for external effects.
- `infrastructure` implements those ports with SQLAlchemy, Redis, Cloudinary,
  JWT/Argon2, the system clock, and SSE publishers.
- `presentation` is the FastAPI boundary. It owns routers, Pydantic schemas,
  dependency wiring, HTTP exceptions, cookies, headers, and response mapping.

SQLAlchemy models remain at each feature root (`models.py`) so Alembic can
discover them explicitly. Mappers prevent those ORM models from leaking into
domain entities or application use-case signatures.

### Project structure

```text
learn_fastapi/
|-- alembic/
|   |-- versions/                  # Database migration scripts
|   `-- env.py                     # Alembic model registration and configuration
|-- docs/                          # FastAPI reference material
|-- src/
|   |-- auth/
|   |   |-- domain/                # Tokens, auth entities, errors, repository ports
|   |   |-- application/           # Login/refresh/logout commands, queries, use cases
|   |   |-- infrastructure/        # JWT, Argon2, token repository, SSE adapters
|   |   |-- presentation/          # Auth routes, cookies, schemas, HTTP dependencies
|   |   |-- config.py              # JWT and cookie settings
|   |   `-- models.py              # RefreshToken SQLAlchemy model
|   |-- users/
|   |   |-- domain/                # User entities, value objects, errors, ports
|   |   |-- application/           # Account commands, queries, use cases, event port
|   |   |-- infrastructure/        # SQLAlchemy repository, mappers, SSE adapter
|   |   |-- presentation/          # Account routes, schemas, mappers, dependencies
|   |   `-- models.py              # User SQLAlchemy model
|   |-- items/
|   |   |-- domain/                # Item entities, value objects, rules, repository port
|   |   |-- application/           # CRUD commands/queries, use cases, external-effect ports
|   |   |-- infrastructure/        # SQLAlchemy, Redis, Cloudinary, SSE adapters
|   |   |-- presentation/          # Item routes, schemas, mappers, dependency composition
|   |   `-- models.py              # Item SQLAlchemy model
|   |-- shared/
|   |   |-- domain/                # Shared IDs and value objects
|   |   |-- application/           # Shared DTOs, security concepts, base use cases
|   |   |-- infrastructure/        # Clock, password hasher, repository helpers
|   |   `-- presentation/          # Current-user dependency and shared HTTP errors
|   |-- cache/                     # Fault-tolerant Redis client
|   |-- sse/
|   |   |-- manager.py             # Subscription and broadcast manager
|   |   `-- presentation/router.py # Authenticated event streams
|   |-- utils/                     # Operational helpers such as Alembic integration
|   |-- config.py                  # Settings and application lifespan
|   |-- database.py                # Async SQLAlchemy engine and session dependency
|   `-- main.py                    # FastAPI app, routers, and API versioning
`-- tests/
    |-- unit/                       # Application tests with fakes
    |-- v1/                         # Version 1 HTTP/integration tests
    |-- v2/                         # Version 2 auth HTTP tests
    `-- conftest.py                 # Shared test app and in-memory database fixtures
```

### Layer responsibilities

| Concern | Contract | Current adapter / boundary |
| :-- | :-- | :-- |
| Item persistence | `domain/ports.py` | `items/infrastructure/repository.py` |
| Item cache | `application/ports.py` | `items/infrastructure/cache.py` |
| Item image storage | `application/ports.py` | `items/infrastructure/image_storage.py` |
| Item events | `application/ports.py` | `items/infrastructure/events.py` |
| Auth token issue/verification | `auth/application/ports.py` | `auth/infrastructure/jwt_access_token_*.py` |
| Refresh token hashing/verification | `auth/application/ports.py` | `auth/infrastructure/argon2_*.py` |
| User persistence | `users/domain/ports.py` | `users/infrastructure/repository.py` |
| User events | `users/application/ports.py` | `users/infrastructure/events.py` |
| HTTP input/output | Commands, queries, domain results | `*/presentation/` |

### Request flow

An HTTP operation follows the same direction across migrated features:

```text
FastAPI router
  -> request schema / authenticated actor
  -> command or query
  -> application use case
  -> domain and declared ports
  -> injected infrastructure adapters
  -> presentation mapper / HTTP response
```

`*/presentation/dependencies.py` is the composition root for each feature. For
example, `items` wires its use cases to `SQLAlchemyItemsRepository`,
`RedisItemCache`, `CloudinaryImageStorage`, and `SSEItemEventPublisher`.

## Features

The application uses `root_path="/api"` and
[`fastapi-versionizer`](https://github.com/DeanWay/fastapi-versionizer).
Versioned endpoints are available under `/api/v1`, `/api/v2`, and the
`/api/latest` alias.

### `items`

The `items` feature demonstrates ownership-aware CRUD, cache-aside reads,
Cloudinary image storage, and domain events without coupling its application
use cases to those concrete technologies.

| Concept | Where |
| :-- | :-- |
| Domain entities and ownership rules | [`domain/entities.py`](src/items/domain/entities.py) |
| Commands and queries | [`application/commands.py`](src/items/application/commands.py), [`application/queries.py`](src/items/application/queries.py) |
| Use cases | [`application/use_cases.py`](src/items/application/use_cases.py) |
| External-effect ports | [`application/ports.py`](src/items/application/ports.py) |
| SQLAlchemy adapter | [`infrastructure/repository.py`](src/items/infrastructure/repository.py) |
| Redis adapter | [`infrastructure/cache.py`](src/items/infrastructure/cache.py) |
| Cloudinary adapter | [`infrastructure/image_storage.py`](src/items/infrastructure/image_storage.py) |
| SSE adapter | [`infrastructure/events.py`](src/items/infrastructure/events.py) |
| FastAPI boundary | [`presentation/router.py`](src/items/presentation/router.py) |

Base prefix: `/items`

| Method | Path | Description |
| :-- | :-- | :-- |
| `GET` | `/` | List all items |
| `GET` | `/owner` | List the authenticated owner's items; admins may request `owner_id` |
| `GET` | `/owner/{id_param}` | Get one owner-scoped item |
| `GET` | `/{id_param}` | Get one item |
| `POST` | `/` | Create an item |
| `PUT` | `/{id_param}` | Replace an owned item |
| `PATCH` | `/{id_param}` | Partially update an owned item |
| `DELETE` | `/{id_param}` | Delete an owned item |
| `POST` | `/image/{id_param}` | Upload or replace an item's image |
| `POST` | `/with-image/` | Create an item and upload its image |

Owner authorization is decided in application use cases using the current
actor, not in a repository or a presentation helper. Regular users can operate
on their own resources; superusers can request another owner explicitly.

#### Cloudinary media

`CloudinaryImageStorage` implements the application `ImageStorage` port.
Uploaded `secure_url` and `public_id` values are stored as `image_url` and
`image_public_id`; keeping the public ID lets replacements delete the previous
remote asset without parsing its URL.

Configure these values in the repository-root `.env`:

```.env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Uploads use the `FastAPI-Ecosystem-Lab/media` Cloudinary asset folder.
Configuration is validated only when an upload or deletion is attempted.

#### Redis cache

`RedisItemCache` implements the application `ItemsCache` port. Reads follow the
cache-aside pattern and return domain records to use cases:

- `items:all`
- `items:by-id:<item_id>`
- `items:owner:<owner_id>`
- `items:owner:<owner_id>:item:<item_id>`

Entries use a 600-second TTL. Mutations invalidate `items:*` so global and
owner-scoped representations cannot become stale. Redis failures are logged
and disable caching for the current process instead of breaking API requests.
Pattern invalidation currently uses Redis `KEYS`, which is suitable for this
learning/low-traffic environment; a production high-traffic deployment should
prefer `SCAN`.

### `auth`

The `auth` feature keeps authentication workflows in application use cases and
places cryptography and persistence behind ports.

| Concept | Where |
| :-- | :-- |
| Auth entities and errors | [`domain/`](src/auth/domain/) |
| Login, refresh, and logout use cases | [`application/use_cases.py`](src/auth/application/use_cases.py) |
| Token/clock/hash/event ports | [`application/ports.py`](src/auth/application/ports.py) |
| JWT and Argon2 adapters | [`infrastructure/`](src/auth/infrastructure/) |
| Cookie and CSRF handling | [`presentation/cookies.py`](src/auth/presentation/cookies.py), [`presentation/router.py`](src/auth/presentation/router.py) |
| Dependency composition | [`presentation/dependencies.py`](src/auth/presentation/dependencies.py) |

Base prefix: `/auth`

| Method | Path | Version | Description |
| :-- | :-- | :-- | :-- |
| `POST` | `/register` | v1 | Register a user |
| `POST` | `/token` | v1 | Return an access token and set refresh/CSRF cookies |
| `POST` | `/token` | v2 | Return access and refresh token details |
| `POST` | `/refresh` | v1 | Issue a new access token from refresh and CSRF cookies |
| `POST` | `/logout` | v1 | Revoke the refresh token and clear auth cookies |

The typical v1 flow is register, login, use the bearer access token, refresh
with the HttpOnly refresh cookie plus `X-CSRF-Token`, and logout.

### `users`

The `users` feature owns account management. Application use cases enforce
identity/administrator rules and publish account events through a port.

| Method | Path | Description |
| :-- | :-- | :-- |
| `GET` | `/users/me` | Return the current profile |
| `GET` | `/users/{user_id}` | Return an authorized account |
| `PATCH` | `/users/{user_id}` | Update email and/or password after verification |
| `DELETE` | `/users/{user_id}` | Delete an account and related records |

See [`users/application/use_cases.py`](src/users/application/use_cases.py) for
the workflows and
[`users/presentation/router.py`](src/users/presentation/router.py) for HTTP
mapping.

### Server-Sent Events

Authenticated clients can subscribe to:

- `GET /api/v1/events/global`
- `GET /api/v1/events/me`

The presentation router owns streaming responses and connection cleanup. The
feature-specific infrastructure publishers translate domain/application
results into JSON-safe SSE payloads. Current event families include
`item.*`, `auth.*`, and `user.*`.

`item.created` is sent globally and to its owner; item updates, image updates,
deletions, and auth/account events are user-scoped. Delivery failures are
external-effect failures and do not move SSE concerns into domain code.

## Running

From the repository root:

```bash
uv sync
uv run run-api-server
```

The API is available at <http://localhost:8000>, with Swagger UI at
<http://localhost:8000/api/docs>.

## Local Services with Docker Compose

From the repository root:

```bash
docker compose up -d redis
```

The active Compose services are the API and Redis. The PostgreSQL service is an
opt-in, commented example in `docker-compose.yaml`; run PostgreSQL separately
or enable that service and keep its credentials aligned with `DATABASE_URL`.
Use [`.env.example`](../.env.example) as the configuration template.

## Database Migrations with Alembic

SQLAlchemy models are imported explicitly in `alembic/env.py`. At startup, the
application checks for pending revisions and logs a warning; it does not apply
migrations automatically.

Run Alembic from `learn_fastapi/`:

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic current
uv run alembic heads
```

Always review autogenerated migrations and test both upgrade and downgrade
paths before deployment.

## Testing and Quality Checks

From the repository root:

```bash
uv run ruff check learn_fastapi
uv run ruff format --check learn_fastapi
uv run ty check learn_fastapi
```

Run tests with `DEBUG=True`. On PowerShell:

```powershell
$env:DEBUG = "True"
uv run pytest --config-file=pyproject.toml
```

On POSIX shells:

```bash
DEBUG=True uv run pytest --config-file=pyproject.toml
```

Tests use in-memory SQLite by default. The suite includes pure application
tests with fake ports plus v1/v2 HTTP tests against the FastAPI app.

## Documentation

- [`../docs/clean-architecture-roadmap.md`](../docs/clean-architecture-roadmap.md)
  — migration rationale and original phased plan.
- [`../docs/clean-architecture-explanations.md`](../docs/clean-architecture-explanations.md)
  — supporting explanations of commands, queries, entities, and ownership.
- [`docs/fastapi-best-practices.md`](docs/fastapi-best-practices.md)
  — FastAPI project and dependency-injection practices.
- [`docs/awesome-fastapi.md`](docs/awesome-fastapi.md)
  — FastAPI ecosystem references.
- [`docs/fastapi-new.md`](docs/fastapi-new.md)
  — additional patterns and modern approaches.

# learn_fastapi

A personal learning module for exploring FastAPI concepts, patterns, and best practices.

## Table of Contents

- [learn\_fastapi](#learn_fastapi)
  - [Table of Contents](#table-of-contents)
  - [Structure](#structure)
  - [Topics Covered](#topics-covered)
  - [API Version 1: Core Concepts and Patterns](#api-version-1-core-concepts-and-patterns)
    - [`items` App](#items-app)
      - [`items` Endpoints](#items-endpoints)
      - [`items` media uploads with Cloudinary](#items-media-uploads-with-cloudinary)
      - [`items` cacheing with Redis](#items-cacheing-with-redis)
      - [`items` SSE (Server-Sent Events)](#items-sse-server-sent-events)
    - [`auth` App](#auth-app)
      - [`auth` Endpoints (Authentication flows only)](#auth-endpoints-authentication-flows-only)
    - [`users` App](#users-app)
      - [`users` Endpoints (Account management only)](#users-endpoints-account-management-only)
  - [API Version 2:  Core Concepts and Patterns](#api-version-2--core-concepts-and-patterns)
    - [`auth` App (V2)](#auth-app-v2)
  - [Running](#running)
  - [Local PostgreSQL with Docker Compose](#local-postgresql-with-docker-compose)
  - [Database Migrations with Alembic](#database-migrations-with-alembic)
    - [How It Works](#how-it-works)
    - [Common Migration Commands](#common-migration-commands)
      - [Generate a new migration after updating models](#generate-a-new-migration-after-updating-models)
      - [Apply all pending migrations](#apply-all-pending-migrations)
      - [Check the current migration version](#check-the-current-migration-version)
      - [View all migration revisions](#view-all-migration-revisions)
      - [Downgrade to the previous migration](#downgrade-to-the-previous-migration)
      - [Downgrade all the way to the start](#downgrade-all-the-way-to-the-start)
    - [How Migrations Run at Startup](#how-migrations-run-at-startup)
    - [Best Practices](#best-practices)
    - [Alembic Configuration Details](#alembic-configuration-details)
  - [Testing](#testing)
  - [Docs](#docs)
    - [Reference Materials](#reference-materials)

## Structure

```text
learn_fastapi/
├── alembic/
|   ├── versions/        # Auto-generated migration scripts
|   ├── env.py           # Alembic configuration and setup
|   └── script.py.mako   # Template for generating migration scripts
├── docs/
|   ├── fastapi-best-practices.md
|   ├── awesome-fastapi.md
|   └── fastapi-new.md
├── src/
│   ├── auth/           # Authentication module (login, register, tokens only)
│   │   ├── annotations.py  # Annotated type aliases for auth models
│   │   ├── config.py       # Auth-specific settings (JWT, cookies)
│   │   ├── dependencies.py # OAuth2 and auth service dependencies
│   │   ├── exceptions.py   # Auth-specific exceptions
│   │   ├── models.py       # SQLAlchemy models (RefreshToken only)
│   │   ├── repository.py   # Auth data access layer (refresh tokens)
│   │   ├── router.py       # Auth endpoints (register, login, refresh, logout)
│   │   ├── schema.py       # Auth Pydantic models (Token, UserCreate, etc.)
│   │   ├── service.py      # Auth business logic layer
│   │   └── utils.py        # Utility functions (hashing, token creation, etc.)
│   ├── cache/          # Cache module (e.g. Redis integration)
│   │   └── redis_client.py        # Redis client integration
│   ├── users/          # User account management module
│   │   ├── annotations.py  # Annotated type aliases for users models
│   │   ├── dependencies.py # User service dependency wiring
│   │   ├── exceptions.py   # User-specific exceptions
│   │   ├── models.py       # SQLAlchemy models (User)
│   │   ├── repository.py   # User account data access layer
│   │   ├── router.py       # User endpoints (profile, update, delete)
│   │   ├── schema.py       # User Pydantic models (UserResponse, UserUpdate, etc.)
│   │   └── service.py      # User account business logic layer
│   ├── items/          # Items module (example domain)
│   │   ├── annotations.py  # Annotated type aliases
│   │   ├── cache.py        # Item-specific caching logic (e.g. Redis caching for item retrieval)
│   │   ├── dependencies.py # Item service dependency wiring
│   │   ├── exceptions.py   # Item-specific exceptions
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── repository.py   # Data access layer
│   │   ├── router.py       # CRUD endpoints for /items
│   │   ├── schema.py       # Item Pydantic model
│   │   ├── service.py      # Business logic layer
│   │   ├── utils.py        # Item helpers (Cloudinary image upload, etc.)
│   │   └── validators.py   # Custom validation logic (Not used in this example, but good for complex business rules)
|   ├── sse/
│   │   ├── manager.py      # Server-Sent Events manager for handling connections and broadcasting
│   │   └── router.py       # SSE endpoints for clients to subscribe to events 
|   ├── static/js/      # Static files (e.g. CSS, JS)
│   ├── utils/          # Shared utilities
│   │   ├── alembic.py      # Alembic integration helpers
│   │   ├── annotations.py  # Shared type annotations
│   │   ├── dependencies.py # Shared dependencies (e.g. CurrentUserDep)
│   │   └── hot_reload.py   # Development hot-reload WebSocket
│   ├── config.py       # Global configuration and lifespan
│   ├── constants.py    # Project paths and constants
│   ├── database.py     # SQLAlchemy engine and session setup
│   ├── main.py         # uvicorn runner (__main__)
│   └── middleware.py   # Custom middleware (e.g. Swagger hot reload, CORS, etc.)
├── tests/
|   ├── v1/
|   |   ├── auth/
|   |   |   ├── conftest.py     # Auth fixtures (seeded user)
|   |   |   └── test_router.py  # Authentication endpoints tests
|   |   ├── users/
|   |   |   ├── conftest.py     # User fixtures (user_data, registered_user, access_token, auth_headers)
|   |   |   └── test_router.py  # User account endpoints tests
|   |   ├── items/
|   |   |   ├── conftest.py     # Item fixtures (test_user, sample_item, seeded_item)
|   |   |   └── test_router.py  # Item CRUD endpoints tests
|   |   ├── conftest.py # V1 global fixtures (if needed)
|   |   └── test_items_authorization.py # Authorization tests for item ownership
|   ├── v2/
|   |   ├── auth/
|   |   |   ├── conftest.py     # Auth fixtures (seeded user)
|   |   |   └── test_router.py  # Authentication endpoints tests
|   |   └── conftest.py # V2 global fixtures (if needed)
|   ├── conftest.py     # Global test fixtures (test_async_engine, test_session, client)
|   └── test_main.py    # Basic smoke test for app startup
├── .env.example
├── alembic.ini
└── README.md
```

## Topics Covered

The API base path is `/api` (configured in `src/main.py`), and the main topics covered include:

## API Version 1: Core Concepts and Patterns

`/v1` is the main versioned API prefix for all endpoints in this project. It includes three main "apps" or modules:

### `items` App

| Concept                                      | Where                                                                            |
|----------------------------------------------|----------------------------------------------------------------------------------|
| `APIRouter` with prefix & tags               | [`router.py`](src/items/router.py)                                               |
| Pydantic model with `Field` validation       | [`schema.py`](src/items/schema.py)                                               |
| `Annotated` aliases                          | [`annotations.py`](src/items/annotations.py)                                     |
| Cross-field business rule validation         | [`validators.py`](src/items/validators.py)                                       |
| Repository + Service pattern                 | [`repository.py`](src/items/repository.py), [`service.py`](src/items/service.py) |
| Ownership-aware CRUD (`User` -> `Item`)      | [`models.py`](src/items/models.py), [`router.py`](src/items/router.py)           |
| Full CRUD: GET / POST / PUT / PATCH / DELETE | [`router.py`](src/items/router.py)                                               |
| HTTP status codes via `starlette.status`     | [`router.py`](src/items/router.py)                                               |
| `HTTPException` for 404 responses            | [`router.py`](src/items/router.py)                                               |
| Integration tests with `httpx.AsyncClient`   | [`tests/items/test_router.py`](tests/v1/items/test_router.py)                    |
| Authorization and ownership tests            | [`tests/test_items_authorization.py`](tests/v1/items/test_items_authorization.py)      |

#### `items` Endpoints

Base prefix: `/items`

| Method   | Path                | Description                            |                           Body Params                           |
|:---------|:--------------------|:---------------------------------------|:---------------------------------------------------------------:|
| `GET`    | `/`                 | List all items                         |                                                                 |
| `GET`    | `/{id_param}`       | Get item by `UUID`                     |                                                                 |
| `POST`   | `/`                 | Create a new item                      |                             `Item`                              |
| `PUT`    | `/{id_param}`       | Replace fields of an existing item     |                `ItemUpdate` (`image_url` allowed)                |
| `PATCH`  | `/{id_param}`       | Partially update an existing item      |                 `ItemPatch` (`image_url` allowed)                |
| `DELETE` | `/{id_param}`       | Delete an item                         |                                                                 |
| `POST`   | `/image/{id_param}` | Upload/update image for an item        | `image_file` (`UploadFile`), `caption`, authenticated item owner |
| `POST`   | `/with-image/`      | Create item with optional image upload | `name`, `description`, `price`, `tax`, `image_file?`, `caption` |

#### `items` media uploads with Cloudinary

The items module now uploads item images to Cloudinary instead of persisting new uploads in the local
`src/media/images` folder. This keeps the API stateless for media files and lets frontend clients render the
Cloudinary-hosted `secure_url` stored on each item as `image_url`.

**Configuration:**

Add these variables to the repository root `.env` file:

```.env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Uploaded assets are sent to the Cloudinary folder:

```text
FastAPI-Ecosystem-Lab/media
```

**Upload flow:**

1. `POST /items/image/{id_param}` receives `multipart/form-data` with `image_file` and optional `caption`.
2. The route requires `CurrentUserDep`; regular users can only update images for their own items, while superusers can
   update any item.
3. `src/items/utils.py` signs the Cloudinary upload parameters and sends the file with `httpx.AsyncClient`.
4. Cloudinary returns a `secure_url`, which is saved on the item as `image_url`.
5. Item cache entries are invalidated and an `item.image_updated` SSE event is broadcast to the owner.

`POST /items/with-image/` uses the same Cloudinary helper when an image is included during item creation.

**Notes:**

- Missing Cloudinary variables raise a runtime error only when an image upload is attempted.
- `PUT /items/{id_param}` and `PATCH /items/{id_param}` accept `image_url` for API compatibility, but normal user-facing
  image changes should go through the upload endpoint so the backend controls media storage.

#### `items` cacheing with Redis

The items module implements a Redis-backed caching layer to improve read performance and reduce database load. The cache follows a cache-aside pattern where the service first attempts to read from Redis, falling back to the database on a cache miss, and then populates the cache with the fresh data.

**Key Architecture:**

- **Namespace**: All item-related keys use the `items:` prefix
- **TTL**: 600 seconds (10 minutes) for all cached entries
- **Key Patterns**:
  - `items:all` → Serialized list of all items (`list[ItemSchema]`)
  - `items:<uuid>` → Serialized single item (`ItemSchema`) by UUID
  - `items:<user_id>` → All items belonging to a specific user
  - `items:<item_id>:<user_id>` → User-scoped single item (for ownership verification)

**Cache Flow:**

1. **Read Operations** (`get_all_items`, `get_item`, `get_user_items`, `get_user_item`):
   - Attempt to retrieve data from Redis using the appropriate key
   - If found (cache hit): deserialize and return immediately
   - If not found (cache miss): query database, serialize result, store in Redis, then return

2. **Write Operations** (`create_item`, `update_item`, `delete_item`, etc.):
   - Perform the database operation
   - Invalidate the entire `items:*` namespace using `delete_cache_pattern("items:*")`
   - This ensures cache consistency by forcing fresh reads on subsequent requests

**Implementation Details:**

- The cache layer lives in `src/items/cache.py` and uses the generic Redis client from `src/cache/redis_client.py`
- The Redis client is fault-tolerant: all operations catch exceptions and log warnings instead of propagating errors, ensuring a missing/unreachable Redis never breaks the API
- Data is serialized/deserialized using JSON (with `default=str` to handle UUID/datetime objects)
- Cache invalidation uses Redis `KEYS` pattern matching (suitable for development/low-traffic; production high-traffic scenarios should consider migrating to `SCAN`-based iteration)

**Performance Benefits:**

- Eliminates repeated database queries for frequently accessed item lists
- Reduces latency for item retrieval operations
- Scales read traffic across Redis instances (in clustered setups)

#### `items` SSE (Server-Sent Events)

The items module includes a Server-Sent Events (SSE) implementation to provide real-time updates to clients when items are created, updated, or deleted. This allows clients to subscribe to a stream of events and receive immediate notifications without polling.

**SSE Architecture:**

- **Global Events**: Broadcast to all connected clients (e.g., when any item is created)
- **User-Scoped Events**: Sent only to clients connected for a specific user (e.g., when that user's item is updated/deleted)
- **Fault Tolerant**: SSE failures are logged but never interrupt the main API flow
- **Authenticated**: All SSE endpoints require valid JWT authentication

**Implementation Details:**

1. **SSE Manager** (`src/sse/manager.py`):
   - Singleton `SSEManager` class managing two types of channels:
     - `_global`: List of `asyncio.Queue` for global event subscribers
     - `_users`: Dictionary mapping `user_id` → list of `asyncio.Queue` for user-scoped subscribers
   - Each client connection gets its own `asyncio.Queue` to receive events
   - Methods for subscription/unsubscription and broadcasting events
   - SSE message format: `"data: {json}\n\n"` (per SSE spec)

2. **SSE Endpoints** (`src/sse/router.py`):
   - `GET /api/v1/events/global` - Stream global events
   - `GET /api/v1/events/me` - Stream events for the authenticated user
   - Both endpoints:
     - Require authentication via `CurrentUserDep` (valid JWT)
     - Return `StreamingResponse` with `media_type="text/event-stream"`
     - Include proper headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`
     - Use keep-alive comments (`: keep-alive\n\n`) to detect disconnections
     - Clean up subscriptions automatically when clients disconnect

3. **Service Integration** (`src/items/service.py`):
   - Static `_broadcast_sse_event()` method wraps SSE calls with exception handling
   - Events broadcasted on item operations:
     - `item.created`: Global broadcast + to item owner
     - `item.updated`: To item owner only
     - `item.deleted`: To item owner only
     - `item.image_updated`: To item owner only
   - Payload: Serialized `ItemSchema` using `model_dump(mode="json")` (handles UUID/datetime)

**How to Use SSE from Clients:**

1. **Connect to Global Events** (all item creations):

   ```javascript
   const eventSource = new EventSource('/api/v1/events/global', {
     headers: {
       'Authorization': 'Bearer <your-jwt-token>'
     }
   });
   
   eventSource.onmessage = (event) => {
     const data = JSON.parse(event.data);
     console.log('Global event:', data.event, data.payload);
     // Handle item.created events from any user
   };
   ```

2. **Connect to User-Specific Events** (your own item updates/deletes):

   ```javascript
   const eventSource = new EventSource('/api/v1/events/me', {
     headers: {
       'Authorization': 'Bearer <your-jwt-token>'
     }
   });
   
   eventSource.onmessage = (event) => {
     const data = JSON.parse(event.data);
     console.log('User event:', data.event, data.payload);
     // Handle item.updated/deleted events for your items
   };
   ```

3. **Event Types** you'll receive:
   - `{"event": "item.created", "payload": {item data}}`
   - `{"event": "item.updated", "payload": {item data}}`
   - `{"event": "item.deleted", "payload": {item data}}`
   - `{"event": "item.image_updated", "payload": {item data}}`

**Benefits:**

- Eliminates need for polling to get real-time updates
- Low-latency push notifications from server to client
- Efficient: only sends data when events occur
- Scalable: each connection is lightweight (HTTP-based)
- Secure: same JWT authentication as REST API

**Note:** The SSE implementation uses HTTP/1.1 chunked encoding and works through most proxies and firewalls since it's standard HTTP GET requests.

### `auth` App

| Concept                                      | Where                                                                          |
|:---------------------------------------------|:-------------------------------------------------------------------------------|
| JWT authentication with refresh tokens       | [`service.py`](src/auth/service.py), [`utils.py`](src/auth/utils.py)           |
| Password hashing with Argon2                 | [`utils.py`](src/auth/utils.py)                                                |
| OAuth2 Password Flow with Bearer tokens      | [`dependencies.py`](src/auth/dependencies.py)                                  |
| Repository + Service pattern                 | [`repository.py`](src/auth/repository.py), [`service.py`](src/auth/service.py) |
| CSRF token protection                        | [`service.py`](src/auth/service.py), [`router.py`](src/auth/router.py)         |
| Refresh token rotation with expiration       | [`service.py`](src/auth/service.py), [`models.py`](src/auth/models.py)         |
| Secure HTTP-only cookie handling             | [`utils.py`](src/auth/utils.py), [`config.py`](src/auth/config.py)             |
| Custom exceptions for auth errors            | [`exceptions.py`](src/auth/exceptions.py)                                      |
| RefreshToken model with SQLAlchemy ORM       | [`models.py`](src/auth/models.py)                                              |
| Circular import avoidance with TYPE_CHECKING | [`models.py`](src/auth/models.py)                                              |
| Integration tests for authentication flow    | [`tests/auth/test_router.py`](tests/v1/auth/test_router.py)                    |

#### `auth` Endpoints (Authentication flows only)

Base prefix: `/auth`

| Method | Path        | Description                        | Body Params                                            | Headers/Cookies                                          |
|:-------|:------------|:-----------------------------------|:-------------------------------------------------------|:---------------------------------------------------------|
| `POST` | `/register` | Register a new user account        | `UserCreate` (email, password)                         | —                                                        |
| `POST` | `/token`    | Login and receive JWT access token | `OAuth2PasswordRequestForm` (username/email, password) | —                                                        |
| `POST` | `/refresh`  | Refresh and rotate access token    | —                                                      | `X-CSRF-Token`, `refresh_token` + `csrf_token` (cookies) |
| `POST` | `/logout`   | Logout and revoke refresh token    | —                                                      | `X-CSRF-Token`, `refresh_token` + `csrf_token` (cookies) |

**Authentication Flow:**

1. **Register** → Create account with email/password
2. **Login** → Get `access_token` (JWT), `refresh_token` (cookie), `csrf_token` (cookie + response body)
3. **Use APIs** → Include `Authorization: Bearer <access_token>` header
4. **Refresh** → Exchange expired access token for new one using refresh token
5. **Logout** → Revoke refresh token and clear cookies

### `users` App

| Concept                                       | Where                                                                            |
|:----------------------------------------------|:---------------------------------------------------------------------------------|
| Repository + Service pattern                  | [`repository.py`](src/users/repository.py), [`service.py`](src/users/service.py) |
| User model with SQLAlchemy ORM                | [`models.py`](src/users/models.py)                                               |
| Ownership-aware operations (user only access) | [`service.py`](src/users/service.py), [`router.py`](src/users/router.py)         |
| Superuser override capability                 | [`service.py`](src/users/service.py), [`router.py`](src/users/router.py)         |
| Account update (email + password with verify) | [`service.py`](src/users/service.py)                                             |
| Account deletion with cascading cleanup       | [`service.py`](src/users/service.py), [`repository.py`](src/users/repository.py) |
| Test fixtures with dependency chains          | [`conftest.py`](tests/v1/users/conftest.py)                                      |
| Integration tests for account flows           | [`tests/users/test_router.py`](tests/v1/users/test_router.py)                    |

#### `users` Endpoints (Account management only)

Base prefix: `/users`

| Method   | Path         | Description                                | Body Params     | Headers                         |
|:---------|:-------------|:-------------------------------------------|:----------------|:--------------------------------|
| `GET`    | `/me`        | Get current user profile                   | —               | `Authorization: Bearer <token>` |
| `GET`    | `/{user_id}` | Get specific user account (if owner/admin) | —               | `Authorization: Bearer <token>` |
| `PATCH`  | `/{user_id}` | Update user email and/or password          | `UserUpdate`    | `Authorization: Bearer <token>` |
| `DELETE` | `/{user_id}` | Delete user account permanently            | `DeleteAccount` | `Authorization: Bearer <token>` |

## API Version 2:  Core Concepts and Patterns

### `auth` App (V2)

Base prefix: `/auth`

| Method | Path        | Description                                        | Body Params                                            |
|:-------|:------------|:---------------------------------------------------|:-------------------------------------------------------|
| `POST` | `/token`    | Login and receive: access token, refresh token,    | `OAuth2PasswordRequestForm` (username/email, password) |
|        |             | (access & refresh tokens)_expires_in and CSRFtoken |                                                        |

## Running

```bash
uv run run-api-server
```

## Local PostgreSQL with Docker Compose

The Docker Compose file is located at the repository root (`../docker-compose.yaml`).

From the repository root:

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

- Models are defined in `src/auth/models.py`, `src/users/models.py`, and `src/items/models.py`
- Migrations are generated automatically from model changes
- Migrations are checked when the FastAPI app starts (via `lifespan`)
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

**Note:** Migrations are **checked** at startup, but not automatically applied. You must run `alembic upgrade head`
manually to apply pending migrations.

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

## Testing

To run the test normally use:

```bash
pytest
```

If you want to run the tests in parallel (faster):

```bash
pytest -n auto
```

Using the `-n auto` flag with pytest-xdist will automatically run tests in parallel across multiple CPU cores,
significantly reducing test execution time for larger test suites.

`xdist` plugin docs: <https://pytest-xdist.readthedocs.io/en/stable/index.html>

Tests use an **in-memory SQLite database** (`sqlite+aiosqlite:///:memory:`) which:

- Is fast and isolated per test
- Doesn't require PostgreSQL to be running
- Automatically creates/drops all tables from models
- Doesn't use Alembic (migrations are only for production PostgreSQL)
- Includes dedicated auth tests, items CRUD tests, and item authorization/ownership tests

If you want to run tests against PostgreSQL instead, change the `TEST_DATABASE_URL` variable inside `tests/conftest.py`
to point to your local PostgreSQL instance:

```python
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db"
```

And run the tests

## Docs

### Reference Materials

- [`docs/fastapi-best-practices.md`](docs/fastapi-best-practices.md) — Opinionated best practices: project structure,
  async routes, Pydantic, dependency injection.
- [`docs/awesome-fastapi.md`](docs/awesome-fastapi.md) — Curated list of FastAPI third-party extensions, resources, and
  open source projects.
- [`docs/fastapi-new.md`](docs/fastapi-new.md) — Additional FastAPI patterns and modern approaches.

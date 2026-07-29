# FastAPI Ecosystem Lab 🚀

A learning monorepo for building a production-oriented FastAPI backend and
consuming it from Next.js and Streamlit frontends.

🌐 API deployment (when active):
<https://fastapi-ecosystem-lab-api.koyeb.app/api/docs>

## What is covered

| Topic | Status |
| :-- | :-- |
| FastAPI routing, dependencies, middleware, and versioning | ✅ Implemented |
| Clean Architecture for `auth`, `users`, and `items` | ✅ Implemented |
| SQLAlchemy, PostgreSQL, and Alembic | ✅ Implemented |
| JWT/OAuth2 authentication, refresh tokens, and CSRF protection | ✅ Implemented |
| Redis caching, Cloudinary media, and Server-Sent Events | ✅ Implemented |
| pytest, httpx, Ruff, and ty validation | ✅ Implemented |
| Streamlit dashboard client | ✅ Implemented |
| Next.js production frontend | 🔁 In progress |
| Docker and deployment | ✅ Implemented |

## Architecture

The backend is feature-oriented and follows Clean Architecture:

```text
presentation -> application -> domain
infrastructure -> application -> domain
```

- `domain` contains business entities, value objects, rules, errors, and
  persistence contracts.
- `application` contains commands, queries, use cases, DTOs, and ports for
  external effects.
- `infrastructure` implements those ports with SQLAlchemy, Redis, Cloudinary,
  JWT/Argon2, and SSE.
- `presentation` maps HTTP requests, authentication context, cookies, and
  Pydantic schemas to and from application use cases.

The dependency composition lives at the FastAPI edge, so business workflows can
be tested with fakes without starting FastAPI or connecting to external
services. The detailed current structure is documented in the
[backend README](learn_fastapi/README.md). The
[Clean Architecture roadmap](docs/clean-architecture-roadmap.md) records the
original migration strategy and design rationale.

The frontends remain framework-native clients of the backend:

- Next.js keeps App Router and Server Actions as presentation boundaries.
- Streamlit remains a thin dashboard/prototyping client.
- Neither frontend owns backend authorization or persistence rules.

## Tech stack

**Backend**

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [uv](https://docs.astral.sh/uv/)
- [SQLAlchemy](https://www.sqlalchemy.org/) and
  [Alembic](https://alembic.sqlalchemy.org/)
- PostgreSQL and Redis
- Cloudinary
- pytest, Ruff, and ty

**Frontends**

- Streamlit
- Next.js 16
- React, TypeScript, Tailwind CSS, and shadcn/ui
- Bun

**Deployment**

- Docker / Docker Compose
- Koyeb

## Repository structure

```text
FastAPI-Ecosystem-Lab/
|-- .agents/                         # Project-local agent skills and guidance
|-- docs/                            # Cross-cutting architecture documentation
|-- learn_fastapi/                   # FastAPI Clean Architecture backend
|   |-- alembic/                     # Database migrations
|   |-- src/
|   |   |-- auth/                    # domain/application/infrastructure/presentation
|   |   |-- users/                   # domain/application/infrastructure/presentation
|   |   |-- items/                   # domain/application/infrastructure/presentation
|   |   |-- shared/                  # Shared architectural boundaries
|   |   |-- cache/                   # Redis client
|   |   `-- sse/                     # SSE manager and presentation router
|   `-- tests/                       # Unit and versioned HTTP tests
|-- learn_nextjs/                    # Next.js web application
|-- learn_streamlit/                 # Streamlit dashboard
|-- .env.example                     # Environment template
|-- AGENTS.md                        # Repository agent instructions
|-- Dockerfile
|-- docker-compose.yaml
|-- pyproject.toml
`-- uv.lock
```

## Environment configuration

Copy [`.env.example`](.env.example) to `.env` and adjust the values for your
environment.

```env
DEBUG=True
ALLOWED_HOSTS=["localhost"]

SECRET_KEY=replace-with-a-secure-secret
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db

COOKIE_SECURE=false
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=None

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

LEARN_FASTAPI_API_URL=http://localhost:8000/api/v1
```

For local SQLite development:

```env
DATABASE_URL=sqlite+aiosqlite:///./learn_fastapi/test.db
```

Cloudinary credentials are required only for image upload/deletion operations.
The backend stores both the returned `secure_url` (`image_url`) and `public_id`
(`image_public_id`) so replaced assets can be removed safely.

API clients can target the stable `/api/v1` prefix. `/api/latest` is also
available when a client intentionally wants the newest versioned routes.

For Streamlit, start from
[`.streamlit/secrets.example.toml`](.streamlit/secrets.example.toml) and use:

```toml
LEARN_FASTAPI_API_URL = "http://localhost:8000/api/v1"
```

## Run locally

Install Python dependencies:

```bash
uv sync
```

Start Redis:

```bash
docker compose up -d redis
```

The PostgreSQL service in `docker-compose.yaml` is currently an opt-in,
commented example. Run PostgreSQL separately or enable that service and keep
its credentials aligned with `DATABASE_URL`.

### FastAPI backend

```bash
uv run run-api-server
```

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/api/docs>
- Stable v1 prefix: <http://localhost:8000/api/v1>
- Latest-version alias: <http://localhost:8000/api/latest>

### Next.js frontend

In a separate terminal:

```bash
cd learn_nextjs
bun install
bun run dev
```

The app is available at <http://localhost:3000>.

### Streamlit frontend

In another terminal:

```bash
uv run streamlit run learn_streamlit/src/app.py
```

The app is available at <http://localhost:8501>. If that port is busy:

```bash
uv run streamlit run learn_streamlit/src/app.py --server.port 8502
```

## Validation

Backend:

```bash
uv run ruff check learn_fastapi
uv run ruff format --check learn_fastapi
uv run ty check learn_fastapi
```

Run the backend tests with `DEBUG=True`. On PowerShell:

```powershell
$env:DEBUG = "True"
uv run pytest --config-file=pyproject.toml
```

On POSIX shells:

```bash
DEBUG=True uv run pytest --config-file=pyproject.toml
```

Next.js:

```bash
cd learn_nextjs
bun run check
bun run tsc
bun run test
```

## Documentation

### Backend

- [FastAPI backend guide](learn_fastapi/README.md)
- [Clean Architecture roadmap](docs/clean-architecture-roadmap.md)
- [Clean Architecture explanations](docs/clean-architecture-explanations.md)
- [ORM model notes](docs/orm-models.md)

### Frontends

- [Next.js frontend](learn_nextjs/README.md)
- [Streamlit frontend](learn_streamlit/)

## Notes

This repository intentionally keeps two frontend approaches:

- Streamlit optimizes for rapid Python dashboards and prototypes.
- Next.js provides the production web surface, typed UI, routing, and richer
  interaction patterns.

Both consume the same versioned FastAPI API. Backend use cases remain the
source of truth for authorization and business behavior.

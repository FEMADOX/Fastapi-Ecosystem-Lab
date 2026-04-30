# FastAPI Ecosystem Lab 🚀

A personal repository documenting my learning journey through the FastAPI ecosystem and modern Python web development.

🌐 API Deployed in the Koyeb platform:\
<https://fastapi-ecosystem-lab-api.koyeb.app/api/docs#>

## Table of Contents

- [FastAPI Ecosystem Lab 🚀](#fastapi-ecosystem-lab-)
  - [Table of Contents](#table-of-contents)
  - [🗺️ What's covered](#️-whats-covered)
  - [🛠️ Tech Stack](#️-tech-stack)
  - [📁 Structure](#-structure)
    - [Environment Configuration](#environment-configuration)
  - [🐳 Local Database](#-local-database)
  - [▶️ Run Apps](#️-run-apps)
    - [FastAPI Backend](#fastapi-backend)
    - [Streamlit Frontend (Data Dashboard)](#streamlit-frontend-data-dashboard)
    - [Next.js Frontend (Production Web App)](#nextjs-frontend-production-web-app)
    - [Running All Components](#running-all-components)
  - [📚 Modules \& Documentation](#-modules--documentation)
    - [Backend](#backend)
    - [Frontends](#frontends)
    - [Learning Guides (Spanish)](#learning-guides-spanish)
    - [Reference \& Community](#reference--community)
  - [📝 Notes](#-notes)
    - [Frontend Comparison](#frontend-comparison)

## 🗺️ What's covered

| Topic                                        | Status       |
|:---------------------------------------------|--------------|
| FastAPI — routing, dependencies, middleware  | ✅ Completed  |
| SQLAlchemy + PostgreSQL + Alembic            | ✅ Completed  |
| Streamlit — dashboards & data apps           | ✅ Completed  |
| Next.js — modern frontend framework          | ✅ Completed  |
| Authentication + Authorization — JWT, OAuth2 | ✅ Completed  |
| Testing — pytest, httpx                      | ✅ Completed  |
| Docker & deployment                          | ✅ Completed  |
| NextJS - Frontend implementation             | 🔁 In-Process |

## 🛠️ Tech Stack

**Backend:**

- **[FastAPI](https://fastapi.tiangolo.com/)** — modern Python web framework
- **[Pydantic v2](https://docs.pydantic.dev/)** — data validation
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM for Python
- **[Alembic](https://alembic.sqlalchemy.org/)** — database migrations
- **[Redis](https://redis.io/)** — in-memory data store (caching, sessions)
- **[PostgreSQL](https://www.postgresql.org/)** — relational database

**Frontends:**

- **[Streamlit](https://streamlit.io/)** — Python-based dashboards (rapid prototyping)
- **[Next.js 15](https://nextjs.org/)** — React framework (production web apps)
- **[TypeScript](https://www.typescriptlang.org/)** — type-safe JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** — utility-first styling

**Deployment:**

- **[Docker](https://www.docker.com/)** — containerization

## 📁 Structure

```text
Fastapi-Ecosystem-Lab/
├── learn_fastapi/                      # 🧪 FastAPI backend implementations (see learn_fastapi/README.md)
├── learn_streamlit/                    # 🎛️ Streamlit data dashboards & prototyping frontend
├── learn_nextjs/                       # ⚡ Next.js production-grade web frontend (see learn_nextjs/README.md)
├── .streamlit/                         # Streamlit config and secrets template
├── .env.example                        # Example environment variables file
├── .gitignore                          # Git ignore file
├── .gitmessage                         # Git commit message template
├── .pre-commit-config.yaml             # pre-commit hooks configuration
├── .python-version                     # Python version for pyenv
├── .AGENTS.md                          # AI agents documentation
├── FastAPI_Learning.code-workspace     # VSCode workspace file
├── Dockerfile                          # Container image for API app
├── docker-compose.yaml                 # Local orchestration for API and services
├── pyproject.toml                      # uv project configuration
├── README.md                           # This file
└── uv.lock                             # uv lock file (auto-generated)
```

### Environment Configuration

Alembic and the application use environment variables defined in `.env` (see `.env.example` for reference).

**Required backend environment variables (`.env`):**

```.env
ALLOWED_HOSTS=[""]         # Allowed host for CORS (defaults: localhost, 127.0.0.1, localhost:3000, 127.0.0.1:3000)
DEBUG=True                 # Set to False in production

# Auth
SECRET_KEY=your-secret-key-here
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db  # For PostgreSQL

# Docker Compose (Local Postgres Database)
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

**Streamlit frontend API configuration (`.streamlit/secrets.toml`):**

```toml
LEARN_FASTAPI_API_URL = "http://localhost:8000/api"
```

Use `.streamlit/secrets.example.toml` as your starting template.

**For SQLite (development):**

```bash
DATABASE_URL=sqlite+aiosqlite:///./learn_fastapi/test.db
```

**Note:** Alembic automatically reads `DATABASE_URL` from the environment. The `alembic.ini` file is only used as a
fallback.

## 🐳 Local Database

PostgreSQL can be started locally with Docker Compose
using [docker-compose.yaml](docker-compose.yaml).

```bash
docker compose up -d
```

## ▶️ Run Apps

### FastAPI Backend

```bash
uv run run-api-server
```

API will be available at `http://localhost:8000` with docs at `/api/docs#`

### Streamlit Frontend (Data Dashboard)

Run in a separate terminal:

```bash
uv run streamlit run learn_streamlit/src/app.py
```

App will be available at `http://localhost:8501`

If port `8501` is in use, specify another:

```bash
uv run streamlit run learn_streamlit/src/app.py --server.port 8502
```

### Next.js Frontend (Production Web App)

Run in another terminal:

```bash
cd learn_nextjs && pnpm dev
```

App will be available at `http://localhost:3000`

### Running All Components

Best practice: use 3 terminals

**Terminal 1 — Backend API:**

```bash
uv run run-api-server
```

**Terminal 2 — Next.js Web App:**

```bash
cd learn_nextjs && pnpm dev
```

**Terminal 3 — Streamlit Dashboard (Optional):**

```bash
streamlit run learn_streamlit/src/app.py
```

Then visit:

- **FastAPI Docs**: <http://localhost:8000/api/docs>
- **Streamlit**: <http://localhost:8501>
- **Next.js**: <http://localhost:3000>

## 📚 Modules & Documentation

### Backend

- **[learn_fastapi](learn_fastapi/README.md)** — Complete FastAPI guide with auth, CRUD, database migrations

### Frontends

- **[learn_streamlit](learn_streamlit/)** — Python-based dashboard UI using Streamlit
- **[learn_nextjs](learn_nextjs/README.md)** — TypeScript + React web framework for production apps

### Learning Guides (Spanish)

- [fastapi-notes.md](fastapi_notes/fastapi-notes.md) — Core concepts, routing, validation
- [fastapi-db.md](fastapi_notes/fastapi-db.md) — SQLAlchemy ORM, PostgreSQL, Alembic migrations
- [fastapi-extras.md](fastapi_notes/fastapi-extras.md) — CORS, environment variables, deployment

### Reference & Community

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)

## 📝 Notes

This is a learning repository for exploring the FastAPI ecosystem and modern Python web development.

### Frontend Comparison

**Streamlit** (`learn_streamlit/`)

- ✅ Rapid prototyping in Python
- ✅ Perfect for dashboards & data visualization
- ✅ Minimal frontend knowledge required
- ❌ Limited customization & routing

**Next.js** (`learn_nextjs/`)

- ✅ Production-ready web apps
- ✅ Full TypeScript type safety
- ✅ SEO-friendly (Server-Side Rendering)
- ✅ Advanced styling & customization
- ❌ Requires JavaScript/TypeScript knowledge

Both frontends consume the same FastAPI backend, demonstrating different approaches to UI development.

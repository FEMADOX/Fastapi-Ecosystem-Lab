# FastAPI Ecosystem Lab 🚀

A personal repository documenting my learning journey through the FastAPI ecosystem and modern Python web development.

🌐 API Deployed in the Koyeb platform:\
https://fastapi-ecosystem-lab-api.koyeb.app/api/docs#

## 🗺️ What's covered

| Topic                                        | Status      |
|:---------------------------------------------|-------------|
| FastAPI — routing, dependencies, middleware  | ✅ Completed |
| SQLAlchemy + PostgreSQL + Alembic            | ✅ Completed |
| Streamlit — dashboards & data apps           | ✅ Completed |
| Authentication + Authorization — JWT, OAuth2 | ✅ Completed |
| Testing — pytest, httpx                      | ✅ Completed |
| Docker & deployment                          | ✅ Completed |

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — modern Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM for Python
- **[PostgreSQL](https://www.postgresql.org/)** — relational database
- **[Streamlit](https://streamlit.io/)** — data apps & dashboards
- **[Pydantic v2](https://docs.pydantic.dev/)** — data validation
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager

## 📁 Structure

```text
Fastapi-Ecosystem-Lab/
├── learn_fastapi/                      # 🧪 Practical implementations (Read more details in learn_fastapi/README.md)
├── learn_streamlit/                    # 🎛️ Streamlit frontend/UI module
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

```bash
DEBUG=True  # Set to False in production

# Auth
SECRET_KEY=your-secret-key-here
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db  # For PostgreSQL
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

Run FastAPI backend:

```bash
uv run run-api-server
```

Run Streamlit frontend:

```bash
uv run streamlit run learn_streamlit/src/app.py
```

If port `8501` is already in use, run Streamlit on another port:

```bash
uv run streamlit run learn_streamlit/src/app.py --server.port 8502
```

## 📚 Resources

### Learning Guides (Spanish)

- [fastapi-notes.md](fastapi_notes/fastapi-notes.md) — Core concepts, routing, validation
- [fastapi-db.md](fastapi_notes/fastapi-db.md) — SQLAlchemy ORM, PostgreSQL, Alembic migrations
- [fastapi-extras.md](fastapi_notes/fastapi-extras.md) — CORS, environment variables, deployment

### Reference & Community

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)

## 📝 Notes

This is a learning repository. Code here prioritizes clarity over production-readiness.

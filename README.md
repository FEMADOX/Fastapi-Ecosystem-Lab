# FastAPI Ecosystem Lab 🚀

A personal repository documenting my learning journey through the FastAPI ecosystem and modern Python web development.

## 🗺️ What's covered

| Topic                                        | Status           |
|:---------------------------------------------|:----------------:|
| FastAPI — routing, dependencies, middleware  | ✅ Completed     |
| SQLAlchemy + PostgreSQL                      | ✅ Completed     |
| Streamlit — dashboards & data apps           | 📅 Planned       |
| Authentication — JWT, OAuth2                 | 📅 Planned       |
| Testing — pytest, httpx                      | ✅ Completed     |
| Docker & deployment                          | 📅 Planned       |

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
├── learn_fastapi/          # 🧪 Practical implementations (Read more details in learn_fastapi/README.md)
└── pyproject.toml          # uv project configuration
```

## 🐳 Local Database

PostgreSQL can be started locally with Docker Compose using [learn_fastapi/docker-compose.yaml](learn_fastapi/docker-compose.yaml).

```bash
cd learn_fastapi
docker compose up -d
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

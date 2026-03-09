# FastAPI Ecosystem Lab 🚀

A personal repository documenting my learning journey through the FastAPI ecosystem and modern Python web development.

## 🗺️ What's covered

| Topic                                        |   Status     |
|:---------------------------------------------|--------------|
| FastAPI — routing, dependencies, middleware  | ✅ Completed |
| SQLAlchemy + PostgreSQL                      | ✅ Completed |
| Streamlit — dashboards & data apps           | 📅 Planned   |
| Authentication — JWT, OAuth2                 | 🔁 Process   |
| Testing — pytest, httpx                      | ✅ Completed |
| Docker & deployment                          | 🔁 Process   |

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

## �️ Database Migrations (Django-style)

Script que simula `python manage.py makemigrations` de Django:

```powershell
# Detectar cambios automáticamente
.\makemigration.ps1
# Output: 0002_add_email_to_users.py

# Con mensaje personalizado
.\makemigration.ps1 -m "add user roles"
# Output: 0002_add_user_roles.py

# Aplicar migración
cd learn_fastapi
uv run alembic upgrade head
```

> 📖 **[Guía completa, troubleshooting y ejemplos →](MAKEMIGRATION.md)**

**Características:**

- ✅ Detección automática de cambios en modelos SQLAlchemy
- ✅ Nombres descriptivos auto-generados (no hashes aleatorios)
- ✅ Secuencia numérica estilo Django (0001, 0002, 0003...)
- ✅ Resumen visual de cambios detectados

**Ejemplos de nombres autogenerados:**

- `create_users` → Nueva tabla 'users'
- `add_email_to_users` → Campo 'email' añadido
- `drop_phone_from_users` → Campo eliminado
- `add_indexes` → Índices añadidos

## �📚 Resources

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

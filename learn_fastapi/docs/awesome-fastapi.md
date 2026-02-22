# Awesome FastAPI

> Source: <https://github.com/mjhea0/awesome-fastapi>  
> A curated list of awesome things related to FastAPI.

---

## Contents

- [Awesome FastAPI](#awesome-fastapi)
  - [Contents](#contents)
  - [Third-Party Extensions](#third-party-extensions)
    - [Admin](#admin)
    - [Auth](#auth)
    - [Databases](#databases)
      - [ORMs](#orms)
      - [Query Builders](#query-builders)
      - [ODMs (MongoDB)](#odms-mongodb)
    - [Dependency Injection](#dependency-injection)
    - [Developer Tools](#developer-tools)
    - [Email](#email)
    - [Utils](#utils)
  - [Resources](#resources)
    - [Official Resources](#official-resources)
    - [External Resources](#external-resources)
    - [Articles](#articles)
    - [Tutorials](#tutorials)
    - [Talks](#talks)
    - [Videos](#videos)
    - [Courses](#courses)
    - [Best Practices](#best-practices)
  - [Hosting](#hosting)
    - [PaaS](#paas)
    - [IaaS](#iaas)
    - [Serverless](#serverless)
  - [Projects](#projects)
    - [Boilerplate](#boilerplate)
    - [Docker Images](#docker-images)
    - [Open Source Projects](#open-source-projects)

---

## Third-Party Extensions

### Admin

- [FastAPI Admin](https://github.com/fastapi-admin/fastapi-admin) - Functional admin panel for CRUD operations. Currently only works with Tortoise ORM.
- [FastAPI Amis Admin](https://github.com/amisadmin/fastapi-amis-admin) - High-performance, extensible FastAPI admin framework.
- [Piccolo Admin](https://github.com/piccolo-orm/piccolo_admin) - Powerful and modern admin GUI using the Piccolo ORM.
- [SQLAlchemy Admin](https://github.com/aminalaee/sqladmin) - Admin Panel for FastAPI/Starlette that works with SQLAlchemy models.
- [Starlette Admin](https://github.com/jowilf/starlette-admin) - Admin framework for FastAPI/Starlette, supporting SQLAlchemy, SQLModel, MongoDB, and ODMantic.

### Auth

- [AuthX](https://github.com/yezz123/AuthX) - Customizable Authentication and Oauth2 management for FastAPI.
- [FastAPI Auth](https://github.com/dmontagu/fastapi-auth) - Pluggable auth with OAuth2 Password Flow, JWT access and refresh tokens.
- [FastAPI Azure Auth](https://github.com/Intility/fastapi-azure-auth) - Azure AD authentication with single and multi tenant support.
- [FastAPI Cloud Auth](https://github.com/tokusumi/fastapi-cloudauth) - Simple integration with AWS Cognito, Auth0, Firebase Authentication.
- [FastAPI JWT Auth](https://github.com/IndominusByte/fastapi-jwt-auth) - JWT auth (based on Flask-JWT-Extended).
- [FastAPI Permissions](https://github.com/holgi/fastapi-permissions) - Row-level permissions.
- [FastAPI Simple Security](https://github.com/mrtolkien/fastapi_simple_security) - Out-of-the-box API key security manageable through path operations.
- [FastAPI Users](https://github.com/fastapi-users/fastapi-users) - Account management, authentication, authorization.

### Databases

#### ORMs

- [FastAPI SQLAlchemy](https://github.com/mfreeborn/fastapi-sqlalchemy) - Simple integration between FastAPI and SQLAlchemy.
- [Fastapi-SQLA](https://github.com/dialoguemd/fastapi-sqla) - SQLAlchemy extension with pagination, asyncio, and pytest support.
- [GINO](https://github.com/python-gino/gino) - Lightweight async ORM built on top of SQLAlchemy core for asyncio.
- [ormar](https://collerek.github.io/ormar/) - Async ORM with Pydantic validation. One set of models for DB + API. Alembic migrations included.
- [Piccolo](https://github.com/piccolo-orm/piccolo) - Async ORM and query builder supporting Postgres and SQLite, with migrations and security.
- [Prisma Client Python](https://github.com/RobertCraigie/prisma-client-py) - Auto-generated, type-safe ORM powered by Pydantic. Supports SQLite, PostgreSQL, MySQL, MongoDB, and more.
- [SQLModel](https://sqlmodel.tiangolo.com/) - Powered by Pydantic and SQLAlchemy. Interact with SQL databases using Python objects. *(By the FastAPI creator)*
- [Tortoise ORM](https://tortoise.github.io) - Easy-to-use asyncio ORM inspired by Django.

#### Query Builders

- [Databases](https://github.com/encode/databases) - Async SQL query builder on top of SQLAlchemy Core.

#### ODMs (MongoDB)

- [Beanie](https://github.com/BeanieODM/beanie) - Async Python ODM for MongoDB, based on Motor and Pydantic. Supports data and schema migrations.
- [Motor](https://motor.readthedocs.io/) - Async Python driver for MongoDB.
- [ODMantic](https://art049.github.io/odmantic/) - AsyncIO MongoDB ODM integrated with Pydantic.
- [PynamoDB](https://github.com/pynamodb/PynamoDB) - Pythonic interface to Amazon's DynamoDB.

### Dependency Injection

- [Wireup](https://github.com/maldoinc/wireup) - Inject dependencies with zero runtime overhead; share across web, CLI, and other interfaces.

### Developer Tools

- [FastAPI Code Generator](https://github.com/koxudaxi/fastapi-code-generator) - Create a FastAPI app from an OpenAPI file (schema-driven development).
- [FastAPI MVC](https://github.com/fastapi-mvc/fastapi-mvc) - Developer productivity tool for high-quality, production-ready FastAPI APIs.
- [FastAPI Profiler](https://github.com/sunhailin-Leo/fastapi_profiler) - Middleware using pyinstrument to check service performance.
- [FastAPI Versioning](https://github.com/DeanWay/fastapi-versioning) - API versioning.
- [Manage FastAPI](https://github.com/ycd/manage-fastapi) - CLI tool for generating and managing FastAPI projects.

### Email

- [FastAPI Mail](https://github.com/sabuhish/fastapi-mail) - Lightweight mail system for sending emails and attachments (individual and bulk).

### Utils

- [Apitally](https://github.com/apitally/apitally-py) - API analytics, monitoring, and request logging.
- [ASGI Correlation ID](https://github.com/snok/asgi-correlation-id) - Request ID logging middleware.
- [FastAPI Cache](https://github.com/long2ice/fastapi-cache) - Cache FastAPI responses and function results. Supports Redis, Memcached, DynamoDB, and in-memory backends.
- [FastAPI Events](https://github.com/melvinkcx/fastapi-events) - Async event dispatching/handling library.
- [FastAPI Injectable](https://github.com/JasperSui/fastapi-injectable) - Use FastAPI's dependency injection outside route handlers (CLI tools, background tasks, workers).
- [FastAPI Limiter](https://github.com/long2ice/fastapi-limiter) - Request rate limiter.
- [FastAPI Pagination](https://github.com/uriyyo/fastapi-pagination) - Pagination for FastAPI.
- [FastAPI SocketIO](https://github.com/pyropy/fastapi-socketio) - Easy integration for FastAPI and SocketIO.
- [FastAPI Utilities](https://github.com/fastapiutils/fastapi-utils) - Class-based views, response inferring router, periodic tasks, timing middleware, SQLAlchemy session.
- [Prometheus FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) - Configurable Prometheus Instrumentator.
- [SlowApi](https://github.com/laurents/slowapi) - Rate limiter (based on Flask-Limiter).
- [Starlette Context](https://github.com/tomwojcik/starlette-context) - Store and access request data anywhere in your project (useful for logging).
- [Strawberry GraphQL](https://github.com/strawberry-graphql/strawberry) - Python GraphQL library based on dataclasses.

---

## Resources

### Official Resources

- [Documentation](https://fastapi.tiangolo.com/) — Comprehensive official docs.
- [Tutorial](https://fastapi.tiangolo.com/tutorial/) — Official step-by-step tutorial.
- [Source Code](https://github.com/fastapi/fastapi) — Hosted on GitHub.
- [Discord](https://discord.com/invite/VQjSZaeJmf) — Chat with other FastAPI users.

### External Resources

- [TestDriven.io FastAPI](https://testdriven.io/blog/topics/fastapi/) - Articles on building and testing production-ready RESTful APIs, ML model serving, and more.

### Articles

- [FastAPI has Ruined Flask Forever for Me](https://medium.com/data-science/fastapi-has-ruined-flask-forever-for-me-73916127da)
- [Why we switched from Flask to FastAPI for production machine learning](https://medium.com/%40calebkaiser/why-we-switched-from-flask-to-fastapi-for-production-machine-learning-765aab9b3679)

### Tutorials

- [Async SQLAlchemy with FastAPI](https://stribny.name/posts/fastapi-asyncalchemy/)
- [Developing and Testing an Asynchronous API with FastAPI and Pytest](https://testdriven.io/blog/fastapi-crud/)
- [FastAPI for Flask Users](https://amitness.com/posts/fastapi-vs-flask) - Side-by-side code comparison.
- [Implementing FastAPI Services – Abstraction and Separation of Concerns](https://camillovisini.com/coding/abstracting-fastapi-services)
- [Introducing FARM Stack - FastAPI, React, and MongoDB](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/integrations/fastapi-integration/)
- [Multitenancy with FastAPI, SQLAlchemy and PostgreSQL](https://mergeboard.com/blog/6-multitenancy-fastapi-sqlalchemy-postgresql/)
- [Real-time data streaming using FastAPI and WebSockets](https://stribny.name/posts/real-time-data-streaming-using-fastapi-and-websockets/)
- [Running FastAPI applications in production](https://stribny.name/posts/fastapi-production/) - Gunicorn + systemd.
- [Using Hypothesis and Schemathesis to Test FastAPI](https://testdriven.io/blog/fastapi-hypothesis/)

### Talks

- [PyConBY 2020: Serve ML models easily with FastAPI](https://www.youtube.com/watch?v=z9K5pwb0rt8)
- [PyCon UK 2019: FastAPI from the ground up](https://www.youtube.com/watch?v=3DLwPcrE5mA)

### Videos

- [Building a Stock Screener with FastAPI](https://www.youtube.com/watch?v=5GorMC2lPpk) - Pydantic models, dependency injection, background tasks, SQLAlchemy.
- [FastAPI vs. Django vs. Flask](https://www.youtube.com/watch?v=9YBAOYQOzWs)

### Courses

- [Test-Driven Development with FastAPI and Docker](https://testdriven.io/courses/tdd-fastapi/) - Build, test, and deploy a text summarization microservice.
- [Modern APIs with FastAPI and Python](https://training.talkpython.fm/courses/modern-fastapi-apis)
- [Full Web Apps with FastAPI Course](https://training.talkpython.fm/courses/full-html-web-applications-with-fastapi)
- [The Definitive Guide to Celery and FastAPI](https://testdriven.io/courses/fastapi-celery/)

### Best Practices

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) — See `fastapi-best-practices.md` in this docs folder.

---

## Hosting

### PaaS

- [Fly.io](https://fly.io) — [tutorial](https://fly.io/docs/python/frameworks/fastapi/)
- [Heroku](https://www.heroku.com/) — [Step-by-step tutorial](https://tutlinks.com/create-and-deploy-fastapi-app-to-heroku/)
- [Google App Engine](https://cloud.google.com/appengine)
- [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)
- [Microsoft Azure App Service](https://azure.microsoft.com/en-us/products/app-service/)

### IaaS

- [AWS EC2](https://aws.amazon.com/ec2/)
- [Digital Ocean](https://www.digitalocean.com/)
- [Google Compute Engine](https://cloud.google.com/compute)
- [Linode](https://www.linode.com/)

### Serverless

- [Mangum](https://mangum.io/) - Adapter for running ASGI apps with AWS Lambda and API Gateway.
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Google Cloud Run](https://cloud.google.com/run)
- [Vercel](https://vercel.com/)

---

## Projects

### Boilerplate

- [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) - FastAPI + React + SQLModel + PostgreSQL + Docker + GitHub Actions. *(By the FastAPI creator)*
- [FastAPI template](https://github.com/s3rius/FastAPI-template) - Flexible generator. Supports SQLAlchemy, multiple DBs, CI/CD, Docker, Kubernetes.
- [fastapi-alembic-sqlmodel-async](https://github.com/jonra1993/fastapi-alembic-sqlmodel-async) - FastAPI + Alembic + async SQLModel.
- [FastAPI Nano](https://github.com/rednafi/fastapi-nano) - Simple FastAPI template with factory pattern architecture.
- [cookiecutter-fastapi](https://github.com/arthurhenrique/cookiecutter-fastapi) - Template using Poetry, Azure Pipelines and pytest.

### Docker Images

- [uvicorn-gunicorn-fastapi-docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) - Docker image with Uvicorn managed by Gunicorn, with performance auto-tuning. *(By the FastAPI creator)*
- [inboard](https://github.com/br3ndonland/inboard) - Docker images to power FastAPI apps.

### Open Source Projects

- [Dispatch](https://github.com/Netflix/dispatch) - Netflix's incident management system built with FastAPI. *(Inspiration for the domain-based project structure)*
- [Awesome FastAPI Projects](https://github.com/Kludex/awesome-fastapi-projects) - Organized list of projects using FastAPI.
- [RealWorld Example App (postgres)](https://github.com/nsidnev/fastapi-realworld-example-app) - Full Conduit/RealWorld implementation.
- [FastAPI with Celery, RabbitMQ, and Redis](https://github.com/GregaVrbancic/fastapi-celery) - Task queue minimal example.
- [OPAL](https://github.com/authorizon/opal) - Real-time authorization updates. Built with FastAPI, Typer, and WebSocket pub/sub.
- [Polar](https://github.com/polarsource/polar) - Funding and monetization platform. FastAPI + SQLAlchemy + Alembic + Arq.

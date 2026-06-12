# PR Title

Use one of the repository project prefixes:

- `[learn_fastapi] <description>`
- `[learn_nextjs] <description>`
- `[learn_streamlit] <description>`
- `[repo] <description>` for root-level, CI, tooling, or shared documentation changes

## Summary

-

## Scope

- [ ] `learn_fastapi` - FastAPI backend/API
- [ ] `learn_nextjs` - Next.js frontend
- [ ] `learn_streamlit` - Streamlit dashboard/prototype
- [ ] Root/tooling/docs - CI, Docker, dependency management, README, shared config

## Type of Change

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Tests
- [ ] Documentation
- [ ] CI/build/tooling
- [ ] Dependency update

## Changes

-

## Behavior and Risk Notes

- [ ] API contract changed
- [ ] Database schema or Alembic migration changed
- [ ] Authentication, authorization, cookies, or security behavior changed
- [ ] Environment variables or secrets configuration changed
- [ ] External service integration changed
- [ ] Media/file upload behavior changed
- [ ] Frontend routing, caching, forms, or protected pages changed
- [ ] No high-risk behavior changed

Notes:

-

## Validation

Mark only the checks that apply.

### FastAPI

- [ ] `uv run pytest --config-file=pyproject.toml`
- [ ] `uv run ruff check learn_fastapi`
- [ ] `uv run ruff format --check learn_fastapi`
- [ ] `uv run ty check learn_fastapi`
- [ ] Alembic migration reviewed, if applicable
- [ ] External services are mocked or safely isolated in tests, if applicable

### Next.js

- [ ] `bun run test`
- [ ] `bun run check`
- [ ] `bun run tsc`
- [ ] `bun run build`
- [ ] Relevant UI flow checked manually, if applicable

### Streamlit

- [ ] App starts locally with `uv run streamlit run learn_streamlit/src/app.py`
- [ ] Relevant dashboard/data flow checked manually, if applicable

### Repository

- [ ] `.env.example` or related docs updated for any configuration changes
- [ ] No real secrets, credentials, tokens, or private keys were committed
- [ ] Large files and generated artifacts were not committed unintentionally
- [ ] Documentation updated where behavior changed

## Screenshots or Evidence

Add screenshots, API responses, logs, or test output when they help reviewers.

-

## Reviewer Notes

-

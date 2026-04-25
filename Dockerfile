# Use an official Python runtime as a parent image

FROM python:3.14.3-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY learn_fastapi/ ./learn_fastapi/
COPY learn_streamlit/ ./learn_streamlit/

RUN uv sync --frozen --no-dev --no-cache

#EXPOSE 8000

ENTRYPOINT [ ".venv/bin/uvicorn" ]
CMD ["learn_fastapi.src.main:app", "--host", "0.0.0.0", "--port", "8000"]

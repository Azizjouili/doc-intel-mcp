FROM python:3.12-slim AS base

# uv from PyPI (avoids the flaky ghcr.io pull)
RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=300 \
    UV_CONCURRENT_DOWNLOADS=2

WORKDIR /app

# Dependency manifests first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Then the source
COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD [".venv/bin/uvicorn", "doc_intel_mcp.api:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12-slim AS base

RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=300 \
    HF_HOME=/app/.hfcache

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY scripts ./scripts
COPY README.md ./
RUN uv sync --frozen --no-dev

# Build the demo index (downloads a few papers + embeds them) at build time.
RUN uv run python scripts/prepare_demo.py

EXPOSE 8000

CMD [".venv/bin/uvicorn", "doc_intel_mcp.api:app", "--host", "0.0.0.0", "--port", "8000"]
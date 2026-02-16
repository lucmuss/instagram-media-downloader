FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:/root/.cargo/bin:$PATH"

COPY pyproject.toml uv.lock /app/

RUN uv venv && uv sync --frozen --no-dev --no-install-project

COPY . /app

RUN uv sync --frozen --no-dev
RUN chmod +x /app/docker/entrypoint.sh /app/scripts/bootstrap.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY ai_agents/dependabot_agent/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Final stage
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /ai_agents

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser ./dependabot_agent ./

USER appuser

ENTRYPOINT ["python", "/ai_agents/main.py"]
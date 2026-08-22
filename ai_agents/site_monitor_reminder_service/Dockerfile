`# Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

# copy ai agent specific libraries
COPY ai_agents/site_monitor_data_ingestion/requirements.txt ./requirements.txt
COPY ai_agents/pyproject.toml ./ai_agents/pyproject.toml
COPY ai_agents/agent_library/ ./ai_agents/agent_library/

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        -r /build/requirements.txt && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build/ai_agents


# Final stage
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /agents

COPY --from=builder /build/wheels /wheels

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser


COPY --chown=appuser:appuser ./ai_agents/site_monitor_data_ingestion ./site_monitor_data_ingestion
COPY --chown=appuser:appuser ./ai_agents/site_monitor_reminder_service ./


USER appuser

ENTRYPOINT ["python", "/agents/main.py"]
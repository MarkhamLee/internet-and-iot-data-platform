# Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Copy dependency manifests first for better Docker layer caching.
COPY ai_agents/site_monitor_data_ingestion/requirements.txt \
     ./requirements.txt

# Copy the shared library project so it can be built into a wheel.
COPY platform_utils/ ./platform_utils/

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        -r requirements.txt && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build/platform_utils


# Runtime image.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

    
COPY --chown=appuser:appuser ai_agents/agent_library/ \
    /app/agent_library/

# Application source.
COPY --chown=appuser:appuser ai_agents/site_monitor_data_ingestion/ \
    /app/site_monitor_data_ingestion/

WORKDIR /app/site_monitor_data_ingestion

USER appuser

ENTRYPOINT ["python", "main.py"]
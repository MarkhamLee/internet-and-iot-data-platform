# Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY site_monitor_data_ingestion/requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        -r /build/requirements.txt && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build


# Final stage
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

    
WORKDIR /agents

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser ./agent_library ./agent_library
COPY --chown=appuser:appuser ./site_monitor_data_ingestion ./site_monitor_data_ingestion
COPY --chown=appuser:appuser ./site_monitor_reminder_service ./

USER appuser

ENTRYPOINT ["python", "/agents/main.py"]
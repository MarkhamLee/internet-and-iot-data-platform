# Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

# copy app specific libraries
COPY ai_agents/dependabot_data_ingestion/requirements.txt ./requirements.txt
COPY ai_agents/pyproject.toml ./ai_agents/pyproject.toml
COPY ai_agents/agent_library/ ./ai_agents/agent_library/


# install packages and create build wheels
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        -r /build/requirements.txt && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build/ai_agents


# Final stage
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /etl

COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser ./ai_agents/dependabot_data_ingestion ./

USER appuser

ENTRYPOINT ["python", "/etl/main.py"]
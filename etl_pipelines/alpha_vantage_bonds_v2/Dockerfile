# BUILD STAGE
FROM python:3.11.9-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY /alpha_vantage_library/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# FINAL STAGE
FROM python:3.11.9-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /etl

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser


COPY --chown=appuser:appuser  ./etl_library ./etl_library
COPY --chown=appuser:appuser  ./alpha_vantage_library ./alpha_vantage_library
COPY --chown=appuser:appuser  ./alpha_vantage_bonds_v2 ./

USER appuser

ENTRYPOINT ["python", "/etl/main.py"]
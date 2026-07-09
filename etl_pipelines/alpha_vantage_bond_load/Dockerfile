FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /app

COPY ./alpha_vantage_library/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt



FROM python:3.11.9-slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser ./etl_library ./etl_library
COPY --chown=appuser:appuser ./alpha_vantage_library ./alpha_vantage_library

WORKDIR /etl

COPY --chown=appuser:appuser ./alpha_vantage_bond_load ./

USER appuser

ENTRYPOINT ["python3", "/etl/main.py"]
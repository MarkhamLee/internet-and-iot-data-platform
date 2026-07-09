# Temp Stage 

FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libpq-dev gcc  g++ libblas-dev liblapack-dev build-essential

COPY /asana/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Final Stage
FROM python:3.11.9-slim-bookworm

RUN apt-get update -y && apt-get install -y libpq5

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser


COPY --chown=appuser:appuser ./etl_library ./etl_library

WORKDIR /etl

COPY --chown=appuser:appuser ./asana ./

USER appuser

ENTRYPOINT ["python3", "/etl/main.py"]
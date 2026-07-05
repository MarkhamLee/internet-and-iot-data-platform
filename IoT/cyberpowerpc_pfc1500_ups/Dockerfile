# temp stage
FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev

COPY /cyberpowerpc_pfc1500_ups/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# final stage - 
FROM python:3.11.9-slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

RUN apt-get update -y && apt-get install -y nut-client

COPY --chown=appuser:appuser ./iot_libraries ./iot_libraries

WORKDIR /hw_telemetry

COPY --chown=appuser:appuser ./cyberpowerpc_pfc1500_ups ./

USER appuser

ENTRYPOINT ["python3", "/hw_telemetry/main.py"]
FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /app

COPY ./kasa_smart_plug/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.11.9-slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser  ./iot_libraries ./iot_libraries 

WORKDIR /iot_sensors

COPY --chown=appuser:appuser  ./kasa_smart_plug ./

USER appuser

ENTRYPOINT ["python3", "/iot_sensors/main.py"]
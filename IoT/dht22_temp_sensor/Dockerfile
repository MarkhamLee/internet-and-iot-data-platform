FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update -y && apt-get install -y gcc python3-dev libgpiod2

# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/



COPY IoT/dht22_temp_sensor/requirements.txt ./requirements.txt 
COPY IoT/pyproject.toml ./IoT/pyproject.toml
COPY IoT/iot_libraries ./IoT/iot_libraries


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
        /build/IoT 


FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y gcc python3-dev libgpiod2


COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser


COPY --chown=appuser:appuser ./IoT/iot_libraries ./IoT/iot_libraries 

WORKDIR /dht22_temp_sensor

COPY --chown=appuser:appuser ./IoT/dht22_temp_sensor ./

USER appuser

ENTRYPOINT ["python3", "/dht22_temp_sensor/main.py"]
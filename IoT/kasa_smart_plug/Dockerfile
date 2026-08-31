FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /build

COPY ./kasa_smart_plug/requirements.txt .


# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

# copy app specific libraries 
COPY IoT/kasa_smart_plug/requirements.txt ./requirements.txt
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


FROM python:3.11.9-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser


WORKDIR /iot_sensors

COPY --chown=appuser:appuser  ./IoT/kasa_smart_plug ./

USER appuser

ENTRYPOINT ["python3", "/iot_sensors/main.py"]
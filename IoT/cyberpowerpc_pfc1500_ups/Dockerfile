# temp stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update -y && apt-get install -y gcc python3-dev

# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

# copy app specific libraries 
COPY Iot/cyberpowerpc_pfc1500_ups/requirements.txt ./requirements.txt
# COPY IoT/pyproject.toml ./IoT/pyproject.toml


# install packages and create build wheels
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        -r /build/requirements.txt && \
    python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /build/wheels \
        /build 


# final stage - 
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

# Install's the nut-client into the container's Linux environment
RUN apt-get update -y && apt-get install -y nut-client


COPY --chown=appuser:appuser ./iot_libraries ./iot_libraries

WORKDIR /hw_telemetry

COPY --chown=appuser:appuser ./cyberpowerpc_pfc1500_ups ./

USER appuser

ENTRYPOINT ["python3", "/hw_telemetry/main.py"]
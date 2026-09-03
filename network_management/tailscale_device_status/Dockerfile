# Temp Stage 
FROM python:slim-bookworm AS builder

WORKDIR /build

# copy platform level libraries 
COPY pyproject.toml ./pyproject.toml
COPY platform_utils/ ./platform_utils/

# copy app specific libraries 
COPY /network_management/tailscale_device_status/requirements.txt . 

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
        /build/network_management

# Final Stage 
FROM python:slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /build/wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser ./network_management/network_monitoring_libraries ./network_monitoring_libraries
COPY --chown=appuser:appuser ./network_management/tailscale_library ./tailscale_library

WORKDIR /tailscale_monitoring

COPY --chown=appuser:appuser ./tailscale_device_status ./

USER appuser

ENTRYPOINT ["python3", "/tailscale_monitoring/main.py"]
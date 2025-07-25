FROM python:alpine as builder

WORKDIR /app

COPY ./tailscale_device_status/requirements.txt . 

RUN pip install -r requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Stage 
FROM python:alpine

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./network_monitoring_libraries ./network_monitoring_libraries
COPY ./tailscale_library ./tailscale_library

WORKDIR /tailscale_monitoring

COPY ./tailscale_device_status ./

ENTRYPOINT ["python3", "/tailscale_monitoring/main.py"]
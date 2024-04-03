FROM python:3.12.2-slim as builder

WORKDIR /app

COPY ./kasa_smart_plug/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.12.2-slim

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./iot_libraries ./iot_libraries 

WORKDIR /iot_sensors

COPY COPY kasa_smart_plug ./

ENTRYPOINT ["python3", "/iot_sensors/main.py"]
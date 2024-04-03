# Using a multi-stage build shaves ~100MB off the image size

FROM python:3.12.2-slim as builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libgpiod2

COPY ./dht22_temp_sensor/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.12.2-slim

RUN apt-get update -y && apt-get install -y libgpiod2

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./iot_libraries ./iot_libraries 

WORKDIR /iot_sensors

COPY ./dht22_temp_sensor ./

ENTRYPOINT ["python3", "/iot_sensors/main.py"]
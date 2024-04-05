FROM python:alpine as builder

WORKDIR /app

COPY ./sds011_air_quality_sensor/requirements.txt . 

RUN pip install -r requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Stage 
FROM python:alpine

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./iot_libraries ./iot_libraries

WORKDIR /iot_sensors

COPY ./sds011_air_quality_sensor ./

ENTRYPOINT ["python3", "/iot_sensors/main.py"]
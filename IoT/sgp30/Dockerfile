FROM python:3.13.3-slim AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libgpiod2

COPY ./sgp30/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.13.3-slim

RUN apt-get update -y && apt-get install -y libgpiod2

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*
RUN python3 -m pip install pimoroni-sgp30

COPY ./iot_libraries ./iot_libraries 

WORKDIR /spg30

COPY ./sgp30 ./

ENTRYPOINT ["python3", "/sgp30/main.py"]
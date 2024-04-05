FROM python:slim-bookworm as builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc  python3-dev

COPY /orangepi_3b/requirements.txt  .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

COPY ./hw_library ./hw_library

RUN pip install --no-cache /wheels/*

WORKDIR /hw_telemetry

COPY ./orangepi_3b ./

ENTRYPOINT ["python3", "/hw_telemetry/main.py"] 
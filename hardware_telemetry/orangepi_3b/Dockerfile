FROM python:slim-bookworm as builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc  python3-dev

COPY /orangepi_3b/requirements.txt  .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

WORKDIR /hw_telemetry

COPY main.py orangepi3b_data.py  /

ENTRYPOINT ["python3", "/hw_telemetry/main.py"] 
# Temp Stage 

FROM python:slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libpq-dev gcc  g++ libblas-dev liblapack-dev build-essential

RUN pip install --upgrade pip setuptools wheel

COPY /asana/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Stage
FROM python:slim-bookworm

RUN apt-get update -y && apt-get install -y libpq5

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./etl_library ./etl_library

WORKDIR /etl

COPY ./asana ./

ENTRYPOINT ["python3", "/etl/main.py"]
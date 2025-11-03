FROM python:alpine as builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libpq-dev

RUN pip install --upgrade pip setuptools wheel

COPY /yield_curve_library/requirements.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt



# Final Stage 
FROM python:alpine

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./etl_library ./etl_library
COPY ./yield_curve_library ./yield_curve_library

WORKDIR /etl

COPY ./yield_curve_daily ./

ENTRYPOINT ["python3", "/etl/main.py"]
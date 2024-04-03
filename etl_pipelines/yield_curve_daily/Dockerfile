FROM python:alpine as build

WORKDIR /app

COPY /yield_curve_library/requirements.txt .

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
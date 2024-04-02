# Temp Stage 

FROM python:alpine as builder

WORKDIR /app

COPY /asana/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Stage
FROM python:alpine

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./etl_library ./etl_library

WORKDIR /etl

COPY ./asana ./

ENTRYPOINT ["python3", "/etl/main.py"]
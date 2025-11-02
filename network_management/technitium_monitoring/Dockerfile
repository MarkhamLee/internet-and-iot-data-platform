# temp stage
FROM python:slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc  python3-dev

COPY /technitium_monitoring/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# final stage - 
FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./network_monitoring_libraries ./network_monitoring_libraries

WORKDIR /technitium_monitoring

COPY ./technitium_monitoring ./

ENTRYPOINT ["python3", "/technitium_monitoring/main.py"]
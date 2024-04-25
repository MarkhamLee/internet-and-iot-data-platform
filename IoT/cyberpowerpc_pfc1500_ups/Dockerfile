# temp stage
FROM python:slim-bookworm as builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev

COPY /cyberpowerpc_pfc1500lcda_ups/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# final stage - 
FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

RUN apt-get update -y && apt-get install -y nut-client

COPY ./hw_monitoring_libraries ./hw_monitoring_libraries

WORKDIR /hw_telemetry

COPY ./cyberpowerpc_pfc1500lcda_ups ./

ENTRYPOINT ["python3", "/hw_telemetry/main.py"]
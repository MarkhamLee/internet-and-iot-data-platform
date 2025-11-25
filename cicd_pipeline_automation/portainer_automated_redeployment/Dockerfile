FROM python:slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev g++ libblas-dev liblapack-dev build-essential

RUN pip install --upgrade pip setuptools wheel

COPY /portainer_automated_redeployment/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# final stage - 
FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./cicd_common ./cicd_common
COPY ./docker_common ./docker_common
COPY ./portainer_common ./portainer_common


WORKDIR /automation

COPY ./portainer_automated_redeployment ./

ENTRYPOINT ["python3", "/automation/main.py"]
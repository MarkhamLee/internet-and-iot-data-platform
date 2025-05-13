# temp stage
FROM python:slim-bookworm AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev

COPY /plantower_s5003_airquality/requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# final stage - 
FROM python:slim-bookworm

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./iot_libraries ./iot_libraries

WORKDIR /plantower_s5003_airquality

COPY ./plantower_s5003_airquality ./

ENTRYPOINT ["python3", "/plantower_s5003_airquality/main.py"]
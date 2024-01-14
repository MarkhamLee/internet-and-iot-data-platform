FROM python:3.11-slim as build

COPY ./etl_library ./etl_library
COPY ./openweather_library ./openweather_library

WORKDIR /etl

COPY ./openweather_current ./

RUN pip install -r /etl/requirements.txt

CMD python3 /etl/main.py
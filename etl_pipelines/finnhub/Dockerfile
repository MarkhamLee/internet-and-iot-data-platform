FROM python:alpine as build

COPY ./etl_library ./etl_library
COPY ./finnhub_libraries ./finnhub_libraries

WORKDIR /etl

COPY ./finnhub ./

RUN pip install -r /etl/requirements.txt

CMD python3 /etl/main.py
FROM python:alpine as build

COPY ./etl_library ./etl_library

WORKDIR /etl

COPY ./asana ./

RUN pip install -r /etl/requirements.txt

CMD python3 /etl/main.py
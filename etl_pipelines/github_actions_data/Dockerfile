FROM python:3.12.2-slim as build

COPY ./etl_library ./etl_library

WORKDIR /etl

COPY ./github_actions_data ./

RUN pip install -r /etl/requirements.txt

CMD python3 /etl/main.py
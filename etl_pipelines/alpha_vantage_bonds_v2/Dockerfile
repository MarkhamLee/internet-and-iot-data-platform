FROM python:3.11-slim as build

COPY ./etl_library ./etl_library
COPY ./alpha_vantage_library ./alpha_vantage_library

WORKDIR /etl

COPY ./alpha_vantage_bonds_v2 ./

RUN pip install -r /alpha_vantage_library/requirements.txt

CMD python3 /etl/main.py
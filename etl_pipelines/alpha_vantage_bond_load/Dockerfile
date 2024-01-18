FROM python:3.11-slim as build

COPY ./etl_library ./etl_library
COPY ./alpha_vantage_library ./alpha_vantage_library

WORKDIR /etl

COPY ./alpha_vantage_bond_load ./

RUN pip install -r /etl/requirements.txt

CMD python3 /etl/main.py
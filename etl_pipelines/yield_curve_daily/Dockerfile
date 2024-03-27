FROM python:alpine as build

COPY ./etl_library ./etl_library
COPY ./yield_curve_library ./yield_curve_library

WORKDIR /etl

COPY ./yield_curve_daily ./

RUN pip install -r /yield_curve_library/requirements.txt

CMD python3 /etl/main.py
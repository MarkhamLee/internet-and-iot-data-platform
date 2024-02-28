FROM python:alpine as build

COPY ./etl_library ./etl_library
COPY ./openweather_library ./openweather_library

WORKDIR /

# creating the file to write XComs to
RUN mkdir -p airflow/xcom
RUN echo "" > airflow/xcom/return.json

COPY ./openweather_current_singular ./

RUN pip install -r /openweather_library/requirements.txt

CMD python3 main.py
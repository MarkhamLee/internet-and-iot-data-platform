FROM python:3.12.2-slim as build

RUN apt-get update -y && apt-get install -y gcc python3-dev libgpiod2

COPY ./iot_libraries ./iot_libraries 

WORKDIR /iot_sensors

COPY ./dht22_temp_sensor ./

RUN pip install -r /iot_sensors/requirements.txt

CMD python3 /iot_sensors/main.py
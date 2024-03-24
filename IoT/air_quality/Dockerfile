FROM python:alpine as build

COPY ./iot_libraries ./iot_libraries 

WORKDIR /iot_sensors

COPY ./air_quality ./

RUN pip install -r /iot_sensors/requirements.txt

CMD python3 iot_sensors/main.py
FROM python:3.11-slim as build

COPY requirements.txt air_quality.py main.py / 

RUN pip install -r /requirements.txt

CMD python3 main.py
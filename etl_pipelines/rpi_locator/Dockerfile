FROM python:3.11-slim as build

COPY files ./

RUN pip install -r /requirements.txt

CMD python3 main.py
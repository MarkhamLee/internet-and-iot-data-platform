FROM python:3.11-slim as build

COPY requirements.txt main.py asana_utilities.py postgres_client.py /

RUN pip install -r /requirements.txt

CMD python3 main.py
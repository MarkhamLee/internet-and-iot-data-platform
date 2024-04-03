FROM python:3.12.2-slim as builder

COPY requirements.txt main.py logging_util.py influx_client.py /

RUN pip install -r /requirements.txt

CMD python3 main.py
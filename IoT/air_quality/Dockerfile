FROM python:3.11-slim as build

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY air_quality.py .
COPY main.py .

CMD python3 main.py 
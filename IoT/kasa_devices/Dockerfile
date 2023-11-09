FROM python:3.11-slim as build

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY main.py .
COPY kasa_utilities.py .

CMD python3 main.py
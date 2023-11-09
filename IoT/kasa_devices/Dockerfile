FROM python:3.9.10-slim-buster

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY kasa_power_plug.py .
COPY kasa_utilities.py .
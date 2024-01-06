FROM python:3.11-slim as build

COPY requirements.txt main.py finnhub_utilities.py influx_client.py stock_prices_payload.json /

RUN pip install -r /requirements.txt

CMD python3 main.py
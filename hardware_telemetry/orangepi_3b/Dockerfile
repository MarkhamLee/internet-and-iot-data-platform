FROM python:3.11-slim as build

RUN apt-get update -y && apt-get install -y gcc  python3-dev

COPY requirements.txt orangepi3b_data.py main.py /
RUN pip install -r /requirements.txt

CMD python3 main.py 
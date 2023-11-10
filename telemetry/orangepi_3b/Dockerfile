FROM python:3.11-slim as build

RUN apt-get update -y && apt-get install -y gcc  python3-dev

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY deviceTools.py .
COPY main.py .
COPY linux_cpu_data.py .

CMD python3 main.py 
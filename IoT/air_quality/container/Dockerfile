FROM python:3.12-slim as build

COPY requirements.txt logging_util.py air_quality.py main.py communications_utilities.py  / 

RUN pip install -r /requirements.txt

CMD python3 main.py
FROM python:alpine as build

COPY requirements.txt logging_util.py air_quality.py main.py communications_utilities.py  / 

RUN pip install -r /requirements.txt

CMD python3 main.py
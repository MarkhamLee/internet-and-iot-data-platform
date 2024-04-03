FROM python:alpine as build

COPY requirements.txt main.py logging_util.py kasa_utilities.py /

RUN pip install -r /requirements.txt

CMD python3 main.py
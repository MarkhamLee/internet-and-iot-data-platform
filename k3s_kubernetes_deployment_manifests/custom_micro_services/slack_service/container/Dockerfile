FROM python:3.11-slim as build

COPY requirements.txt server.py slack_utilities.py logging_util.py wsgi.py  /

RUN pip install -r /requirements.txt

EXPOSE 6200

CMD ["gunicorn" , "--bind", "0.0.0.0:6200",  "wsgi:app"]
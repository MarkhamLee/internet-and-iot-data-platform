FROM python:alpine as build

COPY main.py linux_lepotato.py requirements.txt  /

RUN apt-get update -y && apt-get install -y gcc  python3-dev

RUN pip install -r /requirements.txt

CMD python3 main.py 
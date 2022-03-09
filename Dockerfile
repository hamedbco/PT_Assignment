# FROM python:3.9-slim-buster
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python-dev \
    curl wget locales

WORKDIR /usr/src/app/ 

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

COPY requirements.txt /usr/src/app/

RUN python3 -m pip install --upgrade pip

RUN pip install  \
    setuptools \
    wheel

RUN pip install -r requirements.txt

COPY . /usr/src/app/

RUN ls -la

RUN chmod +x /usr/src/app/entrypoint.sh

ENV FLASK_APP=app.py

EXPOSE 5000

WORKDIR /usr/src/app/

CMD [ "python3", "app.py" ]

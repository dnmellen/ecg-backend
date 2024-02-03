FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y libpq-dev  # Install libpq-dev for psycopg2

COPY requirements* ./
RUN pip install -r requirements-dev.txt

COPY . ./app

ENV PYTHONPATH=$PYTHONPATH:/app

WORKDIR /app

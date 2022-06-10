# syntax=docker/dockerfile:1

FROM python:3.10-bullseye

WORKDIR /app

RUN apt-get update
RUN apt-get install default-libmysqlclient-dev build-essential -y

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "--chdir", "src", "server:app"]
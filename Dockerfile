FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV DEBUG False
ENV APP_ROOT /code

WORKDIR ${APP_ROOT}

COPY ./requirements.txt requirements.txt

RUN apt-get update && \
  apt-get install -y \
  locales \
  locales-all \
  build-essential \
  libpcre3 \
  libpcre3-dev \
  curl \
  libzbar-dev \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && apt-get clean --dry-run

COPY ./mime.types /etc/mime.types
COPY ./uwsgi.ini /conf/uwsgi.ini
COPY . /code

# Start uWSGI
CMD [ "uwsgi", "--ini", "/conf/uwsgi.ini"]

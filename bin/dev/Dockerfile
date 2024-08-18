FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV DEBUG True
COPY requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
ADD . .

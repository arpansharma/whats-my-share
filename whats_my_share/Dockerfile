# pull official base image
FROM python:3

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# copy project
COPY . /code/

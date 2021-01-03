# pull official base image
FROM python:3.8-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY ./whats_my_share ./

ENTRYPOINT ["gunicorn", "whats_my_share.wsgi:application", "--workers=2", "--bind=0.0.0.0:8000"]

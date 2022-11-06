FROM python:3.11-slim-buster

ENV BUILD_DEPS gcc g++

RUN apt-get update && apt-get install -y $BUILD_DEPS --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN pip install cchardet

RUN apt-get purge -y --auto-remove $BUILD_DEPS

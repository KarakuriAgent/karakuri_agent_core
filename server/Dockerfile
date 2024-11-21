FROM python:3.10-slim

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 karakuri && useradd -u 1000 -g karakuri karakuri

RUN mkdir -p /home/karakuri/.cache/pip && \
    mkdir -p /home/karakuri/.local && \
    chown -R karakuri:karakuri /home/karakuri

WORKDIR /home/karakuri/workspace/server
RUN chown karakuri:karakuri /home/karakuri/workspace/server

USER karakuri

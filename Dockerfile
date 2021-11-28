FROM python:3.9-slim

COPY ./src/app/ ./app/
COPY ./requirements.txt ./

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    git \
    git-crypt \
    unzip \
    chromium-driver \
    gcc \
    make

RUN apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# create a virtual environment
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install -r requirements.txt

#RUN pip install -r requirements.txt

WORKDIR /app


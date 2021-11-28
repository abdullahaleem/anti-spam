FROM python:3.9-slim

COPY ./src/app/ /src/app/
COPY ./src/pipelines /src/pipelines/
COPY ./src/notebooks /src/notebooks/
COPY ./requirements.txt /requirements.txt
COPY ./entrypoint.sh /entrypoint.sh
COPY ./.env /.env

#WORKDIR /src

# making entrypoint.sh executable. it might work without this, but it's safer
RUN chmod +x /entrypoint.sh

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

RUN apt-get install python3.9-venv -y

# create a virtual environment and install requirements
# /opt/venv is the standard for path to the virtual environment
# currently, the virtual environment is not activated when we do /bin/bash
# we can actiavte it by running source /opt/venv/bin/activate
RUN python3 -m venv /opt/venv && /opt/venv/bin/python -m pip install -r requirements.txt
#RUN pip install -r requirements.txt

RUN apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# running the pipelines
# we are downloading model in the docker container when tis being build
# this is not the most effective and efficent way to do this
RUN /opt/venv/bin/python -m pypyr src/pipelines/ml-model-download

CMD ["entrypoint.sh"]
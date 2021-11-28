FROM python:3.9-slim

COPY ./src/app/ /src/app/
COPY ./requirements.txt /src/requirements.txt
COPY ./entrypoint.sh /src/entrypoint.sh
COPY .env /src/.env

# # making entrypoint.sh executable. it might work without this, but it's safer
# RUN chmod +x /src/entrypoint.sh

# RUN apt-get update && \
#     apt-get install -y \
#     build-essential \
#     python3-dev \
#     python3-setuptools \
#     git \
#     git-crypt \
#     unzip \
#     chromium-driver \
#     gcc \ 
#     make 

# RUN apt-get install python3.9-venv -y

# # create a virtual environment and install requirements
# # /opt/venv is the standard for path to the virtual environment
# # currently, the virtual environment is not activated when we do /bin/bash
# RUN python3 -m venv /opt/venv && /opt/venv/bin/python -m pip install -r requirements.txt
# #RUN pip install -r requirements.txt

# RUN apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# CMD ["entrypoint.sh"]
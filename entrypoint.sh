#!bin/bash

# equal to the environment port that comes in or the default port of 8000
RUN_PORT=${PORT:-8000}

# runs the gunicorn server in the virtual environment inside docker container
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm -k uvicorn.workers.UvicornWorker --bind "0.0.0.0:${RUN_PORT}" src.app.main:app
FROM python:3-slim

COPY . /app
WORKDIR /app

RUN pip install pipenv \
    && pipenv install --system --ignore-pipfile

CMD ["gunicorn", "-w 3", "-b :80", "juno.wsgi"]

# TODO: Consider switching from wsgi to asgi as follows:
# gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker

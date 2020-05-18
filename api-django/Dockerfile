FROM python:3-slim

COPY . /app
WORKDIR /app

RUN pip install pipenv \
    && pipenv install --system --ignore-pipfile

# TODO: make the database external
#       (currently very small and read only)
RUN python manage.py migrate \
    && python manage.py loaddev

CMD ["gunicorn", "-w 3", "-b :80", "juno.wsgi"]

# TODO: Consider switching from wsgi to asgi as follows:
# gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker

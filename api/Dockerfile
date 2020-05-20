FROM python:3-slim

# pass version at build time (displayed in footer)
ARG VERSION='VERSION'
ENV VERSION=$VERSION

WORKDIR /app

# install (separation of COPY to help cache dependencies)
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv \
    && pipenv install --system --ignore-pipfile

# add rest of code
COPY . /app

# TODO: make the database external
#       (currently very small and read only)
RUN python manage.py migrate \
    && python manage.py loaddev \
    && python manage.py collectstatic

CMD ["gunicorn", "-w 3", "-b :80", "juno.wsgi"]

# TODO: Consider switching from wsgi to asgi as follows:
# gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker

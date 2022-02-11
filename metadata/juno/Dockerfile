FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR /app

# install dependencies
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv coverage==5.5 \
    && pipenv install --system --ignore-pipfile

# add rest of code
COPY . /app

ENV      GUNICORN_PORT=80
ENV      GUNICORN_WORKERS=2
ENV      GUNICORN_TIMEOUT=60
EXPOSE   "$GUNICORN_PORT"
CMD      gunicorn -w "${GUNICORN_WORKERS}" -t "${GUNICORN_TIMEOUT}" -b ":${GUNICORN_PORT}" metadata.wsgi

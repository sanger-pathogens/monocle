FROM     gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

# mandatory build argument PROJECT defined the project for which we are building an image
# this must match the name of a subdirectory which contains the files specific to the project
ARG      PROJECT
RUN      test -n "$PROJECT"

WORKDIR  /app

# install dependencies
COPY     common/Pipfile common/Pipfile.lock /app/
RUN      pip install pipenv coverage==5.5 && \
         pipenv install --system --ignore-pipfile

# add code common to all projects
COPY     common      /app

# add code specific to the project for which we are building this metadata API image
COPY     ${PROJECT}  /app

# sanity check:  existence of crucial files that should have been copied from project subdirectory
RUN      [ -f /app/config.json ]
RUN      [ -f /app/metadata/interface/openapi.yml ]
RUN      [ -f /app/metadata/api/model/metadata.py ]
RUN      [ -f /app/metadata/api/model/in_silico_data.py ]
RUN      [ -f /app/metadata/api/model/qc_data.py ]

# cache bust to update quickly the image build time
# pass a new value as CACHE_BUST, e.g. with `--build-arg "CACHE_BUST=$(date)"`
ARG      CACHE_BUST
RUN      echo "$CACHE_BUST" > /dev/null

ENV      GUNICORN_PORT=80
ENV      GUNICORN_WORKERS=2
ENV      GUNICORN_TIMEOUT=60
EXPOSE   "$GUNICORN_PORT"
CMD      exec gunicorn -w "${GUNICORN_WORKERS}" -t "${GUNICORN_TIMEOUT}" -b ":${GUNICORN_PORT}" metadata.wsgi

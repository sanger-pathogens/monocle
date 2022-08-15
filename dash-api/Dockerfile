FROM     gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR  /app

# Keep `apt-get update` and `apt-get install` in the same `RUN` to prevent `apt-get install` from
# potentially installing old package versions (see https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run).
RUN      apt-get update -qq && apt-get install -y \
                  libldap2-dev \
                  libsasl2-dev \
         && rm -rf /var/lib/apt/lists/*

RUN      pip install flask==2.1.1                     \
                  flask-cors==3.0.10                  \
                  gunicorn==20.1.0                    \
                  python-ldap==3.3.1                  \
                  pandas==1.2.2                       \
                  PyYAML==5.3.1                       \
                  python-dateutil==2.8.1              \
                  'connexion[swagger-ui]'             \
                  mysqlclient==2.0.1                  \
                  SQLAlchemy==1.3.23                  \
                  coverage==5.5

COPY     . /app

# cache bust to update quickly the image build time
# pass a new value as CACHE_BUST, e.g. with `--build-arg "CACHE_BUST=$(date)"`
ARG      CACHE_BUST
RUN      echo "$CACHE_BUST" > /dev/null

# Temp hack until we have a final version of the dash DataSources component available
ENV      PYTHONPATH "${PYTHONPATH}:./dash/api:./dash/api/service"

ENV      GUNICORN_PORT=5000
ENV      GUNICORN_WORKERS=2
ENV      GUNICORN_TIMEOUT=60
EXPOSE   "$GUNICORN_PORT"
CMD      exec gunicorn -w "${GUNICORN_WORKERS}" -t "${GUNICORN_TIMEOUT}" -b ":${GUNICORN_PORT}" dash.wsgi

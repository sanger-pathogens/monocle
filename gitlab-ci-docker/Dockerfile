# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name

# codecov removed 2021-04-15 after security breach notice
      

###################################################################################################################################

# Dash unit test image

FROM  python:3.7 AS gitlab-dash-unit-tests
ARG   DEBIAN_FRONTEND=noninteractive
# RUN   pip install codecov
RUN   pip install dash==1.19.0         \
                  dash-daq==0.5.0      \
                  flask==1.1.2         \
                  gunicorn==20.0.4     \
                  mysqlclient==2.0.1   \
                  pandas==1.2.2        \
                  PyYAML==5.3.1        \
                  SQLAlchemy==1.3.23

###################################################################################################################################

# Front-end unit test image

FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/node:alpine as gitlab-frontend-unit-tests

WORKDIR /app
COPY ../frontend/package.json ../frontend/package-lock.json /app/
RUN npm set audit false &&\
  npm config set fetch-timeout 1000000 &&\
  npm install --silent
ENV PATH /app/node_modules/.bin:$PATH


###################################################################################################################################

# Metadata unit test image

FROM  python:3.7 AS gitlab-metadata-unit-tests
ARG   DEBIAN_FRONTEND=noninteractive
# RUN   pip install codecov
RUN   pip install pipenv
      
###################################################################################################################################
      
# dind image

# This provides the docker daemon.  It runs as a service in gitlab CI, allowing docker commands
# to be executed from within the gitlab-ci-docker image.

# This build just adds Sanger-specific network configuration to docker:dind

FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

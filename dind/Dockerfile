# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name


###################################################################################################################################

# API unit test image

# python base image with pipenv and codecov

FROM  python:3.7 AS gitlab-api-unit-tests
RUN   pip install pipenv codecov


###################################################################################################################################

# App unit test image

# nodejs image with python codecov package installed

FROM  node:12 AS gitlab-ui-unit-tests
ARG   DEBIAN_FRONTEND=noninteractive
RUN   apt-get -qq update && \
      apt-get install -y python-pip && \
      pip install codecov


###################################################################################################################################

# Dash unit test image

FROM  python:3.7 AS gitlab-dash-unit-tests
ARG   DEBIAN_FRONTEND=noninteractive
RUN   pip install codecov
RUN   pip install dash==1.19.0         \
                  dash-daq==0.5.0      \
                  flask==1.1.2         \
                  gunicorn==20.0.4     \
                  mysqlclient==2.0.1   \
                  pandas==1.2.2        \
                  PyYAML==5.3.1        \
                  SQLAlchemy==1.3.23

      
###################################################################################################################################
      
# dind image

# This provides the docker daemon.  It runs as a service in gitlab CI, allowing docker commands
# to be executed from within the gitlab-ci-docker image.

# This build just adds Sanger-specific network configuration to docker:dind

FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

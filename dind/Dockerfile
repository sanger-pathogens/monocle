# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name

###################################################################################################################################

# docker image

# This provides a docker client, allowing docker compose commands to build images and run containers, but
# note the docker daemon is provides by the gitlab-ci-dind image (runs as service in gitlab CI) so you cannot
# run this as a standalone container (e.g. on you development machine) and execute docker commands in it.

FROM  docker:19 AS gitlab-ci-docker
ARG   DEBIAN_FRONTEND=noninteractive
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apk update && \
      apk add  docker-compose nodejs npm yarn
      
      
###################################################################################################################################

# docker image

# This provides a docker client, allowing docker compose commands to build images and run containers, but
# note the docker daemon is provides by the gitlab-ci-dind image (runs as service in gitlab CI) so you cannot
# run this as a standalone container (e.g. on you development machine) and execute docker commands in it.

# Usually a docker:whatever image would be used for this purpose, but we a cypress environment
# including nodesjs and yarn, so require own own build.  This may be flaky.
        
FROM  ubuntu:20.04 AS gitlab-ci-node-with-docker
ARG   DEBIAN_FRONTEND=noninteractive
# don't think this config is needed here (this image doens't run a daemon) but, at worst, it's harmless
COPY  etc-docker-daemon.json /etc/docker/daemon.json
# docker & docker-compose
# note the debian repos have quite old versions, so use docker's debian repo
# and download docker-compose from github
RUN   apt-get update -qq && \
      apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
      apt-get update -qq && \
      apt-get install -y docker-ce && \
      curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
      chmod a+rx /usr/local/bin/docker-compose
# nodejs from own repo
RUN   curl -fsSL https://deb.nodesource.com/setup_12.x | bash - && \
      apt update -qq && \
      apt-get install -y nodejs
# yarn from own repo
RUN   curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg |  apt-key add - && \
      add-apt-repository "deb https://dl.yarnpkg.com/debian/ stable main" && \
      apt update -qq && \
      apt-get install -y yarn
# cypress dependencies (https://docs.cypress.io/guides/getting-started/installing-cypress.html#System-requirements)
RUN   apt-get update -qq && \
      apt-get install -y jq libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb

      
###################################################################################################################################
      
# dind image

# This provides the docker daemon.  It runs as a service in gitlab CI, allowing docker commands
# to be executed from within the gitlab-ci-docker image.

# This build just adds Sanger-specific network configuration to docker:dind

FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name


# caution: docker base image is alpine, and cypress (installed by yarn) is broken 
FROM  docker:19 AS gitlab-ci-docker
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apk update && \
      apk add  docker-compose nodejs npm yarn
        
        
FROM  ubuntu:20.04 AS gitlab-ci-node-with-docker
# docker & docker-compose
# note the debian repos have quite old versions, do use docker's debian repo
# and downlaod docker-compose from github
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apt-get update -qq && \
      apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
      curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
      apt-get update -qq && \
      apt-get install -y docker-ce && \
      curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
      chmod a+rx /usr/local/bin/docker-compose
# node etc.
RUN   apt update -qq && \
      apt-get install -y nodejs npm yarn
# cypress dependencies
ARG   DEBIAN_FRONTEND=noninteractive
RUN   apt-get update -qq && \
      apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb


FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name


FROM  docker:19 AS gitlab-ci-docker
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apk update && \
      apk add  docker-compose nodejs npm yarn
        
FROM  node:12 AS gitlab-ci-node-with-docker
# docker
RUN   apt-get update -qq && \
      apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
      curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
      apt-get update -qq && \
      apt-get install -y docker-ce docker-compose && \
      docker --version
COPY  etc-docker-daemon.json /etc/docker/daemon.json
# cypress dependencies
RUN   apt-get update -qq && \
      apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb


FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

# images for use in CI

# N.B. the build script will use the stage (AS ...) name as the image name


FROM  docker:19 AS gitlab-ci-docker
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apk update && \
      apk add  docker-compose nodejs npm yarn xvfb
        

FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

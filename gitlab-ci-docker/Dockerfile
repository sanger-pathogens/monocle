# dind image

# This provides the docker daemon.  It runs as a service in gitlab CI, allowing docker commands
# to be executed from within the gitlab-ci-docker image.

# This build just adds Sanger-specific network configuration to docker:dind

FROM  docker:20.10.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

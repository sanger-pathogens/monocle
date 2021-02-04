# docker-in-docker image for use with gitlab-ci
# network neeeds to be configured to avoid clash with Sanger private network
# build with
# 
#    TAG=gitlab-ci-dind:$(git rev-parse HEAD)
#    REGISTRY=gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle
#    docker login "${REGISTRY}"
#    docker build --tag "${TAG}" .
#    docker tag "${TAG}" "${REGISTRY}/${TAG}"
#    docker push "${REGISTRY}/$TAG"

FROM  docker:19.03.14-dind AS gitlab-ci-docker
COPY  etc-docker-daemon.json /etc/docker/daemon.json
RUN   apk update && \
      apk add docker-compose nodejs npm yarn
        
FROM  docker:19.03.14-dind AS gitlab-ci-dind
COPY  etc-docker-daemon.json /etc/docker/daemon.json

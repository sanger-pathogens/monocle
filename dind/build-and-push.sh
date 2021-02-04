#!/usr/bin/env bash

set -e

DOCKER_BUILDKIT=1
COMMIT=$(git rev-parse HEAD)
REGISTRY=gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle

docker_login_done=false
if [ ! -z ${GITLAB_USER} ] && [ ! -z ${GITLAB_TOKEN+x} ]; then
   echo "${GITLAB_TOKEN}" | docker login -u "${GITLAB_USER}" --password-stdin "${REGISTRY}"
   if [ 0 -eq $? ]; then
      docker_login_done=true
   fi
fi
# if environment variables not set/didn't work
if [ true != "${docker_login_done}" ]; then
   docker login ${REGISTRY} || exit 1
fi


for IMAGE in gitlab-ci-docker gitlab-ci-dind
do

   remote_image="${REGISTRY}/${IMAGE}"
   
   # build image and tag with commit SHA
   this_build="${IMAGE}:${COMMIT}"
   echo "🐳 Building ${this_build} 🐳"
   docker build --build-arg  BUILDKIT_INLINE_CACHE=1   \
                --cache-from "${remote_image}:latest"  \
                --tag        ${this_build} .
                
   # push image tagged with commit SHA and with 'latest' tag
   for TAG in ${COMMIT} 'latest'
   do
      this_push="${remote_image}:${TAG}"
      echo "🐳 Pushing ${this_push} 🐳"
      docker tag  ${this_build} "${this_push}"
      docker push "${this_push}"
   done
   
done

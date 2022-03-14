# Running unit tests on a personal development box

Running unit tests on a devel box isn't straightforward.

Assuming you are working in `/metadata/juno`, unit tests may be run in a docker container thusly:

``` 
TEST_IMAGE='monocle-metadata:local_build'
DOCKER_BUILDKIT=1 docker build --tag "$TEST_IMAGE" . && \
docker run --rm -it "$TEST_IMAGE" /app/unittests.sh
```

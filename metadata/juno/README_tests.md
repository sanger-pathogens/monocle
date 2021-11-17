# Running unit tests on a personal development box

Running unit tests on a devel box isn't straightforward.

Assuming `pwd` is `/metadata/juno` to your local monocle repo:

``` 
TEST_IMAGE='monocle-metadata:local_build'
DOCKER_BUILDKIT=1 docker build --tag "$TEST_IMAGE" . && \
docker run --rm -it  -v "$(pwd)":'/testdir' "$TEST_IMAGE" bash -c "cd /testdir && ./unittests.sh"
```

(If you have changed `Dockerfile` since the last unstable built, you will need to run your more recent docker image.)

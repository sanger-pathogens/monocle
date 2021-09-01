# Running unit tests on a personal development box

Running unit tests on a devel box isn't straightforward.

Try this:

``` 
LOCAL_MONOCLE_REPO=/your/local/repo
docker run --rm -it  -v "${LOCAL_MONOCLE_REPO}/metadata/juno":'/testdir'
       gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/monocle-metadata:unstable \
       bash -c "cd /testdir && ./unittests.sh"
```

(If you have changed `Dockerfile` since the last unstable built, you will need to run your more recent docker image.)

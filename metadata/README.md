# Metadata API
This component provides an API for accessing and updating metadata in the Monocle database.

## Building a local Docker image
A local docker image can be built using the following:
```
cd metadata/juno
docker build --rm -t metadata-api:test .
```

## Running unit tests in situ
Use the following:
```
cd monocle
docker run  -it --rm metadata-api:test /app/unittests.sh
```

## Running up
The service can be run locally outside of compose using the following:
```
cd monocle
docker run -v `pwd`/metadata/juno/my.cnf:/app/my.cnf -p3001:80 -it --rm metadata-api:test
```

# Testing
If you need to run up a swagger UI for testing then set the ENABLE_SWAGGER_UI environment variable to *true* when running up the container.
The swagger UI can then be accessed on:
```
http://0.0.0.0:3001/metadata/ui/
```
